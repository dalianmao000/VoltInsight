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