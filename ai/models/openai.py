"""
OpenAI模型适配器
"""
from typing import List, Dict, Any
from openai import OpenAI

from .base import BaseModel, ModelError, RateLimitError, AuthenticationError, TokenLimitError


class OpenAIModel(BaseModel):
    """OpenAI模型实现"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化OpenAI模型

        Args:
            config: 配置字典，包含:
                - api_key: OpenAI API密钥
                - model_name: 模型名称 (如 "gpt-4o")
                - temperature: 温度参数
                - max_tokens: 最大token数
                - api_base: API基础URL（可选）
        """
        super().__init__(config)

        # 初始化OpenAI客户端
        client_kwargs = {'api_key': self.api_key}
        if self.api_base:
            client_kwargs['base_url'] = self.api_base

        self.client = OpenAI(**client_kwargs)

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        聊天对话

        Args:
            messages: 消息列表，格式: [{"role": "user", "content": "..."}]

        Returns:
            模型响应
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            error_msg = str(e).lower()

            if 'rate_limit' in error_msg or 'quota' in error_msg:
                raise RateLimitError(f"OpenAI速率限制: {str(e)}")
            elif 'authentication' in error_msg or 'api_key' in error_msg:
                raise AuthenticationError(f"OpenAI认证失败: {str(e)}")
            elif 'token' in error_msg or 'length' in error_msg:
                raise TokenLimitError(f"OpenAI Token限制: {str(e)}")
            else:
                raise ModelError(f"OpenAI调用失败: {str(e)}")

    def analyze(self, data: Dict[str, Any], prompt: str) -> str:
        """
        数据分析

        Args:
            data: 数据字典
            prompt: 分析提示

        Returns:
            分析结果
        """
        # 构建系统提示
        system_prompt = """你是一个专业的数据分析助手。你的任务是分析提供的数据，给出专业、准确的分析结论。

分析要求：
1. 仔细阅读数据和背景信息
2. 基于数据给出客观的分析
3. 使用专业的数据分析术语
4. 发现数据中的模式、趋势和异常
5. 给出有价值的商业洞察"""

        # 构建用户消息
        user_message = f"""数据分析任务

数据信息：
{self._format_data_for_analysis(data)}

分析提示：
{prompt}

请给出详细的分析结论。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        return self.chat(messages)

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
        system_prompt = """你是一个专业的数据洞察专家。请根据提供的数据摘要和分析结果，生成3-5条有价值的洞察。

洞察要求：
1. 每条洞察简洁明了，1-2句话
2. 聚焦于数据中的关键发现
3. 具有商业价值或决策意义
4. 基于事实，避免过度推断

输出格式：
请直接输出洞察列表，每条洞察占一行，格式为：
• 洞察内容"""

        user_message = f"""数据摘要：
{self._format_data_for_analysis(data_summary)}

分析结果：
{self._format_analysis_result(analysis_result)}

请生成3-5条关键洞察。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = self.chat(messages)

        # 解析洞察列表
        insights = []
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('•') or line.startswith('-'):
                insights.append(line[1:].strip())
            elif line and not line.startswith('#'):
                insights.append(line)

        return insights[:5]  # 最多返回5条洞察

    def write_report(
        self,
        all_results: Dict[str, Any],
        report_format: str = "markdown"
    ) -> str:
        """
        编写分析报告

        Args:
            all_results: 所有分析结果
            report_format: 报告格式 ("markdown" 或其他)

        Returns:
            报告内容
        """
        system_prompt = f"""你是一个专业的数据分析报告撰写专家。请根据提供的分析结果，撰写一份结构清晰、内容全面的数据分析报告。

报告要求：
1. 使用Markdown格式
2. 结构清晰，层次分明
3. 内容详实，数据准确
4. 语言专业但不晦涩
5. 包含具体的数值和指标
6. 给出可行的建议和结论

报告结构（请严格遵循）：
# 数据分析报告

## 1. 数据概览
- 简要描述数据的基本情况

## 2. 统计分析
- 描述性统计
- 关键指标解读

## 3. 趋势分析
- 趋势描述
- 同比环比数据
- 季节性分析

## 4. 异常检测
- 异常值说明
- 潜在风险

## 5. 预测结果（如果有）
- 预测概述
- 预测结论

## 6. 风险评估
- 风险等级
- 风险因素
- 风险预警

## 7. 智能洞察
- 3-5条关键洞察
- 商业价值说明

## 8. 结论与建议
- 总结
- 可行建议
- 后续行动"""

        user_message = f"""分析结果：
{self._format_all_results(all_results)}

请撰写完整的数据分析报告。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        return self.chat(messages)

    def _format_data_for_analysis(self, data: Dict[str, Any]) -> str:
        """格式化数据用于分析"""
        lines = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{key}: {str(value)[:200]}...")  # 限制长度
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

    def _format_analysis_result(self, result: Dict[str, Any]) -> str:
        """格式化分析结果"""
        lines = []
        for key, value in result.items():
            lines.append(f"### {key}")
            if isinstance(value, dict):
                for k, v in value.items():
                    lines.append(f"- {k}: {v}")
            else:
                lines.append(f"- {value}")
            lines.append("")
        return "\n".join(lines)

    def _format_all_results(self, results: Dict[str, Any]) -> str:
        """格式化所有分析结果"""
        lines = []
        for section, data in results.items():
            lines.append(f"## {section}")
            lines.append("")
            if isinstance(data, dict):
                for key, value in data.items():
                    lines.append(f"### {key}")
                    if isinstance(value, (dict, list)):
                        lines.append(f"- {str(value)[:300]}...")
                    else:
                        lines.append(f"- {value}")
                    lines.append("")
            else:
                lines.append(f"- {data}")
                lines.append("")

        return "\n".join(lines)
