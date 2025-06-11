from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from rag_service.app.core.llm.openai_service import OpenAIService
from rag_service.app.core.llm.transformer_service import TransformerService
from rag_service.app.core.vectordb.milvus_store import MilvusStore
from rag_service.app.core.rag_service import RAGService

router = APIRouter()

# 请求模型
class QueryRequest(BaseModel):
    question: str
    prompt_template: Optional[str] = None

class DocumentRequest(BaseModel):
    texts: List[str]
    metadatas: Optional[List[Dict[str, Any]]] = None

# 依赖注入
def get_rag_service():
    llm_service = OpenAIService()
    embedding_service = TransformerService()
    vector_db = MilvusStore(embedding_service)
    return RAGService(llm_service, vector_db)

@router.post("/query")
async def query(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """查询RAG系统"""
    try:
        result = await rag_service.query(
            question=request.question,
            prompt_template=request.prompt_template
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents")
async def add_documents(
    request: DocumentRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """添加文档到RAG系统"""
    try:
        result = await rag_service.add_documents(
            texts=request.texts,
            metadatas=request.metadatas
        )
        return {"ids": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 