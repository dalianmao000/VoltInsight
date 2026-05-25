"""数据访问层"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from .models import WorkflowInstance, ExecutionHistory, AnalystFeedback, ScheduledTask

class WorkflowRepository:
    """工作流仓储"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, workflow_type: str, context: dict = None) -> WorkflowInstance:
        """创建工作流实例"""
        workflow = WorkflowInstance(
            id=uuid.uuid4(),
            workflow_type=workflow_type,
            status="pending",
            context=context or {},
        )
        self.session.add(workflow)
        self.session.commit()
        self.session.refresh(workflow)
        return workflow

    def get_by_id(self, workflow_id: uuid.UUID) -> Optional[WorkflowInstance]:
        """根据 ID 获取工作流实例"""
        return self.session.query(WorkflowInstance).filter(WorkflowInstance.id == workflow_id).first()

    def update_status(
        self,
        workflow_id: uuid.UUID,
        status: str,
        current_step: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Optional[WorkflowInstance]:
        """更新工作流状态"""
        workflow = self.get_by_id(workflow_id)
        if workflow:
            workflow.status = status
            if current_step:
                workflow.current_step = current_step
            if error:
                workflow.error = error
            workflow.updated_at = datetime.utcnow()
            self.session.commit()
        return workflow

    def update_result(self, workflow_id: uuid.UUID, result: dict) -> Optional[WorkflowInstance]:
        """更新工作流结果"""
        workflow = self.get_by_id(workflow_id)
        if workflow:
            workflow.result = result
            workflow.updated_at = datetime.utcnow()
            self.session.commit()
        return workflow

    def list_by_status(self, status: str, limit: int = 100) -> List[WorkflowInstance]:
        """根据状态查询工作流"""
        return (
            self.session.query(WorkflowInstance)
            .filter(WorkflowInstance.status == status)
            .order_by(WorkflowInstance.created_at.desc())
            .limit(limit)
            .all()
        )

    def list_all(self, limit: int = 100) -> List[WorkflowInstance]:
        """查询所有工作流"""
        return (
            self.session.query(WorkflowInstance)
            .order_by(WorkflowInstance.created_at.desc())
            .limit(limit)
            .all()
        )


class ExecutionRepository:
    """执行历史仓储"""

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        workflow_instance_id: uuid.UUID,
        step_name: str,
        step_status: str,
        input_data: dict = None,
        output_data: dict = None,
        duration_ms: int = None,
    ) -> ExecutionHistory:
        """创建执行记录"""
        execution = ExecutionHistory(
            id=uuid.uuid4(),
            workflow_instance_id=workflow_instance_id,
            step_name=step_name,
            step_status=step_status,
            input_data=input_data or {},
            output_data=output_data or {},
            duration_ms=duration_ms,
        )
        self.session.add(execution)
        self.session.commit()
        self.session.refresh(execution)
        return execution

    def get_by_workflow(self, workflow_instance_id: uuid.UUID) -> List[ExecutionHistory]:
        """获取工作流的所有执行记录"""
        return (
            self.session.query(ExecutionHistory)
            .filter(ExecutionHistory.workflow_instance_id == workflow_instance_id)
            .order_by(ExecutionHistory.executed_at)
            .all()
        )


class FeedbackRepository:
    """反馈仓储"""

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        workflow_instance_id: uuid.UUID,
        feedback_type: str,
        content: str = None,
    ) -> AnalystFeedback:
        """创建反馈"""
        feedback = AnalystFeedback(
            id=uuid.uuid4(),
            workflow_instance_id=workflow_instance_id,
            feedback_type=feedback_type,
            content=content,
        )
        self.session.add(feedback)
        self.session.commit()
        self.session.refresh(feedback)
        return feedback

    def get_by_workflow(self, workflow_instance_id: uuid.UUID) -> List[AnalystFeedback]:
        """获取工作流的所有反馈"""
        return (
            self.session.query(AnalystFeedback)
            .filter(AnalystFeedback.workflow_instance_id == workflow_instance_id)
            .order_by(AnalystFeedback.created_at)
            .all()
        )