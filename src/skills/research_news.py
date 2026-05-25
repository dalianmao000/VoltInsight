"""Research News Skill"""
from .base import BaseSkill, SkillContext, SkillResult
from .prompts import RESEARCH_NEWS_PROMPT


class ResearchNewsSkill(BaseSkill):
    """研究新闻 Skill"""

    @property
    def name(self) -> str:
        return "research-news"

    @property
    def description(self) -> str:
        return "新闻研究与快评技能"

    async def execute(self, context: SkillContext) -> SkillResult:
        return SkillResult(
            success=True,
            content=f"新闻分析：{context.user_input}\n\n影响：待评估",
            metadata={}
        )

    def get_system_prompt(self) -> str:
        return RESEARCH_NEWS_PROMPT