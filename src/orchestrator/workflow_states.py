"""工作流状态定义"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

class WorkflowStatus(str, Enum):
    """工作流状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowType(str, Enum):
    """工作流类型枚举"""
    DAILY_BRIEFING = "daily_briefing"
    NEWS_REVIEW = "news_review"
    DATA_UPDATE = "data_update"
    DAILY_SUMMARY = "daily_summary"

@dataclass
class WorkflowState:
    """工作流状态"""
    workflow_id: str
    workflow_type: WorkflowType
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type.value,
            "status": self.status.value,
            "current_step": self.current_step,
            "context": self.context,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkflowState":
        return cls(
            workflow_id=data["workflow_id"],
            workflow_type=WorkflowType(data["workflow_type"]),
            status=WorkflowStatus(data.get("status", "pending")),
            current_step=data.get("current_step", ""),
            context=data.get("context", {}),
            result=data.get("result"),
            error=data.get("error"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.utcnow(),
        )
