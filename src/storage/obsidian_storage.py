"""Obsidian笔记存储"""
from pathlib import Path
from datetime import datetime
from typing import Optional

class ObsidianStorage:
    """Obsidian 笔记管理器"""

    def __init__(self, vault_path: Path, templates_path: Path):
        self.vault_path = vault_path
        self.templates_path = templates_path
        self.notes_path = vault_path / "notes"
        self.notes_path.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        return Path(filename).name

    def create_note_from_template(
        self,
        template_name: str,
        filename: str,
        variables: dict
    ) -> Path:
        """从模板创建笔记"""
        try:
            filename = self._sanitize_filename(filename)
            template_path = self.templates_path / template_name
            if not template_path.exists():
                raise FileNotFoundError(f"Template not found: {template_name}")

            content = template_path.read_text(encoding="utf-8")
            for key, value in variables.items():
                content = content.replace(f"{{{{{key}}}}}", str(value))

            note_path = self.notes_path / filename
            note_path.write_text(content, encoding="utf-8")
            return note_path
        except Exception as e:
            raise IOError(f"Failed to create note from template: {e}")

    def create_daily_note(self, date: Optional[datetime] = None) -> Path:
        """创建每日笔记"""
        try:
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
        except Exception as e:
            raise IOError(f"Failed to create daily note: {e}")

    def link_notes(self, from_path: Path, to_path: Path, link_text: Optional[str] = None) -> None:
        """创建笔记间双向链接"""
        try:
            link_text = link_text or to_path.stem

            # Add link from from_path to to_path
            from_content = from_path.read_text(encoding="utf-8")
            link_markdown = f"[[{link_text}]]"
            if link_markdown not in from_content:
                from_content += f"\n\n## 链接\n- {link_markdown}\n"
                from_path.write_text(from_content, encoding="utf-8")

            # Add reverse link from to_path to from_path
            reverse_link = f"[[{from_path.stem}]]"
            to_content = to_path.read_text(encoding="utf-8")
            if reverse_link not in to_content:
                to_content += f"\n\n## 链接\n- {reverse_link}\n"
                to_path.write_text(to_content, encoding="utf-8")
        except Exception as e:
            raise IOError(f"Failed to link notes: {e}")