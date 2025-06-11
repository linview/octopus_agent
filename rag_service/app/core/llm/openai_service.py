from typing import Any, Dict, List
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from rag_service.config.settings import settings
from rag_service.app.core.llm.base import BaseLLMService

class OpenAIService(BaseLLMService):
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name=settings.OPENAI_API_MODEL,
            temperature=0.7,
            streaming=True,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
        )
        self.embeddings = OpenAIEmbeddings()
    
    async def generate(self, prompt: str, **kwargs) -> str:
        response = await self.llm.agenerate([prompt])
        return response.generations[0][0].text
    
    async def generate_with_history(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        response = await self.llm.agenerate([messages])
        return response.generations[0][0].text
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = await self.embeddings.aembed_documents(texts)
        return embeddings
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "openai",
            "model": settings.OPENAI_API_MODEL,
            "type": "chat"
        } 