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