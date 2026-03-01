"""
可复用UI组件

提供Streamlit的通用UI组件
"""
import streamlit as st
import time
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable
import pandas as pd
from pathlib import Path


def load_custom_css():
    """加载自定义CSS样式"""
    from pathlib import Path

    # 加载 Supabase 风格 CSS 文件
    css_path = Path(__file__).parent / "supabase-design.css"
    if css_path.exists():
        with open(css_path, 'r', encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


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


def render_warning_message(message: str):
    """渲染警告消息"""
    st.markdown(f"""
    <div class="supabase-alert supabase-alert-warning">
        <div class="supabase-alert-icon">⚠️</div>
        <div class="supabase-alert-content">
            <p>{message}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_success_message(message: str):
    """渲染成功消息"""
    st.markdown(f"""
    <div class="supabase-alert supabase-alert-success">
        <div class="supabase-alert-icon">✅</div>
        <div class="supabase-alert-content">
            <p>{message}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============ Supabase 风格组件 ============

def supabase_card(title: str, icon: str, content: str = "", footer: str = ""):
    """渲染 Supabase 风格卡片

    Args:
        title: 卡片标题
        icon: 图标emoji
        content: 卡片内容
        footer: 底部信息
    """
    st.markdown(f"""
    <div class="supabase-card">
        <div class="supabase-card-content">
            <div class="supabase-card-header">
                <span class="supabase-card-icon">{icon}</span>
                <h3 class="supabase-card-title">{title}</h3>
            </div>
            <div class="supabase-card-body">
                {content}
            </div>
            {footer}
        </div>
    </div>
    """, unsafe_allow_html=True)


def supabase_button(
    label: str,
    icon: str = "",
    variant: str = "primary",
    on_click = None,
    disabled: bool = False,
    use_container_width: bool = False
):
    """渲染 Supabase 风格按钮

    Args:
        label: 按钮文字
        icon: 图标emoji
        variant: 'primary', 'secondary', 'ghost', 'destructive'
        on_click: 点击回调函数
        disabled: 是否禁用
        use_container_width: 是否使用全宽
    """
    button_class = f"supabase-button supabase-button-{variant}"

    # 构建属性
    kwargs = {}
    if icon:
        kwargs['icon'] = icon
    if disabled:
        kwargs['disabled'] = True
    if use_container_width:
        kwargs['use_container_width'] = True

    if variant == "primary":
        kwargs['type'] = "primary"
    elif variant == "secondary":
        kwargs['type'] = "secondary"
    elif variant == "ghost":
        kwargs['type'] = "default"

    # 额外的 on_click 包装
    if on_click:
        original_on_click = kwargs.get('on_click')
        def wrapped_on_click():
            if not disabled:
                original_on_click()
        kwargs['on_click'] = wrapped_on_click
        return wrapped_on_click

    st.button(label, key=kwargs, on_click=wrapped_on_click, **kwargs)

    return button_class


def supabase_input(
    label: str,
    placeholder: str = "",
    value: str = "",
    type: str = "text",
    icon: str = "",
    disabled: bool = False
) -> str:
    """渲染 Supabase 风格输入框

    Args:
        label: 标签
        placeholder: 占位符
        value: 默认值
        type: 输入类型 ('text', 'number', 'password')
        icon: 图标
        disabled: 是否禁用
    """
    input_key = kwargs = {}

    if icon:
        input_key['icon'] = icon

    if value:
        input_key['value'] = value

    if disabled:
        input_key['disabled'] = True
        input_key['help'] = placeholder

    if type == "password":
        input_key['type'] = "password"
    else:
        input_key['type'] = "default"

    if type == "number":
        return st.number_input(label, **input_key)
    else:
        return st.text_input(label, **input_key)


def supabase_tag(text: str, variant: str = "default", icon: str = "") -> str:
    """渲染 Supabase 风格标签

    Args:
        text: 标签文字
        variant: 'default', 'emerald', 'blue', 'violet', 'pink'
        icon: 图标emoji

    Returns:
        HTML 字符串
    """
    variant_classes = {
        'default': 'supabase-tag-default',
        'emerald': 'supabase-tag-emerald',
        'blue': 'supabase-tag-blue',
        'violet': 'supabase-tag-violet',
        'pink': 'supabase-tag-pink'
    }

    tag_class = f"supabase-tag {variant_classes.get(variant, 'supabase-tag-default')}"

    icon_html = f"<span class='supabase-tag-icon'>{icon}</span>" if icon else ""

    return f"""
    <span class="{tag_class}">
        {icon_html}{text}
    </span>
    """


def supabase_section_header(title: str, description: str = "", show_back: bool = False):
    """渲染 Supabase 风格分区标题

    Args:
        title: 标题
        description: 描述
        show_back: 是否显示返回按钮
    """
    back_button = ""

    if show_back:
        back_button = st.button("← 返回", key=f"back_{title}", type="secondary", use_container_width=True)

    st.markdown(f"""
    <div class="supabase-section-header">
        <div class="supabase-section-header-left">
            <h2 class="supabase-section-title">{title}</h2>
            {description}
        </div>
        {back_button}
    </div>
    """, unsafe_allow_html=True)


def supabase_metric(label: str, value: str, delta: str = "", delta_color: str = "normal", icon: str = ""):
    """渲染 Supabase 风格指标卡片

    Args:
        label: 标签
        value: 显示值
        delta: 变化值
        delta_color: 'normal', 'positive', 'negative', 'warning'
        icon: 图标emoji
    """
    color_class = f"supabase-metric-delta-{delta_color}"

    delta_html = ""
    if delta:
        if delta_color == "positive":
            delta_html = f"<span class='supabase-metric-up'>↑</span>"
        elif delta_color == "negative":
            delta_html = f"<span class='supabase-metric-down'>↓</span>"
        elif delta_color == "warning":
            delta_html = f"<span class='supabase-metric-warning'>⚠️</span>"

    icon_html = f"<span class='supabase-metric-icon'>{icon}</span>" if icon else ""

    st.markdown(f"""
    <div class="supabase-metric {color_class}">
        <div class="supabase-metric-header">
            <span class="supabase-metric-label">{label}</span>
            <span class="supabase-metric-value">{value}</span>
            {delta_html}
            {icon_html}
        </div>
        <p class="supabase-metric-delta">{delta}</p>
    </div>
    """, unsafe_allow_html=True)


def supabase_stat_grid(items: list, cols: int = 4, icon_map: dict = None):
    """渲染 Supabase 风格统计数据网格

    Args:
        items: 项目列表
        cols: 列数
        icon_map: 图标映射字典 {label: icon}
    """
    if not items:
        return ""

    rows = []
    for i in range(0, len(items), cols):
        row_items = items[i * cols:(i+1)]
        rows.append(row_items)

    for row in rows:
        cols = st.columns(cols)
        for idx, item in enumerate(row_items):
            label = item.get('label', str(idx + 1))
            value = item.get('value', '')
            icon = icon_map.get(label, '') if icon_map else '📊'

            cols[idx].metric(label=label, value=f"{value:,}", delta_color='normal', icon=icon)


def supabase_table(headers: list, data: list, max_rows: int = 10):
    """渲染 Supabase 风格表格

    Args:
        headers: 表头列表
        data: 数据列表
        max_rows: 最大显示行数
    """
    if not headers or not data:
        return

    # 处理表头
    header_html = ""
    for header in headers:
        header_html += f"<th class='supabase-table-head'>{header}</th>"

    # 处理数据行
    rows_html = ""
    for row in data[:max_rows]:
        row_html = "<tr>"
        for value in row:
            row_html += f"<td class='supabase-table-cell'>{value}</td>"
        row_html += "</tr>"
        rows_html += row_html

    # 构建完整HTML
    table_html = f"""
    <div class="supabase-table-container">
        <div class="supabase-table">
            <table>
                <thead>
                    <tr>
                        {header_html}
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)


# ============ 登录和认证相关组件 ============

def render_login_page() -> bool:
    """渲染登录页面

    Returns:
        是否登录成功
    """
    st.markdown("""
    <div class="login-container">
        <div class="login-card">
            <h1 class="login-title">🔐 系统管理</h1>
            <p class="login-subtitle">请输入管理员密码以访问后台管理功能</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 登录表单
    password = st.text_input(
        "管理员密码",
        type="password",
        placeholder="请输入密码...",
        help="默认密码: admin123"
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("登录", type="primary", use_container_width=True):
            if check_password(password):
                st.session_state['admin_logged_in'] = True
                st.session_state['login_time'] = datetime.now().isoformat()
                render_success_message("登录成功！正在跳转...")
                st.rerun()
            else:
                render_error_message("密码错误，请重试")

    with col2:
        if st.button("返回前台", use_container_width=True):
            st.session_state['mode'] = 'frontend'
            st.rerun()

    return st.session_state.get('admin_logged_in', False)


def check_password(password: str) -> bool:
    """验证密码

    Args:
        password: 输入的密码

    Returns:
        密码是否正确
    """
    # 从数据库或环境变量获取密码
    import os
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    return password == admin_password


def is_admin_logged_in() -> bool:
    """检查是否已登录

    Returns:
        是否已登录管理员
    """
    return st.session_state.get('admin_logged_in', False)


def require_admin_login():
    """要求管理员登录，如果未登录则显示登录页面"""
    if not is_admin_logged_in():
        render_login_page()
        return True
    return False


def render_admin_header():
    """渲染后台管理页面头部"""
    st.markdown("""
    <div class="admin-header">
        <div class="admin-header-left">
            <h1>⚙️ 系统管理</h1>
            <p>管理模型配置、数据、系统设置</p>
        </div>
        <div class="admin-header-right">
            <span class="admin-badge">管理员模式</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_logout_button():
    """渲染登出按钮"""
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("🏠 返回前台", key="return_frontend", use_container_width=True):
            st.session_state['mode'] = 'frontend'
            st.rerun()

    with col2:
        if st.button("🔄 刷新", key="admin_refresh", use_container_width=True):
            st.rerun()

    with col3:
        if st.button("🚪 登出", key="admin_logout", type="secondary", use_container_width=True):
            st.session_state['admin_logged_in'] = False
            del st.session_state['login_time']
            render_success_message("已登出")
            st.rerun()
