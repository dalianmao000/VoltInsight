# Research Assistant AI Agent - Phase 2 设计文档

> 日期：2026-05-25
> 目标：Phase 2 扩展 - API驱动编排层 + 定时任务 + 状态持久化

---

## 一、设计目标

**Phase 2 目标**：
- 引入 LangGraph 工作流编排层，将多个 Skill 串联成复杂工作流
- 实现定时任务触发（每日早报自动生成、新闻推送、数据更新）
- 引入 PostgreSQL 持久化任务状态、历史执行、分析师反馈
- 保持 Phase 1 架构兼容，现有 Skills/存储层平滑迁移

---

## 二、系统架构

### 2.1 层次结构

```
┌─────────────────────────────────────────────────────────┐
│                    用户交互层（保留）                      │
│         Claude Code 对话 + Obsidian + 本地文件            │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│              Orchestrator 层（新增）                       │
│  LangGraph 工作流引擎 + APScheduler 定时器                 │
│  ┌────────────────┐ ┌────────────────┐                   │
│  │ WorkflowManager│ │ TaskScheduler   │                   │
│  └────────────────┘ └────────────────┘                   │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                  能力调度层（Phase 1 保留）                 │
│  Skills（提示模板）+ MCP（数据源连接）                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                   │
│  │News经纪 │ │Data经纪 │ │Report经纪 │                   │
│  └──────────┘ └──────────┘ └──────────┘                   │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│              持久化层（新增）                              │
│  PostgreSQL（任务状态/历史/反馈）+ ChromaDB（向量检索）     │
└─────────────────────────────────────────────────────────┘
```

### 2.2 核心组件更新

| 组件 | 职责 | 技术实现 |
|------|------|----------|
| **WorkflowManager** | 定义和管理工作流，执行状态机 | LangGraph |
| **TaskScheduler** | 定时任务触发与管理 | APScheduler |
| **TaskState** | 任务状态持久化与查询 | PostgreSQL + SQLAlchemy |
| **ExecutionHistory** | 执行历史记录与反馈 | PostgreSQL + SQLAlchemy |
| **NotificationService** | 任务完成/异常通知 | WebSocket / 文件推送 |

---

## 三、核心功能设计

### 3.1 工作流编排（LangGraph）

#### 3.1.1 预定义工作流

**工作流1：每日早报生成**
```
[触发：每日 8:00] → [News经纪：获取过去24h新闻]
   → [Data经纪：更新价格/装机量数据]
   → [Report经纪：生成早报草稿]
   → [审批节点：人工确认/修改]
   → [归档：文件+Obsidian+向量库]
   → [通知：推送至用户]
```

**工作流2：新闻快评全流程**
```
[触发：人工/定时] → [News经纪：获取指定新闻]
   → [Report经纪：生成快评]
   → [审批节点：人工确认]
   → [归档]
```

**工作流3：数据批量更新**
```
[触发：定时/手动] → [Data经纪：批量获取数据]
   → [规则校验]
   → [异常告警]
   → [归档]
```

#### 3.1.2 LangGraph 状态定义

```python
@dataclass
class WorkflowState:
    """工作流状态"""
    workflow_id: str
    workflow_type: str  # "daily_briefing" / "news_review" / "data_update"
    current_step: str
    status: str  # "pending" / "running" / "waiting_approval" / "completed" / "failed"
    context: dict  # 工作流上下文数据
    result: Optional[dict]  # 最终结果
    error: Optional[str]  # 错误信息
    created_at: datetime
    updated_at: datetime
```

#### 3.1.3 节点定义

```python
class WorkflowNodes:
    """工作流节点"""

    @staticmethod
    def fetch_news(state: WorkflowState) -> WorkflowState:
        """获取新闻"""
        pass

    @staticmethod
    def update_data(state: WorkflowState) -> WorkflowState:
        """更新数据"""
        pass

    @staticmethod
    def generate_report(state: WorkflowState) -> WorkflowState:
        """生成报告"""
        pass

    @staticmethod
    def await_approval(state: WorkflowState) -> WorkflowState:
        """等待审批（Human-in-the-Loop）"""
        pass

    @staticmethod
    def archive_result(state: WorkflowState) -> WorkflowState:
        """归档结果"""
        pass

    @staticmethod
    def notify_user(state: WorkflowState) -> WorkflowState:
        """通知用户"""
        pass
```

### 3.2 定时任务调度（APScheduler）

#### 3.2.1 预设定时任务

| 任务ID | 触发时间 | 工作流类型 | 说明 |
|--------|----------|------------|------|
| `daily_briefing` | 每日 08:00 | `daily_briefing` | 每日早报生成 |
| `morning_news` | 每日 07:30 | `news_update` | 早间新闻推送 |
| `price_update` | 每日 17:00 | `data_update` | 日间价格更新 |
| `evening_summary` | 每日 18:00 | `daily_summary` | 晚间行业总结 |

#### 3.2.2 调度器配置

```python
class TaskScheduler:
    """定时任务调度器"""

    def __init__(self, workflow_manager: WorkflowManager):
        self.scheduler = APScheduler()
        self.workflow_manager = workflow_manager

    def add_job(self, job_id: str, workflow_type: str, trigger: Trigger):
        """添加定时任务"""
        self.scheduler.add_job(
            func=self.workflow_manager.trigger_workflow,
            trigger=trigger,
            args=[workflow_type],
            id=job_id,
            replace_existing=True
        )

    def remove_job(self, job_id: str):
        """移除定时任务"""
        self.scheduler.remove_job(job_id)
```

### 3.3 状态持久化（PostgreSQL + SQLAlchemy）

#### 3.3.1 数据库 Schema

```sql
-- 工作流实例表
CREATE TABLE workflow_instances (
    id UUID PRIMARY KEY,
    workflow_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    current_step VARCHAR(50),
    context JSONB,
    result JSONB,
    error TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 执行历史表
CREATE TABLE execution_history (
    id UUID PRIMARY KEY,
    workflow_instance_id UUID REFERENCES workflow_instances(id),
    step_name VARCHAR(50) NOT NULL,
    step_status VARCHAR(20),
    input_data JSONB,
    output_data JSONB,
    duration_ms INTEGER,
    executed_at TIMESTAMP DEFAULT NOW()
);

-- 分析师反馈表
CREATE TABLE analyst_feedback (
    id UUID PRIMARY KEY,
    workflow_instance_id UUID REFERENCES workflow_instances(id),
    feedback_type VARCHAR(20),  -- "approve" / "reject" / "modify"
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 定时任务表
CREATE TABLE scheduled_tasks (
    id VARCHAR(100) PRIMARY KEY,
    workflow_type VARCHAR(50) NOT NULL,
    cron_expression VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    last_run_at TIMESTAMP,
    next_run_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 3.3.2 ORM 模型

```python
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class WorkflowInstance(Base):
    __tablename__ = "workflow_instances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    current_step = Column(String(50))
    context = Column(JSON)
    result = Column(JSON)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    executions = relationship("ExecutionHistory", back_populates="workflow")
    feedbacks = relationship("AnalystFeedback", back_populates="workflow")

class ExecutionHistory(Base):
    __tablename__ = "execution_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_instance_id = Column(UUID(as_uuid=True), ForeignKey("workflow_instances.id"))
    step_name = Column(String(50), nullable=False)
    step_status = Column(String(20))
    input_data = Column(JSON)
    output_data = Column(JSON)
    duration_ms = Column(Integer)
    executed_at = Column(DateTime, default=datetime.utcnow)

    workflow = relationship("WorkflowInstance", back_populates="executions")

class AnalystFeedback(Base):
    __tablename__ = "analyst_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_instance_id = Column(UUID(as_uuid=True), ForeignKey("workflow_instances.id"))
    feedback_type = Column(String(20))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    workflow = relationship("WorkflowInstance", back_populates="feedbacks")

class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    id = Column(String(100), primary_key=True)
    workflow_type = Column(String(50), nullable=False)
    cron_expression = Column(String(50))
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime)
    next_run_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 3.4 通知机制

#### 3.4.1 通知类型

| 通知类型 | 触发条件 | 通知方式 |
|----------|----------|----------|
| `workflow_completed` | 工作流成功完成 | 文件/控制台 |
| `workflow_failed` | 工作流执行失败 | 文件/控制台 |
| `approval_required` | 等待人工审批 | 文件/控制台 |
| `daily_summary` | 每日任务汇总 | 文件 |

#### 3.4.2 通知服务

```python
class NotificationService:
    """通知服务"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def notify(self, notification_type: str, content: dict) -> None:
        """发送通知"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{notification_type}_{timestamp}.json"
        path = self.output_dir / "notifications" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content, ensure_ascii=False, indent=2))
```

---

## 四、数据流设计

### 4.1 工作流执行数据流

```
[定时触发/手动调用]
        ↓
[WorkflowManager.create_workflow()]
        ↓
[LangGraph 执行工作流]
   ├── Node: fetch_news → News经纪
   ├── Node: update_data → Data经纪
   ├── Node: generate_report → Report经纪
   ├── Node: await_approval → 暂停等待人工确认
   ├── Node: archive_result → 存储层
   └── Node: notify_user → NotificationService
        ↓
[状态持久化到 PostgreSQL]
        ↓
[返回执行结果]
```

### 4.2 审批流程数据流

```
[工作流执行到 await_approval 节点]
        ↓
[状态更新为 "waiting_approval"]
        ↓
[生成待审批通知]
        ↓
[用户确认/修改/驳回]
        ↓
[AnalystFeedback 记录反馈]
        ↓
[工作流继续或终止]
```

---

## 五、技术栈

### 5.1 新增依赖

```txt
# Phase 2 新增
langgraph>=0.0.20
apscheduler>=3.10.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0  # PostgreSQL 驱动
```

### 5.2 技术选型理由

| 技术 | 选型理由 |
|------|----------|
| **LangGraph** | 微软开源，基于LangChain，支持循环/条件分支，状态可视化强 |
| **APScheduler** | 轻量级，支持 Cron/Interval/Date 触发，与 Python 无缝集成 |
| **SQLAlchemy** | ORM 层，兼容 PostgreSQL/SQLite，便于后续迁移 |

---

## 六、目录结构（Phase 2 扩展）

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
├── tests/                     # 测试扩展
│   ├── test_orchestrator.py
│   └── test_db.py
└── requirements.txt           # 更新
```

---

## 七、实施计划

### Week 1：基础设施
- [ ] 数据库配置（PostgreSQL/SQLite）
- [ ] SQLAlchemy 模型定义
- [ ] 数据访问层实现
- [ ] 通知服务基础

### Week 2：工作流编排
- [ ] LangGraph 安装与基础配置
- [ ] 工作流状态定义
- [ ] 核心节点实现
- [ ] 工作流定义（早报/快评/数据更新）

### Week 3：定时调度
- [ ] APScheduler 集成
- [ ] 预设定时任务配置
- [ ] 定时任务管理接口

### Week 4：集成与测试
- [ ] 端到端工作流测试
- [ ] 定时任务测试
- [ ] 状态持久化验证
- [ ] 文档更新

---

## 八、关键设计决策

### 8.1 数据库选择
- 开发/测试环境：SQLite（零配置）
- 生产环境：PostgreSQL（推荐）
- 通过 SQLAlchemy ORM 统一接口

### 8.2 Human-in-the-Loop 设计
- 审批节点使用 `interrupt()` 暂停工作流
- 用户通过文件系统或 API 提交审批结果
- 工作流根据审批结果决定继续或终止

### 8.3 错误处理
- 工作流级别：节点失败自动重试 3 次，失败则终止并告警
- 任务级别：定时任务失败不影响其他任务
- 持久化：所有状态变更立即持久化，支持断点恢复

### 8.4 向后兼容
- Phase 1 的 Skills/存储层完全保留
- 新增 Orchestrator 层不破坏现有接口
- 渐进式迁移：可单独启用工作流编排或定时任务

---

## 九、风险与应对

| 风险 | 应对 |
|------|------|
| 数据库连接失败 | 本地 SQLite 回退 |
| LangGraph 学习成本 | 提供预定义工作流模板 |
| 定时任务积压 | 任务队列 + 超时机制 |
| 状态一致性问题 | 事务保证 + 幂等设计 |

---

## 十、成功指标

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| 工作流执行成功率 | ≥95% | PostgreSQL 统计 |
| 定时任务准时率 | ≥90% | 任务执行时间戳 |
| 审批流程完成率 | 100% | 待审批任务清理 |
| 系统恢复时间 | <1分钟 | 断电重启测试 |