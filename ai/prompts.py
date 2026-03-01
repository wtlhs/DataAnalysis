"""
Prompt模板管理

定义各种分析场景的Prompt模板
"""
from typing import Dict, Any, List


class PromptTemplates:
    """Prompt模板集合"""

    # 系统提示模板
    SYSTEM_ANALYST = """你是一个专业的数据分析专家。你的任务是分析提供的数据，给出专业、准确、有洞察力的分析结论。

分析原则：
1. 基于数据，客观分析，避免主观臆断
2. 使用专业的数据分析术语和方法
3. 发现数据中的模式、趋势和异常
4. 将数据洞察转化为商业价值
5. 提供可行的决策建议"""

    SYSTEM_REPORTER = """你是一个专业的数据分析报告撰写专家。你擅长将复杂的数据分析结果转化为清晰、易懂、有价值的报告。

报告撰写原则：
1. 结构清晰，层次分明
2. 内容详实，数据准确
3. 语言专业但不晦涩
4. 突出重点，突出价值
5. 提供可行的建议和结论"""

    # 数据分析Prompt模板
    ANALYZE_TREND = """请分析以下数据的趋势：

数据描述：
{data_description}

关键指标：
{key_metrics}

分析要求：
1. 描述数据的整体趋势
2. 识别趋势中的关键转折点
3. 分析趋势的驱动因素
4. 预测趋势的延续性
5. 给出基于趋势的建议"""

    ANALYZE_ANOMALY = """请分析以下数据中的异常值：

数据描述：
{data_description}

异常值信息：
{anomaly_info}

分析要求：
1. 分析异常值的特点和分布
2. 探索异常值的可能原因
3. 评估异常值的影响
4. 判断异常值是否需要处理
5. 给出异常值处理建议"""

    ANALYZE_CORRELATION = """请分析以下数据特征之间的相关性：

相关性矩阵：
{correlation_matrix}

分析要求：
1. 识别强相关性特征对
2. 解释相关性的含义
3. 分析相关性对业务的影响
4. 探索因果关系（如有）
5. 基于相关性的决策建议"""

    # 洞察生成模板
    GENERATE_INSIGHTS = """请根据以下数据和分析结果，生成3-5条有价值的洞察。

数据摘要：
{data_summary}

分析结果：
{analysis_results}

洞察要求：
1. 每条洞察简洁明了，1-2句话
2. 聚焦于数据中的关键发现
3. 具有商业价值或决策意义
4. 基于事实，避免过度推断
5. 涵盖不同维度（趋势、异常、机会、风险）

输出格式：
• 洞察1
• 洞察2
• 洞察3
..."""

    # 报告生成模板
    REPORT_STRUCTURE = """请撰写一份完整的数据分析报告。

报告结构（请严格遵循）：
# 数据分析报告

## 1. 执行摘要
- 报告目的
- 核心发现（3-5个要点）

## 2. 数据概览
- 数据来源和范围
- 时间范围和数据量
- 关键指标说明

## 3. 统计分析
- 描述性统计
- 数据分布特征
- 关键指标解读

## 4. 趋势分析
- 整体趋势描述
- 关键趋势指标
- 同比环比分析
- 季节性分析

## 5. 异常检测
- 异常值识别
- 异常原因分析
- 异常影响评估

## 6. 预测结果（如有）
- 预测概述
- 预测趋势
- 预测置信度
- 预测结论

## 7. 风险评估
- 风险等级
- 主要风险因素
- 风险预警

## 8. 智能洞察
- 关键洞察（3-5条）
- 商业价值说明

## 9. 结论与建议
- 总结
- 具体建议
- 后续行动

## 10. 附录
- 分析方法说明
- 数据说明"""

    # 预测分析模板
    ANALYZE_FORECAST = """请分析以下预测结果：

历史数据摘要：
{historical_summary}

预测结果：
{forecast_results}

预测评估指标：
{evaluation_metrics}

分析要求：
1. 评估预测的可靠性
2. 分析预测趋势的含义
3. 识别预测中的关键信号
4. 评估预测的不确定性
5. 基于预测给出决策建议"""

    # 风险分析模板
    ANALYZE_RISK = """请分析以下风险情况：

数据质量评分：
{quality_score}

异常检测结果：
{anomaly_results}

趋势变化：
{trend_changes}

分析要求：
1. 评估整体风险等级
2. 识别主要风险因素
3. 分析风险的潜在影响
4. 评估风险的紧急程度
5. 给出风险应对建议"""

    # 问答模板
    QA_TEMPLATE = """基于以下数据分析结果回答用户问题：

背景信息：
{background}

分析结果：
{analysis_results}

用户问题：{question}

回答要求：
1. 基于已有分析结果回答
2. 如需额外分析，明确说明
3. 回答清晰、准确、有依据
4. 必要时引用具体数据"""


class PromptBuilder:
    """Prompt构建器"""

    @staticmethod
    def build_analyze_prompt(
        data_description: str,
        key_metrics: Dict[str, Any],
        analysis_type: str = "trend"
    ) -> str:
        """
        构建分析Prompt

        Args:
            data_description: 数据描述
            key_metrics: 关键指标
            analysis_type: 分析类型

        Returns:
            完整的Prompt
        """
        templates = {
            'trend': PromptTemplates.ANALYZE_TREND,
            'anomaly': PromptTemplates.ANALYZE_ANOMALY,
            'correlation': PromptTemplates.ANALYZE_CORRELATION
        }

        template = templates.get(analysis_type, PromptTemplates.ANALYZE_TREND)

        return template.format(
            data_description=data_description,
            key_metrics=str(key_metrics),
            anomaly_info=str(key_metrics),  # 复用
            correlation_matrix=str(key_metrics)  # 复用
        )

    @staticmethod
    def build_insight_prompt(
        data_summary: Dict[str, Any],
        analysis_results: Dict[str, Any]
    ) -> str:
        """
        构建洞察生成Prompt

        Args:
            data_summary: 数据摘要
            analysis_results: 分析结果

        Returns:
            完整的Prompt
        """
        return PromptTemplates.GENERATE_INSIGHTS.format(
            data_summary=str(data_summary),
            analysis_results=str(analysis_results)
        )

    @staticmethod
    def build_report_prompt(
        all_results: Dict[str, Any]
    ) -> str:
        """
        构建报告生成Prompt

        Args:
            all_results: 所有分析结果

        Returns:
            完整的Prompt
        """
        prompt = PromptTemplates.REPORT_STRUCTURE + "\n\n"

        prompt += "分析结果：\n\n"
        for section, data in all_results.items():
            prompt += f"## {section}\n"
            prompt += f"{str(data)}\n\n"

        prompt += "\n请根据以上分析结果撰写报告。"

        return prompt

    @staticmethod
    def build_qa_prompt(
        question: str,
        background: str,
        analysis_results: Dict[str, Any]
    ) -> str:
        """
        构建问答Prompt

        Args:
            question: 用户问题
            background: 背景信息
            analysis_results: 分析结果

        Returns:
            完整的Prompt
        """
        return PromptTemplates.QA_TEMPLATE.format(
            background=background,
            question=question,
            analysis_results=str(analysis_results)
        )

    @staticmethod
    def build_forecast_analysis_prompt(
        historical_summary: str,
        forecast_results: str,
        evaluation_metrics: str
    ) -> str:
        """
        构建预测分析Prompt

        Args:
            historical_summary: 历史数据摘要
            forecast_results: 预测结果
            evaluation_metrics: 评估指标

        Returns:
            完整的Prompt
        """
        return PromptTemplates.ANALYZE_FORECAST.format(
            historical_summary=historical_summary,
            forecast_results=forecast_results,
            evaluation_metrics=evaluation_metrics
        )

    @staticmethod
    def build_risk_analysis_prompt(
        quality_score: str,
        anomaly_results: str,
        trend_changes: str
    ) -> str:
        """
        构建风险分析Prompt

        Args:
            quality_score: 质量评分
            anomaly_results: 异常结果
            trend_changes: 趋势变化

        Returns:
            完整的Prompt
        """
        return PromptTemplates.ANALYZE_RISK.format(
            quality_score=quality_score,
            anomaly_results=anomaly_results,
            trend_changes=trend_changes
        )
