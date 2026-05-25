"""通知服务"""
import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional
import uuid

class NotificationType(str, Enum):
    """通知类型枚举"""
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    APPROVAL_REQUIRED = "approval_required"
    DAILY_SUMMARY = "daily_summary"

class NotificationService:
    """通知服务"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def notify(
        self,
        notification_type: NotificationType,
        content: dict,
        workflow_id: Optional[str] = None,
    ) -> Path:
        """发送通知到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        filename = f"{notification_type.value}_{timestamp}_{unique_id}.json"
        path = self.output_dir / filename

        notification_data = {
            "type": notification_type.value,
            "workflow_id": workflow_id,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }

        path.write_text(json.dumps(notification_data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def notify_workflow_completed(self, workflow_id: str, workflow_type: str, result: dict) -> Path:
        """通知工作流完成"""
        return self.notify(
            NotificationType.WORKFLOW_COMPLETED,
            {"workflow_type": workflow_type, "result": result},
            workflow_id=workflow_id,
        )

    def notify_workflow_failed(self, workflow_id: str, workflow_type: str, error: str) -> Path:
        """通知工作流失败"""
        return self.notify(
            NotificationType.WORKFLOW_FAILED,
            {"workflow_type": workflow_type, "error": error},
            workflow_id=workflow_id,
        )

    def notify_approval_required(self, workflow_id: str, workflow_type: str, current_step: str) -> Path:
        """通知需要审批"""
        return self.notify(
            NotificationType.APPROVAL_REQUIRED,
            {"workflow_type": workflow_type, "current_step": current_step},
            workflow_id=workflow_id,
        )

    def list_notifications(self, limit: int = 50) -> list:
        """列出最近的notify文件"""
        if not self.output_dir.exists():
            return []
        files = sorted(self.output_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        return [f.name for f in files[:limit]]