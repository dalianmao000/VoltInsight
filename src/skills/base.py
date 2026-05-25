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