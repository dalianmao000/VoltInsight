"""Research Review Skill"""
from .base import BaseSkill, SkillContext, SkillResult


class ResearchReviewSkill(BaseSkill):
    """研究评审 Skill"""

    @property
    def name(self) -> str:
        return "research-review"

    @property
    def description(self) -> str:
        return "报告评审与优化技能"

    async def execute(self, context: SkillContext) -> SkillResult:
        return SkillResult(
            success=True,
            content="",
            metadata={}
        )