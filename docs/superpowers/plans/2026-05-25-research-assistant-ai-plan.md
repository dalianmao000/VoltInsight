# Research Assistant AI Agent 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建以 Claude Code 为基座的汽车与电池材料研究助理 AI 系统 Phase 1，验证新闻监控→数据更新→快评生成→审批→归档核心闭环

**Architecture:** 采用层次架构：用户交互层（Claude Code + Obsidian）→ 能力调度层（Skills + MCP） → 存储层（文件 + Obsidian + 向量库）。Skills 作为领域提示模板驱动核心流程，MCP 作为数据源连接器，ChromaDB 提供语义检索能力。

**Tech Stack:** Claude Code / Claude API, Python 3.11+, ChromaDB, Obsidian, MCP Server, NewsAPI

---

## 文件结构

```
p39_VoltInsight/
├── src/                           # Python源代码
│   ├── skills/                    # Skills实现
│   │   ├── __init__.py
│   │   ├── research_news.py       # 新闻监控Skill
│   │   ├── research_data.py      # 数据更新Skill
│   │   ├── research_report.py     # 报告生成Skill
│   │   └── research_review.py     # 内容审查Skill
│   ├── agents/                    # Agent逻辑
│   │   ├── __init__.py
│   │   ├── news_broker.py         # News经纪
│   │   ├── data_broker.py        # Data经纪
│   │   └── report_broker.py      # Report经纪
│   ├── storage/                  # 存储层
│   │   ├── __init__.py
│   │   ├── file_storage.py       # 文件存储
│   │   ├── obsidian_storage.py   # Obsidian集成
│   │   └── vector_storage.py     # 向量库
│   ├── mcp/                      # MCP连接器
│   │   ├── __init__.py
│   │   ├── news_mcp.py          # 新闻MCP
│   │   └── data_mcp.py          # 数据MCP
│   └── utils/
│       ├── __init__.py
│       └── config.py            # 配置管理
├── data/                         # 数据目录
│   ├── raw/
│   ├── processed/
│   └── archive/
├── research/                      # 研究产出
│   ├── drafts/
│   ├── final/
│   └── versions/
├── knowledge/                     # 知识库
│   ├── templates/                 # Obsidian模板
│   │   ├── quick_review.md       # 快评模板
│   │   ├── daily_note.md         # 每日笔记模板
│   │   └── company_note.md       # 公司笔记模板
│   └── notes/
├── vector_db/                     # ChromaDB
├── tests/                        # 测试
│   ├── test_skills.py
│   ├── test_agents.py
│   └── test_storage.py
├── docs/superpowers/
│   ├── specs/
│   └── plans/
└── CLAUDE.md
```

---

## Task 1: 项目基础设置

**Files:**
- Create: `.claude/projects/-Users-yinjili-p39-VoltInsight/CLAUDE.md`
- Create: `src/__init__.py`
- Create: `src/utils/__init__.py`
- Create: `src/utils/config.py`
- Create: `requirements.txt`

- [ ] **Step 1: 创建 CLAUDE.md 项目配置**

```markdown
# Project: Research Assistant AI Agent

## 目标
构建以 Claude Code 为基座的汽车与电池材料研究助理 AI 系统 Phase 1

## 核心流程
新闻监控 → 数据更新 → 快评生成 → 审批 → 归档

## 技术栈
- Claude Code / Claude API
- Python 3.11+
- ChromaDB (向量库)
- Obsidian (笔记)
- MCP Server (数据源)

## 关键约定
- 所有计算通过 Python 代码执行，LLM 仅负责逻辑描述
- 敏感内容需人工审批后才能发布
- 数据源 MCP 配置外置，支持按需切换

## Skills
- `/research` - 新闻监控与快评
- `/data` - 数据更新与校验
- `/report` - 报告生成
- `/review` - 内容审查
```

- [ ] **Step 2: 创建 requirements.txt**

```txt
chromadb>=0.4.0
anthropic>=0.20.0
httpx>=0.25.0
python-dateutil>=2.8.0
pyyaml>=6.0
obsidian-py>=0.1.0
```

- [ ] **Step 3: 创建配置管理模块**

```python
# src/utils/config.py
"""配置管理"""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProjectConfig:
    project_root: Path
    data_dir: Path
    research_dir: Path
    knowledge_dir: Path
    vector_db_dir: Path
    anthropic_api_key: Optional[str] = None

    @classmethod
    def from_env(cls) -> "ProjectConfig":
        root = Path(__file__).parent.parent.parent
        return cls(
            project_root=root,
            data_dir=root / "data",
            research_dir=root / "research",
            knowledge_dir=root / "knowledge",
            vector_db_dir=root / "vector_db",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        )

config = ProjectConfig.from_env()
```

- [ ] **Step 4: 提交**

```bash
git add CLAUDE.md requirements.txt src/utils/config.py
git commit -m "feat: project setup with config management"
```

---

## Task 2: 目录结构创建

**Files:**
- Create: `data/raw/.gitkeep`
- Create: `data/processed/.gitkeep`
- Create: `data/archive/.gitkeep`
- Create: `research/drafts/.gitkeep`
- Create: `research/final/.gitkeep`
- Create: `research/versions/.gitkeep`
- Create: `knowledge/templates/.gitkeep`
- Create: `knowledge/notes/.gitkeep`
- Create: `vector_db/.gitkeep`

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p data/raw data/processed data/archive
mkdir -p research/drafts research/final research/versions
mkdir -p knowledge/templates knowledge/notes
mkdir -p vector_db
```

- [ ] **Step 2: 创建 .gitkeep 文件用于Git追踪空目录**

```bash
touch data/raw/.gitkeep data/processed/.gitkeep data/archive/.gitkeep
touch research/drafts/.gitkeep research/final/.gitkeep research/versions/.gitkeep
touch knowledge/templates/.gitkeep knowledge/notes/.gitkeep
touch vector_db/.gitkeep
```

- [ ] **Step 3: 提交**

```bash
git add data/ research/ knowledge/ vector_db/
git commit -m "feat: create directory structure"
```

---

## Task 3: 存储层基础实现

**Files:**
- Create: `src/storage/__init__.py`
- Create: `src/storage/file_storage.py`
- Create: `src/storage/vector_storage.py`
- Create: `src/storage/obsidian_storage.py`
- Create: `tests/test_storage.py`

- [ ] **Step 1: 创建存储层初始化**

```python
# src/storage/__init__.py
"""存储层"""
from .file_storage import FileStorage
from .vector_storage import VectorStorage
from .obsidian_storage import ObsidianStorage

__all__ = ["FileStorage", "VectorStorage", "ObsidianStorage"]
```

- [ ] **Step 2: 创建文件存储模块**

```python
# src/storage/file_storage.py
"""本地文件存储"""
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import yaml

class FileStorage:
    """文件存储管理器"""

    def __init__(self, root: Path):
        self.root = root

    def save_draft(self, content: str, filename: str, metadata: Optional[dict] = None) -> Path:
        """保存草稿"""
        draft_dir = self.root / "research" / "drafts"
        draft_dir.mkdir(parents=True, exist_ok=True)
        path = draft_dir / filename
        path.write_text(content, encoding="utf-8")
        if metadata:
            meta_path = draft_dir / f"{filename}.meta.yaml"
            meta_path.write_text(yaml.dump(metadata), encoding="utf-8")
        return path

    def save_final(self, content: str, filename: str, metadata: Optional[dict] = None) -> Path:
        """保存定稿"""
        final_dir = self.root / "research" / "final"
        final_dir.mkdir(parents=True, exist_ok=True)
        path = final_dir / filename
        path.write_text(content, encoding="utf-8")
        if metadata:
            meta_path = final_dir / f"{filename}.meta.yaml"
            meta_path.write_text(yaml.dump(metadata), encoding="utf-8")
        return path

    def save_version(self, content: str, filename: str, version: str) -> Path:
        """保存版本快照"""
        version_dir = self.root / "research" / "versions" / filename.replace(".md", "")
        version_dir.mkdir(parents=True, exist_ok=True)
        path = version_dir / f"{version}.md"
        path.write_text(content, encoding="utf-8")
        return path

    def archive_data(self, data: Any, filename: str, data_type: str = "raw") -> Path:
        """归档数据"""
        archive_dir = self.root / "data" / data_type / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = archive_dir / f"{timestamp}_{filename}"
        if isinstance(data, str):
            path.write_text(data, encoding="utf-8")
        else:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path
```

- [ ] **Step 3: 创建向量库存储模块**

```python
# src/storage/vector_storage.py
"""向量库存储"""
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import Optional

class VectorStorage:
    """ChromaDB 向量库管理器"""

    def __init__(self, persist_dir: Path):
        self.persist_dir = persist_dir
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(
            name="research_notes",
            metadata={"description": "Research notes for semantic search"}
        )

    def add_document(self, doc_id: str, content: str, metadata: dict) -> None:
        """添加文档到向量库"""
        self.collection.add(
            documents=[content],
            ids=[doc_id],
            metadatas=[metadata]
        )

    def search(self, query: str, n_results: int = 5) -> list:
        """语义检索"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results

    def delete(self, doc_id: str) -> None:
        """删除文档"""
        self.collection.delete(ids=[doc_id])
```

- [ ] **Step 4: 创建Obsidian存储模块**

```python
# src/storage/obsidian_storage.py
"""Obsidian笔记存储"""
from pathlib import Path
from datetime import datetime
from typing import Optional
import re

class ObsidianStorage:
    """Obsidian 笔记管理器"""

    def __init__(self, vault_path: Path, templates_path: Path):
        self.vault_path = vault_path
        self.templates_path = templates_path
        self.notes_path = vault_path / "notes"
        self.notes_path.mkdir(parents=True, exist_ok=True)

    def create_note_from_template(
        self,
        template_name: str,
        filename: str,
        variables: dict
    ) -> Path:
        """从模板创建笔记"""
        template_path = self.templates_path / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_name}")

        content = template_path.read_text(encoding="utf-8")
        for key, value in variables.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))

        note_path = self.notes_path / filename
        note_path.write_text(content, encoding="utf-8")
        return note_path

    def create_daily_note(self, date: Optional[datetime] = None) -> Path:
        """创建每日笔记"""
        date = date or datetime.now()
        filename = f"Daily/{date.strftime('%Y-%m-%d')}.md"
        note_path = self.notes_path / filename
        note_path.parent.mkdir(parents=True, exist_ok=True)

        content = f"""# Daily Note - {date.strftime('%Y-%m-%d')}

## 今日任务

## 研究产出

## 待处理

"""
        note_path.write_text(content, encoding="utf-8")
        return note_path

    def link_notes(self, from_path: Path, to_path: Path, link_text: Optional[str] = None) -> None:
        """创建笔记间双向链接"""
        link_text = link_text or to_path.stem
        from_content = from_path.read_text(encoding="utf-8")
        link_markdown = f"[[{link_text}]]"
        if link_markdown not in from_content:
            from_content += f"\n\n## 链接\n- {link_markdown}\n"
            from_path.write_text(from_content, encoding="utf-8")
```

- [ ] **Step 5: 创建存储层测试**

```python
# tests/test_storage.py
"""存储层测试"""
import pytest
import tempfile
from pathlib import Path
from src.storage.file_storage import FileStorage
from src.storage.vector_storage import VectorStorage
from src.storage.obsidian_storage import ObsidianStorage

def test_file_storage_save_draft():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        storage = FileStorage(root)
        path = storage.save_draft("# Test", "test.md", {"type": "draft"})
        assert path.exists()
        assert path.read_text() == "# Test"

def test_vector_storage_add_and_search():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = VectorStorage(Path(tmpdir))
        storage.add_document("doc1", "电池材料价格上涨", {"type": "news"})
        results = storage.search("原材料", n_results=1)
        assert len(results["ids"][0]) > 0

def test_obsidian_create_note():
    with tempfile.TemporaryDirectory() as tmpdir:
        vault = Path(tmpdir) / "vault"
        templates = Path(tmpdir) / "templates"
        vault.mkdir()
        templates.mkdir()

        template = templates / "test.md"
        template.write_text("# {{title}}")

        storage = ObsidianStorage(vault, templates)
        path = storage.create_note_from_template(
            "test.md", "note.md", {"title": "Test Note"}
        )
        assert path.exists()
        assert "Test Note" in path.read_text()
```

- [ ] **Step 6: 运行测试**

```bash
cd /Users/yinjili/p39_VoltInsight
pip install pytest pytest-mock -q
pytest tests/test_storage.py -v
```

Expected: 3 PASS

- [ ] **Step 7: 提交**

```bash
git add src/storage/ tests/test_storage.py
git commit -m "feat: implement storage layer (FileStorage, VectorStorage, ObsidianStorage)"
```

---

## Task 4: Obsidian 模板设计

**Files:**
- Create: `knowledge/templates/quick_review.md`
- Create: `knowledge/templates/daily_note.md`
- Create: `knowledge/templates/company_note.md`

- [ ] **Step 1: 创建快评模板**

```markdown
# {{title}}

> 类型：{{type}}
> 日期：{{date}}
> 标签：{{tags}}
> 状态：{{status}}

## 📰 事件摘要

## 🔗 影响链分析

### 影响方向
- [ ] 正面
- [ ] 负面
- [ ] 中性

### 影响程度
- [ ] 重大
- [ ] 中等
- [ ] 轻微

### 影响持续时间
- [ ] 长期
- [ ] 中期
- [ ] 短期

## 📊 标的映射

| 公司/标的 | 影响方向 | 影响程度 | 备注 |
|---------|---------|---------|------|
| | | | |

## ⚠️ 风险提示

## 📚 相关链接

## 💬 分析师备注

```

- [ ] **Step 2: 创建每日笔记模板**

```markdown
# Daily Note - {{date}}

## 📅 日期：{{date}}

## 📰 今日新闻

### 重点新闻
-

### 行业动态
-

## 📊 数据更新

### 价格跟踪
- 锂：{{lithium_price}}
- 钴：{{cobalt_price}}
- 镍：{{nickel_price}}

### 装机量
-

## ✍️ 研究产出

- [[]]

## 🎯 明日计划

- [ ]

## ⏰ 时间戳

> 创建时间：{{created_at}}
> 更新时间：{{updated_at}}
```

- [ ] **Step 3: 创建公司笔记模板**

```markdown
# {{company_name}}

> 类型：公司研究
> 日期：{{date}}
> 标签：{{tags}}

## 基本信息

| 项目 | 内容 |
|------|------|
| 股票代码 | {{stock_code}} |
| 主营业务 | {{business}} |
| 上市地 | {{listing}} |

## 核心数据

### 产能
-

### 出货量
-

### 财务数据
- 营收：
- 毛利：
- 净利润：

## 行业地位

## 近期动态

## 风险因素

## 相关研究

- [[快评]]
- [[报告]]

## 📚 外部链接

```

- [ ] **Step 4: 提交**

```bash
git add knowledge/templates/
git commit -m "feat: add Obsidian templates (quick_review, daily_note, company_note)"
```

---

## Task 5: Skills 基础框架

**Files:**
- Create: `src/skills/__init__.py`
- Create: `src/skills/base.py`
- Create: `src/skills/prompts.py`
- Create: `tests/test_skills.py`

- [ ] **Step 1: 创建 Skills 初始化**

```python
# src/skills/__init__.py
"""Skills 模块"""
from .research_news import ResearchNewsSkill
from .research_data import ResearchDataSkill
from .research_report import ResearchReportSkill
from .research_review import ResearchReviewSkill

__all__ = [
    "ResearchNewsSkill",
    "ResearchDataSkill",
    "ResearchReportSkill",
    "ResearchReviewSkill",
]
```

- [ ] **Step 2: 创建 Skill 基类**

```python
# src/skills/base.py
"""Skill 基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class SkillContext:
    """Skill 执行上下文"""
    user_input: str
    config: dict
    storage: Optional[object] = None

@dataclass
class SkillResult:
    """Skill 执行结果"""
    success: bool
    content: str
    metadata: dict
    error: Optional[str] = None

class BaseSkill(ABC):
    """Skill 基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Skill 名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Skill 描述"""
        pass

    @abstractmethod
    async def execute(self, context: SkillContext) -> SkillResult:
        """执行 Skill"""
        pass

    def get_system_prompt(self) -> str:
        """获取系统提示"""
        return ""
```

- [ ] **Step 3: 创建提示词模板**

```python
# src/skills/prompts.py
"""提示词模板"""

RESEARCH_NEWS_PROMPT = """你是一位专业的汽车与电池材料行业研究员，擅长从新闻中提取关键信息并生成结构化快评。

## 你的任务
给定一篇新闻或新闻列表，你需要：
1. 提取关键事实（谁、什么、何时、何地、为什么）
2. 分析对汽车/电池材料行业的影响方向和程度
3. 识别受影响的标的（公司、上下游）
4. 生成专业、简洁的快评

## 输出格式
请按以下格式输出：

### 📰 事件摘要
[2-3句话概括核心事件]

### 🔗 影响链分析
- **影响方向**：正面/负面/中性
- **影响程度**：重大/中等/轻微
- **影响持续**：长期/中期/短期
- **影响逻辑**：[1-2句话解释逻辑]

### 📊 标的映射
| 标的 | 影响方向 | 影响程度 | 备注 |
|-----|---------|---------|------|
| | | | |

### ⚠️ 风险提示
[如有风险需要提示]

### 💬 分析师备注
[补充观点或待验证事项]

## 重要原则
- 只基于提供的新闻内容进行推断，不要添加假设
- 如果信息不足以做出判断，明确标注"待验证"
- 保持专业金融分析的表述风格
"""

RESEARCH_REPORT_PROMPT = """你是一位专业的股票研究分析师，擅长撰写汽车与电池材料行业的投资研究报告。

## 你的任务
根据提供的信息，生成研究报告的各个章节。

## 输出格式
请按以下格式输出：

### 章节标题
[内容]

## 重要原则
- 数据必须准确，标注数据来源
- 逻辑链条清晰，观点有据可依
- 符合投行专业研报格式
"""

DATA_VALIDATION_PROMPT = """你是一位数据校验专家，负责检查财务数据的准确性和一致性。

## 校验规则
1. 三张表勾稽关系：资产 = 负债 + 所有者权益
2. 同比环比变化阈值：超过20%需要解释
3. 缺失值检测：标记所有缺失数据点
4. 异常值检测：标记超出合理范围的数值

## 输出格式
```json
{
  "valid": true/false,
  "errors": [],
  "warnings": [],
  "summary": "摘要"
}
```
"""
```

- [ ] **Step 4: 创建测试文件**

```python
# tests/test_skills.py
"""Skills 测试"""
import pytest
from src.skills.base import SkillContext, SkillResult
from src.skills.research_news import ResearchNewsSkill

def test_research_news_skill_initialization():
    skill = ResearchNewsSkill()
    assert skill.name == "research-news"
    assert "新闻" in skill.description

def test_research_news_system_prompt():
    skill = ResearchNewsSkill()
    prompt = skill.get_system_prompt()
    assert "新闻" in prompt
    assert "影响" in prompt
```

- [ ] **Step 5: 运行测试**

```bash
pytest tests/test_skills.py -v
```

Expected: 2 PASS

- [ ] **Step 6: 提交**

```bash
git add src/skills/ tests/test_skills.py
git commit -m "feat: implement Skills framework with base class and prompts"
```

---

## Task 6: News经纪 实现

**Files:**
- Create: `src/skills/research_news.py`
- Modify: `src/skills/__init__.py`

- [ ] **Step 1: 创建 ResearchNewsSkill**

```python
# src/skills/research_news.py
"""新闻监控 Skill"""
from .base import BaseSkill, SkillContext, SkillResult
from .prompts import RESEARCH_NEWS_PROMPT
import httpx
import asyncio
from typing import Optional

class ResearchNewsSkill(BaseSkill):
    """新闻监控与快评生成"""

    @property
    def name(self) -> str:
        return "research-news"

    @property
    def description(self) -> str:
        return "新闻监控与快评生成：输入新闻内容，输出结构化快评"

    def get_system_prompt(self) -> str:
        return RESEARCH_NEWS_PROMPT

    async def execute(self, context: SkillContext) -> SkillResult:
        try:
            news_content = context.user_input

            if not news_content:
                return SkillResult(
                    success=False,
                    content="",
                    metadata={},
                    error="未提供新闻内容"
                )

            prompt = self._build_prompt(news_content)

            return SkillResult(
                success=True,
                content=prompt,
                metadata={
                    "skill": self.name,
                    "type": "quick_review"
                }
            )

        except Exception as e:
            return SkillResult(
                success=False,
                content="",
                metadata={},
                error=str(e)
            )

    def _build_prompt(self, news_content: str) -> str:
        return f"""请根据以下新闻内容生成结构化快评：

{news_content}

请按照以下格式输出：

### 📰 事件摘要
[2-3句话概括核心事件]

### 🔗 影响链分析
- **影响方向**：正面/负面/中性
- **影响程度**：重大/中等/轻微
- **影响持续**：长期/中期/短期
- **影响逻辑**：[1-2句话解释逻辑]

### 📊 标的映射
| 标的 | 影响方向 | 影响程度 | 备注 |
|-----|---------|---------|------|
| | | | |

### ⚠️ 风险提示
[如有风险需要提示]

### 💬 分析师备注
[补充观点或待验证事项]
"""
```

- [ ] **Step 2: 更新 __init__.py**

```python
# src/skills/__init__.py
from .base import BaseSkill, SkillContext, SkillResult
from .research_news import ResearchNewsSkill
# ... other imports
```

- [ ] **Step 3: 提交**

```bash
git add src/skills/research_news.py
git commit -m "feat: implement ResearchNewsSkill"
```

---

## Task 7: Report经纪 实现

**Files:**
- Create: `src/skills/research_report.py`

- [ ] **Step 1: 创建 ResearchReportSkill**

```python
# src/skills/research_report.py
"""报告生成 Skill"""
from .base import BaseSkill, SkillContext, SkillResult
from .prompts import RESEARCH_REPORT_PROMPT

class ResearchReportSkill(BaseSkill):
    """报告章节生成"""

    @property
    def name(self) -> str:
        return "research-report"

    @property
    def description(self) -> str:
        return "报告生成：输入公司/行业信息，输出研究报告章节"

    def get_system_prompt(self) -> str:
        return RESEARCH_REPORT_PROMPT

    async def execute(self, context: SkillContext) -> SkillResult:
        try:
            content = context.user_input

            if not content:
                return SkillResult(
                    success=False,
                    content="",
                    metadata={},
                    error="未提供内容"
                )

            report_content = self._generate_report(content)

            return SkillResult(
                success=True,
                content=report_content,
                metadata={
                    "skill": self.name,
                    "type": "report"
                }
            )

        except Exception as e:
            return SkillResult(
                success=False,
                content="",
                metadata={},
                error=str(e)
            )

    def _generate_report(self, content: str) -> str:
        return f"""## 研究报告

### 一、公司/行业概况
{content}

### 二、核心观点

### 三、风险因素

### 四、数据来源
- 公司公告
- 行业数据
- 公开信息
"""
```

- [ ] **Step 2: 提交**

```bash
git add src/skills/research_report.py
git commit -m "feat: implement ResearchReportSkill"
```

---

## Task 8: Data经纪 实现

**Files:**
- Create: `src/skills/research_data.py`

- [ ] **Step 1: 创建 ResearchDataSkill**

```python
# src/skills/research_data.py
"""数据更新 Skill"""
from .base import BaseSkill, SkillContext, SkillResult
from .prompts import DATA_VALIDATION_PROMPT
import re

class ResearchDataSkill(BaseSkill):
    """数据更新与校验"""

    @property
    def name(self) -> str:
        return "research-data"

    @property
    def description(self) -> str:
        return "数据更新：输入数据或文件路径，输出更新结果和校验报告"

    def get_system_prompt(self) -> str:
        return DATA_VALIDATION_PROMPT

    async def execute(self, context: SkillContext) -> SkillResult:
        try:
            content = context.user_input

            if not content:
                return SkillResult(
                    success=False,
                    content="",
                    metadata={},
                    error="未提供数据"
                )

            validation_result = self._validate_data(content)

            return SkillResult(
                success=True,
                content=validation_result,
                metadata={
                    "skill": self.name,
                    "type": "data_validation"
                }
            )

        except Exception as e:
            return SkillResult(
                success=False,
                content="",
                metadata={},
                error=str(e)
            )

    def _validate_data(self, content: str) -> str:
        """数据校验"""
        warnings = []
        errors = []

        lines = content.strip().split("\n")
        for i, line in enumerate(lines, 1):
            if "N/A" in line or "null" in line.lower():
                warnings.append(f"Line {i}: 存在缺失值")
            if "%" in line:
                try:
                    pct = float(re.search(r"(-?\d+\.?\d*)%", line).group(1))
                    if abs(pct) > 100:
                        errors.append(f"Line {i}: 百分比超出合理范围 ({pct}%)")
                except:
                    pass

        if errors:
            return f"❌ 数据校验失败:\n" + "\n".join(f"  - {e}" for e in errors)
        elif warnings:
            return f"⚠️ 数据校验通过（有警告）:\n" + "\n".join(f"  - {w}" for w in warnings)
        else:
            return "✅ 数据校验通过"
```

- [ ] **Step 2: 提交**

```bash
git add src/skills/research_data.py
git commit -m "feat: implement ResearchDataSkill"
```

---

## Task 9: Review Skill 实现

**Files:**
- Create: `src/skills/research_review.py`

- [ ] **Step 1: 创建 ResearchReviewSkill**

```python
# src/skills/research_review.py
"""内容审查 Skill"""
from .base import BaseSkill, SkillContext, SkillResult

class ResearchReviewSkill(BaseSkill):
    """快速内容审查"""

    @property
    def name(self) -> str:
        return "research-review"

    @property
    def description(self) -> str:
        return "内容审查：输入文本，返回质量评估和改进建议"

    async def execute(self, context: SkillContext) -> SkillResult:
        try:
            content = context.user_input

            if not content:
                return SkillResult(
                    success=False,
                    content="",
                    metadata={},
                    error="未提供审查内容"
                )

            review_result = self._review_content(content)

            return SkillResult(
                success=True,
                content=review_result,
                metadata={
                    "skill": self.name,
                    "type": "review"
                }
            )

        except Exception as e:
            return SkillResult(
                success=False,
                content="",
                metadata={},
                error=str(e)
            )

    def _review_content(self, content: str) -> str:
        """审查内容"""
        word_count = len(content)
        issues = []
        suggestions = []

        if word_count < 50:
            issues.append("内容过短，可能缺乏深度分析")
        elif word_count > 5000:
            issues.append("内容过长，建议精简")

        if "？" in content and content.count("？") > 5:
            suggestions.append("疑问句较多，请确保事实陈述与观点推断区分清晰")

        if not any(marker in content for marker in ["正面", "负面", "中性", "影响"]):
            issues.append("缺少影响方向判断")

        if "待验证" not in content and "需确认" not in content:
            suggestions.append("建议标注不确定性内容")

        result = "## 📋 内容审查报告\n\n"
        result += f"**字数**：{word_count}\n\n"

        if issues:
            result += "### ⚠️ 问题\n"
            for issue in issues:
                result += f"- {issue}\n"
            result += "\n"

        if suggestions:
            result += "### 💡 建议\n"
            for suggestion in suggestions:
                result += f"- {suggestion}\n"
            result += "\n"

        if not issues and not suggestions:
            result += "✅ 内容审查通过\n"

        return result
```

- [ ] **Step 2: 提交**

```bash
git add src/skills/research_review.py
git commit -m "feat: implement ResearchReviewSkill"
```

---

## Task 10: MCP 基础连接器

**Files:**
- Create: `src/mcp/__init__.py`
- Create: `src/mcp/news_mcp.py`
- Create: `src/mcp/data_mcp.py`

- [ ] **Step 1: 创建 MCP 模块初始化**

```python
# src/mcp/__init__.py
"""MCP 连接器模块"""
from .news_mcp import NewsMCP
from .data_mcp import DataMCP

__all__ = ["NewsMCP", "DataMCP"]
```

- [ ] **Step 2: 创建新闻 MCP 连接器**

```python
# src/mcp/news_mcp.py
"""新闻 MCP 连接器"""
import httpx
from typing import Optional
from dataclasses import dataclass

@dataclass
class NewsItem:
    """新闻条目"""
    title: str
    content: str
    source: str
    published_at: str
    url: Optional[str] = None
    entities: Optional[list] = None

class NewsMCP:
    """新闻数据连接器（支持多种数据源）"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2" if api_key else None

    async def fetch_news(self, keywords: list[str], limit: int = 10) -> list[NewsItem]:
        """获取新闻"""
        if not self.api_key:
            return self._mock_news(keywords)

        async with httpx.AsyncClient() as client:
            query = " AND ".join(keywords)
            response = await client.get(
                f"{self.base_url}/everything",
                params={
                    "q": query,
                    "pageSize": limit,
                    "apiKey": self.api_key,
                    "language": "zh"
                }
            )
            data = response.json()

            return [
                NewsItem(
                    title=article["title"],
                    content=article.get("description", ""),
                    source=article["source"]["name"],
                    published_at=article["publishedAt"],
                    url=article.get("url")
                )
                for article in data.get("articles", [])
            ]

    def _mock_news(self, keywords: list[str]) -> list[NewsItem]:
        """模拟新闻数据（无API Key时使用）"""
        return [
            NewsItem(
                title=f"{keywords[0] if keywords else '电池材料'}行业动态",
                content="行业最新动态，具体内容待补充",
                source="模拟数据源",
                published_at="2026-05-25T10:00:00Z"
            )
        ]
```

- [ ] **Step 3: 创建数据 MCP 连接器**

```python
# src/mcp/data_mcp.py
"""数据 MCP 连接器"""
from pathlib import Path
from typing import Optional
import csv
from io import StringIO

class DataMCP:
    """数据文件连接器"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def read_csv(self, filename: str) -> list[dict]:
        """读取CSV文件"""
        path = self.data_dir / filename
        if not path.exists():
            return []

        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def write_csv(self, filename: str, data: list[dict]) -> Path:
        """写入CSV文件"""
        path = self.data_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)

        if not data:
            return path

        fieldnames = data[0].keys()
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        return path

    def append_csv(self, filename: str, row: dict) -> Path:
        """追加CSV行"""
        path = self.data_dir / filename
        file_exists = path.exists()

        with open(path, "a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

        return path
```

- [ ] **Step 4: 提交**

```bash
git add src/mcp/
git commit -m "feat: implement MCP connectors (NewsMCP, DataMCP)"
```

---

## Task 11: Agent 协调层

**Files:**
- Create: `src/agents/__init__.py`
- Create: `src/agents/news_broker.py`
- Create: `src/agents/data_broker.py`
- Create: `src/agents/report_broker.py`

- [ ] **Step 1: 创建 Agents 初始化**

```python
# src/agents/__init__.py
"""Agent 协调层"""
from .news_broker import NewsBroker
from .data_broker import DataBroker
from .report_broker import ReportBroker

__all__ = ["NewsBroker", "DataBroker", "ReportBroker"]
```

- [ ] **Step 2: 创建 NewsBroker**

```python
# src/agents/news_broker.py
"""News 经纪：协调新闻获取、处理、生成的完整流程"""
from typing import Optional
from src.skills.research_news import ResearchNewsSkill
from src.skills.base import SkillContext
from src.storage import FileStorage, VectorStorage, ObsidianStorage

class NewsBroker:
    """新闻经纪：协调新闻处理全流程"""

    def __init__(
        self,
        file_storage: FileStorage,
        vector_storage: VectorStorage,
        obsidian_storage: ObsidianStorage
    ):
        self.file_storage = file_storage
        self.vector_storage = vector_storage
        self.obsidian_storage = obsidian_storage
        self.skill = ResearchNewsSkill()

    async def process_news(self, news_content: str, metadata: Optional[dict] = None) -> dict:
        """处理新闻：获取→生成快评→归档"""
        metadata = metadata or {}

        context = SkillContext(
            user_input=news_content,
            config={}
        )

        result = await self.skill.execute(context)

        if result.success:
            self.file_storage.save_draft(
                result.content,
                f"news_review_{metadata.get('date', 'draft')}.md",
                metadata
            )

            self.vector_storage.add_document(
                doc_id=f"news_{metadata.get('date', 'draft')}",
                content=result.content,
                metadata={**metadata, "type": "news_review"}
            )

        return {
            "success": result.success,
            "content": result.content,
            "error": result.error
        }

    async def generate_quick_review(self, news_content: str) -> str:
        """生成快评"""
        context = SkillContext(user_input=news_content, config={})
        result = await self.skill.execute(context)
        return result.content if result.success else result.error
```

- [ ] **Step 3: 创建 DataBroker**

```python
# src/agents/data_broker.py
"""Data 经纪：协调数据更新、校验、归档流程"""
from typing import Optional
from src.skills.research_data import ResearchDataSkill
from src.skills.base import SkillContext
from src.storage import FileStorage

class DataBroker:
    """数据经纪：协调数据处理全流程"""

    def __init__(self, file_storage: FileStorage):
        self.file_storage = file_storage
        self.skill = ResearchDataSkill()

    async def update_data(self, data_content: str, data_type: str = "raw") -> dict:
        """更新数据：校验→归档"""
        context = SkillContext(user_input=data_content, config={})
        result = await self.skill.execute(context)

        if result.success:
            self.file_storage.archive_data(data_content, f"data_update.md", data_type)

        return {
            "success": result.success,
            "validation": result.content,
            "error": result.error
        }

    async def validate_data(self, data_content: str) -> str:
        """校验数据"""
        context = SkillContext(user_input=data_content, config={})
        result = await self.skill.execute(context)
        return result.content if result.success else result.error
```

- [ ] **Step 4: 创建 ReportBroker**

```python
# src/agents/report_broker.py
"""Report 经纪：协调报告生成、审批、归档流程"""
from typing import Optional
from src.skills.research_report import ResearchReportSkill
from src.skills.base import SkillContext
from src.storage import FileStorage, VectorStorage, ObsidianStorage

class ReportBroker:
    """报告经纪：协调报告生成全流程"""

    def __init__(
        self,
        file_storage: FileStorage,
        vector_storage: VectorStorage,
        obsidian_storage: ObsidianStorage
    ):
        self.file_storage = file_storage
        self.vector_storage = vector_storage
        self.obsidian_storage = obsidian_storage
        self.skill = ResearchReportSkill()

    async def generate_report(
        self,
        content: str,
        title: str,
        metadata: Optional[dict] = None
    ) -> dict:
        """生成报告"""
        metadata = metadata or {}
        context = SkillContext(user_input=content, config={})
        result = await self.skill.execute(context)

        if result.success:
            filename = f"{title}.md"
            self.file_storage.save_draft(result.content, filename, metadata)

        return {
            "success": result.success,
            "content": result.content,
            "error": result.error
        }

    async def finalize_report(
        self,
        draft_path: str,
        approved_content: str
    ) -> dict:
        """定稿报告"""
        import shutil
        from pathlib import Path

        draft = Path(draft_path)
        final_path = self.file_storage.save_final(
            approved_content,
            draft.name,
            {"status": "final", "finalized_at": "2026-05-25"}
        )

        self.vector_storage.add_document(
            doc_id=f"report_{draft.stem}",
            content=approved_content,
            metadata={"type": "report", "status": "final"}
        )

        return {"success": True, "path": str(final_path)}
```

- [ ] **Step 5: 提交**

```bash
git add src/agents/
git commit -m "feat: implement Agent brokers (NewsBroker, DataBroker, ReportBroker)"
```

---

## Task 12: Skills 指令注册

**Files:**
- Create: `src/skills/registry.py`
- Modify: `CLAUDE.md`

- [ ] **Step 1: 创建 Skill 注册表**

```python
# src/skills/registry.py
"""Skill 注册表"""
from typing import Dict, Type
from .base import BaseSkill
from .research_news import ResearchNewsSkill
from .research_data import ResearchDataSkill
from .research_report import ResearchReportSkill
from .research_review import ResearchReviewSkill

SKILL_REGISTRY: Dict[str, Type[BaseSkill]] = {
    "research-news": ResearchNewsSkill,
    "research-data": ResearchDataSkill,
    "research-report": ResearchReportSkill,
    "research-review": ResearchReviewSkill,
}

def get_skill(name: str) -> BaseSkill:
    """获取 Skill 实例"""
    skill_class = SKILL_REGISTRY.get(name)
    if not skill_class:
        raise ValueError(f"Unknown skill: {name}")
    return skill_class()
```

- [ ] **Step 2: 更新 CLAUDE.md 添加 Skills 使用说明**

```markdown
## Skills 使用

### /research
新闻监控与快评生成
```
/research
[粘贴新闻内容]
```
输出：结构化快评（事件摘要、影响链分析、标的映射）

### /data
数据更新与校验
```
/data
[粘贴数据内容]
```
输出：数据校验报告

### /report
报告生成
```
/report 公司名称
[输入公司/行业信息]
```
输出：研究报告章节

### /review
内容审查
```
/review
[粘贴文本内容]
```
输出：质量评估和改进建议
```

- [ ] **Step 3: 提交**

```bash
git add src/skills/registry.py CLAUDE.md
git commit -m "feat: add skill registry and usage documentation"
```

---

## Task 13: 端到端集成测试

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: 创建集成测试**

```python
# tests/test_integration.py
"""端到端集成测试"""
import pytest
import asyncio
import tempfile
from pathlib import Path

from src.storage import FileStorage, VectorStorage, ObsidianStorage
from src.agents import NewsBroker, DataBroker, ReportBroker
from src.skills import get_skill, ResearchNewsSkill

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def storages(temp_dir):
    file_storage = FileStorage(temp_dir)
    vector_storage = VectorStorage(temp_dir / "vector_db")
    obsidian_storage = ObsidianStorage(
        temp_dir / "vault",
        temp_dir / "templates"
    )
    return file_storage, vector_storage, obsidian_storage

def test_news_broker_integration(storages):
    file_storage, vector_storage, obsidian_storage = storages
    broker = NewsBroker(file_storage, vector_storage, obsidian_storage)

    news_content = "宁德时代宣布在江西追加锂矿投资50亿元"

    result = asyncio.run(broker.generate_quick_review(news_content))

    assert result is not None
    assert len(result) > 0
    assert "影响" in result

def test_data_broker_integration(storages):
    file_storage, _, _ = storages
    broker = DataBroker(file_storage)

    data_content = "公司,营收,毛利\nA公司,100,30"

    result = asyncio.run(broker.validate_data(data_content))

    assert result is not None
    assert "校验" in result

def test_skill_registry():
    skill = get_skill("research-news")
    assert isinstance(skill, ResearchNewsSkill)
    assert skill.name == "research-news"
```

- [ ] **Step 2: 运行集成测试**

```bash
pytest tests/test_integration.py -v
```

Expected: 3 PASS

- [ ] **Step 3: 提交**

```bash
git add tests/test_integration.py
git commit -m "test: add integration tests for full workflow"
```

---

## 实施检查清单

- [ ] Task 1: 项目基础设置
- [ ] Task 2: 目录结构创建
- [ ] Task 3: 存储层基础实现
- [ ] Task 4: Obsidian 模板设计
- [ ] Task 5: Skills 基础框架
- [ ] Task 6: News经纪 实现
- [ ] Task 7: Report经纪 实现
- [ ] Task 8: Data经纪 实现
- [ ] Task 9: Review Skill 实现
- [ ] Task 10: MCP 基础连接器
- [ ] Task 11: Agent 协调层
- [ ] Task 12: Skills 指令注册
- [ ] Task 13: 端到端集成测试

---

## 依赖关系

```
Task 1 (基础配置) → Task 2 (目录结构) → Task 3 (存储层) → Task 4 (模板)
                                                           ↓
Task 5 (Skills框架) ← ────────────────────────────── Task 3
        ↓
Task 6,7,8,9 (各Skill实现)
        ↓
Task 10 (MCP) ← Task 3
        ↓
Task 11 (Agent协调层) ← Task 6,7,8,9,10
        ↓
Task 12 (注册) ← Task 11
        ↓
Task 13 (集成测试)
```

**Plan complete and saved to `docs/superpowers/plans/2026-05-25-research-assistant-ai-plan.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?