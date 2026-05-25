"""Research Data Skill"""
from .base import BaseSkill, SkillContext, SkillResult


class ResearchDataSkill(BaseSkill):
    """研究数据 Skill"""

    @property
    def name(self) -> str:
        return "research-data"

    @property
    def description(self) -> str:
        return "数据收集与验证技能"

    async def execute(self, context: SkillContext) -> SkillResult:
        return SkillResult(
            success=True,
            content="",
            metadata={}
        )