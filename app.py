"""
数据分析智能体 - Streamlit主应用

用户上传Excel文件，进行数据分析、预测、风险预警
支持数据持久化、多表格管理、异步任务处理
"""
import streamlit as st
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 页面配置
st.set_page_config(
    page_title="数据分析智能体",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

from db.session_manager import SessionManager
from db.task_manager import TaskManager
from ui.frontend import render_frontend_page
from ui.backend import render_backend_page


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


# 初始化管理器
session_manager = get_session_manager()
task_manager = get_task_manager()


def render_sidebar():
    """渲染侧边栏"""
    # 模式切换
    mode = st.sidebar.radio(
        "工作模式",
        ["👤 前台操作", "🔧 后台管理"],
        label_visibility="collapsed"
    )

    # 模式说明
    if mode == "👤 前台操作":
        st.sidebar.info("""
        **前台操作模式**

        - 📁 数据上传与预览
        - 📈 统计分析与可视化
        - 🔮 趋势预测
        - ⚠️ 风险预警
        - 🤖 AI智能分析
        - 📝 报告生成
        """)
    else:
        st.sidebar.info("""
        **后台管理模式**

        - 🤖 模型参数配置
        - ⚠️ 风险阈值设置
        - 📊 数据管理与清理
        - 🎨 界面设置
        """)

    # 系统信息
    st.sidebar.divider()

    st.sidebar.write("#### 系统信息")

    # 获取统计信息
    datasets = session_manager.list_datasets(limit=1000)
    tasks = task_manager.list_tasks(limit=1000)

    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("数据集", len(datasets))
    with col2:
        st.metric("任务", len(tasks))

    # 清理旧任务按钮
    if st.sidebar.button("🧹 清理旧任务", key="cleanup_tasks"):
        count = task_manager.cleanup_old_tasks(days=7)
        st.sidebar.success(f"已清理 {count} 个旧任务")
        st.rerun()

    return mode


def main():
    """主函数"""
    # 渲染侧边栏
    mode = render_sidebar()

    # 根据模式渲染对应页面
    if mode == "👤 前台操作":
        render_frontend_page(session_manager, task_manager)
    else:
        render_backend_page(session_manager)


if __name__ == "__main__":
    main()
