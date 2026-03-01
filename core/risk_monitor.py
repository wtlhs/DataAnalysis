"""
风险预警系统

实现阈值检查、异常预警、风险评分等功能
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

from config.settings import settings


class RiskLevel(Enum):
    """风险等级"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RiskAlert:
    """风险告警"""
    alert_id: str
    risk_type: str  # 风险类型
    risk_level: RiskLevel
    message: str
    severity: float  # 严重程度 0-1
    timestamp: str
    affected_column: str
    affected_rows: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class RiskScore:
    """风险评分"""
    overall_score: float  # 0-100
    risk_level: RiskLevel
    breakdown: Dict[str, float]  # 各维度评分
    recommendations: List[str]


class RiskMonitor:
    """风险预警引擎"""

    def __init__(self):
        self.thresholds = settings.risk

    def check_value_thresholds(
        self,
        df: pd.DataFrame,
        column: str,
        min_threshold: Optional[float] = None,
        max_threshold: Optional[float] = None
    ) -> List[RiskAlert]:
        """
        检查数值阈值

        Args:
            df: 数据框
            column: 列名
            min_threshold: 最小阈值
            max_threshold: 最大阈值

        Returns:
            风险告警列表
        """
        alerts = []
        series = df[column].dropna()

        # 检查低于最小阈值
        if min_threshold is not None:
            below_min = series < min_threshold
            if below_min.any():
                count = below_min.sum()
                alert = RiskAlert(
                    alert_id=f"threshold_min_{column}_{datetime.now().timestamp()}",
                    risk_type="值过低",
                    risk_level=RiskLevel.HIGH if count > len(series) * 0.1 else RiskLevel.MEDIUM,
                    message=f"列 '{column}' 中有 {count} 个值低于最小阈值 {min_threshold}",
                    severity=float(count / len(series)),
                    timestamp=str(datetime.now()),
                    affected_column=column,
                    affected_rows=df[below_min].index.tolist()
                )
                alerts.append(alert)

        # 检查高于最大阈值
        if max_threshold is not None:
            above_max = series > max_threshold
            if above_max.any():
                count = above_max.sum()
                alert = RiskAlert(
                    alert_id=f"threshold_max_{column}_{datetime.now().timestamp()}",
                    risk_type="值过高",
                    risk_level=RiskLevel.HIGH if count > len(series) * 0.1 else RiskLevel.MEDIUM,
                    message=f"列 '{column}' 中有 {count} 个值高于最大阈值 {max_threshold}",
                    severity=float(count / len(series)),
                    timestamp=str(datetime.now()),
                    affected_column=column,
                    affected_rows=df[above_max].index.tolist()
                )
                alerts.append(alert)

        return alerts

    def detect_statistical_anomalies(
        self,
        df: pd.DataFrame,
        column: str,
        method: str = "zscore"
    ) -> List[RiskAlert]:
        """
        基于统计方法的异常检测

        Args:
            df: 数据框
            column: 列名
            method: 方法 ('zscore', 'iqr')

        Returns:
            风险告警列表
        """
        alerts = []
        series = df[column].dropna()

        if len(series) < self.thresholds.min_data_points:
            return []

        if method == "zscore":
            mean = series.mean()
            std = series.std()

            if std == 0:
                return []

            z_scores = np.abs((series - mean) / std)

            # 高风险: 3-sigma
            high_risk = z_scores >= self.thresholds.high_risk_sigma
            # 中风险: 2-sigma
            medium_risk = (z_scores >= self.thresholds.medium_risk_sigma) & (z_scores < self.thresholds.high_risk_sigma)

            if high_risk.any():
                count = high_risk.sum()
                alert = RiskAlert(
                    alert_id=f"stat_anomaly_high_{column}_{datetime.now().timestamp()}",
                    risk_type="统计异常(高)",
                    risk_level=RiskLevel.HIGH,
                    message=f"列 '{column}' 发现 {count} 个高异常值 (3-Sigma)",
                    severity=float(count / len(series)),
                    timestamp=str(datetime.now()),
                    affected_column=column,
                    affected_rows=df.loc[series[high_risk].index].index.tolist()
                )
                alerts.append(alert)

            if medium_risk.any():
                count = medium_risk.sum()
                alert = RiskAlert(
                    alert_id=f"stat_anomaly_medium_{column}_{datetime.now().timestamp()}",
                    risk_type="统计异常(中)",
                    risk_level=RiskLevel.MEDIUM,
                    message=f"列 '{column}' 发现 {count} 个中等异常值 (2-Sigma)",
                    severity=float(count / len(series)),
                    timestamp=str(datetime.now()),
                    affected_column=column,
                    affected_rows=df.loc[series[medium_risk].index].index.tolist()
                )
                alerts.append(alert)

        elif method == "iqr":
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1

            if IQR == 0:
                return []

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = (series < lower_bound) | (series > upper_bound)

            if outliers.any():
                count = outliers.sum()
                alert = RiskAlert(
                    alert_id=f"stat_anomaly_iqr_{column}_{datetime.now().timestamp()}",
                    risk_type="统计异常(IQR)",
                    risk_level=RiskLevel.MEDIUM,
                    message=f"列 '{column}' 发现 {count} 个异常值 (IQR方法)",
                    severity=float(count / len(series)),
                    timestamp=str(datetime.now()),
                    affected_column=column,
                    affected_rows=df.loc[outliers].index.tolist()
                )
                alerts.append(alert)

        return alerts

    def detect_trend_reversal(
        self,
        df: pd.DataFrame,
        date_col: str,
        value_col: str,
        window: int = 10
    ) -> List[RiskAlert]:
        """
        检测趋势反转

        Args:
            df: 数据框
            date_col: 日期列名
            value_col: 数值列名
            window: 窗口大小

        Returns:
            风险告警列表
        """
        alerts = []

        df_sorted = df.sort_values(date_col)
        series = df_sorted[value_col].dropna()

        if len(series) < window * 2:
            return []

        # 计算移动平均
        ma = series.rolling(window=window).mean()

        # 检测趋势变化
        recent_trend = ma.diff().tail(window).mean()
        historical_trend = ma.diff().head(len(series) - window).mean()

        # 如果趋势方向相反且变化显著
        if (recent_trend > 0 and historical_trend < 0) or (recent_trend < 0 and historical_trend > 0):
            if abs(recent_trend - historical_trend) > self.thresholds.trend_change_threshold:
                alert = RiskAlert(
                    alert_id=f"trend_reversal_{value_col}_{datetime.now().timestamp()}",
                    risk_type="趋势反转",
                    risk_level=RiskLevel.HIGH,
                    message=f"列 '{value_col}' 检测到趋势反转信号",
                    severity=0.8,
                    timestamp=str(datetime.now()),
                    affected_column=value_col,
                    metadata={
                        'previous_trend': float(historical_trend),
                        'current_trend': float(recent_trend)
                    }
                )
                alerts.append(alert)

        return alerts

    def detect_data_quality_issues(self, df: pd.DataFrame) -> List[RiskAlert]:
        """
        检测数据质量问题

        Args:
            df: 数据框

        Returns:
            风险告警列表
        """
        alerts = []

        # 检查缺失值
        missing_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))

        if missing_ratio > 0.3:
            alerts.append(RiskAlert(
                alert_id=f"data_quality_missing_{datetime.now().timestamp()}",
                risk_type="数据缺失",
                risk_level=RiskLevel.HIGH,
                message=f"数据缺失比例过高: {missing_ratio:.2%}",
                severity=float(missing_ratio),
                timestamp=str(datetime.now()),
                affected_column="全局",
                metadata={'missing_ratio': float(missing_ratio)}
            ))
        elif missing_ratio > 0.1:
            alerts.append(RiskAlert(
                alert_id=f"data_quality_missing_{datetime.now().timestamp()}",
                risk_type="数据缺失",
                risk_level=RiskLevel.MEDIUM,
                message=f"数据缺失比例: {missing_ratio:.2%}",
                severity=float(missing_ratio),
                timestamp=str(datetime.now()),
                affected_column="全局",
                metadata={'missing_ratio': float(missing_ratio)}
            ))

        # 检查重复行
        duplicate_count = df.duplicated().sum()
        duplicate_ratio = duplicate_count / len(df)

        if duplicate_ratio > 0.1:
            alerts.append(RiskAlert(
                alert_id=f"data_quality_duplicate_{datetime.now().timestamp()}",
                risk_type="重复数据",
                risk_level=RiskLevel.MEDIUM,
                message=f"数据重复比例: {duplicate_ratio:.2%} ({duplicate_count} 行)",
                severity=float(duplicate_ratio),
                timestamp=str(datetime.now()),
                affected_column="全局",
                metadata={'duplicate_count': int(duplicate_count)}
            ))

        # 检查空值过多的列
        for col in df.columns:
            col_missing_ratio = df[col].isnull().sum() / len(df)
            if col_missing_ratio > 0.5:
                alerts.append(RiskAlert(
                    alert_id=f"data_quality_col_missing_{col}_{datetime.now().timestamp()}",
                    risk_type="列缺失过多",
                    risk_level=RiskLevel.HIGH,
                    message=f"列 '{col}' 缺失比例过高: {col_missing_ratio:.2%}",
                    severity=float(col_missing_ratio),
                    timestamp=str(datetime.now()),
                    affected_column=col
                ))

        return alerts

    def calculate_risk_score(
        self,
        df: pd.DataFrame,
        alerts: List[RiskAlert]
    ) -> RiskScore:
        """
        计算综合风险评分

        Args:
            df: 数据框
            alerts: 风险告警列表

        Returns:
            风险评分
        """
        breakdown = {
            'data_quality': 0,
            'statistical_anomaly': 0,
            'threshold_violation': 0,
            'trend_reversal': 0
        }

        recommendations = []

        # 根据告警计算各维度得分
        for alert in alerts:
            if alert.risk_type == "数据缺失" or alert.risk_type == "重复数据" or alert.risk_type == "列缺失过多":
                breakdown['data_quality'] += alert.severity * 100
                if alert.risk_level == RiskLevel.HIGH:
                    recommendations.append(f"紧急处理: {alert.message}")
            elif "异常" in alert.risk_type:
                breakdown['statistical_anomaly'] += alert.severity * 100
                if alert.risk_level == RiskLevel.HIGH:
                    recommendations.append(f"需要检查: {alert.message}")
            elif "阈值" in alert.risk_type:
                breakdown['threshold_violation'] += alert.severity * 100
                recommendations.append(f"注意: {alert.message}")
            elif alert.risk_type == "趋势反转":
                breakdown['trend_reversal'] += alert.severity * 100
                recommendations.append(f"关注: {alert.message}")

        # 计算总分
        total_score = sum(breakdown.values())
        total_score = min(total_score, 100)

        # 确定风险等级
        if total_score >= 70:
            risk_level = RiskLevel.CRITICAL
        elif total_score >= 50:
            risk_level = RiskLevel.HIGH
        elif total_score >= 30:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        # 添加通用建议
        if total_score > 0:
            recommendations.append("建议对异常数据进行人工复核")
            recommendations.append("考虑进行数据清洗和标准化")

        return RiskScore(
            overall_score=round(total_score, 2),
            risk_level=risk_level,
            breakdown=breakdown,
            recommendations=recommendations
        )

    def generate_comprehensive_report(
        self,
        df: pd.DataFrame,
        columns_to_monitor: Optional[List[str]] = None,
        date_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成综合风险报告

        Args:
            df: 数据框
            columns_to_monitor: 要监控的列名列表
            date_column: 日期列名（用于趋势检测）

        Returns:
            综合风险报告
        """
        all_alerts = []

        # 数据质量检查
        data_quality_alerts = self.detect_data_quality_issues(df)
        all_alerts.extend(data_quality_alerts)

        # 监控指定列
        if columns_to_monitor is None:
            columns_to_monitor = df.select_dtypes(include=[np.number]).columns.tolist()

        for col in columns_to_monitor:
            if col not in df.columns:
                continue

            # 统计异常检测
            anomaly_alerts = self.detect_statistical_anomalies(df, col)
            all_alerts.extend(anomaly_alerts)

            # 阈值检查（使用3-Sigma作为阈值）
            series = df[col].dropna()
            if len(series) > 0 and series.std() > 0:
                mean = series.mean()
                std = series.std()
                threshold_alerts = self.check_value_thresholds(
                    df, col,
                    min_threshold=mean - 3 * std,
                    max_threshold=mean + 3 * std
                )
                all_alerts.extend(threshold_alerts)

        # 趋势检测
        if date_column and len(columns_to_monitor) > 0:
            for col in columns_to_monitor:
                if col in df.columns and date_column in df.columns:
                    trend_alerts = self.detect_trend_reversal(df, date_column, col)
                    all_alerts.extend(trend_alerts)

        # 计算风险评分
        risk_score = self.calculate_risk_score(df, all_alerts)

        return {
            'alerts': all_alerts,
            'risk_score': risk_score,
            'summary': {
                'total_alerts': len(all_alerts),
                'high_risk_count': sum(1 for a in all_alerts if a.risk_level == RiskLevel.HIGH),
                'medium_risk_count': sum(1 for a in all_alerts if a.risk_level == RiskLevel.MEDIUM),
                'low_risk_count': sum(1 for a in all_alerts if a.risk_level == RiskLevel.LOW)
            }
        }
