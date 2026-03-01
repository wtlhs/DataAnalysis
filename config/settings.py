"""
配置管理模块

管理API密钥、模型配置、系统参数等
密钥从数据库读取，确保安全性
"""
import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class ModelConfig:
    """模型配置"""
    provider: str = "openai"  # openai, anthropic, zhipu
    model_name: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4000
    api_key: str = ""
    api_base: Optional[str] = None


@dataclass
class RiskThresholds:
    """风险阈值配置"""
    # 阈值倍数（标准差）
    high_risk_sigma: float = 3.0
    medium_risk_sigma: float = 2.0
    low_risk_sigma: float = 1.5

    # 数值阈值（可根据具体业务场景配置）
    min_data_points: int = 10
    max_missing_ratio: float = 0.3  # 最大缺失值比例

    # 趋势阈值
    trend_change_threshold: float = 0.2  # 20%变化视为显著

    def get_risk_level(self, sigma: float) -> str:
        """根据Sigma值返回风险等级"""
        if sigma >= self.high_risk_sigma:
            return "HIGH"
        elif sigma >= self.medium_risk_sigma:
            return "MEDIUM"
        else:
            return "LOW"


@dataclass
class DataConfig:
    """数据处理配置"""
    # 文件限制
    max_file_size_mb: int = 500
    allowed_extensions: list = field(default_factory=lambda: [".xlsx", ".xls", ".csv"])

    # 数据处理
    chunk_size: int = 10000  # 分块读取大小
    sample_size: int = 500  # AI分析采样大小
    date_columns: list = field(default_factory=lambda: ["date", "时间", "日期", "日期时间"])
    max_missing_ratio: float = 0.3  # 最大缺失值比例
    min_data_points: int = 10  # 最小数据点数

    # 预测配置
    forecast_periods: int = 30  # 预测未来30个周期
    prediction_confidence: float = 0.95  # 置信度


@dataclass
class AppConfig:
    """应用配置"""
    app_name: str = "数据分析智能体"
    version: str = "1.0.0"
    debug: bool = False

    # 路径配置
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = field(init=False)
    upload_dir: Path = field(init=False)
    output_dir: Path = field(init=False)

    def __post_init__(self):
        self.data_dir = self.base_dir / "data"
        self.upload_dir = self.base_dir / "uploads"
        self.output_dir = self.base_dir / "outputs"

        # 创建必要的目录
        self.data_dir.mkdir(exist_ok=True)
        self.upload_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)


class Settings:
    """全局配置管理器"""

    _instance: Optional['Settings'] = None
    _session_manager = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_session_manager(self):
        """获取会话管理器"""
        if Settings._session_manager is None:
            from db.session_manager import SessionManager
            Settings._session_manager = SessionManager(db_path="data/data_analysis.db")
        return Settings._session_manager

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.app = AppConfig()
            self.risk = RiskThresholds()
            self.data = DataConfig(
                max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "500")),
                chunk_size=int(os.getenv("CHUNK_SIZE", "10000"))
            )
            # 从数据库加载模型配置
            self.model = self._load_model_config()
            self.initialized = True

    def _load_model_config(self) -> ModelConfig:
        """从数据库加载模型配置"""
        try:
            session_manager = self._get_session_manager()
            api_config = session_manager.get_active_api_config()
            if api_config and api_config.get('api_key'):
                return ModelConfig(
                    provider=api_config.get('provider', 'openai'),
                    model_name=api_config.get('model_name', 'gpt-4o'),
                    temperature=api_config.get('temperature', 0.7),
                    max_tokens=api_config.get('max_tokens', 4000),
                    api_key=api_config.get('api_key', ''),
                    api_base=api_config.get('api_base')
                )
        except Exception:
            pass  # 数据库连接失败时使用默认值

        # 返回默认配置
        return ModelConfig(
            provider="openai",
            model_name="gpt-4o",
            temperature=0.7,
            max_tokens=4000,
            api_key="",
            api_base=None
        )

    def reload_model_config(self):
        """重新加载模型配置"""
        self.model = self._load_model_config()

    def get_model_config(self, provider: Optional[str] = None) -> ModelConfig:
        """获取模型配置"""
        if provider and provider != self.model.provider:
            # 从数据库获取指定provider的配置
            try:
                session_manager = self._get_session_manager()
                api_config = session_manager.get_api_config(provider)
                if api_config and api_config.get('api_key'):
                    return ModelConfig(
                        provider=api_config.get('provider', provider),
                        model_name=api_config.get('model_name', 'gpt-4o'),
                        temperature=api_config.get('temperature', 0.7),
                        max_tokens=api_config.get('max_tokens', 4000),
                        api_key=api_config.get('api_key', ''),
                        api_base=api_config.get('api_base')
                    )
            except Exception:
                pass
        return self.model

    def save_api_config(
        self,
        provider: str,
        api_key: str,
        api_base: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> bool:
        """保存API配置到数据库"""
        try:
            session_manager = self._get_session_manager()
            session_manager.save_api_config(
                provider=provider,
                api_key=api_key,
                api_base=api_base,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
            # 重新加载配置
            self.reload_model_config()
            return True
        except Exception as e:
            raise Exception(f"保存API配置失败: {str(e)}")

    def update_model(self, provider: str, model_name: str):
        """更新模型配置"""
        self.model.provider = provider
        self.model.model_name = model_name

    def validate(self) -> bool:
        """验证配置是否有效"""
        if self.model.provider == "openai" and not self.model.api_key:
            return False
        if self.model.provider == "anthropic" and not self.model.api_key:
            return False
        if self.model.provider == "zhipu" and not self.model.api_key:
            return False
        return True


# 全局配置实例
settings = Settings()
