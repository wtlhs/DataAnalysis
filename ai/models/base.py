"""
基础模型接口

定义统一的大模型接口，支持多模型切换
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseModel(ABC):
    """大模型基础接口"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化模型

        Args:
            config: 模型配置
        """
        self.config = config
        self.api_key = config.get('api_key', '')
        self.model_name = config.get('model_name', '')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 4000)
        self.api_base = config.get('api_base', None)

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        聊天对话

        Args:
            messages: 消息列表，格式: [{"role": "user", "content": "..."}]

        Returns:
            模型响应
        """
        pass

    @abstractmethod
    def analyze(self, data: Dict[str, Any], prompt: str) -> str:
        """
        数据分析

        Args:
            data: 数据字典
            prompt: 分析提示

        Returns:
            分析结果
        """
        pass

    @abstractmethod
    def generate_insights(
        self,
        data_summary: Dict[str, Any],
        analysis_result: Dict[str, Any]
    ) -> List[str]:
        """
        生成智能洞察

        Args:
            data_summary: 数据摘要
            analysis_result: 分析结果

        Returns:
            洞察列表
        """
        pass

    @abstractmethod
    def write_report(
        self,
        all_results: Dict[str, Any],
        report_format: str = "markdown"
    ) -> str:
        """
        编写分析报告

        Args:
            all_results: 所有分析结果
            report_format: 报告格式

        Returns:
            报告内容
        """
        pass

    def get_model_info(self) -> Dict[str, str]:
        """获取模型信息"""
        return {
            'provider': self.__class__.__name__,
            'model_name': self.model_name,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens
        }


class ModelError(Exception):
    """模型错误"""
    pass


class RateLimitError(ModelError):
    """速率限制错误"""
    pass


class AuthenticationError(ModelError):
    """认证错误"""
    pass


class TokenLimitError(ModelError):
    """Token限制错误"""
    pass
