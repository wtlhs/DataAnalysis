"""
统计分析引擎

提供描述性统计、趋势分析、异常检测、相关性分析等功能
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict


@dataclass
class DescriptiveStats:
    """描述性统计结果"""
    count: int
    mean: float
    std: float
    min: float
    q25: float
    median: float
    q75: float
    max: float
    variance: float
    skewness: float
    kurtosis: float

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class TrendAnalysis:
    """趋势分析结果"""
    start_date: str
    end_date: str
    total_change: float
    total_change_pct: float
    mean_value: float
    volatility: float
    trend_direction: str  # 'up', 'down', 'stable'
    trend_strength: float  # 趋势强度 (0-1)


@dataclass
class AnomalyDetection:
    """异常检测结果"""
    anomaly_count: int
    anomaly_percentage: float
    anomalies: pd.DataFrame
    threshold: float
    method: str


class Analyzer:
    """统计分析引擎"""

    def __init__(self):
        pass

    def descriptive_statistics(self, df: pd.DataFrame, column: str) -> DescriptiveStats:
        """
        计算描述性统计

        Args:
            df: 数据框
            column: 列名

        Returns:
            描述性统计结果
        """
        series = df[column].dropna()

        stats = DescriptiveStats(
            count=len(series),
            mean=series.mean(),
            std=series.std(),
            min=series.min(),
            q25=series.quantile(0.25),
            median=series.median(),
            q75=series.quantile(0.75),
            max=series.max(),
            variance=series.var(),
            skewness=series.skew(),
            kurtosis=series.kurtosis()
        )

        return stats

    def batch_descriptive_statistics(self, df: pd.DataFrame) -> Dict[str, DescriptiveStats]:
        """
        批量计算描述性统计（针对所有数值列）

        Args:
            df: 数据框

        Returns:
            {列名: 描述性统计结果}
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        results = {}
        for col in numeric_cols:
            results[col] = self.descriptive_statistics(df, col)

        return results

    def trend_analysis(
        self,
        df: pd.DataFrame,
        date_col: str,
        value_col: str
    ) -> TrendAnalysis:
        """
        趋势分析

        Args:
            df: 数据框
            date_col: 日期列名
            value_col: 数值列名

        Returns:
            趋势分析结果
        """
        # 按日期排序
        df_sorted = df.sort_values(date_col)
        series = df_sorted[value_col].dropna()

        if len(series) < 2:
            raise ValueError("数据点不足，无法进行趋势分析")

        start_date = df_sorted[date_col].min()
        end_date = df_sorted[date_col].max()

        first_value = series.iloc[0]
        last_value = series.iloc[-1]

        total_change = last_value - first_value
        total_change_pct = (total_change / first_value * 100) if first_value != 0 else 0

        mean_value = series.mean()
        volatility = series.std() / mean_value if mean_value != 0 else 0

        # 计算趋势方向
        if total_change_pct > 5:
            trend_direction = 'up'
        elif total_change_pct < -5:
            trend_direction = 'down'
        else:
            trend_direction = 'stable'

        # 计算趋势强度（基于R平方的简化版本）
        if len(series) > 2:
            x = np.arange(len(series))
            y = series.values
            coeffs = np.polyfit(x, y, 1)
            y_pred = np.polyval(coeffs, x)
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            trend_strength = abs(r_squared)
        else:
            trend_strength = 0

        return TrendAnalysis(
            start_date=str(start_date),
            end_date=str(end_date),
            total_change=float(total_change),
            total_change_pct=float(total_change_pct),
            mean_value=float(mean_value),
            volatility=float(volatility),
            trend_direction=trend_direction,
            trend_strength=float(trend_strength)
        )

    def detect_anomalies(
        self,
        df: pd.DataFrame,
        column: str,
        method: str = "iqr",
        threshold: float = 1.5
    ) -> AnomalyDetection:
        """
        异常检测

        Args:
            df: 数据框
            column: 列名
            method: 检测方法 ('iqr', 'zscore', 'isolation')
            threshold: 阈值参数

        Returns:
            异常检测结果
        """
        series = df[column].copy()

        if method == "iqr":
            # IQR方法
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR

            anomalies_mask = (series < lower_bound) | (series > upper_bound)

        elif method == "zscore":
            # Z-Score方法
            mean = series.mean()
            std = series.std()
            z_scores = np.abs((series - mean) / std)

            anomalies_mask = z_scores > threshold

        else:
            raise ValueError(f"不支持的异常检测方法: {method}")

        anomaly_count = anomalies_mask.sum()
        anomaly_percentage = anomaly_count / len(series) * 100

        anomalies_df = df[anomalies_mask].copy()

        return AnomalyDetection(
            anomaly_count=int(anomaly_count),
            anomaly_percentage=float(anomaly_percentage),
            anomalies=anomalies_df,
            threshold=float(threshold),
            method=method
        )

    def correlation_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        相关性分析

        Args:
            df: 数据框

        Returns:
            相关性矩阵
        """
        numeric_df = df.select_dtypes(include=[np.number])
        return numeric_df.corr()

    def get_highly_correlated_pairs(
        self,
        df: pd.DataFrame,
        threshold: float = 0.7
    ) -> List[Tuple[str, str, float]]:
        """
        获取高相关性特征对

        Args:
            df: 数据框
            threshold: 相关性阈值

        Returns:
            [(特征1, 特征2, 相关系数), ...]
        """
        corr_matrix = self.correlation_analysis(df)

        highly_correlated = []

        # 获取上三角（不含对角线）
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]

                if abs(corr_value) >= threshold:
                    highly_correlated.append((col1, col2, corr_value))

        # 按相关系数绝对值降序排序
        highly_correlated.sort(key=lambda x: abs(x[2]), reverse=True)

        return highly_correlated

    def moving_average(
        self,
        series: pd.Series,
        window: int = 7
    ) -> pd.Series:
        """
        计算移动平均

        Args:
            series: 数据序列
            window: 窗口大小

        Returns:
            移动平均序列
        """
        return series.rolling(window=window, min_periods=1).mean()

    def year_over_year(
        self,
        df: pd.DataFrame,
        date_col: str,
        value_col: str
    ) -> pd.DataFrame:
        """
        计算同比增长

        Args:
            df: 数据框
            date_col: 日期列名
            value_col: 数值列名

        Returns:
            包含同比增长的数据框
        """
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col])

        df_copy['year'] = df_copy[date_col].dt.year
        df_copy['month'] = df_copy[date_col].dt.month

        # 按年月分组聚合
        monthly_data = df_copy.groupby(['year', 'month'])[value_col].sum().reset_index()

        # 计算同比增长
        monthly_data['yoy_growth'] = monthly_data.groupby('month')[value_col].pct_change() * 100

        return monthly_data

    def month_over_month(
        self,
        df: pd.DataFrame,
        date_col: str,
        value_col: str
    ) -> pd.DataFrame:
        """
        计算环比增长

        Args:
            df: 数据框
            date_col: 日期列名
            value_col: 数值列名

        Returns:
            包含环比增长的数据框
        """
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col])

        # 按日期排序
        df_copy = df_copy.sort_values(date_col)

        # 计算环比
        df_copy['mom_growth'] = df_copy[value_col].pct_change() * 100

        return df_copy

    def compare_categories(
        self,
        df: pd.DataFrame,
        category_col: str,
        value_col: str
    ) -> pd.DataFrame:
        """
        分类对比分析

        Args:
            df: 数据框
            category_col: 分类列名
            value_col: 数值列名

        Returns:
            分类统计数据
        """
        result = df.groupby(category_col)[value_col].agg([
            'count', 'sum', 'mean', 'std', 'min', 'max'
        ]).round(2)

        result.columns = ['数据量', '总和', '平均值', '标准差', '最小值', '最大值']

        return result.sort_values('总和', ascending=False)

    def detect_seasonality(
        self,
        df: pd.DataFrame,
        date_col: str,
        value_col: str
    ) -> Dict[str, Any]:
        """
        检测季节性

        Args:
            df: 数据框
            date_col: 日期列名
            value_col: 数值列名

        Returns:
            季节性分析结果
        """
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col])

        # 按月聚合
        monthly_stats = df_copy.groupby(df_copy[date_col].dt.month)[value_col].agg(['mean', 'std'])

        # 按季度聚合
        quarterly_stats = df_copy.groupby(df_copy[date_col].dt.quarter)[value_col].agg(['mean', 'std'])

        # 计算变异系数（CV = std/mean）
        monthly_cv = (monthly_stats['std'] / monthly_stats['mean']).max()
        quarterly_cv = (quarterly_stats['std'] / quarterly_stats['mean']).max()

        return {
            'monthly_variation': float(monthly_cv),
            'quarterly_variation': float(quarterly_cv),
            'has_seasonality': monthly_cv > 0.3,
            'monthly_stats': monthly_stats.to_dict(),
            'quarterly_stats': quarterly_stats.to_dict()
        }
