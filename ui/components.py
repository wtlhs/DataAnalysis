"""
可复用UI组件

提供Streamlit的通用UI组件
"""
import streamlit as st
import time
from typing import Optional, List, Dict, Any, Callable
import pandas as pd
from pathlib import Path


def load_custom_css():
    """加载自定义CSS样式"""
    st.markdown("""
    <style>
    /* 全局样式 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    [data-testid="stAppViewContainer"] {
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 20px;
        padding: 20px;
    }

    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }

    [data-testid="stSidebar"] [role="img"] {
        filter: brightness(0) invert(1);
    }

    /* 卡片样式 */
    .custom-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: white;
    }

    /* 按钮样式 */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }

    /* 指标卡片 */
    [data-testid="stMetricDelta"] {
        color: #48bb78 !important;
    }

    /* 进度条 */
    .stProgress .progress-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }

    /* 成功/错误消息样式 */
    .success-message {
        background-color: #c6f6d5;
        color: #22543d;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #48bb78;
    }

    .error-message {
        background-color: #fed7d7;
        color: #822727;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #e53e3e;
    }

    .warning-message {
        background-color: #feebc8;
        color: #744210;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #dd6b20;
    }

    /* expander样式 */
    [data-testid="stExpander"] {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        margin: 10px 0;
    }

    /* tabs样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f7fafc;
        border-radius: 8px 8px 0 0;
        padding: 0 20px;
    }
    </style>
    """, unsafe_allow_html=True)


def render_multi_file_upload(label: str = "上传多个Excel文件") -> List:
    """渲染多文件上传组件

    Args:
        label: 上传标签

    Returns:
        上传的文件列表
    """
    uploaded_files = st.file_uploader(
        label=label,
        type=['xlsx', 'xls', 'csv'],
        accept_multiple_files=True,
        key='multi_upload'
    )
    return uploaded_files if uploaded_files else []


def render_dataset_list(datasets: List[Dict[str, Any]], session_manager=None):
    """渲染数据集列表

    Args:
        datasets: 数据集列表
        session_manager: 会话管理器

    Returns:
        选中的数据集ID
    """
    if not datasets:
        st.info("暂无上传的数据集")
        return None

    st.subheader("📊 数据集列表")

    selected_id = None

    for ds in datasets:
        with st.expander(
            f"📁 {ds['name']} ({ds['rows']:,} 行 × {ds['columns']} 列)"
        ):
            cols = st.columns([3, 1, 1, 1])

            with cols[0]:
                st.write(f"上传时间: {ds['upload_time'][:10] if ds['upload_time'] else 'N/A'}")
                st.write(f"文件大小: {ds.get('size_mb', 0):.2f} MB")
                if ds.get('is_active'):
                    st.success("✅ 当前选中")

            with cols[1]:
                if not ds.get('is_active') and session_manager:
                    if st.button("设为当前", key=f"select_{ds['id']}", use_container_width=True):
                        session_manager.set_active_dataset(ds['id'])
                        st.rerun()

            with cols[2]:
                if session_manager:
                    if st.button("删除", key=f"delete_{ds['id']}", type="secondary", use_container_width=True):
                        session_manager.delete_dataset(ds['id'])
                        st.rerun()

            with cols[3]:
                if st.button("查看", key=f"view_{ds['id']}", use_container_width=True):
                    selected_id = ds['id']

    return selected_id


def render_progress_indicator(
    task_id: str,
    task_manager,
    auto_refresh: bool = True,
    refresh_interval: int = 500
) -> Optional[Dict[str, Any]]:
    """渲染异步任务进度指示器

    Args:
        task_id: 任务ID
        task_manager: 任务管理器
        auto_refresh: 是否自动刷新
        refresh_interval: 刷新间隔（毫秒）

    Returns:
        任务结果，如果任务完成则返回结果，否则返回None
    """
    status = task_manager.get_task_status(task_id)

    if not status:
        st.error("任务不存在")
        return None

    # 根据状态显示不同的UI
    if status['status'] == 'pending':
        st.info("⏳ 任务等待中...")
        if auto_refresh:
            time.sleep(0.5)
            st.rerun()

    elif status['status'] == 'running':
        progress_bar = st.progress(status['progress'] / 100)
        st.write(f"处理中... {status['progress']}%")
        if auto_refresh:
            time.sleep(refresh_interval / 1000)
            st.rerun()

    elif status['status'] == 'completed':
        st.success("✅ 处理完成！")
        progress_bar = st.progress(1.0)
        return status.get('result')

    elif status['status'] == 'failed':
        st.error(f"❌ 处理失败: {status.get('error', '未知错误')}")
        return None

    elif status['status'] == 'cancelled':
        st.warning("⚠️ 任务已取消")
        return None

    return None


def render_metric_card(title: str, value, delta=None, delta_color="normal"):
    """渲染美化指标卡片

    Args:
        title: 标题
        value: 值
        delta: 变化值
        delta_color: 颜色
    """
    st.metric(title, value, delta, delta_color=delta_color)


def render_info_card(title: str, content: str, icon: str = "ℹ️"):
    """渲染信息卡片

    Args:
        title: 标题
        content: 内容
        icon: 图标
    """
    st.markdown(f"""
    <div class="custom-card">
        <h2>{icon} {title}</h2>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)


def render_task_history(tasks: List[Dict[str, Any]], limit: int = 10):
    """渲染任务历史

    Args:
        tasks: 任务列表
        limit: 显示数量
    """
    if not tasks:
        return

    st.subheader("📋 任务历史")

    for task in tasks[:limit]:
        status_emoji = {
            'pending': '⏳',
            'running': '🔄',
            'completed': '✅',
            'failed': '❌',
            'cancelled': '⚠️'
        }.get(task['status'], '❓')

        with st.expander(f"{status_emoji} {task['task_type']} - {task['status']}"):
            cols = st.columns([2, 1, 1])

            with cols[0]:
                st.write(f"**任务ID**: {task['id'][:8]}...")
            with cols[1]:
                st.write(f"**状态**: {task['status']}")
            with cols[2]:
                st.write(f"**进度**: {task['progress']}%")

            if task.get('created_at'):
                st.write(f"**创建时间**: {task['created_at'][:19] if task['created_at'] else 'N/A'}")

            if task.get('error'):
                st.error(f"错误: {task['error']}")


def render_chat_history(chats: List[Dict[str, Any]], limit: int = 10):
    """渲染聊天历史

    Args:
        chats: 聊天记录列表
        limit: 显示数量
    """
    if not chats:
        return

    st.subheader("💬 对话历史")

    for i, chat in enumerate(reversed(chats[:limit]), 1):
        with st.chat_message("user"):
            st.write(chat['question'])

        with st.chat_message("assistant"):
            st.write(chat['answer'])

        st.divider()


def render_report_list(reports: List[Dict[str, Any]], session_manager=None):
    """渲染报告列表

    Args:
        reports: 报告列表
        session_manager: 会话管理器
    """
    if not reports:
        st.info("暂无生成的报告")
        return None

    st.subheader("📝 报告列表")

    for report in reports:
        with st.expander(f"📄 {report['title']} - {report['created_at'][:10]}"):
            st.write(f"**报告ID**: {report['id']}")
            st.write(f"**创建时间**: {report['created_at'][:19]}")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("查看", key=f"view_report_{report['id']}", use_container_width=True):
                    st.session_state['viewing_report_id'] = report['id']
                    st.rerun()

            with col2:
                if report.get('content'):
                    st.download_button(
                        label="下载",
                        data=report['content'],
                        file_name=f"{report['title']}.md",
                        mime="text/markdown",
                        key=f"download_report_{report['id']}",
                        use_container_width=True
                    )


def render_data_preview(df: pd.DataFrame, max_rows: int = 10):
    """渲染数据预览

    Args:
        df: 数据框
        max_rows: 最大显示行数
    """
    if df is None or df.empty:
        st.info("暂无数据")
        return

    # 数据概览
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("数据行数", f"{len(df):,}")
    with col2:
        st.metric("数据列数", len(df.columns))
    with col3:
        st.metric("数据大小", f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

    # 数据预览
    st.subheader("📋 数据预览")
    st.dataframe(df.head(max_rows), use_container_width=True)

    # 列信息
    st.subheader("📊 列信息")
    col_info = pd.DataFrame({
        '列名': df.columns,
        '数据类型': df.dtypes.astype(str).values,
        '非空值': df.count().values,
        '缺失值': df.isnull().sum().values,
        '缺失比例': (df.isnull().sum() / len(df) * 100).round(2)
    })
    st.dataframe(col_info, use_container_width=True)


def render_responsive_layout(num_items: int) -> List:
    """响应式布局组件

    Args:
        num_items: 项目数量

    Returns:
        Streamlit columns列表
    """
    # 根据屏幕宽度调整列数
    screen_width = st.session_state.get('screen_width', 1200)

    if screen_width < 768:
        # 小屏幕：单列
        return [st.container()] * num_items
    elif screen_width < 1024:
        # 中等屏幕：两列
        cols_per_row = 2
    else:
        # 大屏幕：三列
        cols_per_row = 3

    # 创建列
    columns = []
    for _ in range((num_items + cols_per_row - 1) // cols_per_row):
        columns.extend(st.columns(cols_per_row))

    return columns[:num_items]


def render_error_message(message: str):
    """渲染错误消息

    Args:
        message: 错误消息
    """
    st.markdown(f"""
    <div class="error-message">
        <strong>错误</strong>
        <p>{message}</p>
    </div>
    """, unsafe_allow_html=True)


def render_success_message(message: str):
    """渲染成功消息

    Args:
        message: 成功消息
    """
    st.markdown(f"""
    <div class="success-message">
        <strong>成功</strong>
        <p>{message}</p>
    </div>
    """, unsafe_allow_html=True)


def render_warning_message(message: str):
    """渲染警告消息

    Args:
        message: 警告消息
    """
    st.markdown(f"""
    <div class="warning-message">
        <strong>警告</strong>
        <p>{message}</p>
    </div>
    """, unsafe_allow_html=True)
