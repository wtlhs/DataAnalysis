"""
数据分析智能体 - Streamlit主应用（重构版）

支持路由系统、前后台分离、管理员登录
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import parse_qs

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from db.session_manager import SessionManager
from db.task_manager import TaskManager
from ui.frontend import render_frontend_page
from ui.backend import render_backend_page
from ui.components import (
    load_custom_css,
    is_admin_logged_in,
    render_login_page,
    render_admin_header,
    render_logout_button
)

# ============ 页面配置 ============

# 设置页面
st.set_page_config(
    page_title="数据分析智能体",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============ 路由系统 ============

def get_page_mode():
    """从URL参数获取页面模式

    Returns:
        'frontend', 'admin', 或 'login'
    """
    # 获取查询参数
    query_params = st.query_params

    # 检查模式参数
    mode = query_params.get('mode', ['frontend'])[0]

    # 检查 session_state 中的模式（优先级更高）
    if 'mode' in st.session_state:
        mode = st.session_state['mode']

    return mode


def init_session_state():
    """初始化session_state"""
    if 'admin_logged_in' not in st.session_state:
        st.session_state['admin_logged_in'] = False

    if 'login_time' not in st.session_state:
        st.session_state['login_time'] = None

    if 'mode' not in st.session_state:
        st.session_state['mode'] = get_page_mode()


# ============ 全局状态管理 ============

@st.cache_resource
def get_session_manager():
    """获取会话管理器（单例）"""
    return SessionManager(db_path="data/data_analysis.db")


@st.cache_resource
def get_task_manager():
    """获取任务管理器（单例）"""
    session_manager = get_session_manager()
    return TaskManager(session_manager)


# ============ 主应用逻辑 ============

def main():
    """主函数"""
    # 初始化session_state
    init_session_state()

    # 加载自定义CSS
    load_custom_css()

    # 获取当前模式
    mode = get_page_mode()

    # 根据模式渲染不同的页面
    if mode == 'admin':
        # 检查是否需要登录
        needs_login = not is_admin_logged_in()

        if needs_login:
            # 未登录，只显示登录页面
            render_login_page()
            return  # 不显示页脚
        else:
            # 已登录，显示后台管理页面
            render_admin_header()
            render_logout_button()

            st.markdown('<div class="admin-content">', unsafe_allow_html=True)

            session_manager = get_session_manager()
            task_manager = get_task_manager()
            render_backend_page(session_manager)

            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # 前台操作页面
        session_manager = get_session_manager()
        task_manager = get_task_manager()
        render_frontend_page(session_manager, task_manager)

        # 前台和后台都显示页脚
        st.markdown("""
        <div class="page-footer">
            <div class="footer-content">
                <div class="footer-left">
                    <span class="footer-text">© 2026 数据分析智能体</span>
                </div>
                <div class="footer-right">
                    <span class="footer-text">v2.0</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
