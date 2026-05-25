"""数据库测试"""
import pytest
import tempfile
from pathlib import Path
from datetime import datetime
import uuid

from src.db.models import Base, WorkflowInstance, ExecutionHistory, AnalystFeedback
from src.orchestrator.workflow_states import WorkflowState, WorkflowType, WorkflowStatus

def test_workflow_repository():
    """测试工作流仓储"""
    class MockSession:
        pass

    from src.db.repositories import WorkflowRepository
    repo = WorkflowRepository(MockSession())
    assert repo.session is not None

def test_workflow_state_to_dict():
    """测试工作流状态序列化"""
    state = WorkflowState(
        workflow_id="test-123",
        workflow_type=WorkflowType.DAILY_BRIEFING,
        status=WorkflowStatus.PENDING,
        current_step="fetch_news",
    )

    data = state.to_dict()
    assert data["workflow_id"] == "test-123"
    assert data["workflow_type"] == "daily_briefing"
    assert data["status"] == "pending"

def test_workflow_state_serialization():
    """测试工作流状态序列化往返"""
    state = WorkflowState(
        workflow_id="test-456",
        workflow_type=WorkflowType.NEWS_REVIEW,
        status=WorkflowStatus.COMPLETED,
    )

    data = state.to_dict()
    restored = WorkflowState.from_dict(data)

    assert restored.workflow_id == state.workflow_id
    assert restored.workflow_type == state.workflow_type
    assert restored.status == state.status

def test_workflow_status_enum():
    """测试工作流状态枚举"""
    assert WorkflowStatus.PENDING.value == "pending"
    assert WorkflowStatus.RUNNING.value == "running"
    assert WorkflowStatus.WAITING_APPROVAL.value == "waiting_approval"
    assert WorkflowStatus.COMPLETED.value == "completed"
    assert WorkflowStatus.FAILED.value == "failed"
    assert WorkflowStatus.CANCELLED.value == "cancelled"

def test_workflow_type_enum():
    """测试工作流类型枚举"""
    assert WorkflowType.DAILY_BRIEFING.value == "daily_briefing"
    assert WorkflowType.NEWS_REVIEW.value == "news_review"
    assert WorkflowType.DATA_UPDATE.value == "data_update"
    assert WorkflowType.DAILY_SUMMARY.value == "daily_summary"