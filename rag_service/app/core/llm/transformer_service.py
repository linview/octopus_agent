from typing import Any, Dict, List
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

from rag_service.config.settings import settings
from rag_service.app.core.llm.base import BaseLLMService

class TransformerService(BaseLLMService):
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        self.model.eval()  # 设置为评估模式
    
    def _mean_pooling(self, model_output, attention_mask):
        """对模型输出进行平均池化"""
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 0) / torch.clamp(input_mask_expanded.sum(0), min=1e-9)
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本响应（这里仅作为示例，实际使用时需要实现）"""
        raise NotImplementedError("TransformerService 目前仅支持嵌入功能")
    
    async def generate_with_history(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        """基于历史消息生成响应（这里仅作为示例，实际使用时需要实现）"""
        raise NotImplementedError("TransformerService 目前仅支持嵌入功能")
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """获取文本的嵌入向量"""
        # 对文本进行编码
        encoded_input = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors='pt'
        )
        
        # 计算嵌入向量
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        
        # 进行平均池化
        embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])
        
        # 转换为numpy数组并归一化
        embeddings = embeddings.numpy()
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        return embeddings.tolist()
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": "transformers",
            "model": self.model_name,
            "type": "embedding"
        } 