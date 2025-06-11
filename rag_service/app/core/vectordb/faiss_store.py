from typing import List, Dict, Any, Optional
import faiss
import numpy as np
from langchain.vectorstores import FAISS
from langchain.embeddings.base import Embeddings

from rag_service.config.settings import settings
from rag_service.app.core.vectordb.base import BaseVectorDB

class FAISSStore(BaseVectorDB):
    def __init__(self, embeddings: Embeddings):
        self.embeddings = embeddings
        self.vector_store = None
        self._initialize_store()
    
    def _initialize_store(self):
        """初始化FAISS存储"""
        dimension = 1536  # OpenAI embeddings维度
        self.vector_store = FAISS.from_texts(
            [""], 
            self.embeddings,
            metadatas=[{"source": "init"}]
        )
        self.vector_store.delete([self.vector_store.index_to_docstore_id[0]])
    
    async def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> List[str]:
        if not metadatas:
            metadatas = [{"source": f"doc_{i}"} for i in range(len(texts))]
        
        self.vector_store.add_texts(texts=texts, metadatas=metadatas)
        return [str(i) for i in range(len(texts))]
    
    async def similarity_search(
        self,
        query: str,
        k: int = 4,
        **kwargs
    ) -> List[Dict[str, Any]]:
        docs = self.vector_store.similarity_search(query, k=k)
        return [
            {
                "text": doc.page_content,
                "metadata": doc.metadata,
                "score": doc.metadata.get("score", 0.0)
            }
            for doc in docs
        ]
    
    async def delete(self, ids: List[str]) -> None:
        # FAISS不支持直接删除，需要重建索引
        pass
    
    async def clear(self) -> None:
        self._initialize_store() 