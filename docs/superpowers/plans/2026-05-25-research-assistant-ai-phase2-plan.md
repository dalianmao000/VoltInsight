# Research Assistant AI Agent - Phase 2 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Phase 2 扩展 - 引入 LangGraph 工作流编排层 + APScheduler 定时任务 + PostgreSQL 状态持久化

**Architecture:** 采用层次架构扩展：新增 Orchestrator 层（LangGraph 工作流引擎 + APScheduler 定时器）、DB 层（PostgreSQL/SQLite + SQLAlchemy ORM）、Services 层（通知服务）。Phase 1 的 Skills/存储层完全保留。

**Tech Stack:** Python 3.11+, LangGraph, APScheduler, SQLAlchemy, PostgreSQL/SQLite

---

## 文件结构

```
p39_VoltInsight/
├── src/
│   ├── orchestrator/           # ⭐ 新增：编排层
│   │   ├── __init__.py
│   │   ├── workflow_manager.py # LangGraph 工作流管理
│   │   ├── scheduler.py       # APScheduler 定时器
│   │   └── workflow_states.py # 工作流状态定义
│   ├── db/                     # ⭐ 新增：数据库层
│   │   ├── __init__.py
│   │   ├── models.py          # SQLAlchemy 模型
│   │   ├── session.py         # 数据库会话
│   │   └── repositories.py   # 数据访问层
│   ├── services/              # ⭐ 新增：服务层
│   │   ├── __init__.py
│   │   └── notification.py   # 通知服务
│   ├── skills/               # Phase 1 保留
│   ├── storage/              # Phase 1 保留
│   └── mcp/                  # Phase 1 保留
├── tests/
│   ├── test_db.py
│   └── test_orchestrator.py
├── requirements.txt           # 更新
└── docs/superpowers/
    ├── specs/
    └── plans/
```

---

## Task 1: 项目基础设置（Phase 2 依赖）

**Files:**
- Modify: `requirements.txt`
- Create: `src/orchestrator/__init__.py`
- Create: `src/db/__init__.py`
- Create: `src/services/__init__.py`

- [ ] **Step 1: 更新 requirements.txt**

```txt
chromadb>=0.4.0
anthropic>=0.20.0
httpx>=0.25.0
python-dateutil>=2.8.0
pyyaml>=6.0
obsidian-py>=0.1.0
# Phase 2 新增
langgraph>=0.0.20
apscheduler>=3.10.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
```

- [ ] **Step 2: 创建目录结构**

```bash
mkdir -p /Users/yinjili/p39_VoltInsight/src/orchestrator
mkdir -p /Users/yinjili/p39_VoltInsight/src/db
mkdir -p /Users/yinjili/p39_VoltInsight/src/services
mkdir -p /Users/yinjili/p39_VoltInsight/notifications
```

- [ ] **Step 3: 创建 __init__.py 文件**

```python
# src/orchestrator/__init__.py
"""Orchestrator 模块 - 工作流编排层"""
from .workflow_manager import WorkflowManager
from .workflow_states import WorkflowState, WorkflowStatus
from .scheduler import TaskScheduler

__all__ = ["WorkflowManager", "WorkflowState", "WorkflowStatus", "TaskScheduler"]
```

```python
# src/db/__init__.py
"""数据库模块 - 持久化层"""
from .models import Base, WorkflowInstance, ExecutionHistory, AnalystFeedback, ScheduledTask
from .session import get_db_session, init_db
from .repositories import WorkflowRepository, ExecutionRepository, FeedbackRepository

__all__ = [
    "Base",
    "WorkflowInstance",
    "ExecutionHistory",
    "AnalystFeedback",
    "ScheduledTask",
    "get_db_session",
    "init_db",
    "WorkflowRepository",
    "ExecutionRepository",
    "FeedbackRepository",
]
```

```python
# src/services/__init__.py
"""服务模块"""
from .notification import NotificationService, NotificationType

__all__ = ["NotificationService", "NotificationType"]
```

- [ ] **Step 4: 提交**

```bash
git add requirements.txt src/orchestrator/__init__.py src/db/__init__.py src/services/__init__.py
git commit -m "feat(phase2): add project structure and requirements"
```

---

## Task 2: 数据库模型定义

**Files:**
- Create: `src/db/models.py`

- [ ] **Step 1: 创建 SQLAlchemy 模型**

```python
# src/db/models.py
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
```

- [ ] **Step 2: 提交**

```bash
git add src/db/models.py && git commit -m "feat(db): add SQLAlchemy models (WorkflowInstance, ExecutionHistory, etc.)"
```

---

## Task 3: 数据库会话管理

**Files:**
- Create: `src/db/session.py`

- [ ] **Step 1: 创建数据库会话管理**

```python
# src/db/session.py
"""数据库会话管理"""
import os
from contextlib import contextmanager
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .models import Base

# 数据库 URL 配置
# 开发/测试环境使用 SQLite，生产环境使用 PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{Path(__file__).parent.parent.parent / 'data' / 'research_assistant.db'}"
)

# 创建引擎
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)

def get_db_session() -> Generator[Session, None, None]:
    """获取数据库会话的上下文管理器"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@contextmanager
def db_transaction() -> Generator[Session, None, None]:
    """带事务的数据库会话"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

- [ ] **Step 2: 提交**

```bash
git add src/db/session.py && git commit -m "feat(db): add session management with SQLite/PostgreSQL support"
```

---

## Task 4: 数据访问层

**Files:**
- Create: `src/db/repositories.py`

- [ ] **Step 1: 创建数据访问层**

```python
# src/db/repositories.py
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
```

- [ ] **Step 2: 提交**

```bash
git add src/db/repositories.py && git commit -m "feat(db): add repositories (WorkflowRepository, ExecutionRepository, FeedbackRepository)"
```

---

## Task 5: 通知服务

**Files:**
- Create: `src/services/notification.py`

- [ ] **Step 1: 创建通知服务**

```python
# src/services/notification.py
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
```

- [ ] **Step 2: 提交**

```bash
git add src/services/notification.py && git commit -m "feat(services): add NotificationService"
```

---

## Task 6: 工作流状态定义

**Files:**
- Create: `src/orchestrator/workflow_states.py`

- [ ] **Step 1: 创建工作流状态定义**

```python
# src/orchestrator/workflow_states.py
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
```

- [ ] **Step 2: 提交**

```bash
git add src/orchestrator/workflow_states.py && git commit -m "feat(orchestrator): add WorkflowState and WorkflowStatus definitions"
```

---

## Task 7: 工作流节点定义

**Files:**
- Create: `src/orchestrator/nodes.py`

- [ ] **Step 1: 创建工作流节点**

```python
# src/orchestrator/nodes.py
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
```

- [ ] **Step 2: 提交**

```bash
git add src/orchestrator/nodes.py && git commit -m "feat(orchestrator): add WorkflowNodes with fetch_news, generate_report, etc."
```

---

## Task 8: WorkflowManager 实现

**Files:**
- Create: `src/orchestrator/workflow_manager.py`

- [ ] **Step 1: 创建 WorkflowManager**

```python
# src/orchestrator/workflow_manager.py
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
```

- [ ] **Step 2: 提交**

```bash
git add src/orchestrator/workflow_manager.py && git commit -m "feat(orchestrator): add WorkflowManager with LangGraph integration"
```

---

## Task 9: 定时任务调度器

**Files:**
- Create: `src/orchestrator/scheduler.py`

- [ ] **Step 1: 创建 TaskScheduler**

```python
# src/orchestrator/scheduler.py
"""定时任务调度器"""
import logging
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from .workflow_manager import WorkflowManager
from .workflow_states import WorkflowType
from src.db.session import db_transaction
from src.db.repositories import WorkflowRepository

logger = logging.getLogger(__name__)

class TaskScheduler:
    """定时任务调度器"""

    def __init__(self, workflow_manager: WorkflowManager):
        self.workflow_manager = workflow_manager
        self.scheduler = BackgroundScheduler()
        self._running = False

    def start(self) -> None:
        """启动调度器"""
        if not self._running:
            self.scheduler.start()
            self._running = True
            logger.info("TaskScheduler started")

    def stop(self) -> None:
        """停止调度器"""
        if self._running:
            self.scheduler.shutdown(wait=False)
            self._running = False
            logger.info("TaskScheduler stopped")

    def add_cron_job(
        self,
        job_id: str,
        workflow_type: WorkflowType,
        hour: int,
        minute: int,
        **kwargs,
    ) -> None:
        """添加 Cron 定时任务"""
        trigger = CronTrigger(hour=hour, minute=minute)
        self.scheduler.add_job(
            func=self._run_workflow,
            trigger=trigger,
            args=[workflow_type, kwargs.get("context", {})],
            id=job_id,
            name=f"{workflow_type.value} - {job_id}",
            replace_existing=True,
        )
        self._update_scheduled_task(job_id, workflow_type, f"{minute} {hour} * * *")
        logger.info(f"Added cron job: {job_id} for {workflow_type.value} at {hour}:{minute}")

    def add_interval_job(
        self,
        job_id: str,
        workflow_type: WorkflowType,
        hours: int = 0,
        minutes: int = 0,
        **kwargs,
    ) -> None:
        """添加间隔定时任务"""
        trigger = IntervalTrigger(hours=hours, minutes=minutes)
        self.scheduler.add_job(
            func=self._run_workflow,
            trigger=trigger,
            args=[workflow_type, kwargs.get("context", {})],
            id=job_id,
            name=f"{workflow_type.value} - {job_id}",
            replace_existing=True,
        )
        self._update_scheduled_task(job_id, workflow_type, f"interval {hours}h {minutes}m")
        logger.info(f"Added interval job: {job_id} for {workflow_type.value} every {hours}h {minutes}m")

    def remove_job(self, job_id: str) -> None:
        """移除定时任务"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job: {job_id}")
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")

    def _run_workflow(self, workflow_type: WorkflowType, context: dict) -> None:
        """运行工作流（内部方法）"""
        logger.info(f"Triggering workflow: {workflow_type.value}")
        try:
            self.workflow_manager.trigger_workflow(workflow_type, context)
        except Exception as e:
            logger.error(f"Workflow {workflow_type.value} failed: {e}")

    def _update_scheduled_task(
        self,
        job_id: str,
        workflow_type: WorkflowType,
        cron_expression: str,
    ) -> None:
        """更新定时任务记录"""
        try:
            with db_transaction() as session:
                from src.db.models import ScheduledTask
                task = session.query(ScheduledTask).filter(ScheduledTask.id == job_id).first()
                if task:
                    task.cron_expression = cron_expression
                    task.is_active = True
                else:
                    task = ScheduledTask(
                        id=job_id,
                        workflow_type=workflow_type.value,
                        cron_expression=cron_expression,
                        is_active=True,
                    )
                    session.add(task)
        except Exception as e:
            logger.error(f"Failed to update scheduled task {job_id}: {e}")

    def setup_default_jobs(self) -> None:
        """设置默认定时任务"""
        self.add_cron_job("daily_briefing", WorkflowType.DAILY_BRIEFING, hour=8, minute=0)
        self.add_cron_job("morning_news", WorkflowType.NEWS_REVIEW, hour=7, minute=30)
        self.add_cron_job("price_update", WorkflowType.DATA_UPDATE, hour=17, minute=0)
        logger.info("Setup default scheduled jobs")
```

- [ ] **Step 2: 提交**

```bash
git add src/orchestrator/scheduler.py && git commit -m "feat(orchestrator): add TaskScheduler with APScheduler"
```

---

## Task 10: 单元测试

**Files:**
- Create: `tests/test_orchestrator.py`
- Create: `tests/test_db.py`

- [ ] **Step 1: 创建数据库测试**

```python
# tests/test_db.py
"""数据库测试"""
import pytest
import tempfile
from pathlib import Path
from datetime import datetime
import uuid

from src.db.models import Base, WorkflowInstance, ExecutionHistory, AnalystFeedback
from src.db.session import init_db, get_db_session, DATABASE_URL
from src.db.repositories import WorkflowRepository, ExecutionRepository, FeedbackRepository

def test_database_initialization():
    """测试数据库初始化"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        # This test just verifies imports work
        assert Base is not None
        assert WorkflowInstance is not None

def test_workflow_repository():
    """测试工作流仓储"""
    # Test that repository can be instantiated with a mock session
    class MockSession:
        pass

    repo = WorkflowRepository(MockSession())
    assert repo.session is not None

def test_workflow_state_to_dict():
    """测试工作流状态序列化"""
    from src.orchestrator.workflow_states import WorkflowState, WorkflowType, WorkflowStatus

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
```

- [ ] **Step 2: 创建编排层测试**

```python
# tests/test_orchestrator.py
"""编排层测试"""
import pytest
from datetime import datetime

from src.orchestrator.workflow_states import WorkflowState, WorkflowStatus, WorkflowType
from src.orchestrator.nodes import WorkflowNodes
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

def test_workflow_state_serialization():
    """测试工作流状态序列化"""
    state = WorkflowState(
        workflow_id="test-456",
        workflow_type=WorkflowType.DAILY_BRIEFING,
        status=WorkflowStatus.COMPLETED,
    )

    data = state.to_dict()
    restored = WorkflowState.from_dict(data)

    assert restored.workflow_id == state.workflow_id
    assert restored.workflow_type == state.workflow_type
    assert restored.status == state.status

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

def test_workflow_status_enum():
    """测试工作流状态枚举"""
    assert WorkflowStatus.PENDING.value == "pending"
    assert WorkflowStatus.RUNNING.value == "running"
    assert WorkflowStatus.WAITING_APPROVAL.value == "waiting_approval"
    assert WorkflowStatus.COMPLETED.value == "completed"
    assert WorkflowStatus.FAILED.value == "failed"

def test_workflow_type_enum():
    """测试工作流类型枚举"""
    assert WorkflowType.DAILY_BRIEFING.value == "daily_briefing"
    assert WorkflowType.NEWS_REVIEW.value == "news_review"
    assert WorkflowType.DATA_UPDATE.value == "data_update"
```

- [ ] **Step 3: 运行测试**

```bash
cd /Users/yinjili/p39_VoltInsight && pip install langgraph apscheduler sqlalchemy -q && PYTHONPATH=/Users/yinjili/p39_VoltInsight pytest tests/test_orchestrator.py tests/test_db.py -v
```

Expected: All tests PASS

- [ ] **Step 4: 提交**

```bash
git add tests/test_orchestrator.py tests/test_db.py && git commit -m "test(phase2): add orchestrator and db tests"
```

---

## Task 11: 主入口与集成

**Files:**
- Modify: `src/orchestrator/__init__.py`
- Create: `src/main.py`

- [ ] **Step 1: 更新 __init__.py 导出**

```python
# src/orchestrator/__init__.py
"""Orchestrator 模块 - 工作流编排层"""
from .workflow_manager import WorkflowManager
from .workflow_states import WorkflowState, WorkflowStatus, WorkflowType
from .scheduler import TaskScheduler
from .nodes import WorkflowNodes

__all__ = [
    "WorkflowManager",
    "WorkflowState",
    "WorkflowStatus",
    "WorkflowType",
    "TaskScheduler",
    "WorkflowNodes",
]
```

- [ ] **Step 2: 创建主入口**

```python
# src/main.py
"""Phase 2 主入口"""
import argparse
import logging
from pathlib import Path

from src.db.session import init_db
from src.storage import FileStorage, VectorStorage, ObsidianStorage
from src.services.notification import NotificationService
from src.orchestrator import WorkflowManager, TaskScheduler, WorkflowType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_workflow_manager() -> WorkflowManager:
    """创建工作流管理器"""
    project_root = Path(__file__).parent.parent

    file_storage = FileStorage(project_root)
    vector_storage = VectorStorage(project_root / "vector_db")
    obsidian_storage = ObsidianStorage(
        project_root / "knowledge",
        project_root / "knowledge" / "templates"
    )
    notification_service = NotificationService(project_root / "notifications")

    return WorkflowManager(
        file_storage=file_storage,
        vector_storage=vector_storage,
        obsidian_storage=obsidian_storage,
        notification_service=notification_service,
    )

def main():
    parser = argparse.ArgumentParser(description="Research Assistant AI Agent - Phase 2")
    parser.add_argument("--init-db", action="store_true", help="Initialize database")
    parser.add_argument("--workflow", type=str, choices=["daily_briefing", "news_review", "data_update"], help="Run specific workflow")
    parser.add_argument("--start-scheduler", action="store_true", help="Start the scheduler")
    args = parser.parse_args()

    if args.init_db:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized")
        return

    if args.workflow:
        logger.info(f"Running workflow: {args.workflow}")
        manager = create_workflow_manager()
        workflow_type = WorkflowType(args.workflow)
        result = manager.trigger_workflow(workflow_type)
        logger.info(f"Workflow completed: {result.status}")
        return

    if args.start_scheduler:
        logger.info("Starting scheduler...")
        manager = create_workflow_manager()
        scheduler = TaskScheduler(manager)
        scheduler.setup_default_jobs()
        scheduler.start()
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        try:
            import time
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            scheduler.stop()
            logger.info("Scheduler stopped")
        return

    parser.print_help()

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 提交**

```bash
git add src/orchestrator/__init__.py src/main.py && git commit -m "feat(phase2): add main entry point and exports"
```

---

## 实施检查清单

- [ ] Task 1: 项目基础设置（依赖+目录）
- [ ] Task 2: 数据库模型定义
- [ ] Task 3: 数据库会话管理
- [ ] Task 4: 数据访问层
- [ ] Task 5: 通知服务
- [ ] Task 6: 工作流状态定义
- [ ] Task 7: 工作流节点定义
- [ ] Task 8: WorkflowManager 实现
- [ ] Task 9: TaskScheduler 实现
- [ ] Task 10: 单元测试
- [ ] Task 11: 主入口与集成

---

## 依赖关系

```
Task 1 (基础设置) → Task 2 (模型) → Task 3 (会话) → Task 4 (仓储)
                              ↓
Task 5 (通知服务) ← Task 1
         ↓
Task 6 (状态) → Task 7 (节点) → Task 8 (Manager)
         ↓                        ↓
Task 9 (Scheduler) ← Task 8
         ↓
Task 10 (测试) ← Task 8, Task 9
         ↓
Task 11 (集成)
```

**Plan complete and saved to `docs/superpowers/plans/2026-05-25-research-assistant-ai-phase2-plan.md`.**

**Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?