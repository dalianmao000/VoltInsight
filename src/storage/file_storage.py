"""本地文件存储"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import yaml

class FileStorage:
    """文件存储管理器"""

    def __init__(self, root: Path):
        self.root = root

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        return Path(filename).name

    def save_draft(self, content: str, filename: str, metadata: Optional[dict] = None) -> Path:
        """保存草稿"""
        try:
            filename = self._sanitize_filename(filename)
            draft_dir = self.root / "research" / "drafts"
            draft_dir.mkdir(parents=True, exist_ok=True)
            path = draft_dir / filename
            path.write_text(content, encoding="utf-8")
            if metadata:
                meta_path = draft_dir / f"{filename}.meta.yaml"
                meta_path.write_text(yaml.dump(metadata), encoding="utf-8")
            return path
        except Exception as e:
            raise IOError(f"Failed to save draft: {e}")

    def save_final(self, content: str, filename: str, metadata: Optional[dict] = None) -> Path:
        """保存定稿"""
        try:
            filename = self._sanitize_filename(filename)
            final_dir = self.root / "research" / "final"
            final_dir.mkdir(parents=True, exist_ok=True)
            path = final_dir / filename
            path.write_text(content, encoding="utf-8")
            if metadata:
                meta_path = final_dir / f"{filename}.meta.yaml"
                meta_path.write_text(yaml.dump(metadata), encoding="utf-8")
            return path
        except Exception as e:
            raise IOError(f"Failed to save final: {e}")

    def save_version(self, content: str, filename: str, version: str) -> Path:
        """保存版本快照"""
        try:
            filename = self._sanitize_filename(filename)
            version_dir = self.root / "research" / "versions" / filename.replace(".md", "")
            version_dir.mkdir(parents=True, exist_ok=True)
            path = version_dir / f"{version}.md"
            path.write_text(content, encoding="utf-8")
            return path
        except Exception as e:
            raise IOError(f"Failed to save version: {e}")

    def archive_data(self, data: Any, filename: str, data_type: str = "raw") -> Path:
        """归档数据"""
        try:
            filename = self._sanitize_filename(filename)
            archive_dir = self.root / "data" / data_type / "archive"
            archive_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = archive_dir / f"{timestamp}_{filename}"
            if isinstance(data, str):
                path.write_text(data, encoding="utf-8")
            else:
                path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            return path
        except Exception as e:
            raise IOError(f"Failed to archive data: {e}")