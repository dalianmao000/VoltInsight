"""工作流节点定义"""
import time
from typing import Dict, Any, Callable
from .workflow_states import WorkflowState, WorkflowStatus
from src.skills.research_news import ResearchNewsSkill
from src.skills.research_data import ResearchDataSkill
from src.skills.research_report import ResearchReportSkill
from src.skills.base import SkillContext
from src.storage import FileStorage, VectorStorage, ObsidianStorage

# 节点函数类型
NodeFunc = Callable[[WorkflowState], WorkflowState]

class WorkflowNodes:
    """工作流节点集合"""

    def __init__(self, file_storage: FileStorage, vector_storage: VectorStorage, obsidian_storage: ObsidianStorage):
        self.file_storage = file_storage
        self.vector_storage = vector_storage
        self.obsidian_storage = obsidian_storage
        self.news_skill = ResearchNewsSkill()
        self.data_skill = ResearchDataSkill()
        self.report_skill = ResearchReportSkill()

    def fetch_news(self, state: WorkflowState) -> WorkflowState:
        """获取新闻节点"""
        state.current_step = "fetch_news"
        state.status = WorkflowStatus.RUNNING
        start_time = time.time()

        try:
            keywords = state.context.get("keywords", ["电池材料", "新能源汽车"])
            news_content = state.context.get("news_content", "")

            if not news_content:
                news_content = f"请获取关于 {', '.join(keywords)} 的最新新闻"

            context = SkillContext(user_input=news_content, config={})
            result = self.news_skill.execute(context)

            state.context["news_result"] = result.content if result.success else ""
            state.context["news_error"] = result.error if not result.success else None

            duration_ms = int((time.time() - start_time) * 1000)
            state.context["fetch_news_duration_ms"] = duration_ms

        except Exception as e:
            state.error = f"fetch_news failed: {str(e)}"
            state.status = WorkflowStatus.FAILED

        return state

    def update_data(self, state: WorkflowState) -> WorkflowState:
        """更新数据节点"""
        state.current_step = "update_data"
        state.status = WorkflowStatus.RUNNING
        start_time = time.time()

        try:
            data_content = state.context.get("data_content", "")

            if not data_content:
                data_content = "数据更新任务执行"

            context = SkillContext(user_input=data_content, config={})
            result = self.data_skill.execute(context)

            state.context["data_result"] = result.content if result.success else ""
            state.context["data_error"] = result.error if not result.success else None

            duration_ms = int((time.time() - start_time) * 1000)
            state.context["update_data_duration_ms"] = duration_ms

        except Exception as e:
            state.error = f"update_data failed: {str(e)}"
            state.status = WorkflowStatus.FAILED

        return state

    def generate_report(self, state: WorkflowState) -> WorkflowState:
        """生成报告节点"""
        state.current_step = "generate_report"
        state.status = WorkflowStatus.RUNNING
        start_time = time.time()

        try:
            news_result = state.context.get("news_result", "")
            data_result = state.context.get("data_result", "")
            workflow_type = state.workflow_type.value

            if workflow_type == "daily_briefing":
                report_content = f"""# 每日早报

## 今日新闻摘要
{news_result}

## 数据更新
{data_result}

## 分析师备注
自动生成，请人工审核。
"""
            elif workflow_type == "news_review":
                report_content = f"""# 新闻快评

## 新闻内容
{news_result}

## 快评
自动生成，请人工审核。
"""
            else:
                report_content = f"""# 研究报告

## 内容
{news_result}

## 数据
{data_result}
"""

            context = SkillContext(user_input=report_content, config={})
            result = self.report_skill.execute(context)

            state.result = {"report": result.content if result.success else report_content}
            state.context["report_error"] = result.error if not result.success else None

            duration_ms = int((time.time() - start_time) * 1000)
            state.context["generate_report_duration_ms"] = duration_ms

        except Exception as e:
            state.error = f"generate_report failed: {str(e)}"
            state.status = WorkflowStatus.FAILED

        return state

    def await_approval(self, state: WorkflowState) -> WorkflowState:
        """等待审批节点（Human-in-the-Loop）"""
        state.current_step = "await_approval"
        state.status = WorkflowStatus.WAITING_APPROVAL
        return state

    def archive_result(self, state: WorkflowState) -> WorkflowState:
        """归档结果节点"""
        state.current_step = "archive_result"

        try:
            if state.result and "report" in state.result:
                filename = f"{state.workflow_type.value}_{state.workflow_id[:8]}.md"
                self.file_storage.save_draft(
                    state.result["report"],
                    filename,
                    {"workflow_id": state.workflow_id, "workflow_type": state.workflow_type.value}
                )

                self.vector_storage.add_document(
                    doc_id=f"workflow_{state.workflow_id}",
                    content=state.result["report"],
                    metadata={
                        "workflow_id": state.workflow_id,
                        "workflow_type": state.workflow_type.value,
                        "type": "workflow_result"
                    }
                )

            state.status = WorkflowStatus.COMPLETED

        except Exception as e:
            state.error = f"archive_result failed: {str(e)}"
            state.status = WorkflowStatus.FAILED

        return state

    def notify_user(self, state: WorkflowState) -> WorkflowState:
        """通知用户节点"""
        state.current_step = "notify_user"
        return state