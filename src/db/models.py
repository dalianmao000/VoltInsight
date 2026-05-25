"""数据库模型"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from typing import Optional

Base = declarative_base()

class WorkflowInstance(Base):
    """工作流实例"""
    __tablename__ = "workflow_instances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    current_step = Column(String(50))
    context = Column(JSON, default=dict)
    result = Column(JSON, default=dict)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    executions = relationship("ExecutionHistory", back_populates="workflow", cascade="all, delete-orphan")
    feedbacks = relationship("AnalystFeedback", back_populates="workflow", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "workflow_type": self.workflow_type,
            "status": self.status,
            "current_step": self.current_step,
            "context": self.context,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class ExecutionHistory(Base):
    """执行历史"""
    __tablename__ = "execution_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_instance_id = Column(UUID(as_uuid=True), ForeignKey("workflow_instances.id", ondelete="CASCADE"))
    step_name = Column(String(50), nullable=False)
    step_status = Column(String(20))
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    duration_ms = Column(Integer, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow)

    workflow = relationship("WorkflowInstance", back_populates="executions")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "workflow_instance_id": str(self.workflow_instance_id),
            "step_name": self.step_name,
            "step_status": self.step_status,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "duration_ms": self.duration_ms,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
        }

class AnalystFeedback(Base):
    """分析师反馈"""
    __tablename__ = "analyst_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_instance_id = Column(UUID(as_uuid=True), ForeignKey("workflow_instances.id", ondelete="CASCADE"))
    feedback_type = Column(String(20))  # "approve" / "reject" / "modify"
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    workflow = relationship("WorkflowInstance", back_populates="feedbacks")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "workflow_instance_id": str(self.workflow_instance_id),
            "feedback_type": self.feedback_type,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class ScheduledTask(Base):
    """定时任务"""
    __tablename__ = "scheduled_tasks"

    id = Column(String(100), primary_key=True)
    workflow_type = Column(String(50), nullable=False)
    cron_expression = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "workflow_type": self.workflow_type,
            "cron_expression": self.cron_expression,
            "is_active": self.is_active,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }