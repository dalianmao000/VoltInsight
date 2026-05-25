"""向量库存储"""
import chromadb
from pathlib import Path
from typing import Optional

class VectorStorage:
    """ChromaDB 向量库管理器"""

    def __init__(self, persist_dir: Path):
        self.persist_dir = persist_dir
        try:
            self.client = chromadb.PersistentClient(path=str(persist_dir))
            self.collection = self.client.get_or_create_collection(
                name="research_notes",
                metadata={"description": "Research notes for semantic search"}
            )
        except Exception as e:
            raise IOError(f"Failed to initialize vector storage: {e}")

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        return Path(filename).name

    def add_document(self, doc_id: str, content: str, metadata: dict) -> None:
        """添加文档到向量库"""
        try:
            doc_id = self._sanitize_filename(doc_id)
            self.collection.add(
                documents=[content],
                ids=[doc_id],
                metadatas=[metadata]
            )
        except Exception as e:
            raise IOError(f"Failed to add document: {e}")

    def search(self, query: str, n_results: int = 5) -> list:
        """语义检索"""
        try:
            if n_results <= 0:
                raise ValueError("n_results must be a positive integer")
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return results
        except ValueError:
            raise
        except Exception as e:
            raise IOError(f"Failed to search: {e}")

    def delete(self, doc_id: str) -> None:
        """删除文档"""
        try:
            doc_id = self._sanitize_filename(doc_id)
            self.collection.delete(ids=[doc_id])
        except Exception as e:
            raise IOError(f"Failed to delete document: {e}")