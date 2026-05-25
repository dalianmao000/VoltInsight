"""Research Report Skill"""
from .base import BaseSkill, SkillContext, SkillResult


class ResearchReportSkill(BaseSkill):
    """研究报告 Skill"""

    @property
    def name(self) -> str:
        return "research-report"

    @property
    def description(self) -> str:
        return "研报撰写技能"

    async def execute(self, context: SkillContext) -> SkillResult:
        return SkillResult(
            success=True,
            content="",
            metadata={}
        )