"""工作流管理器"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from langgraph.graph import StateGraph, END
from .workflow_states import WorkflowState, WorkflowStatus, WorkflowType
from .nodes import WorkflowNodes
from src.storage import FileStorage, VectorStorage, ObsidianStorage
from src.db.session import db_transaction
from src.db.repositories import WorkflowRepository, ExecutionRepository
from src.db.models import WorkflowInstance
from src.services.notification import NotificationService, NotificationType

class WorkflowManager:
    """工作流管理器"""

    def __init__(
        self,
        file_storage: FileStorage,
        vector_storage: VectorStorage,
        obsidian_storage: ObsidianStorage,
        notification_service: NotificationService,
    ):
        self.file_storage = file_storage
        self.vector_storage = vector_storage
        self.obsidian_storage = obsidian_storage
        self.notification_service = notification_service
        self.nodes = WorkflowNodes(file_storage, vector_storage, obsidian_storage)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """构建工作流图"""
        workflow = StateGraph(WorkflowState)

        workflow.add_node("fetch_news", self.nodes.fetch_news)
        workflow.add_node("update_data", self.nodes.update_data)
        workflow.add_node("generate_report", self.nodes.generate_report)
        workflow.add_node("await_approval", self.nodes.await_approval)
        workflow.add_node("archive_result", self.nodes.archive_result)
        workflow.add_node("notify_user", self.nodes.notify_user)

        workflow.set_entry_point("fetch_news")

        workflow.add_edge("fetch_news", "update_data")
        workflow.add_edge("update_data", "generate_report")
        workflow.add_edge("generate_report", "await_approval")

        workflow.add_conditional_edges(
            "await_approval",
            self._approval_decision,
            {
                "continue": "archive_result",
                "reject": END,
            }
        )

        workflow.add_edge("archive_result", "notify_user")
        workflow.add_edge("notify_user", END)

        return workflow.compile()

    def _approval_decision(self, state: WorkflowState) -> str:
        """审批决策函数"""
        approval_result = state.context.get("approval_result")
        if approval_result == "approve":
            return "continue"
        return "reject"

    def create_workflow(
        self,
        workflow_type: WorkflowType,
        context: Dict[str, Any] = None,
    ) -> WorkflowState:
        """创建工作流实例"""
        workflow_id = str(uuid.uuid4())
        state = WorkflowState(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            status=WorkflowStatus.PENDING,
            context=context or {},
        )

        with db_transaction() as session:
            repo = WorkflowRepository(session)
            db_workflow = repo.create(
                workflow_type=workflow_type.value,
                context=state.context,
            )
            state.workflow_id = str(db_workflow.id)

        return state

    def trigger_workflow(self, workflow_type: WorkflowType, context: Dict[str, Any] = None) -> WorkflowState:
        """触发工作流执行"""
        state = self.create_workflow(workflow_type, context)

        try:
            final_state = self.graph.invoke(state)

            with db_transaction() as session:
                repo = WorkflowRepository(session)
                repo.update_status(
                    uuid.UUID(final_state.workflow_id),
                    final_state.status.value,
                    final_state.current_step,
                    final_state.error,
                )
                if final_state.result:
                    repo.update_result(uuid.UUID(final_state.workflow_id), final_state.result)

            if final_state.status == WorkflowStatus.WAITING_APPROVAL:
                self.notification_service.notify_approval_required(
                    final_state.workflow_id,
                    final_state.workflow_type.value,
                    final_state.current_step,
                )
            elif final_state.status == WorkflowStatus.COMPLETED:
                self.notification_service.notify_workflow_completed(
                    final_state.workflow_id,
                    final_state.workflow_type.value,
                    final_state.result or {},
                )
            elif final_state.status == WorkflowStatus.FAILED:
                self.notification_service.notify_workflow_failed(
                    final_state.workflow_id,
                    final_state.workflow_type.value,
                    final_state.error or "Unknown error",
                )

            return final_state

        except Exception as e:
            state.status = WorkflowStatus.FAILED
            state.error = str(e)
            self.notification_service.notify_workflow_failed(
                state.workflow_id,
                state.workflow_type.value,
                state.error,
            )
            return state

    def submit_approval(self, workflow_id: str, approval_result: str, approved_content: str = None) -> bool:
        """提交审批结果"""
        try:
            with db_transaction() as session:
                repo = WorkflowRepository(session)
                workflow_uuid = uuid.UUID(workflow_id)
                workflow = repo.get_by_id(workflow_uuid)

                if not workflow:
                    return False

                workflow.status = "running"
                workflow.context = workflow.context or {}
                workflow.context["approval_result"] = approval_result

                if approved_content and approval_result == "approve":
                    workflow.result = {"report": approved_content}

                from src.db.repositories import FeedbackRepository
                feedback_repo = FeedbackRepository(session)
                feedback_repo.create(
                    workflow_instance_id=workflow_uuid,
                    feedback_type=approval_result,
                    content=approved_content,
                )

            return True

        except Exception as e:
            print(f"Failed to submit approval: {e}")
            return False
