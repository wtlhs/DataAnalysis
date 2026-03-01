"""
可视化工具模块

生成各种数据分析图表
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional


def plot_distribution(df: pd.DataFrame, column: str) -> go.Figure:
    """
    绘制数据分布图（直方图）

    Args:
        df: 数据框
        column: 列名

    Returns:
        Plotly图表对象
    """
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df[column],
        name=column,
        nbinsx=30,
        marker_color='lightblue',
        opacity=0.7
    ))

    # 添加均值线
    mean_val = df[column].mean()
    fig.add_vline(x=mean_val, line_dash="dash", line_color="red",
                  annotation_text=f"均值: {mean_val:.2f}")

    fig.update_layout(
        title=f"{column} 数据分布",
        xaxis_title=column,
        yaxis_title="频数",
        hovermode='x unified',
        template="plotly_white"
    )

    return fig


def plot_trend(df: pd.DataFrame, date_col: str, value_col: str) -> go.Figure:
    """
    绘制趋势图

    Args:
        df: 数据框
        date_col: 日期列名
        value_col: 数值列名

    Returns:
        Plotly图表对象
    """
    df_sorted = df.sort_values(date_col)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_sorted[date_col],
        y=df_sorted[value_col],
        mode='lines+markers',
        name=value_col,
        line=dict(color='#1e88e5', width=2),
        marker=dict(size=4)
    ))

    # 添加移动平均线
    ma_period = min(7, len(df_sorted) // 2)  # 自适应移动平均周期
    if ma_period > 1:
        df_sorted[f'{value_col}_MA'] = df_sorted[value_col].rolling(
            window=ma_period, min_periods=1
        ).mean()

        fig.add_trace(go.Scatter(
            x=df_sorted[date_col],
            y=df_sorted[f'{value_col}_MA'],
            mode='lines',
            name=f'移动平均({ma_period}期)',
            line=dict(color='orange', width=1.5, dash='dash')
        ))

    fig.update_layout(
        title=f"{value_col} 趋势分析",
        xaxis_title=date_col,
        yaxis_title=value_col,
        hovermode='x unified',
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig


def plot_correlation(corr_df: pd.DataFrame) -> go.Figure:
    """
    绘制相关性热力图

    Args:
        corr_df: 相关性矩阵

    Returns:
        Plotly图表对象
    """
    fig = go.Figure(data=go.Heatmap(
        z=corr_df.values,
        x=corr_df.columns,
        y=corr_df.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_df.round(2).values,
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="相关系数")
    ))

    fig.update_layout(
        title="特征相关性热力图",
        template="plotly_white",
        width=600,
        height=600
    )

    return fig


def plot_forecast(
    historical: pd.DataFrame,
    forecast: pd.DataFrame,
    date_col: str,
    value_col: str,
    title: str = "趋势预测"
) -> go.Figure:
    """
    绘制预测图（历史数据 + 预测数据）

    Args:
        historical: 历史数据
        forecast: 预测数据
        date_col: 日期列名
        value_col: 数值列名
        title: 图表标题

    Returns:
        Plotly图表对象
    """
    fig = go.Figure()

    # 历史数据
    fig.add_trace(go.Scatter(
        x=historical[date_col],
        y=historical[value_col],
        mode='lines',
        name='历史数据',
        line=dict(color='#1e88e5', width=2)
    ))

    # 预测数据
    if 'ds' in forecast.columns:
        forecast_dates = pd.to_datetime(forecast['ds'])
        if 'yhat' in forecast.columns:
            fig.add_trace(go.Scatter(
                x=forecast_dates,
                y=forecast['yhat'],
                mode='lines',
                name='预测值',
                line=dict(color='green', width=2, dash='dot')
            ))

            # 置信区间
            if 'yhat_lower' in forecast.columns and 'yhat_upper' in forecast.columns:
                fig.add_trace(go.Scatter(
                    x=forecast_dates,
                    y=forecast['yhat_upper'],
                    mode='lines',
                    name='置信区间上界',
                    line=dict(color='green', width=0),
                    showlegend=False
                ))

                fig.add_trace(go.Scatter(
                    x=forecast_dates,
                    y=forecast['yhat_lower'],
                    mode='lines',
                    name='置信区间下界',
                    line=dict(color='green', width=0),
                    fill='tonexty',
                    fillcolor='rgba(0, 255, 0, 0.1)',
                    showlegend=False
                ))

    fig.update_layout(
        title=title,
        xaxis_title=date_col,
        yaxis_title=value_col,
        hovermode='x unified',
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig


def plot_boxplot(df: pd.DataFrame, columns: list, title: str = "箱线图") -> go.Figure:
    """
    绘制箱线图（用于异常检测）

    Args:
        df: 数据框
        columns: 要绘制的列名列表
        title: 图表标题

    Returns:
        Plotly图表对象
    """
    fig = go.Figure()

    for col in columns:
        fig.add_trace(go.Box(
            y=df[col].dropna(),
            name=col,
            boxpoints='outliers',
            jitter=0.5,
            pointpos=-1.8
        ))

    fig.update_layout(
        title=title,
        yaxis_title="数值",
        template="plotly_white"
    )

    return fig


def plot_pie_chart(
    df: pd.DataFrame,
    column: str,
    title: str = "占比分析"
) -> go.Figure:
    """
    绘制饼图

    Args:
        df: 数据框
        column: 列名
        title: 图表标题

    Returns:
        Plotly图表对象
    """
    value_counts = df[column].value_counts().head(10)

    fig = go.Figure(data=[go.Pie(
        labels=value_counts.index,
        values=value_counts.values,
        hole=0.3
    )])

    fig.update_layout(
        title=title,
        template="plotly_white"
    )

    return fig
