"""
前台用户操作页面

提供数据上传、分析、预测、风险预警等用户操作界面
"""
import streamlit as st
import pandas as pd
from typing import Optional

from ui.components import (
    load_custom_css,
    render_multi_file_upload,
    render_dataset_list,
    render_progress_indicator,
    render_data_preview,
    render_metric_card,
    render_info_card,
    render_task_history,
    render_chat_history,
    render_report_list
)

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


def render_frontend_page(session_manager, task_manager):
    """渲染前台用户操作页面"""
    # 加载自定义CSS
    load_custom_css()

    # 页面标题
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem;">
        <div>
            <h1 style="font-size: 1.875rem; font-weight: 600; margin: 0;">📊 数据分析工作台</h1>
            <p style="color: #71717a; font-size: 0.875rem; margin-top: 0.25rem;">上传数据文件，获取智能分析报告</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 初始化session state
    _init_session_state()

    # 功能导航 (使用 shadcn 风格 tabs)
    nav_options = [
        ("📁 数据上传", "upload"),
        ("📊 数据预览", "preview"),
        ("📈 统计分析", "analysis"),
        ("🔮 趋势预测", "prediction"),
        ("⚠️ 风险预警", "risk"),
        ("🤖 AI分析", "ai"),
        ("📝 报告中心", "reports")
    ]
    
    # 创建导航
    cols = st.columns([1] * len(nav_options))
    selected_nav = "upload"
    
    # 侧边栏导航
    page = st.sidebar.radio("选择功能", [
        "📁 数据上传",
        "📊 数据预览",
        "📈 统计分析",
        "🔮 趋势预测",
        "⚠️ 风险预警",
        "🤖 AI分析",
        "📝 报告中心"
    ])

    # 根据选择的页面渲染内容
    if page == "📁 数据上传":
        render_data_upload_section(session_manager)
    elif page == "📊 数据预览":
        render_data_preview_section(session_manager)
    elif page == "📈 统计分析":
        render_analysis_section(session_manager)
    elif page == "🔮 趋势预测":
        render_prediction_section(session_manager, task_manager)
    elif page == "⚠️ 风险预警":
        render_risk_section(session_manager, task_manager)
    elif page == "🤖 AI分析":
        render_ai_section(session_manager, task_manager)
    elif page == "📝 报告中心":
        render_report_center_section(session_manager)


def _init_session_state():
    """初始化session state"""
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'current_dataset_id' not in st.session_state:
        st.session_state.current_dataset_id = None
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
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []


def render_data_upload_section(session_manager):
    """数据上传页面"""
    # 页面标题
    st.markdown("""
    <div class="section-header">
        <h2 style="font-size: 1.25rem; font-weight: 600; margin: 0;">📁 数据上传</h2>
        <p style="color: #71717a; font-size: 0.875rem; margin-top: 0.25rem;">上传您的Excel或CSV文件，开始智能数据分析</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 功能介绍卡片
    st.markdown("""
    <div class="feature-grid" style="margin-bottom: 1.5rem;">
        <div class="feature-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📊</div>
            <h3 style="font-size: 0.875rem; font-weight: 600; margin: 0 0 0.25rem 0;">统计分析</h3>
            <p style="font-size: 0.75rem; color: #71717a; margin: 0;">描述性统计、分布分析、相关性分析</p>
        </div>
        <div class="feature-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🔮</div>
            <h3 style="font-size: 0.875rem; font-weight: 600; margin: 0 0 0.25rem 0;">趋势预测</h3>
            <p style="font-size: 0.75rem; color: #71717a; margin: 0;">时间序列预测、未来走势分析</p>
        </div>
        <div class="feature-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">⚠️</div>
            <h3 style="font-size: 0.875rem; font-weight: 600; margin: 0 0 0.25rem 0;">风险预警</h3>
            <p style="font-size: 0.75rem; color: #71717a; margin: 0;">异常检测、风险评估、预警通知</p>
        </div>
        <div class="feature-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🤖</div>
            <h3 style="font-size: 0.875rem; font-weight: 600; margin: 0 0 0.25rem 0;">AI智能分析</h3>
            <p style="font-size: 0.75rem; color: #71717a; margin: 0;">大模型驱动的智能洞察与报告</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 上传区域
    st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
    
    uploaded_files = render_multi_file_upload("拖拽文件到此处或点击选择")
    
    if uploaded_files:
        st.markdown(f"""
        <div style="margin-top: 1rem;">
            <span class="status-badge info">已选择 {len(uploaded_files)} 个文件</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 上传按钮
    col1, col2 = st.columns([1, 4])
    with col1:
        if uploaded_files and st.button("🚀 开始上传", type="primary", use_container_width=True):
        from config.settings import settings

        with st.spinner("正在处理文件..."):
            try:
                # 准备文件数据
                file_list = [(f.name, f.getvalue()) for f in uploaded_files]

                # 加载文件
                loader = st.session_state.loader
                datasets = loader.load_multiple_files(
                    file_list,
                    str(settings.app.upload_dir),
                    session_manager
                )

                st.success(f"✅ 成功上传 {len(datasets)} 个文件！")

                # 设置第一个数据集为激活状态
                if datasets:
                    first_id = list(datasets.keys())[0]
                    session_manager.set_active_dataset(first_id)
                    st.rerun()

            except Exception as e:
                render_error_message(f"上传失败: {str(e)}")

    # 显示数据集列表
    datasets = session_manager.list_datasets()
    render_dataset_list(datasets, session_manager)


def render_data_preview_section(session_manager):
    """数据预览页面"""
    st.markdown("""
    <div class="section-header">
        <h2 style="font-size: 1.25rem; font-weight: 600; margin: 0;">📊 数据预览</h2>
        <p style="color: #71717a; font-size: 0.875rem; margin-top: 0.25rem;">查看已上传数据的结构和内容</p>
    </div>
    """, unsafe_allow_html=True)

    # 获取当前数据集
    dataset = session_manager.get_active_dataset()

    if not dataset:
        st.info("👈 请先上传数据文件")
        return

    # 加载数据
    if st.session_state.df is None or st.session_state.current_dataset_id != dataset['id']:
        try:
            loader = st.session_state.loader
            df = loader.get_dataset_from_db(dataset['id'], session_manager)
            st.session_state.df = df
            st.session_state.current_dataset_id = dataset['id']
        except Exception as e:
            render_error_message(f"数据加载失败: {str(e)}")
            return

    # 渲染数据预览
    render_data_preview(st.session_state.df)


def render_analysis_section(session_manager):
    """统计分析页面"""
    st.markdown("""
    <div class="section-header">
        <h2 style="font-size: 1.25rem; font-weight: 600; margin: 0;">📈 统计分析</h2>
        <p style="color: #71717a; font-size: 0.875rem; margin-top: 0.25rem;">对数据进行描述性统计和可视化分析</p>
    </div>
    """, unsafe_allow_html=True)

    # 获取当前数据集
    dataset = session_manager.get_active_dataset()

    if not dataset:
        st.info("👈 请先上传数据文件")
        return

    # 加载数据
    df = st.session_state.df
    if df is None:
        try:
            loader = st.session_state.loader
            df = loader.get_dataset_from_db(dataset['id'], session_manager)
            st.session_state.df = df
        except Exception as e:
            render_error_message(f"数据加载失败: {str(e)}")
            return

    loader = st.session_state.loader

    # 数值列选择
    numeric_cols = loader.get_numeric_columns(df)

    if not numeric_cols:
        st.warning("⚠️ 未检测到数值列，请确保数据中包含数值类型的列")
        return

    selected_col = st.selectbox("选择要分析的数值列", numeric_cols)

    if not selected_col:
        return

    analyzer = st.session_state.analyzer

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


def render_prediction_section(session_manager, task_manager):
    """预测分析页面"""
    st.markdown("""
    <div class="section-header">
        <h2 style="font-size: 1.25rem; font-weight: 600; margin: 0;">🔮 趋势预测</h2>
        <p style="color: #71717a; font-size: 0.875rem; margin-top: 0.25rem;">基于历史数据进行时间序列预测</p>
    </div>
    """, unsafe_allow_html=True)

    # 获取当前数据集
    dataset = session_manager.get_active_dataset()

    if not dataset:
        st.info("👈 请先上传数据文件")
        return

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

    # 异步预测
    if st.button("🚀 开始预测", key="start_forecast", type="primary"):
        def run_forecast():
            return predictor.run_forecast(
                df,
                date_col,
                value_col,
                periods=forecast_periods,
                freq=freq,
                seasonality_mode=seasonality_mode
            )

        task_id = task_manager.submit_task('prediction', run_forecast)

        # 保存任务ID以便后续查询
        st.session_state['current_task_id'] = task_id
        st.rerun()

    # 检查并显示任务结果
    if 'current_task_id' in st.session_state:
        result = render_progress_indicator(st.session_state['current_task_id'], task_manager)

        if result:
            # 保存结果
            st.session_state.analysis_results['forecast'] = result
            del st.session_state['current_task_id']
            st.rerun()

    # 显示预测结果
    if 'forecast' in st.session_state.analysis_results:
        forecast_data = st.session_state.analysis_results['forecast']

        # 预测准确度
        st.subheader("📊 预测准确度")
        accuracy = forecast_data.get('accuracy', {})
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_metric_card("MAE", f"{accuracy.get('mae', 0):.2f}")
        with col2:
            render_metric_card("RMSE", f"{accuracy.get('rmse', 0):.2f}")
        with col3:
            render_metric_card("MAPE", f"{accuracy.get('mape', 0):.2f}%")
        with col4:
            render_metric_card("覆盖率", f"{accuracy.get('coverage', 0):.1%}")

        # 预测图表
        st.subheader("📈 预测趋势图")
        forecast_df = forecast_data.get('forecast')
        if forecast_df is not None:
            fig = plot_forecast(
                df,
                forecast_df,
                date_col,
                value_col,
                title=f"{value_col} 预测结果"
            )
            st.plotly_chart(fig, use_container_width=True)


def render_risk_section(session_manager, task_manager):
    """风险预警页面"""
    st.markdown("""
    <div class="section-header">
        <h2 style="font-size: 1.25rem; font-weight: 600; margin: 0;">⚠️ 风险预警</h2>
        <p style="color: #71717a; font-size: 0.875rem; margin-top: 0.25rem;">智能识别异常数据，评估风险等级</p>
    </div>
    """, unsafe_allow_html=True)

    # 获取当前数据集
    dataset = session_manager.get_active_dataset()

    if not dataset:
        st.info("👈 请先上传数据文件")
        return

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
    if st.button("🔍 开始风险评估", key="start_risk", type="primary"):
        def run_risk_assessment():
            date_column = date_cols[0] if date_cols else None
            return risk_monitor.generate_comprehensive_report(
                df,
                columns_to_monitor=columns_to_monitor,
                date_column=date_column
            )

        task_id = task_manager.submit_task('risk', run_risk_assessment)
        st.session_state['current_task_id'] = task_id
        st.rerun()

    # 检查并显示任务结果
    if 'current_task_id' in st.session_state:
        result = render_progress_indicator(st.session_state['current_task_id'], task_manager)

        if result:
            st.session_state.analysis_results['risk'] = result
            del st.session_state['current_task_id']
            st.rerun()

    # 显示风险结果
    if 'risk' in st.session_state.analysis_results:
        risk_data = st.session_state.analysis_results['risk']

        # 风险评分
        st.subheader("📊 风险评分")
        risk_score = risk_data.get('risk_score', {})
        score_value = risk_score.get('overall_score', 0)
        risk_level = risk_score.get('risk_level', {}).get('value', 'UNKNOWN')

        col1, col2 = st.columns(2)
        with col1:
            render_metric_card("综合风险评分", f"{score_value}/100")
        with col2:
            render_metric_card("风险等级", risk_level)

        # 告警列表
        st.subheader("🚨 告警列表")
        alerts = risk_data.get('alerts', [])
        summary = risk_data.get('summary', {})

        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric_card("总告警数", summary.get('total_alerts', 0))
        with col2:
            render_metric_card("高风险", summary.get('high_risk_count', 0))
        with col3:
            render_metric_card("中风险", summary.get('medium_risk_count', 0))

        if alerts:
            for alert in alerts[:10]:
                level_icon = {
                    'HIGH': '🔴',
                    'MEDIUM': '🟠',
                    'LOW': '🟡'
                }.get(alert.risk_level.value if hasattr(alert, 'risk_level') else 'UNKNOWN', '❓')

                with st.expander(f"{level_icon} {alert.risk_type} - {alert.affected_column}"):
                    st.write(f"**消息**: {alert.message}")
                    st.write(f"**严重程度**: {alert.severity:.2%}")


def render_ai_section(session_manager, task_manager):
    """AI智能分析页面"""
    st.markdown("""
    <div class="section-header">
        <h2 style="font-size: 1.25rem; font-weight: 600; margin: 0;">🤖 AI智能分析</h2>
        <p style="color: #71717a; font-size: 0.875rem; margin-top: 0.25rem;">利用大模型进行深度数据分析和智能洞察</p>
    </div>
    """, unsafe_allow_html=True)

    # 获取当前数据集
    dataset = session_manager.get_active_dataset()

    if not dataset:
        st.info("👈 请先上传数据文件")
        return

    from config.settings import settings

    # 检查API配置
    if not settings.validate():
        st.error("❌ 请先配置API密钥（在后台管理页面）")
        return

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

        df = st.session_state.df
        loader = st.session_state.loader
        numeric_cols = loader.get_numeric_columns(df)

        if st.button("✨ 生成洞察", key="generate_insights", type="primary"):
            def run_insights_generation():
                data_summary = ai_agent.summarize_data(df)
                analyzer = st.session_state.analyzer

                stats_results = {}
                for col in numeric_cols[:5]:
                    stats_results[col] = analyzer.descriptive_statistics(df, col)

                return ai_agent.generate_insights(data_summary, {'stats': stats_results}, count=5)

            task_id = task_manager.submit_task('ai_analysis', run_insights_generation)
            st.session_state['current_task_id'] = task_id
            st.rerun()

        # 检查并显示任务结果
        if 'current_task_id' in st.session_state:
            result = render_progress_indicator(st.session_state['current_task_id'], task_manager)

            if result:
                st.session_state.analysis_results['ai_insights'] = result
                del st.session_state['current_task_id']
                st.rerun()

        # 显示洞察
        if 'ai_insights' in st.session_state.analysis_results:
            insights = st.session_state.analysis_results['ai_insights']
            st.subheader("📌 关键洞察")
            for i, insight in enumerate(insights, 1):
                st.write(f"{i}. {insight}")

    elif ai_function == "交互式问答":
        st.subheader("💬 交互式问答")

        st.info("""
        💡 **提问示例**：
        - "数据的整体趋势如何？"
        - "有哪些异常值需要注意？"
        - "给我一些商业建议"
        """)

        # 问题输入
        question = st.text_input(
            "请输入你的问题",
            key="ai_question",
            placeholder="例如：数据的整体趋势如何？"
        )

        if st.button("🤖 提问", key="ask_ai", type="primary"):
            def run_qa():
                context = st.session_state.analysis_results
                return ai_agent.chat_async(
                    question,
                    st.session_state.df,
                    context
                )

            task_id = task_manager.submit_task('ai_analysis', run_qa)
            st.session_state['current_task_id'] = task_id
            st.rerun()

        # 检查并显示任务结果
        if 'current_task_id' in st.session_state:
            result = render_progress_indicator(st.session_state['current_task_id'], task_manager)

            if result:
                st.session_state.chat_history.append({
                    'question': question,
                    'answer': result
                })
                session_manager.save_chat(question, result)
                del st.session_state['current_task_id']
                st.rerun()

        # 显示聊天历史
        render_chat_history(st.session_state.chat_history)

        # 清空历史按钮
        if st.button("🗑️ 清空对话历史", key="clear_chat"):
            st.session_state.chat_history = []
            session_manager.clear_chat_history()
            st.rerun()


def render_report_center_section(session_manager):
    """报告中心页面"""
    st.markdown("""
    <div class="section-header">
        <h2 style="font-size: 1.25rem; font-weight: 600; margin: 0;">📝 报告中心</h2>
        <p style="color: #71717a; font-size: 0.875rem; margin-top: 0.25rem;">管理和下载已生成的智能分析报告</p>
    </div>
    """, unsafe_allow_html=True)

    # 显示报告列表
    reports = session_manager.list_reports()
    render_report_list(reports, session_manager)
