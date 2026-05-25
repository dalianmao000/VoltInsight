"""编排层测试"""
import pytest
import tempfile
from datetime import datetime
from pathlib import Path

from src.orchestrator.workflow_states import WorkflowState, WorkflowStatus, WorkflowType
from src.services.notification import NotificationService, NotificationType

def test_workflow_state_creation():
    """测试工作流状态创建"""
    state = WorkflowState(
        workflow_id="test-123",
        workflow_type=WorkflowType.NEWS_REVIEW,
        context={"keywords": ["电池材料"]},
    )

    assert state.workflow_id == "test-123"
    assert state.workflow_type == WorkflowType.NEWS_REVIEW
    assert state.status == WorkflowStatus.PENDING
    assert state.context["keywords"] == ["电池材料"]

def test_notification_service():
    """测试通知服务"""
    with tempfile.TemporaryDirectory() as tmpdir:
        service = NotificationService(Path(tmpdir))
        path = service.notify_workflow_completed(
            workflow_id="test-123",
            workflow_type="daily_briefing",
            result={"report": "test content"},
        )

        assert path.exists()
        content = path.read_text()
        assert "workflow_completed" in content
        assert "test-123" in content

def test_notification_types():
    """测试通知类型枚举"""
    assert NotificationType.WORKFLOW_COMPLETED.value == "workflow_completed"
    assert NotificationType.WORKFLOW_FAILED.value == "workflow_failed"
    assert NotificationType.APPROVAL_REQUIRED.value == "approval_required"
    assert NotificationType.DAILY_SUMMARY.value == "daily_summary"

def test_workflow_state_default_values():
    """测试工作流状态默认值"""
    state = WorkflowState(
        workflow_id="test-default",
        workflow_type=WorkflowType.DATA_UPDATE,
    )

    assert state.status == WorkflowStatus.PENDING
    assert state.current_step == ""
    assert state.context == {}
    assert state.result is None
    assert state.error is None

def test_workflow_state_to_dict_roundtrip():
    """测试工作流状态往返序列化"""
    original = WorkflowState(
        workflow_id="roundtrip-test",
        workflow_type=WorkflowType.DAILY_SUMMARY,
        status=WorkflowStatus.RUNNING,
        current_step="generate_report",
        context={"news_result": "test news"},
        result={"report": "test report"},
    )

    data = original.to_dict()
    restored = WorkflowState.from_dict(data)

    assert restored.workflow_id == original.workflow_id
    assert restored.workflow_type == original.workflow_type
    assert restored.status == original.status
    assert restored.current_step == original.current_step
    assert restored.context == original.context
    assert restored.result == original.result