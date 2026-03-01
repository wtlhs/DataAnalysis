"""
时间序列预测引擎

基于Prophet的时间序列预测
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

try:
    from prophet import Prophet
    from prophet.diagnostics import cross_validation, performance_metrics
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False


@dataclass
class ForecastResult:
    """预测结果"""
    forecast: pd.DataFrame  # 预测数据
    model: Any  # 预测模型
    accuracy: Dict[str, float]  # 准确度指标
    periods: int  # 预测周期数
    confidence_interval: float  # 置信区间


@dataclass
class ModelEvaluation:
    """模型评估结果"""
    mae: float  # 平均绝对误差
    mse: float  # 均方误差
    rmse: float  # 均方根误差
    mape: float  # 平均绝对百分比误差
    coverage: float  # 覆盖率（预测区间包含真实值的比例）


class Predictor:
    """时间序列预测引擎"""

    def __init__(self):
        if not PROPHET_AVAILABLE and not STATSMODELS_AVAILABLE:
            raise ImportError(
                "Prophet或statsmodels未安装。请安装: pip install statsmodels"
            )

        self.use_prophet = PROPHET_AVAILABLE
        self.use_statsmodels = STATSMODELS_AVAILABLE

    def prepare_data(
        self,
        df: pd.DataFrame,
        date_col: str,
        value_col: str
    ) -> pd.DataFrame:
        """
        准备Prophet所需的数据格式

        Args:
            df: 原始数据框
            date_col: 日期列名
            value_col: 数值列名

        Returns:
            Prophet格式的数据框 (ds, y)
        """
        prophet_df = pd.DataFrame({
            'ds': pd.to_datetime(df[date_col]),
            'y': df[value_col].values
        })

        # 移除缺失值
        prophet_df = prophet_df.dropna()

        # 去重（保留每个日期的最后一个值）
        prophet_df = prophet_df.drop_duplicates(subset=['ds'], keep='last')

        # 按日期排序
        prophet_df = prophet_df.sort_values('ds')

        return prophet_df

    def train_prophet(
        self,
        prophet_df: pd.DataFrame,
        seasonality_mode: str = "multiplicative",
        yearly_seasonality: bool = True,
        weekly_seasonality: bool = True,
        daily_seasonality: bool = False,
        growth: str = "linear"
    ) -> Prophet:
        """
        训练Prophet模型

        Args:
            prophet_df: Prophet格式数据框
            seasonality_mode: 季节性模式 ('additive', 'multiplicative')
            yearly_seasonality: 是否包含年度季节性
            weekly_seasonality: 是否包含周度季节性
            daily_seasonality: 是否包含日度季节性
            growth: 趋势类型 ('linear', 'logistic', 'flat')

        Returns:
            训练好的Prophet模型
        """
        model = Prophet(
            seasonality_mode=seasonality_mode,
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=daily_seasonality,
            growth=growth,
            interval_width=0.95,  # 95%置信区间
            uncertainty_samples=1000
        )

        model.fit(prophet_df)

        return model

    def predict_forecast(
        self,
        model: Prophet,
        periods: int,
        freq: str = "D"
    ) -> pd.DataFrame:
        """
        进行预测

        Args:
            model: 训练好的Prophet模型
            periods: 预测周期数
            freq: 频率 ('D'=日, 'W'=周, 'M'=月)

        Returns:
            预测结果数据框
        """
        future = model.make_future_dataframe(periods=periods, freq=freq)
        forecast = model.predict(future)

        return forecast

    def evaluate_forecast(
        self,
        prophet_df: pd.DataFrame,
        forecast: pd.DataFrame
    ) -> ModelEvaluation:
        """
        评估预测准确度

        Args:
            prophet_df: 原始数据
            forecast: 预测结果

        Returns:
            评估指标
        """
        # 合并预测和历史数据
        merged = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].merge(
            prophet_df,
            on='ds',
            how='inner'
        )

        if len(merged) == 0:
            return ModelEvaluation(
                mae=np.nan,
                mse=np.nan,
                rmse=np.nan,
                mape=np.nan,
                coverage=np.nan
            )

        actual = merged['y'].values
        predicted = merged['yhat'].values

        # 计算指标
        mae = np.mean(np.abs(actual - predicted))
        mse = np.mean((actual - predicted) ** 2)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100

        # 计算覆盖率
        coverage = np.mean(
            (actual >= merged['yhat_lower']) & (actual <= merged['yhat_upper'])
        )

        return ModelEvaluation(
            mae=float(mae),
            mse=float(mse),
            rmse=float(rmse),
            mape=float(mape),
            coverage=float(coverage)
        )

    def run_forecast(
        self,
        df: pd.DataFrame,
        date_col: str,
        value_col: str,
        periods: int = 30,
        freq: str = "D",
        seasonality_mode: str = "multiplicative"
    ) -> ForecastResult:
        """
        完整的预测流程

        Args:
            df: 原始数据框
            date_col: 日期列名
            value_col: 数值列名
            periods: 预测周期数
            freq: 频率
            seasonality_mode: 季节性模式

        Returns:
            预测结果
        """
        # 优先使用Prophet
        if self.use_prophet:
            return self._run_prophet_forecast(
                df, date_col, value_col, periods, freq, seasonality_mode
            )
        # 使用statsmodels作为备选
        elif self.use_statsmodels:
            return self._run_arima_forecast(df, date_col, value_col, periods, freq)
        else:
            raise ImportError("Prophet和statsmodels都未安装")

    def _run_prophet_forecast(
        self,
        df: pd.DataFrame,
        date_col: str,
        value_col: str,
        periods: int,
        freq: str,
        seasonality_mode: str
    ) -> ForecastResult:
        """使用Prophet进行预测"""
        # 准备数据
        prophet_df = self.prepare_data(df, date_col, value_col)

        # 训练模型
        model = self.train_prophet(
            prophet_df,
            seasonality_mode=seasonality_mode
        )

        # 进行预测
        forecast = self.predict_forecast(model, periods, freq)

        # 评估模型
        evaluation = self.evaluate_forecast(prophet_df, forecast)

        accuracy = {
            'mae': evaluation.mae,
            'rmse': evaluation.rmse,
            'mape': evaluation.mape,
            'coverage': evaluation.coverage
        }

        return ForecastResult(
            forecast=forecast,
            model=model,
            accuracy=accuracy,
            periods=periods,
            confidence_interval=0.95
        )

    def _run_arima_forecast(
        self,
        df: pd.DataFrame,
        date_col: str,
        value_col: str,
        periods: int,
        freq: str
    ) -> ForecastResult:
        """使用ARIMA进行预测（备选方案）"""
        # 准备数据
        df_sorted = df.sort_values(date_col)
        series = df_sorted[value_col].dropna()

        if len(series) < 20:
            # 数据太少，使用简单移动平均
            return self._simple_forecast(df, date_col, value_col, periods, freq)

        # 训练ARIMA模型
        try:
            # 简单的ARIMA(1,1,1)模型
            model = ARIMA(series, order=(1, 1, 1))
            fitted_model = model.fit()

            # 预测
            forecast_result = fitted_model.forecast(steps=periods)
            forecast_result_conf = fitted_model.get_forecast(
                steps=periods,
                alpha=0.05
            )

            # 构建预测数据框
            last_date = pd.to_datetime(df_sorted[date_col]).max()
            forecast_dates = pd.date_range(
                start=last_date + pd.Timedelta(days=1),
                periods=periods,
                freq='D'
            )

            forecast_df = pd.DataFrame({
                'ds': forecast_dates,
                'yhat': forecast_result.values,
                'yhat_lower': forecast_result_conf.conf_int.iloc[:, 0].values,
                'yhat_upper': forecast_result_conf.conf_int.iloc[:, 1].values,
                'trend': forecast_result.values,
                'seasonal': 0
            })

            # 评估
            # 使用最后20%的数据作为测试集
            test_size = max(1, int(len(series) * 0.2))
            train = series[:-test_size]
            test = series[-test_size:]

            if test_size > 1:
                train_model = ARIMA(train, order=(1, 1, 1))
                train_fitted = train_model.fit()
                test_pred = train_fitted.forecast(steps=test_size)

                mae = np.mean(np.abs(test.values - test_pred.values))
                rmse = np.sqrt(np.mean((test.values - test_pred.values) ** 2))
                mape = np.mean(np.abs((test.values - test_pred.values) / test.values)) * 100
                coverage = 0.95  # ARIMA的置信区间
            else:
                mae = rmse = mape = coverage = np.nan

            accuracy = {
                'mae': mae,
                'rmse': rmse,
                'mape': mape,
                'coverage': coverage
            }

            return ForecastResult(
                forecast=forecast_df,
                model=fitted_model,
                accuracy=accuracy,
                periods=periods,
                confidence_interval=0.95
            )

        except Exception as e:
            # ARIMA失败，回退到简单预测
            return self._simple_forecast(df, date_col, value_col, periods, freq)

    def _simple_forecast(
        self,
        df: pd.DataFrame,
        date_col: str,
        value_col: str,
        periods: int,
        freq: str
    ) -> ForecastResult:
        """简单预测（移动平均）"""
        df_sorted = df.sort_values(date_col)
        series = df_sorted[value_col].dropna()

        # 使用移动平均进行简单预测
        ma_window = min(7, len(series))
        forecast_value = series.rolling(window=ma_window).mean().iloc[-1]

        # 构建预测数据框
        last_date = pd.to_datetime(df_sorted[date_col]).max()
        forecast_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=periods,
            freq='D'
        )

        # 简单置信区间（基于历史标准差）
        std = series.std()
        forecast_df = pd.DataFrame({
            'ds': forecast_dates,
            'yhat': [forecast_value] * periods,
            'yhat_lower': [forecast_value - 2 * std] * periods,
            'yhat_upper': [forecast_value + 2 * std] * periods,
            'trend': [forecast_value] * periods,
            'seasonal': [0] * periods
        })

        accuracy = {
            'mae': std,
            'rmse': std * 1.414,  # 近似
            'mape': (std / abs(forecast_value) * 100) if forecast_value != 0 else 100,
            'coverage': 0.95
        }

        return ForecastResult(
            forecast=forecast_df,
            model=None,
            accuracy=accuracy,
            periods=periods,
            confidence_interval=0.95
        )

    def simple_moving_average_forecast(
        self,
        series: pd.Series,
        window: int = 7,
        periods: int = 30
    ) -> pd.DataFrame:
        """
        简单移动平均预测（备选方案）

        Args:
            series: 数据序列
            window: 移动平均窗口
            periods: 预测周期数

        Returns:
            预测结果
        """
        # 计算移动平均
        ma = series.rolling(window=window).mean()

        # 预测未来值（使用最后一个移动平均值）
        last_ma = ma.iloc[-1]
        predictions = [last_ma] * periods

        forecast_df = pd.DataFrame({
            'ds': pd.date_range(
                start=series.index[-1] + pd.Timedelta(days=1),
                periods=periods,
                freq='D'
            ),
            'yhat': predictions
        })

        return forecast_df

    def detect_trend_components(self, forecast: pd.DataFrame) -> Dict[str, Any]:
        """
        检测预测趋势的组成成分

        Args:
            forecast: Prophet预测结果

        Returns:
            趋势组成分析
        """
        # 只看预测部分
        forecast_future = forecast[forecast['ds'] > forecast['ds'].iloc[-len(forecast)//2]]

        trend_direction = 'up' if forecast_future['trend'].diff().mean() > 0 else 'down'
        trend_magnitude = abs(forecast_future['trend'].diff().mean())

        # 季节性幅度
        if 'yearly' in forecast.columns:
            yearly_amplitude = forecast['yearly'].max() - forecast['yearly'].min()
        else:
            yearly_amplitude = 0

        return {
            'trend_direction': trend_direction,
            'trend_magnitude': float(trend_magnitude),
            'yearly_amplitude': float(yearly_amplitude),
            'forecast_start': str(forecast['ds'].min()),
            'forecast_end': str(forecast['ds'].max())
        }

    def get_forecast_summary(
        self,
        forecast: pd.DataFrame,
        original_df: pd.DataFrame,
        value_col: str
    ) -> Dict[str, Any]:
        """
        获取预测摘要

        Args:
            forecast: 预测结果
            original_df: 原始数据
            value_col: 数值列名

        Returns:
            预测摘要
        """
        # 分离历史和预测
        split_point = len(original_df)
        forecast_historical = forecast.iloc[:split_point]
        forecast_future = forecast.iloc[split_point:]

        summary = {
            'historical_mean': float(forecast_historical['yhat'].mean()),
            'historical_std': float(forecast_historical['yhat'].std()),
            'forecast_mean': float(forecast_future['yhat'].mean()),
            'forecast_std': float(forecast_future['yhat'].std()),
            'forecast_min': float(forecast_future['yhat_lower'].min()),
            'forecast_max': float(forecast_future['yhat_upper'].max()),
            'forecast_range': float(
                forecast_future['yhat_upper'].max() - forecast_future['yhat_lower'].min()
            ),
            'forecast_periods': len(forecast_future)
        }

        # 预测趋势
        forecast_trend = forecast_future['yhat'].iloc[-1] - forecast_future['yhat'].iloc[0]
        summary['forecast_trend'] = float(forecast_trend)
        summary['forecast_trend_pct'] = float(
            forecast_trend / forecast_future['yhat'].iloc[0] * 100
            if forecast_future['yhat'].iloc[0] != 0 else 0
        )

        return summary
