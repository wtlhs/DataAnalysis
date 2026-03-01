"""
AI智能体核心类

协调大模型调用，实现智能数据分析功能
"""
from typing import Dict, Any, List, Optional
import pandas as pd

from .models.base import BaseModel
from .models.factory import ModelFactory
from .prompts import PromptBuilder, PromptTemplates
from config.settings import settings


class DataAnalysisAgent:
    """数据分析智能体"""

    def __init__(self, model_provider: Optional[str] = None):
        """
        初始化AI智能体

        Args:
            model_provider: 模型提供商 ('openai', 'anthropic')
                          如果为None，使用settings中的默认值
        """
        if model_provider is None:
            model_provider = settings.model.provider

        # 获取模型配置
        model_config = settings.get_model_config(model_provider)

        # 创建模型实例
        self.model = ModelFactory.create_model(model_provider, model_config.__dict__)
        self.model_provider = model_provider

        # Prompt构建器
        self.prompt_builder = PromptBuilder()

    def analyze_context(
        self,
        df: pd.DataFrame,
        data_summary: Dict[str, Any]
    ) -> str:
        """
        分析数据上下文

        Args:
            df: 数据框
            data_summary: 数据摘要

        Returns:
            上下文分析结果
        """
        # 构建数据描述
        data_description = self._build_data_description(df, data_summary)

        # 构建关键指标
        key_metrics = self._extract_key_metrics(data_summary)

        # 构建分析Prompt
        prompt = self.prompt_builder.build_analyze_prompt(
            data_description=data_description,
            key_metrics=key_metrics,
            analysis_type='trend'
        )

        # 调用模型
        system_message = PromptTemplates.SYSTEM_ANALYST

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]

        return self.model.chat(messages)

    def generate_insights(
        self,
        data_summary: Dict[str, Any],
        analysis_result: Dict[str, Any],
        count: int = 5
    ) -> List[str]:
        """
        生成智能洞察

        Args:
            data_summary: 数据摘要
            analysis_result: 分析结果
            count: 洞察数量

        Returns:
            洞察列表
        """
        return self.model.generate_insights(data_summary, analysis_result)[:count]

    def generate_comprehensive_insights(
        self,
        df: pd.DataFrame,
        stats: Dict[str, Any],
        trend: Dict[str, Any],
        anomalies: Dict[str, Any],
        forecast: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[str]]:
        """
        生成多维度洞察

        Args:
            df: 数据框
            stats: 统计分析结果
            trend: 趋势分析结果
            anomalies: 异常检测结果
            forecast: 预测结果（可选）

        Returns:
            分组洞察字典
        """
        insights = {
            'trend': [],
            'anomaly': [],
            'opportunity': [],
            'risk': []
        }

        # 数据摘要
        data_summary = {
            'data_shape': df.shape,
            'columns': df.columns.tolist(),
            'stats': stats
        }

        # 趋势洞察
        if trend:
            trend_prompt = self._build_trend_insight_prompt(trend)
            trend_insight = self._query_model(trend_prompt)
            insights['trend'] = self._parse_insights(trend_insight, 2)

        # 异常洞察
        if anomalies:
            anomaly_prompt = self._build_anomaly_insight_prompt(anomalies)
            anomaly_insight = self._query_model(anomaly_prompt)
            insights['anomaly'] = self._parse_insights(anomaly_insight, 2)

        # 机会洞察
        opportunity_prompt = self._build_opportunity_prompt(stats, trend)
        opportunity_insight = self._query_model(opportunity_prompt)
        insights['opportunity'] = self._parse_insights(opportunity_insight, 2)

        # 风险洞察
        risk_prompt = self._build_risk_prompt(anomalies)
        risk_insight = self._query_model(risk_prompt)
        insights['risk'] = self._parse_insights(risk_insight, 2)

        return insights

    def write_report(
        self,
        all_results: Dict[str, Any],
        include_charts: bool = False
    ) -> str:
        """
        编写分析报告

        Args:
            all_results: 所有分析结果
            include_charts: 是否包含图表（预留）

        Returns:
            Markdown格式的报告
        """
        return self.model.write_report(all_results, report_format="markdown")

    def chat(
        self,
        question: str,
        df: Optional[pd.DataFrame] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        交互式问答

        Args:
            question: 用户问题
            df: 数据框（可选）
            context: 上下文信息（可选）

        Returns:
            回答
        """
        # 构建背景信息
        background = ""

        if df is not None:
            background += self._build_data_description(df, {})

        if context:
            background += "\n\n" + str(context)

        # 如果没有背景，使用默认背景
        if not background:
            background = "基于当前数据分析结果进行问答"

        # 构建问答Prompt
        analysis_results = context or {}
        prompt = self.prompt_builder.build_qa_prompt(
            question=question,
            background=background,
            analysis_results=analysis_results
        )

        # 调用模型
        system_message = """你是一个专业的数据分析师助手。请基于提供的数据和分析结果回答用户的问题。

回答要求：
1. 准确、清晰、有依据
2. 必要时引用具体数据
3. 如需额外分析，明确说明
4. 鼓励探索性提问"""

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]

        return self.model.chat(messages)

    def summarize_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        生成数据摘要（供AI使用）

        Args:
            df: 数据框

        Returns:
            数据摘要
        """
        summary = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'sample': df.head(5).to_dict(),
        }

        # 数值列统计
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary['numeric_summary'] = df[numeric_cols].describe().to_dict()

        return summary

    def analyze_anomalies_in_context(
        self,
        df: pd.DataFrame,
        anomaly_results: Dict[str, Any]
    ) -> str:
        """
        在上下文中分析异常值

        Args:
            df: 数据框
            anomaly_results: 异常检测结果

        Returns:
            异常分析结果
        """
        prompt = PromptTemplates.ANALYZE_ANOMALY.format(
            data_description=self._build_data_description(df, {}),
            anomaly_info=str(anomaly_results)
        )

        messages = [
            {"role": "system", "content": PromptTemplates.SYSTEM_ANALYST},
            {"role": "user", "content": prompt}
        ]

        return self.model.chat(messages)

    # 私有辅助方法

    def _build_data_description(
        self,
        df: pd.DataFrame,
        data_summary: Dict[str, Any]
    ) -> str:
        """构建数据描述"""
        description = f"数据集包含 {len(df)} 行和 {len(df.columns)} 列。\n\n"

        description += "列名：\n"
        for col in df.columns:
            dtype = str(df[col].dtype)
            missing = df[col].isnull().sum()
            missing_pct = (missing / len(df) * 100) if len(df) > 0 else 0
            description += f"- {col} ({dtype}), 缺失率: {missing_pct:.1f}%\n"

        return description

    def _extract_key_metrics(self, data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """提取关键指标"""
        metrics = {}

        if 'stats' in data_summary:
            metrics.update(data_summary['stats'])

        if 'shape' in data_summary:
            metrics['row_count'] = data_summary['shape'][0]
            metrics['column_count'] = data_summary['shape'][1]

        return metrics

    def _query_model(self, prompt: str) -> str:
        """查询模型"""
        messages = [
            {"role": "system", "content": PromptTemplates.SYSTEM_ANALYST},
            {"role": "user", "content": prompt}
        ]

        return self.model.chat(messages)

    def _parse_insights(self, response: str, max_count: int = 5) -> List[str]:
        """解析洞察列表"""
        insights = []

        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('•') or line.startswith('-'):
                insights.append(line[1:].strip())
            elif line and len(line) > 10:
                insights.append(line)

        return insights[:max_count]

    def _build_trend_insight_prompt(self, trend_data: Dict[str, Any]) -> str:
        """构建趋势洞察Prompt"""
        return f"""基于以下趋势数据，生成2条关于趋势的洞察：

趋势数据：
{str(trend_data)}

洞察要求：
- 每条洞察1-2句话
- 关注趋势的显著特征
- 突出趋势的商业含义

输出格式：
• 洞察1
• 洞察2"""

    def _build_anomaly_insight_prompt(self, anomaly_data: Dict[str, Any]) -> str:
        """构建异常洞察Prompt"""
        return f"""基于以下异常检测数据，生成2条关于异常的洞察：

异常数据：
{str(anomaly_data)}

洞察要求：
- 每条洞察1-2句话
- 关注异常的可能原因
- 评估异常的影响

输出格式：
• 洞察1
• 洞察2"""

    def _build_opportunity_prompt(self, stats: Dict, trend: Dict) -> str:
        """构建机会洞察Prompt"""
        return f"""基于以下数据，生成2条商业机会洞察：

统计数据：{str(stats)}
趋势数据：{str(trend)}

洞察要求：
- 每条洞察1-2句话
- 识别数据中的增长机会
- 提供可行的方向

输出格式：
• 洞察1
• 洞察2"""

    def _build_risk_prompt(self, anomaly_data: Dict) -> str:
        """构建风险洞察Prompt"""
        return f"""基于以下数据，生成2条风险洞察：

异常数据：{str(anomaly_data)}

洞察要求：
- 每条洞察1-2句话
- 识别潜在风险因素
- 评估风险的紧急程度

输出格式：
• 洞察1
• 洞察2"""

    def switch_model(self, provider: str, model_name: Optional[str] = None):
        """
        切换模型

        Args:
            provider: 提供商名称
            model_name: 模型名称（可选）
        """
        # 更新settings
        settings.update_model(provider, model_name or settings.model.model_name)

        # 获取新配置
        model_config = settings.get_model_config(provider)

        # 创建新模型
        self.model = ModelFactory.create_model(provider, model_config.__dict__)
        self.model_provider = provider

    def get_model_info(self) -> Dict[str, str]:
        """获取当前模型信息"""
        return self.model.get_model_info()

    # ============ 异步支持方法 ============

    def generate_insights_async(
        self,
        data_summary: Dict[str, Any],
        analysis_result: Dict[str, Any],
        count: int = 5,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> List[str]:
        """异步生成洞察，支持进度回调

        Args:
            data_summary: 数据摘要
            analysis_result: 分析结果
            count: 洞察数量
            progress_callback: 进度回调 (progress_percent, message)

        Returns:
            洞察列表
        """
        if progress_callback:
            progress_callback(10, "正在准备数据摘要...")

        # 生成洞察
        insights = self.generate_insights(data_summary, analysis_result, count)

        if progress_callback:
            progress_callback(50, "AI正在分析数据...")
            # 模拟处理时间（实际LLM调用可能需要几秒）
            import time
            time.sleep(0.5)
            progress_callback(100, "完成")

        return insights

    def write_report_async(
        self,
        all_results: Dict[str, Any],
        include_charts: bool = False,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> str:
        """异步生成报告，支持进度回调

        Args:
            all_results: 所有分析结果
            include_charts: 是否包含图表
            progress_callback: 进度回调 (progress_percent, message)

        Returns:
            Markdown格式的报告
        """
        steps = [
            (10, "📋 收集数据摘要..."),
            (30, "📊 进行统计分析..."),
            (50, "📈 分析趋势..."),
            (70, "⚠️ 检测风险..."),
            (90, "🤖 生成AI洞察..."),
            (100, "✅ 生成报告...")
        ]

        for progress, message in steps:
            if progress_callback:
                progress_callback(progress, message)

        # 生成报告
        report = self.write_report(all_results, include_charts)

        return report

    def chat_async(
        self,
        question: str,
        df: Optional[pd.DataFrame] = None,
        context: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> str:
        """异步交互式问答，支持进度回调

        Args:
            question: 用户问题
            df: 数据框（可选）
            context: 上下文信息（可选）
            progress_callback: 进度回调 (progress_percent, message)

        Returns:
            回答
        """
        if progress_callback:
            progress_callback(20, "正在理解问题...")

        # 构建背景信息
        background = ""

        if df is not None:
            background += self._build_data_description(df, {})

        if context:
            background += "\n\n" + str(context)

        if not background:
            background = "基于当前数据分析结果进行问答"

        if progress_callback:
            progress_callback(40, "正在分析数据上下文...")

        # 构建问答Prompt
        analysis_results = context or {}
        prompt = self.prompt_builder.build_qa_prompt(
            question=question,
            background=background,
            analysis_results=analysis_results
        )

        if progress_callback:
            progress_callback(60, "AI正在思考...")

        # 调用模型
        system_message = """你是一个专业的数据分析师助手。请基于提供的数据和分析结果回答用户的问题。

回答要求：
1. 准确、清晰、有依据
2. 必要时引用具体数据
3. 如需额外分析，明确说明
4. 鼓励探索性提问"""

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]

        answer = self.model.chat(messages)

        if progress_callback:
            progress_callback(100, "完成")

        return answer
