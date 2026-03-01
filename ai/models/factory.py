"""
模型工厂

使用工厂模式创建不同的大模型实例
"""
from typing import Dict, Any, Optional

from .base import BaseModel
from .openai import OpenAIModel
from .anthropic import AnthropicModel


class ModelFactory:
    """模型工厂类"""

    # 模型注册表
    _models: Dict[str, type] = {
        'openai': OpenAIModel,
        'anthropic': AnthropicModel
    }

    @classmethod
    def register_model(cls, name: str, model_class: type):
        """
        注册新模型

        Args:
            name: 模型名称
            model_class: 模型类
        """
        cls._models[name] = model_class

    @classmethod
    def create_model(cls, provider: str, config: Optional[Dict[str, Any]] = None) -> BaseModel:
        """
        创建模型实例

        Args:
            provider: 提供商名称 ('openai', 'anthropic')
            config: 模型配置

        Returns:
            模型实例

        Raises:
            ValueError: 不支持的提供商
        """
        provider = provider.lower()

        if provider not in cls._models:
            raise ValueError(
                f"不支持的模型提供商: {provider}. "
                f"支持的提供商: {', '.join(cls._models.keys())}"
            )

        model_class = cls._models[provider]

        if config is None:
            config = {}

        return model_class(config)

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """获取支持的提供商列表"""
        return list(cls._models.keys())

    @classmethod
    def get_default_config(cls, provider: str) -> Dict[str, Any]:
        """
        获取默认配置

        Args:
            provider: 提供商名称

        Returns:
            默认配置字典
        """
        default_configs = {
            'openai': {
                'model_name': 'gpt-4o',
                'temperature': 0.7,
                'max_tokens': 4000
            },
            'anthropic': {
                'model_name': 'claude-sonnet-4-20250514',
                'temperature': 0.7,
                'max_tokens': 4000
            }
        }

        return default_configs.get(provider, {})


def get_model(provider: str, config: Optional[Dict[str, Any]] = None) -> BaseModel:
    """
    便捷函数：获取模型实例

    Args:
        provider: 提供商名称
        config: 模型配置

    Returns:
        模型实例
    """
    return ModelFactory.create_model(provider, config)
