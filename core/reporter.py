"""
报告生成器

生成结构化的数据分析报告（Markdown格式）
"""
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        self.report_sections = []

    def generate_markdown_report(
        self,
        df: pd.DataFrame,
        data_summary: Dict[str, Any],
        stats_result: Dict[str, Any],
        trend_result: Optional[Dict[str, Any]] = None,
        anomaly_result: Optional[Dict[str, Any]] = None,
        forecast_result: Optional[Dict[str, Any]] = None,
        risk_result: Optional[Dict[str, Any]] = None,
        ai_insights: Optional[List[str]] = None,
        ai_report: Optional[str] = None
    ) -> str:
        """
        生成完整的Markdown报告

        Args:
            df: 原始数据框
            data_summary: 数据摘要
            stats_result: 统计分析结果
            trend_result: 趋势分析结果（可选）
            anomaly_result: 异常检测结果（可选）
            forecast_result: 预测结果（可选）
            risk_result: 风险评估结果（可选）
            ai_insights: AI生成的洞察（可选）
            ai_report: AI生成的完整报告（可选）

        Returns:
            Markdown格式的报告
        """
        lines = []

        # 标题
        lines.append("# 数据分析报告")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # 如果有AI生成的完整报告，直接使用
        if ai_report:
            lines.append(ai_report)
            return "\n".join(lines)

        # 否则，按照模板生成报告

        # 1. 数据概览
        lines.append("## 1. 数据概览")
        lines.append("")
        lines.append(self._generate_data_overview(df, data_summary))
        lines.append("")

        # 2. 统计分析
        lines.append("## 2. 统计分析")
        lines.append("")
        lines.append(self._generate_stats_section(stats_result))
        lines.append("")

        # 3. 趋势分析
        if trend_result:
            lines.append("## 3. 趋势分析")
            lines.append("")
            lines.append(self._generate_trend_section(trend_result))
            lines.append("")

        # 4. 异常检测
        if anomaly_result:
            lines.append("## 4. 异常检测")
            lines.append("")
            lines.append(self._generate_anomaly_section(anomaly_result))
            lines.append("")

        # 5. 预测结果
        if forecast_result:
            lines.append("## 5. 预测结果")
            lines.append("")
            lines.append(self._generate_forecast_section(forecast_result))
            lines.append("")

        # 6. 风险评估
        if risk_result:
            lines.append("## 6. 风险评估")
            lines.append("")
            lines.append(self._generate_risk_section(risk_result))
            lines.append("")

        # 7. 智能洞察
        if ai_insights:
            lines.append("## 7. 智能洞察")
            lines.append("")
            lines.extend(self._generate_insights_section(ai_insights))
            lines.append("")

        # 8. 结论
        lines.append("## 8. 结论")
        lines.append("")
        lines.append(self._generate_conclusion(stats_result, trend_result, risk_result))
        lines.append("")

        # 页脚
        lines.append("---")
        lines.append("")
        lines.append("*本报告由数据分析智能体自动生成*")

        return "\n".join(lines)

    def _generate_data_overview(
        self,
        df: pd.DataFrame,
        data_summary: Dict[str, Any]
    ) -> str:
        """生成数据概览部分"""
        lines = []

        lines.append("### 基本信息")
        lines.append("")
        lines.append(f"- **数据行数**: {len(df):,}")
        lines.append(f"- **数据列数**: {len(df.columns)}")
        lines.append(f"- **数据类型分布**:")

        dtype_counts = df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            lines.append(f"  - {dtype}: {count} 列")

        lines.append("")
        lines.append("### 数据列")
        lines.append("")
        lines.append("| 列名 | 数据类型 | 缺失值数 | 缺失比例 |")
        lines.append("|------|----------|----------|----------|")

        for col in df.columns:
            dtype = str(df[col].dtype)
            missing = df[col].isnull().sum()
            missing_pct = (missing / len(df) * 100) if len(df) > 0 else 0
            lines.append(f"| {col} | {dtype} | {missing} | {missing_pct:.2f}% |")

        return "\n".join(lines)

    def _generate_stats_section(self, stats_result: Dict[str, Any]) -> str:
        """生成统计分析部分"""
        lines = []

        if not stats_result:
            lines.append("暂无统计分析结果")
            return "\n".join(lines)

        lines.append("### 描述性统计")

        if 'batch_stats' in stats_result:
            for col, stats in stats_result['batch_stats'].items():
                if hasattr(stats, 'to_dict'):
                    stats_dict = stats.to_dict()
                else:
                    stats_dict = stats

                lines.append("")
                lines.append(f"#### {col}")
                lines.append("")
                lines.append(f"- **均值**: {stats_dict.get('mean', 'N/A'):.2f}")
                lines.append(f"- **标准差**: {stats_dict.get('std', 'N/A'):.2f}")
                lines.append(f"- **最小值**: {stats_dict.get('min', 'N/A'):.2f}")
                lines.append(f"- **中位数**: {stats_dict.get('median', 'N/A'):.2f}")
                lines.append(f"- **最大值**: {stats_dict.get('max', 'N/A'):.2f}")
                lines.append(f"- **偏度**: {stats_dict.get('skewness', 'N/A'):.2f}")
                lines.append(f"- **峰度**: {stats_dict.get('kurtosis', 'N/A'):.2f}")

        return "\n".join(lines)

    def _generate_trend_section(self, trend_result: Dict[str, Any]) -> str:
        """生成趋势分析部分"""
        lines = []

        if not trend_result:
            lines.append("暂无趋势分析结果")
            return "\n".join(lines)

        lines.append("### 趋势概览")

        if 'trend_analysis' in trend_result:
            trend = trend_result['trend_analysis']

            lines.append("")
            lines.append(f"- **时间范围**: {trend.get('start_date', 'N/A')} 至 {trend.get('end_date', 'N/A')}")
            lines.append(f"- **趋势方向**: {self._format_trend_direction(trend.get('trend_direction', 'N/A'))}")
            lines.append(f"- **总变化量**: {trend.get('total_change', 'N/A'):.2f}")
            lines.append(f"- **变化百分比**: {trend.get('total_change_pct', 'N/A'):.2f}%")
            lines.append(f"- **平均波动率**: {trend.get('volatility', 'N/A'):.2f}")
            lines.append(f"- **趋势强度**: {trend.get('trend_strength', 'N/A'):.2f}")

        if 'seasonality' in trend_result:
            seasonality = trend_result['seasonality']
            lines.append("")
            lines.append("### 季节性分析")
            lines.append("")
            lines.append(f"- **存在季节性**: {'是' if seasonality.get('has_seasonality', False) else '否'}")
            lines.append(f"- **月度变异系数**: {seasonality.get('monthly_variation', 'N/A'):.2f}")

        return "\n".join(lines)

    def _generate_anomaly_section(self, anomaly_result: Dict[str, Any]) -> str:
        """生成异常检测部分"""
        lines = []

        if not anomaly_result:
            lines.append("暂无异常检测结果")
            return "\n".join(lines)

        lines.append("### 异常统计")

        if 'anomaly_detection' in anomaly_result:
            anomaly = anomaly_result['anomaly_detection']

            lines.append("")
            lines.append(f"- **检测方法**: {anomaly.get('method', 'N/A')}")
            lines.append(f"- **异常数量**: {anomaly.get('anomaly_count', 0)}")
            lines.append(f"- **异常比例**: {anomaly.get('anomaly_percentage', 0):.2f}%")
            lines.append(f"- **阈值**: {anomaly.get('threshold', 'N/A')}")

            if anomaly.get('anomaly_count', 0) > 0:
                lines.append("")
                lines.append("### 异常详情")
                lines.append("")
                lines.append("前5个异常值：")

                anomalies_df = anomaly.get('anomalies')
                if anomalies_df is not None and len(anomalies_df) > 0:
                    lines.append("")
                    lines.append(anomalies_df.head(5).to_markdown(index=False))

        return "\n".join(lines)

    def _generate_forecast_section(self, forecast_result: Dict[str, Any]) -> str:
        """生成预测结果部分"""
        lines = []

        if not forecast_result:
            lines.append("暂无预测结果")
            return "\n".join(lines)

        lines.append("### 预测概览")

        if 'forecast_summary' in forecast_result:
            summary = forecast_result['forecast_summary']

            lines.append("")
            lines.append(f"- **预测周期数**: {summary.get('forecast_periods', 0)}")
            lines.append(f"- **预测均值**: {summary.get('forecast_mean', 'N/A'):.2f}")
            lines.append(f"- **预测范围**: {summary.get('forecast_min', 'N/A'):.2f} 至 {summary.get('forecast_max', 'N/A'):.2f}")
            lines.append(f"- **预测趋势**: {summary.get('forecast_trend', 'N/A'):.2f}")
            lines.append(f"- **预测趋势百分比**: {summary.get('forecast_trend_pct', 'N/A'):.2f}%")

        if 'accuracy' in forecast_result:
            accuracy = forecast_result['accuracy']

            lines.append("")
            lines.append("### 预测准确度")
            lines.append("")
            lines.append(f"- **MAE (平均绝对误差)**: {accuracy.get('mae', 'N/A'):.2f}")
            lines.append(f"- **RMSE (均方根误差)**: {accuracy.get('rmse', 'N/A'):.2f}")
            lines.append(f"- **MAPE (平均绝对百分比误差)**: {accuracy.get('mape', 'N/A'):.2f}%")
            lines.append(f"- **覆盖率**: {accuracy.get('coverage', 'N/A'):.2%}")

        return "\n".join(lines)

    def _generate_risk_section(self, risk_result: Dict[str, Any]) -> str:
        """生成风险评估部分"""
        lines = []

        if not risk_result:
            lines.append("暂无风险评估结果")
            return "\n".join(lines)

        # 风险评分
        if 'risk_score' in risk_result:
            risk_score = risk_result['risk_score']

            lines.append("### 风险评分")
            lines.append("")
            lines.append(f"- **综合评分**: {risk_score.overall_score}/100")
            lines.append(f"- **风险等级**: {self._format_risk_level(risk_score.risk_level)}")
            lines.append("")

            # 风险细分
            lines.append("### 风险细分")
            lines.append("")
            for category, score in risk_score.breakdown.items():
                lines.append(f"- **{category}**: {score:.2f}")

        # 告警摘要
        if 'summary' in risk_result:
            summary = risk_result['summary']
            lines.append("")
            lines.append("### 告警摘要")
            lines.append("")
            lines.append(f"- **总告警数**: {summary.get('total_alerts', 0)}")
            lines.append(f"- **高风险**: {summary.get('high_risk_count', 0)}")
            lines.append(f"- **中风险**: {summary.get('medium_risk_count', 0)}")
            lines.append(f"- **低风险**: {summary.get('low_risk_count', 0)}")

        # 建议
        if 'risk_score' in risk_result and risk_result['risk_score'].recommendations:
            lines.append("")
            lines.append("### 风险应对建议")
            lines.append("")
            for i, recommendation in enumerate(risk_result['risk_score'].recommendations, 1):
                lines.append(f"{i}. {recommendation}")

        return "\n".join(lines)

    def _generate_insights_section(self, insights: List[str]) -> List[str]:
        """生成洞察部分"""
        lines = []

        for i, insight in enumerate(insights, 1):
            lines.append(f"{i}. {insight}")

        return lines

    def _generate_conclusion(
        self,
        stats_result: Dict[str, Any],
        trend_result: Optional[Dict[str, Any]],
        risk_result: Optional[Dict[str, Any]]
    ) -> str:
        """生成结论部分"""
        lines = []

        lines.append("### 总体评估")

        # 数据质量评估
        lines.append("")
        if stats_result and 'batch_stats' in stats_result:
            lines.append("本次分析涵盖了完整的数据集，统计指标显示了数据的分布特征和基本趋势。")

        # 趋势评估
        if trend_result and 'trend_analysis' in trend_result:
            trend_dir = trend_result['trend_analysis'].get('trend_direction', '')
            if trend_dir == 'up':
                lines.append("数据呈现上升趋势，整体增长态势明显。")
            elif trend_dir == 'down':
                lines.append("数据呈现下降趋势，需要关注潜在风险。")
            else:
                lines.append("数据整体保持稳定。")

        # 风险评估
        if risk_result and 'risk_score' in risk_result:
            risk_level = risk_result['risk_score'].risk_level.value
            if risk_level == 'LOW':
                lines.append("整体风险较低，数据质量良好。")
            elif risk_level == 'MEDIUM':
                lines.append("存在一定风险，建议关注异常值和数据质量。")
            else:
                lines.append("风险较高，需要及时处理异常和数据质量问题。")

        lines.append("")
        lines.append("### 后续建议")

        lines.append("1. 定期进行数据分析，监控关键指标变化")
        lines.append("2. 对异常值进行人工复核和处理")
        lines.append("3. 基于趋势预测调整业务策略")
        lines.append("4. 持续优化数据质量")

        return "\n".join(lines)

    def _format_trend_direction(self, direction: str) -> str:
        """格式化趋势方向"""
        mapping = {
            'up': '📈 上升',
            'down': '📉 下降',
            'stable': '➡️ 稳定'
        }
        return mapping.get(direction, direction)

    def _format_risk_level(self, level) -> str:
        """格式化风险等级"""
        level_str = level.value if hasattr(level, 'value') else str(level)

        mapping = {
            'LOW': '🟢 低',
            'MEDIUM': '🟡 中',
            'HIGH': '🟠 高',
            'CRITICAL': '🔴 严重'
        }
        return mapping.get(level_str, level_str)

    def save_report(self, report: str, output_path: str):
        """
        保存报告到文件

        Args:
            report: 报告内容
            output_path: 输出文件路径
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

    def export_to_html(self, report: str, output_path: str):
        """
        导出报告为HTML（简单版本）

        Args:
            report: Markdown格式的报告
            output_path: 输出文件路径
        """
        # 简单的Markdown到HTML转换
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数据分析报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{ color: #1e88e5; border-bottom: 2px solid #1e88e5; padding-bottom: 10px; }}
        h2 {{ color: #333; margin-top: 30px; }}
        h3 {{ color: #666; margin-top: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
        code {{ background-color: #f5f5f5; padding: 2px 5px; border-radius: 3px; }}
        pre {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #1e88e5; padding-left: 15px; color: #666; }}
    </style>
</head>
<body>
{self._markdown_to_html(report)}
</body>
</html>"""

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

    def _markdown_to_html(self, md: str) -> str:
        """简单的Markdown到HTML转换"""
        html = md

        # 标题转换
        html = html.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)
        html = html.replace('## ', '<h2>').replace('\n', '</h2>\n', 1)
        html = html.replace('### ', '<h3>').replace('\n', '</h3>\n', 1)

        # 粗体
        html = html.replace('**', '<strong>', 1).replace('**', '</strong>', 1)

        return html
