from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from tenacity import retry, stop_after_attempt, wait_exponential

from rag_service.app.core.llm.base import BaseLLMService
from rag_service.app.core.vectordb.base import BaseVectorDB
from rag_service.config.settings import settings

class RAGService:
    def __init__(
        self,
        llm_service: BaseLLMService,
        vector_db: BaseVectorDB
    ):
        self.llm_service = llm_service
        self.vector_db = vector_db
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        # 默认的RAG提示模板
        self.default_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""使用以下上下文来回答问题。如果你不知道答案，就说你不知道，不要试图编造答案。

上下文: {context}

问题: {question}

回答:"""
        )
    
    async def add_documents(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None):
        """添加文档到向量数据库"""
        chunks = self.text_splitter.split_texts(texts)
        return await self.vector_db.add_texts(chunks, metadatas)
    
    @retry(
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def query(
        self,
        question: str,
        prompt_template: Optional[PromptTemplate] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """查询RAG系统"""
        # 检索相关文档
        docs = await self.vector_db.similarity_search(
            question,
            k=settings.TOP_K_RESULTS
        )
        
        # 评估检索结果
        context = self._evaluate_retrieval(docs, question)
        
        # 使用提示模板生成回答
        prompt = prompt_template or self.default_prompt
        response = await self.llm_service.generate(
            prompt.format(context=context, question=question)
        )
        
        return {
            "answer": response,
            "context": context,
            "sources": [doc["metadata"] for doc in docs]
        }
    
    def _evaluate_retrieval(
        self,
        docs: List[Dict[str, Any]],
        question: str
    ) -> str:
        """评估检索结果的相关性"""
        # 这里可以实现更复杂的评估逻辑
        # 例如：使用另一个LLM来评估相关性
        return "\n\n".join([doc["text"] for doc in docs]) 