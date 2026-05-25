"""端到端集成测试"""
import pytest
import asyncio
import tempfile
from pathlib import Path

from src.storage import FileStorage, VectorStorage, ObsidianStorage
from src.skills.research_news import ResearchNewsSkill
from src.skills.research_data import ResearchDataSkill

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

    skill = ResearchNewsSkill()
    news_content = "宁德时代宣布在江西追加锂矿投资50亿元"

    # Test Skill execution
    from src.skills.base import SkillContext
    context = SkillContext(user_input=news_content, config={})
    result = asyncio.run(skill.execute(context))

    assert result.success
    assert len(result.content) > 0
    assert "影响" in result.content

def test_data_broker_integration(storages):
    file_storage, _, _ = storages

    skill = ResearchDataSkill()
    data_content = "公司,营收,毛利\nA公司,100,30"

    from src.skills.base import SkillContext
    context = SkillContext(user_input=data_content, config={})
    result = asyncio.run(skill.execute(context))

    assert result.success
    assert "校验" in result.content

def test_skill_registry():
    skill = ResearchNewsSkill()
    assert isinstance(skill, ResearchNewsSkill)
    assert skill.name == "research-news"

def test_file_storage_workflow(storages):
    file_storage, _, _ = storages

    # Test save_draft
    draft_path = file_storage.save_draft("# Test Draft", "test_draft.md", {"type": "test"})
    assert draft_path.exists()

    # Test save_final
    final_path = file_storage.save_final("# Test Final", "test_final.md", {"type": "test"})
    assert final_path.exists()

    # Test save_version
    version_path = file_storage.save_version("# Test Version", "test_version.md", "v1")
    assert version_path.exists()

def test_vector_storage_search(storages):
    _, vector_storage, _ = storages

    vector_storage.add_document(
        doc_id="test_doc",
        content="电池材料价格上涨影响分析",
        metadata={"type": "test"}
    )

    results = vector_storage.search("电池材料", n_results=1)
    assert len(results["ids"]) > 0
    assert "电池材料" in results["documents"][0][0]

def test_obsidian_note_creation(storages):
    _, _, obsidian_storage = storages

    # Create a template first
    template_dir = obsidian_storage.templates_path
    template_dir.mkdir(parents=True, exist_ok=True)
    template_file = template_dir / "test_template.md"
    template_file.write_text("# {{title}}\n\n{{content}}")

    # Create note from template
    note_path = obsidian_storage.create_note_from_template(
        "test_template.md",
        "test_note.md",
        {"title": "Test Note", "content": "Test content"}
    )

    assert note_path.exists()
    content = note_path.read_text()
    assert "Test Note" in content
    assert "Test content" in content