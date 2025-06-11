from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Base Settings
    PYTHONPATH: str = "."
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "RAG Service"
    
    # LLM Settings
    LLM_PROVIDER: str = "openai"  # 可选的LLM提供商
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None
    OPENAI_API_MODEL: str = "gpt-3.5-turbo"
    
    # Vector DB Settings
    VECTOR_DB_TYPE: str = "faiss"  # 或 "milvus"
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    
    # Embedding Settings
    EMBEDDING_MODEL: str = "bert-base-uncased"  # 使用 BERT 基础模型
    
    # RAG Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 4
    
    # Retry Settings
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 