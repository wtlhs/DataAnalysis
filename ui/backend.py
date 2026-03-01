"""
后台管理页面

提供模型配置、风险阈值、数据管理、系统设置等功能
密钥存储在数据库中，确保安全性
"""
import streamlit as st
from typing import Dict, Any

from ui.components import (
    load_custom_css,
    render_success_message,
    render_error_message
)

from config.settings import settings


def render_backend_page(session_manager):
    """渲染后台管理页面"""
    # 加载自定义CSS
    load_custom_css()

    # 页面标题
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem;">
        <div>
            <h1 style="font-size: 1.875rem; font-weight: 600; margin: 0;">⚙️ 系统管理</h1>
            <p style="color: #71717a; font-size: 0.875rem; margin-top: 0.25rem;">配置模型参数、管理数据、调整界面设置</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 模型配置",
        "⚠️ 风险阈值",
        "📊 数据管理",
        "🎨 界面设置"
    ])

    with tab1:
        render_model_config(session_manager)
    with tab2:
        render_risk_thresholds()
    with tab3:
        render_data_management(session_manager)
    with tab4:
        render_ui_settings()


def render_model_config(session_manager):
    """模型配置"""
    st.subheader("🤖 AI模型配置")

    # 获取已保存的配置
    current_config = session_manager.get_active_api_config()

    # 模型提供商映射
    provider_map = {
        "openai": "openai",
        "智谱AI(GLM)": "zhipu",
        "anthropic": "anthropic"
    }

    # 当前选择的提供商
    current_provider = current_config.get('provider', 'openai') if current_config else 'openai'

    # 反向映射显示
    display_provider = [k for k, v in provider_map.items() if v == current_provider]
    default_idx = list(provider_map.values()).index(current_provider) if current_provider in provider_map.values() else 0

    # 模型提供商
    model_provider = st.selectbox(
        "模型提供商",
        list(provider_map.keys()),
        index=default_idx
    )

    provider = provider_map[model_provider]

    # 获取该provider的配置
    provider_config = session_manager.get_api_config(provider) if provider else None

    # 根据提供商显示不同的配置
    if model_provider == "openai":
        saved = render_openai_config(provider_config)
    elif model_provider == "智谱AI(GLM)":
        saved = render_zhipu_config(provider_config)
    else:
        saved = render_anthropic_config(provider_config)

    # 保存配置
    if saved:
        try:
            settings.reload_model_config()
            render_success_message("✅ 配置已保存到数据库！")
        except Exception as e:
            render_error_message(f"保存失败: {str(e)}")

    # 显示已保存的配置列表
    st.divider()
    st.write("**已保存的配置**")
    configs = session_manager.list_api_configs()
    if configs:
        for config in configs:
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**{config['provider']}**")
                st.caption(f"模型: {config.get('model_name', 'N/A')}")
            with col2:
                st.write(f"API Key: {config.get('api_key', 'N/A')}")
            with col3:
                if config.get('is_active'):
                    st.success("✅ 激活")
                elif st.button("设为默认", key=f"set_default_{config['provider']}"):
                    session_manager.set_active_api_config(config['provider'])
                    settings.reload_model_config()
                    st.rerun()
    else:
        st.info("暂无保存的配置，请在上方添加")


def render_openai_config(provider_config: Dict = None):
    """OpenAI配置"""
    st.write("**OpenAI / 兼容API 配置**")

    # 获取当前值
    default_key = provider_config.get('api_key', '') if provider_config else ''
    default_base = provider_config.get('api_base', '') if provider_config else ''
    default_model = provider_config.get('model_name', 'gpt-4o') if provider_config else 'gpt-4o'
    default_temp = provider_config.get('temperature', 0.7) if provider_config else 0.7
    default_tokens = provider_config.get('max_tokens', 4000) if provider_config else 4000

    model_options = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
    default_model_idx = model_options.index(default_model) if default_model in model_options else 0

    api_key = st.text_input(
        "API密钥 *",
        type="password",
        value=default_key,
        help="OpenAI API Key"
    )

    api_base = st.text_input(
        "API Base URL (可选)",
        value=default_base,
        help="例如: https://api.openai.com/v1"
    )

    model_name = st.selectbox(
        "模型名称",
        model_options,
        index=default_model_idx
    )

    temperature = st.slider(
        "Temperature",
        0.0, 2.0, default_temp, 0.1,
        help="控制输出的随机性，越高越有创造性"
    )

    max_tokens = st.number_input(
        "最大Token数",
        1000, 8000, default_tokens, 100,
        help="响应的最大长度"
    )

    # 保存按钮
    saved = False
    if st.button("💾 保存 OpenAI 配置", type="primary"):
        if not api_key:
            render_error_message("请输入API密钥")
        else:
            from db.session_manager import SessionManager
            session_mgr = SessionManager(db_path="data/data_analysis.db")
            session_mgr.save_api_config(
                provider="openai",
                api_key=api_key,
                api_base=api_base if api_base else None,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
            # 设置为激活
            session_mgr.set_active_api_config("openai")
            saved = True

    st.info("""
    💡 **提示**：
    - OpenAI API Key: https://platform.openai.com/api-keys
    - gpt-4o: 最新的GPT-4模型
    - gpt-4o-mini: 更快的GPT-4模型
    """)

    return saved


def render_zhipu_config(provider_config: Dict = None):
    """智谱AI配置"""
    st.write("**智谱AI GLM 配置**")

    # 获取当前值
    default_key = provider_config.get('api_key', '') if provider_config else ''
    default_model = provider_config.get('model_name', 'glm-5') if provider_config else 'glm-5'
    default_temp = provider_config.get('temperature', 0.7) if provider_config else 0.7
    default_tokens = provider_config.get('max_tokens', 4000) if provider_config else 4000

    model_options = ["glm-5", "glm-4", "glm-4-flash", "glm-3-turbo", "glm-4-air", "glm-4-long"]
    default_model_idx = model_options.index(default_model) if default_model in model_options else 0

    api_key = st.text_input(
        "API密钥 *",
        type="password",
        value=default_key,
        help="智谱AI API Key"
    )

    model_name = st.selectbox(
        "模型名称",
        model_options,
        index=default_model_idx
    )

    temperature = st.slider(
        "Temperature",
        0.0, 2.0, default_temp, 0.1
    )

    max_tokens = st.number_input(
        "最大Token数",
        1000, 8000, default_tokens, 100
    )

    # 保存按钮
    saved = False
    if st.button("💾 保存智谱AI 配置", type="primary"):
        if not api_key:
            render_error_message("请输入API密钥")
        else:
            from db.session_manager import SessionManager
            session_mgr = SessionManager(db_path="data/data_analysis.db")
            session_mgr.save_api_config(
                provider="zhipu",
                api_key=api_key,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
            # 设置为激活
            session_mgr.set_active_api_config("zhipu")
            saved = True

    st.info("""
    💡 **提示**：
    - 智谱AI官网: https://open.bigmodel.cn/
    - API文档: https://open.bigmodel.cn/dev/api
    - glm-5: 最新的GLM模型
    - glm-4-flash: 快速响应模型
    """)

    return saved


def render_anthropic_config(provider_config: Dict = None):
    """Anthropic配置"""
    st.write("**Anthropic Claude 配置**")

    # 获取当前值
    default_key = provider_config.get('api_key', '') if provider_config else ''
    default_model = provider_config.get('model_name', 'claude-sonnet-4-20250514') if provider_config else 'claude-sonnet-4-20250514'
    default_temp = provider_config.get('temperature', 0.7) if provider_config else 0.7
    default_tokens = provider_config.get('max_tokens', 4000) if provider_config else 4000

    model_options = ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]
    default_model_idx = model_options.index(default_model) if default_model in model_options else 0

    api_key = st.text_input(
        "API密钥 *",
        type="password",
        value=default_key,
        help="Anthropic API Key"
    )

    model_name = st.selectbox(
        "模型名称",
        model_options,
        index=default_model_idx
    )

    temperature = st.slider(
        "Temperature",
        0.0, 2.0, default_temp, 0.1
    )

    max_tokens = st.number_input(
        "最大Token数",
        1000, 8000, default_tokens, 100
    )

    # 保存按钮
    saved = False
    if st.button("💾 保存 Anthropic 配置", type="primary"):
        if not api_key:
            render_error_message("请输入API密钥")
        else:
            from db.session_manager import SessionManager
            session_mgr = SessionManager(db_path="data/data_analysis.db")
            session_mgr.save_api_config(
                provider="anthropic",
                api_key=api_key,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
            # 设置为激活
            session_mgr.set_active_api_config("anthropic")
            saved = True

    st.info("""
    💡 **提示**：
    - Anthropic官网: https://console.anthropic.com/
    - Claude Sonnet 4: 最新的Claude模型
    - Claude Haiku: 快速、低成本模型
    """)

    return saved


def render_risk_thresholds():
    """风险阈值配置"""
    st.subheader("⚠️ 风险预警阈值")

    st.write("**统计异常检测阈值 (标准差倍数)**")

    col1, col2, col3 = st.columns(3)

    with col1:
        high_risk = st.number_input(
            "高风险阈值 (Sigma)",
            1.0, 5.0, 3.0, 0.1,
            help="3倍标准差外视为高风险"
        )

    with col2:
        medium_risk = st.number_input(
            "中风险阈值 (Sigma)",
            1.0, 5.0, 2.0, 0.1,
            help="2倍标准差外视为中风险"
        )

    with col3:
        low_risk = st.number_input(
            "低风险阈值 (Sigma)",
            1.0, 5.0, 1.5, 0.1,
            help="1.5倍标准差外视为低风险"
        )

    st.write("**数据质量阈值**")

    col1, col2 = st.columns(2)

    with col1:
        max_missing_ratio = st.slider(
            "最大缺失值比例",
            0.0, 1.0, 0.3, 0.05,
            help="缺失值比例超过此值将发出警告"
        )

    with col2:
        min_data_points = st.number_input(
            "最小数据点数",
            1, 100, 10, 1,
            help="最少需要的数据点数"
        )

    st.write("**趋势检测阈值**")

    trend_change_threshold = st.slider(
        "趋势变化阈值",
        0.0, 1.0, 0.2, 0.05,
        help="趋势变化超过此比例将触发告警"
    )

    if st.button("💾 保存阈值", type="primary"):
        # 保存到session_state（实际应保存到数据库或配置文件）
        st.session_state['risk_thresholds'] = {
            'high_risk': high_risk,
            'medium_risk': medium_risk,
            'low_risk': low_risk,
            'max_missing_ratio': max_missing_ratio,
            'min_data_points': min_data_points,
            'trend_change_threshold': trend_change_threshold
        }
        render_success_message("风险阈值已保存！")


def render_data_management(session_manager):
    """数据管理"""
    st.subheader("📊 数据管理")

    # 统计信息
    datasets = session_manager.list_datasets()
    analyses = session_manager.list_analyses()
    reports = session_manager.list_reports()
    chats = session_manager.get_chat_history()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("数据集数量", len(datasets))
    with col2:
        st.metric("分析结果", len(analyses))
    with col3:
        st.metric("生成报告", len(reports))
    with col4:
        st.metric("聊天记录", len(chats))

    # 数据集列表
    st.write("#### 数据集列表")

    if not datasets:
        st.info("暂无数据集")
    else:
        for ds in datasets:
            with st.expander(f"📁 {ds['name']} ({ds['rows']:,} 行)"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**上传时间**: {ds['upload_time'][:10] if ds['upload_time'] else 'N/A'}")
                    st.write(f"**文件大小**: {ds.get('size_mb', 0):.2f} MB")
                with col2:
                    st.write(f"**列数**: {ds['columns']}")
                    st.write(f"**状态**: {'✅ 激活' if ds['is_active'] else '⚪ 未激活'}")

                if st.button("删除此数据集", key=f"delete_{ds['id']}", type="secondary"):
                    session_manager.delete_dataset(ds['id'])
                    render_success_message("数据集已删除！")
                    st.rerun()

    # 清理数据按钮
    st.write("#### 数据清理")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🗑️ 清空所有聊天记录", key="clear_chats", type="secondary"):
            count = session_manager.clear_chat_history()
            render_success_message(f"已清空 {count} 条聊天记录！")
            st.rerun()

    with col2:
        if st.button("🗑️ 清空所有报告", key="clear_reports", type="secondary"):
            # 需要实现删除报告的方法
            render_success_message("报告清理功能开发中...")

    with col3:
        if st.button("🗑️ 清空所有分析结果", key="clear_analyses", type="secondary"):
            # 需要实现删除分析结果的方法
            render_success_message("分析结果清理功能开发中...")


def render_ui_settings():
    """界面设置"""
    st.subheader("🎨 界面设置")

    st.write("**显示设置**")

    show_advanced_options = st.checkbox(
        "显示高级选项",
        value=False,
        help="是否显示更多配置选项"
    )

    auto_refresh = st.checkbox(
        "自动刷新",
        value=True,
        help="任务执行时自动刷新页面"
    )

    refresh_interval = st.number_input(
        "刷新间隔 (秒)",
        0.1, 5.0, 0.5, 0.1,
        help="自动刷新的时间间隔"
    )

    st.write("**性能设置**")

    max_preview_rows = st.number_input(
        "数据预览最大行数",
        5, 50, 10, 1,
        help="数据预览时显示的最大行数"
    )

    use_cache = st.checkbox(
        "启用缓存",
        value=True,
        help="缓存分析结果以提高性能"
    )

    st.write("**主题设置**")

    theme_mode = st.selectbox(
        "主题模式",
        ["自动", "浅色", "深色"],
        index=0
    )

    if st.button("💾 保存设置", type="primary"):
        st.session_state['ui_settings'] = {
            'show_advanced_options': show_advanced_options,
            'auto_refresh': auto_refresh,
            'refresh_interval': refresh_interval,
            'max_preview_rows': max_preview_rows,
            'use_cache': use_cache,
            'theme_mode': theme_mode
        }
        render_success_message("界面设置已保存！")
