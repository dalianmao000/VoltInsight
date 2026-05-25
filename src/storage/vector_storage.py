"""向量库存储"""
import chromadb
from pathlib import Path
from typing import Optional

class VectorStorage:
    """ChromaDB 向量库管理器"""

    def __init__(self, persist_dir: Path):
        self.persist_dir = persist_dir
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(
            name="research_notes",
            metadata={"description": "Research notes for semantic search"}
        )

    def add_document(self, doc_id: str, content: str, metadata: dict) -> None:
        """添加文档到向量库"""
        self.collection.add(
            documents=[content],
            ids=[doc_id],
            metadatas=[metadata]
        )

    def search(self, query: str, n_results: int = 5) -> list:
        """语义检索"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results

    def delete(self, doc_id: str) -> None:
        """删除文档"""
        self.collection.delete(ids=[doc_id])