from typing import List, Dict, Any, Optional
import numpy as np
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)

from rag_service.config.settings import settings
from rag_service.app.core.vectordb.base import BaseVectorDB

class MilvusStore(BaseVectorDB):
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.collection_name = "rag_documents"
        self.dimension = 1536  # OpenAI embeddings维度
        self._connect()
        self._init_collection()
    
    def _connect(self):
        """连接到Milvus服务器"""
        connections.connect(
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT
        )
    
    def _init_collection(self):
        """初始化集合"""
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            return
        
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
            FieldSchema(name="metadata", dtype=DataType.JSON)
        ]
        
        schema = CollectionSchema(fields=fields, description="RAG documents collection")
        self.collection = Collection(name=self.collection_name, schema=schema)
        
        # 创建索引
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        self.collection.create_index(field_name="embedding", index_params=index_params)
    
    async def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> List[str]:
        """添加文本到向量数据库"""
        if not metadatas:
            metadatas = [{"source": f"doc_{i}"} for i in range(len(texts))]
        
        # 获取文本的嵌入向量
        embeddings = await self.embeddings.aembed_documents(texts)
        
        # 准备数据
        entities = [
            {"text": text, "embedding": embedding, "metadata": metadata}
            for text, embedding, metadata in zip(texts, embeddings, metadatas)
        ]
        
        # 插入数据
        self.collection.insert(entities)
        self.collection.flush()
        
        return [str(i) for i in range(len(texts))]
    
    async def similarity_search(
        self,
        query: str,
        k: int = 4,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """相似度搜索"""
        # 获取查询文本的嵌入向量
        query_embedding = await self.embeddings.aembed_documents([query])
        
        # 搜索参数
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }
        
        # 执行搜索
        results = self.collection.search(
            data=query_embedding,
            anns_field="embedding",
            param=search_params,
            limit=k,
            output_fields=["text", "metadata"]
        )
        
        # 格式化结果
        docs = []
        for hits in results:
            for hit in hits:
                docs.append({
                    "text": hit.entity.get("text"),
                    "metadata": hit.entity.get("metadata"),
                    "score": hit.distance
                })
        
        return docs
    
    async def delete(self, ids: List[str]) -> None:
        """删除向量"""
        expr = f'id in {ids}'
        self.collection.delete(expr)
    
    async def clear(self) -> None:
        """清空数据库"""
        utility.drop_collection(self.collection_name)
        self._init_collection() 