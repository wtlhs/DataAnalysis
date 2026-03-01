"""
数据分析智能体 - Streamlit主应用

用户上传Excel文件，进行数据分析、预测、风险预警
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from core.data_loader import DataLoader
from core.analyzer import Analyzer
from core.predictor import Predictor
from core.risk_monitor import RiskMonitor
from core.reporter import ReportGenerator
from ai.agent import DataAnalysisAgent
from utils.visualizations import (
    plot_trend, plot_distribution, plot_correlation,
    plot_forecast, plot_boxplot
)


# 页面配置
st.set_page_config(
    page_title="数据分析智能体",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1e88e5;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        color: #333;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# 初始化session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'loader' not in st.session_state:
    st.session_state.loader = DataLoader()
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = Analyzer()
if 'predictor' not in st.session_state:
    st.session_state.predictor = Predictor()
if 'risk_monitor' not in st.session_state:
    st.session_state.risk_monitor = RiskMonitor()
if 'reporter' not in st.session_state:
    st.session_state.reporter = ReportGenerator()
if 'ai_agent' not in st.session_state:
    st.session_state.ai_agent = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'generated_report' not in st.session_state:
    st.session_state.generated_report = None


def render_sidebar():
    """渲染侧边栏"""
    st.sidebar.title("⚙️ 配置")

    # 模型选择
    st.sidebar.subheader("🤖 AI模型配置")
    model_provider = st.sidebar.selectbox(
        "选择AI模型",
        ["openai", "智谱AI(GLM)", "anthropic"],
        index=0
    )

    model_options = {
        "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        "智谱AI(GLM)": ["glm-5", "glm-4", "glm-4-flash", "glm-3-turbo", "glm-4-air", "glm-4-long"],
        "anthropic": ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022"]
    }

    model_name = st.sidebar.selectbox(
        "模型版本",
        model_options[model_provider],
        index=0
    )

    # 温度设置
    temperature = st.sidebar.slider(
        "Temperature",
        0.0, 2.0, 0.7, 0.1,
        help="控制输出的随机性，越高越有创造性"
    )

    # 应用配置更新
    if st.sidebar.button("更新模型配置"):
        # 智谱AI使用OpenAI兼容接口
        if model_provider == "智谱AI(GLM)":
            model_provider = "openai"
            # 智谱AI的API_BASE已经在.env中配置
        settings.update_model(model_provider, model_name)
        st.sidebar.success("✅ 模型配置已更新！")

    # 风险阈值
    st.sidebar.subheader("⚠️ 风险预警阈值")
    high_risk = st.sidebar.number_input("高风险阈值 (Sigma)", 1.0, 5.0, 3.0, 0.1)
    medium_risk = st.sidebar.number_input("中风险阈值 (Sigma)", 1.0, 5.0, 2.0, 0.1)

    # 预测参数
    st.sidebar.subheader("🔮 预测参数")
    forecast_periods = st.sidebar.number_input("预测周期数", 1, 365, 30)


def render_upload_section():
    """文件上传区域"""
    st.markdown('<div class="main-header">📊 数据分析智能体</div>', unsafe_allow_html=True)

    st.info("""
    📤 **上传您的Excel或CSV文件**，我将为您进行智能数据分析

    支持功能：
    - ✅ 统计分析与趋势洞察
    - ✅ 时间序列预测
    - ✅ 异常检测与风险预警
    - ✅ AI智能分析报告
    """)

    uploaded_file = st.file_uploader(
        "选择文件",
        type=['xlsx', 'xls', 'csv'],
        help=f"最大文件大小: {settings.data.max_file_size_mb}MB"
    )

    if uploaded_file:
        # 保存文件
        file_path = settings.app.upload_dir / uploaded_file.name
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        # 加载数据
        with st.spinner("正在加载数据..."):
            df, validation = st.session_state.loader.load_file(str(file_path))

        if validation.is_valid:
            # 预处理数据
            df, preprocess_info = st.session_state.loader.preprocess(df)
            st.session_state.df = df

            # 显示成功消息
            st.success(f"✅ 数据加载成功！")

            # 数据概览
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("数据行数", f"{len(df):,}")
            with col2:
                st.metric("数据列数", len(df.columns))
            with col3:
                file_size = validation.file_info.get('size_mb', 0)
                st.metric("文件大小", f"{file_size:.2f} MB")

            # 数据预览
            st.subheader("📋 数据预览")
            st.dataframe(df.head(10), use_container_width=True)

            # 显示列信息
            st.subheader("📊 列信息")
            col_info = pd.DataFrame({
                '列名': df.columns,
                '数据类型': df.dtypes.astype(str).values,
                '非空值': df.count().values,
                '缺失值': df.isnull().sum().values,
                '缺失比例': (df.isnull().sum() / len(df) * 100).round(2)
            })
            st.dataframe(col_info, use_container_width=True)

            # 检查警告
            if preprocess_info.get('warning'):
                st.warning(preprocess_info['warning'])

        else:
            st.error("❌ 数据加载失败：")
            for error in validation.errors:
                st.error(f"  • {error}")


def render_analysis_section():
    """数据分析区域"""
    if st.session_state.df is None:
        st.info("👈 请先上传数据文件")
        return

    df = st.session_state.df

    st.markdown('<div class="section-header">📈 统计分析</div>', unsafe_allow_html=True)

    # 显示数据概览
    st.info(f"当前数据: {len(df)} 行 x {len(df.columns)} 列")

    # 列选择
    loader = st.session_state.loader

    # 数值列选择
    numeric_cols = loader.get_numeric_columns(df)
    if not numeric_cols:
        st.warning("⚠️ 未检测到数值列，请确保数据中包含数值类型的列")
        return

    selected_col = st.selectbox("选择要分析的数值列", numeric_cols)

    if not selected_col:
        return

    # 描述性统计
    st.subheader("📊 描述性统计")
    try:
        stats_df = df[selected_col].describe().to_frame().T
        st.dataframe(stats_df, use_container_width=True)
    except Exception as e:
        st.error(f"统计计算失败: {str(e)}")

        # 分布图
        st.subheader("📉 数据分布")
        try:
            fig = plot_distribution(df, selected_col)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"分布图生成失败: {str(e)}")

        # 趋势分析
        date_cols = loader.get_date_columns(df)
        if date_cols:
            st.subheader("📈 趋势分析")
            trend_col = st.selectbox("选择时间列", date_cols, key="trend_date")
            try:
                fig = plot_trend(df, trend_col, selected_col)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"趋势图生成失败: {str(e)}")
        else:
            st.info("💡 提示：未检测到日期列，无法进行趋势分析")

    # 相关性分析
    if len(numeric_cols) > 1:
        st.subheader("🔗 相关性分析")
        try:
            corr_df = df[numeric_cols].corr()
            fig = plot_correlation(corr_df)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"相关性分析失败: {str(e)}")
    else:
        st.info("💡 提示：需要至少2个数值列才能进行相关性分析")


def render_prediction_section():
    """预测分析区域"""
    if st.session_state.df is None:
        st.info("👈 请先上传数据文件")
        return

    st.markdown('<div class="section-header">🔮 趋势预测</div>', unsafe_allow_html=True)

    df = st.session_state.df
    loader = st.session_state.loader
    predictor = st.session_state.predictor

    # 选择日期列和数值列
    date_cols = loader.get_date_columns(df)
    numeric_cols = loader.get_numeric_columns(df)

    if not date_cols:
        st.warning("⚠️ 未检测到日期列，请确保数据中包含日期类型字段")
        return

    if not numeric_cols:
        st.warning("⚠️ 未检测到数值列")
        return

    col1, col2 = st.columns(2)
    with col1:
        date_col = st.selectbox("选择日期列", date_cols, key="pred_date")
    with col2:
        value_col = st.selectbox("选择数值列", numeric_cols, key="pred_value")

    # 预测参数
    col1, col2, col3 = st.columns(3)
    with col1:
        forecast_periods = st.number_input("预测周期数", 1, 365, 30, key="forecast_periods")
    with col2:
        freq = st.selectbox("时间频率", ["D", "W", "M"], index=0, key="forecast_freq")
    with col3:
        seasonality_mode = st.selectbox("季节性模式", ["multiplicative", "additive"], index=0)

    # 执行预测
    if st.button("🚀 开始预测", key="start_forecast"):
        with st.spinner("正在训练模型并进行预测..."):
            try:
                result = predictor.run_forecast(
                    df,
                    date_col,
                    value_col,
                    periods=forecast_periods,
                    freq=freq,
                    seasonality_mode=seasonality_mode
                )

                # 保存结果
                st.session_state.analysis_results['forecast'] = {
                    'forecast': result.forecast,
                    'accuracy': result.accuracy,
                    'forecast_summary': predictor.get_forecast_summary(
                        result.forecast, df, value_col
                    )
                }

                st.success("✅ 预测完成！")

            except Exception as e:
                st.error(f"❌ 预测失败: {str(e)}")
                st.info("💡 提示：请确保日期列和数值列数据完整，且数据量足够（至少30个数据点）")

    # 显示预测结果
    if 'forecast' in st.session_state.analysis_results:
        forecast_data = st.session_state.analysis_results['forecast']

        # 预测准确度
        st.subheader("📊 预测准确度")
        accuracy = forecast_data['accuracy']
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("MAE", f"{accuracy.get('mae', 0):.2f}")
        with col2:
            st.metric("RMSE", f"{accuracy.get('rmse', 0):.2f}")
        with col3:
            st.metric("MAPE", f"{accuracy.get('mape', 0):.2f}%")
        with col4:
            st.metric("覆盖率", f"{accuracy.get('coverage', 0):.1%}")

        # 预测图表
        st.subheader("📈 预测趋势图")
        fig = plot_forecast(
            df,
            forecast_data['forecast'],
            date_col,
            value_col,
            title=f"{value_col} 预测结果"
        )
        st.plotly_chart(fig, use_container_width=True)

        # 预测摘要
        st.subheader("📋 预测摘要")
        summary = forecast_data['forecast_summary']
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**预测均值**: {summary['forecast_mean']:.2f}")
            st.write(f"**预测范围**: {summary['forecast_min']:.2f} - {summary['forecast_max']:.2f}")
        with col2:
            st.write(f"**预测趋势**: {summary['forecast_trend']:.2f}")
            st.write(f"**趋势百分比**: {summary['forecast_trend_pct']:.2f}%")


def render_risk_section():
    """风险预警区域"""
    if st.session_state.df is None:
        st.info("👈 请先上传数据文件")
        return

    st.markdown('<div class="section-header">⚠️ 风险预警</div>', unsafe_allow_html=True)

    df = st.session_state.df
    loader = st.session_state.loader
    risk_monitor = st.session_state.risk_monitor

    # 选择要监控的列
    numeric_cols = loader.get_numeric_columns(df)
    date_cols = loader.get_date_columns(df)

    columns_to_monitor = st.multiselect(
        "选择要监控的列",
        numeric_cols,
        default=numeric_cols[:3] if len(numeric_cols) > 3 else numeric_cols
    )

    # 检测方法
    detection_method = st.selectbox("异常检测方法", ["zscore", "iqr"])

    # 执行风险评估
    if st.button("🔍 开始风险评估", key="start_risk"):
        with st.spinner("正在分析风险..."):
            date_column = date_cols[0] if date_cols else None

            try:
                risk_report = risk_monitor.generate_comprehensive_report(
                    df,
                    columns_to_monitor=columns_to_monitor,
                    date_column=date_column
                )

                st.session_state.analysis_results['risk'] = risk_report
                st.success("✅ 风险评估完成！")

            except Exception as e:
                st.error(f"❌ 风险评估失败: {str(e)}")

    # 显示风险结果
    if 'risk' in st.session_state.analysis_results:
        risk_data = st.session_state.analysis_results['risk']

        # 风险评分
        st.subheader("📊 风险评分")
        risk_score = risk_data['risk_score']
        col1, col2 = st.columns(2)
        with col1:
            score_value = risk_score.overall_score
            score_color = "🔴" if score_value >= 70 else "🟠" if score_value >= 50 else "🟡" if score_value >= 30 else "🟢"
            st.metric("综合风险评分", f"{score_value}/100")
        with col2:
            risk_level = risk_score.risk_level.value
            st.metric("风险等级", f"{score_color} {risk_level}")

        # 风险细分
        st.subheader("📈 风险细分")
        breakdown = risk_score.breakdown
        breakdown_df = pd.DataFrame({
            '维度': ['数据质量', '统计异常', '阈值违规', '趋势反转'],
            '评分': [breakdown.get('data_quality', 0),
                   breakdown.get('statistical_anomaly', 0),
                   breakdown.get('threshold_violation', 0),
                   breakdown.get('trend_reversal', 0)]
        })
        st.bar_chart(breakdown_df.set_index('维度'))

        # 告警列表
        st.subheader("🚨 告警列表")
        alerts = risk_data['alerts']
        summary = risk_data['summary']

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总告警数", summary['total_alerts'])
        with col2:
            st.metric("高风险", summary['high_risk_count'], delta_color="inverse")
        with col3:
            st.metric("中风险", summary['medium_risk_count'], delta_color="normal")

        if alerts:
            # 按风险等级分类显示
            for alert in alerts[:10]:  # 最多显示10条
                level_icon = "🔴" if alert.risk_level.value == "HIGH" else "🟠" if alert.risk_level.value == "MEDIUM" else "🟡"
                with st.expander(f"{level_icon} {alert.risk_type} - {alert.affected_column}"):
                    st.write(f"**消息**: {alert.message}")
                    st.write(f"**严重程度**: {alert.severity:.2%}")
                    if alert.affected_rows:
                        st.write(f"**受影响行数**: {len(alert.affected_rows)}")
                        st.write(f"**受影响行索引**: {alert.affected_rows[:10]}...")

        # 应对建议
        if risk_score.recommendations:
            st.subheader("💡 应对建议")
            for i, rec in enumerate(risk_score.recommendations, 1):
                st.write(f"{i}. {rec}")


def render_ai_section():
    """AI智能体区域"""
    if st.session_state.df is None:
        st.info("👈 请先上传数据文件")
        return

    st.markdown('<div class="section-header">🤖 AI智能分析</div>', unsafe_allow_html=True)

    # 检查API配置
    if not settings.validate():
        st.error("❌ 请先配置API密钥（在.env文件中）")
        st.info("""
        💡 **配置步骤**：
        1. 复制 `.env.example` 为 `.env`
        2. 在 `.env` 文件中填入你的 API 密钥
        3. 重启应用
        """)
        return

    df = st.session_state.df
    analyzer = st.session_state.analyzer
    reporter = st.session_state.reporter

    # 初始化AI智能体
    if st.session_state.ai_agent is None:
        st.session_state.ai_agent = DataAnalysisAgent()

    ai_agent = st.session_state.ai_agent

    # 功能选择
    ai_function = st.selectbox(
        "选择AI功能",
        ["生成分析洞察", "生成完整报告", "交互式问答"],
        key="ai_function"
    )

    if ai_function == "生成分析洞察":
        st.subheader("💡 智能洞察生成")

        # 列选择
        loader = st.session_state.loader
        numeric_cols = loader.get_numeric_columns(df)

        if st.button("✨ 生成洞察", key="generate_insights"):
            with st.spinner("AI正在分析数据..."):
                try:
                    # 收集分析结果
                    data_summary = ai_agent.summarize_data(df)

                    # 基本统计分析
                    stats_results = {}
                    for col in numeric_cols[:5]:  # 最多分析5列
                        stats_results[col] = analyzer.descriptive_statistics(df, col)

                    # 生成洞察
                    insights = ai_agent.generate_insights(
                        data_summary,
                        {'stats': stats_results},
                        count=5
                    )

                    st.session_state.analysis_results['ai_insights'] = insights
                    st.success("✅ 洞察生成完成！")

                except Exception as e:
                    st.error(f"❌ 生成失败: {str(e)}")

        # 显示洞察
        if 'ai_insights' in st.session_state.analysis_results:
            insights = st.session_state.analysis_results['ai_insights']
            st.subheader("📌 关键洞察")
            for i, insight in enumerate(insights, 1):
                st.write(f"{i}. {insight}")

    elif ai_function == "生成完整报告":
        st.subheader("📝 生成分析报告")

        # 列选择
        loader = st.session_state.loader
        numeric_cols = loader.get_numeric_columns(df)

        # 报告选项
        use_ai = st.checkbox("使用AI增强报告（需API调用）", value=True, key="use_ai_report")

        if st.button("📊 生成报告", key="generate_report"):
            with st.spinner("正在生成分析报告..."):
                try:
                    st.write("📋 步骤1: 正在收集数据摘要...")
                    # 收集所有分析结果
                    data_summary = ai_agent.summarize_data(df)

                    st.write("📊 步骤2: 正在进行统计分析...")
                    # 统计分析
                    batch_stats = analyzer.batch_descriptive_statistics(df)

                    st.write("📈 步骤3: 正在分析趋势...")
                    # 趋势分析（如果有日期列）
                    date_cols = loader.get_date_columns(df)
                    trend_result = None
                    if date_cols and numeric_cols:
                        trend_result = analyzer.trend_analysis(df, date_cols[0], numeric_cols[0])

                    st.write("⚠️  步骤4: 正在检测异常...")
                    # 异常检测
                    anomaly_result = None
                    if numeric_cols:
                        anomaly = analyzer.detect_anomalies(df, numeric_cols[0])
                        anomaly_result = {'anomaly_detection': anomaly}

                    # 预测结果（如果有）
                    forecast_result = st.session_state.analysis_results.get('forecast')
                    risk_result = st.session_state.analysis_results.get('risk')

                    # AI生成的完整报告
                    ai_report = None
                    ai_insights = None

                    if use_ai:
                        st.write("🤖 步骤5: 正在调用AI生成报告（这可能需要几秒钟）...")
                        try:
                            # 生成AI洞察
                            ai_insights = ai_agent.generate_insights(
                                data_summary,
                                {'stats': batch_stats},
                                count=5
                            )

                            # 生成完整报告
                            all_results = {
                                'data_summary': data_summary,
                                'stats_result': {'batch_stats': batch_stats},
                                'trend_result': trend_result,
                                'anomaly_result': anomaly_result,
                                'forecast_result': forecast_result,
                                'risk_result': risk_result
                            }

                            ai_report = ai_agent.write_report(all_results)
                            st.success("✅ AI报告生成完成！")

                        except Exception as e:
                            st.warning(f"⚠️ AI报告生成失败，使用标准模板: {str(e)}")
                            # AI失败不影响报告生成，继续使用标准模板
                        except Exception as e:
                            st.warning(f"⚠️ AI报告生成失败，使用标准模板: {str(e)}")

                    # 生成报告
                    report = reporter.generate_markdown_report(
                        df=df,
                        data_summary=data_summary,
                        stats_result={'batch_stats': batch_stats},
                        trend_result=trend_result,
                        anomaly_result=anomaly_result,
                        forecast_result=forecast_result,
                        risk_result=risk_result,
                        ai_insights=ai_insights,
                        ai_report=ai_report
                    )

                    st.session_state.generated_report = report
                    st.success("✅ 报告生成完成！")

                except Exception as e:
                    st.error(f"❌ 报告生成失败: {str(e)}")

        # 显示和下载报告
        if st.session_state.generated_report:
            report = st.session_state.generated_report

            st.subheader("📄 分析报告")
            st.markdown(report)

            # 下载按钮
            st.download_button(
                label="📥 下载报告 (Markdown)",
                data=report,
                file_name=f"数据分析报告_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )

    elif ai_function == "交互式问答":
        st.subheader("💬 交互式问答")

        st.info("""
        💡 **提问示例**：
        - "数据的整体趋势如何？"
        - "有哪些异常值需要注意？"
        - "预测结果可靠吗？"
        - "给我一些商业建议"
        """)

        # 问题输入
        question = st.text_input(
            "请输入你的问题",
            key="ai_question",
            placeholder="例如：数据的整体趋势如何？"
        )

        # 聊天历史
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        if st.button("🤖 提问", key="ask_ai"):
            if question:
                with st.spinner("AI正在思考..."):
                    try:
                        # 获取上下文
                        context = st.session_state.analysis_results

                        # 调用AI
                        answer = ai_agent.chat(question, df, context)

                        # 保存到历史
                        st.session_state.chat_history.append({
                            'question': question,
                            'answer': answer
                        })

                        st.success("✅ 回答完成！")

                    except Exception as e:
                        st.error(f"❌ 回答失败: {str(e)}")

        # 显示聊天历史
        if st.session_state.chat_history:
            st.subheader("💭 对话历史")
            for i, chat in enumerate(reversed(st.session_state.chat_history), 1):
                with st.chat_message("user"):
                    st.write(chat['question'])
                with st.chat_message("assistant"):
                    st.write(chat['answer'])
                st.divider()

            # 清空历史按钮
            if st.button("🗑️ 清空对话历史", key="clear_chat"):
                st.session_state.chat_history = []
                st.rerun()


def main():
    """主函数"""
    # 渲染侧边栏
    render_sidebar()

    # 页面导航
    page = st.sidebar.radio(
        "📑 功能导航",
        ["数据上传", "统计分析", "趋势预测", "风险预警", "AI智能分析"]
    )

    # 根据选择的页面渲染内容
    if page == "数据上传":
        render_upload_section()
    elif page == "统计分析":
        render_analysis_section()
    elif page == "趋势预测":
        render_prediction_section()
    elif page == "风险预警":
        render_risk_section()
    elif page == "AI智能分析":
        render_ai_section()


if __name__ == "__main__":
    main()
