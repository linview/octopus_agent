from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseVectorDB(ABC):
    """向量数据库的基础接口"""
    
    @abstractmethod
    async def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> List[str]:
        """添加文本到向量数据库"""
        pass
    
    @abstractmethod
    async def similarity_search(
        self,
        query: str,
        k: int = 4,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """相似度搜索"""
        pass
    
    @abstractmethod
    async def delete(self, ids: List[str]) -> None:
        """删除向量"""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """清空数据库"""
        pass 