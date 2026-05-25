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