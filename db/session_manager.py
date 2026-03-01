"""
会话状态管理器

负责数据持久化和加载，管理应用状态
"""
from sqlalchemy import create_engine, Session
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Dict, Any
from pathlib import Path
import json

from .models import (
    Base, Dataset, Analysis, Report, ChatHistory, Task, Preference
)
import pandas as pd


class SessionManager:
    """会话状态管理器 - 负责持久化和加载"""

    def __init__(self, db_path: str = "data/data_analysis.db"):
        """初始化会话管理器

        Args:
            db_path: 数据库文件路径
        """
        # 确保数据目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # 创建数据库引擎
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,
            connect_args={"check_same_thread": False}  # 允许多线程访问
        )

        # 创建所有表
        Base.metadata.create_all(self.engine)

        # 创建会话工厂
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.Session()

    # ============ Dataset 操作 ============

    def save_dataset(
        self,
        file_path: str,
        name: str,
        df: pd.DataFrame,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """保存数据集元数据

        Args:
            file_path: 文件路径
            name: 数据集名称
            df: 数据框
            metadata: 额外元数据

        Returns:
            数据集ID
        """
        session = self.get_session()
        try:
            # 如果有激活的dataset，先取消激活状态
            session.query(Dataset).update({'is_active': False})

            # 计算文件大小
            file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)

            # 创建数据集记录
            dataset = Dataset(
                name=name,
                file_path=file_path,
                rows=len(df),
                columns=len(df.columns),
                column_names=list(df.columns),
                size_mb=file_size_mb,
                is_active=True,
                metadata=metadata or {}
            )
            session.add(dataset)
            session.commit()
            session.refresh(dataset)

            return dataset.id
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"保存数据集失败: {str(e)}")
        finally:
            session.close()

    def get_active_dataset(self) -> Optional[Dict[str, Any]]:
        """获取当前激活的数据集

        Returns:
            数据集字典，如果没有则返回None
        """
        session = self.get_session()
        try:
            dataset = session.query(Dataset).filter_by(is_active=True).first()
            return dataset.to_dict() if dataset else None
        finally:
            session.close()

    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取数据集

        Args:
            dataset_id: 数据集ID

        Returns:
            数据集字典，如果没有则返回None
        """
        session = self.get_session()
        try:
            dataset = session.query(Dataset).filter_by(id=dataset_id).first()
            return dataset.to_dict() if dataset else None
        finally:
            session.close()

    def list_datasets(self, limit: int = 50) -> List[Dict[str, Any]]:
        """列出所有数据集

        Args:
            limit: 最大返回数量

        Returns:
            数据集列表
        """
        session = self.get_session()
        try:
            datasets = session.query(Dataset).order_by(
                Dataset.upload_time.desc()
            ).limit(limit).all()
            return [d.to_dict() for d in datasets]
        finally:
            session.close()

    def set_active_dataset(self, dataset_id: str) -> bool:
        """设置当前激活的数据集

        Args:
            dataset_id: 数据集ID

        Returns:
            是否成功
        """
        session = self.get_session()
        try:
            # 取消所有激活状态
            session.query(Dataset).update({'is_active': False})

            # 激活指定数据集
            dataset = session.query(Dataset).filter_by(id=dataset_id).first()
            if dataset:
                dataset.is_active = True
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"设置激活数据集失败: {str(e)}")
        finally:
            session.close()

    def delete_dataset(self, dataset_id: str) -> bool:
        """删除数据集

        Args:
            dataset_id: 数据集ID

        Returns:
            是否成功
        """
        session = self.get_session()
        try:
            dataset = session.query(Dataset).filter_by(id=dataset_id).first()
            if dataset:
                # 删除文件
                try:
                    Path(dataset.file_path).unlink(missing_ok=True)
                except Exception:
                    pass  # 文件删除失败不影响数据库删除

                # 删除相关的分析结果和报告
                session.query(Analysis).filter_by(dataset_id=dataset_id).delete()
                session.query(Report).filter_by(dataset_id=dataset_id).delete()

                # 删除数据集
                session.delete(dataset)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"删除数据集失败: {str(e)}")
        finally:
            session.close()

    # ============ Analysis 操作 ============

    def save_analysis(
        self,
        dataset_id: str,
        analysis_type: str,
        result: Dict[str, Any],
        status: str = 'completed'
    ) -> str:
        """保存分析结果

        Args:
            dataset_id: 数据集ID
            analysis_type: 分析类型
            result: 分析结果
            status: 状态

        Returns:
            分析ID
        """
        session = self.get_session()
        try:
            analysis = Analysis(
                dataset_id=dataset_id,
                analysis_type=analysis_type,
                result=result,
                status=status
            )
            session.add(analysis)
            session.commit()
            session.refresh(analysis)

            return analysis.id
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"保存分析结果失败: {str(e)}")
        finally:
            session.close()

    def get_analysis(
        self,
        dataset_id: str,
        analysis_type: str
    ) -> Optional[Dict[str, Any]]:
        """获取分析结果

        Args:
            dataset_id: 数据集ID
            analysis_type: 分析类型

        Returns:
            分析结果，如果没有则返回None
        """
        session = self.get_session()
        try:
            analysis = session.query(Analysis).filter_by(
                dataset_id=dataset_id,
                analysis_type=analysis_type
            ).order_by(Analysis.created_at.desc()).first()
            return analysis.to_dict() if analysis else None
        finally:
            session.close()

    def list_analyses(
        self,
        dataset_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """列出分析结果

        Args:
            dataset_id: 数据集ID（可选）
            limit: 最大返回数量

        Returns:
            分析结果列表
        """
        session = self.get_session()
        try:
            query = session.query(Analysis)
            if dataset_id:
                query = query.filter_by(dataset_id=dataset_id)

            analyses = query.order_by(
                Analysis.created_at.desc()
            ).limit(limit).all()

            return [a.to_dict() for a in analyses]
        finally:
            session.close()

    # ============ Report 操作 ============

    def save_report(
        self,
        dataset_id: str,
        title: str,
        content: str
    ) -> str:
        """保存报告

        Args:
            dataset_id: 数据集ID
            title: 报告标题
            content: 报告内容（Markdown）

        Returns:
            报告ID
        """
        session = self.get_session()
        try:
            report = Report(
                dataset_id=dataset_id,
                title=title,
                content=content
            )
            session.add(report)
            session.commit()
            session.refresh(report)

            return report.id
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"保存报告失败: {str(e)}")
        finally:
            session.close()

    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """获取报告

        Args:
            report_id: 报告ID

        Returns:
            报告字典，如果没有则返回None
        """
        session = self.get_session()
        try:
            report = session.query(Report).filter_by(id=report_id).first()
            return report.to_dict() if report else None
        finally:
            session.close()

    def list_reports(
        self,
        dataset_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """列出报告

        Args:
            dataset_id: 数据集ID（可选）
            limit: 最大返回数量

        Returns:
            报告列表
        """
        session = self.get_session()
        try:
            query = session.query(Report)
            if dataset_id:
                query = query.filter_by(dataset_id=dataset_id)

            reports = query.order_by(
                Report.created_at.desc()
            ).limit(limit).all()

            return [r.to_dict() for r in reports]
        finally:
            session.close()

    # ============ Chat History 操作 ============

    def save_chat(
        self,
        question: str,
        answer: str,
        session_id: Optional[str] = None
    ) -> str:
        """保存聊天记录

        Args:
            question: 问题
            answer: 回答
            session_id: 会话ID（可选）

        Returns:
            聊天记录ID
        """
        session = self.get_session()
        try:
            chat = ChatHistory(
                question=question,
                answer=answer,
                session_id=session_id
            )
            session.add(chat)
            session.commit()
            session.refresh(chat)

            return chat.id
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"保存聊天记录失败: {str(e)}")
        finally:
            session.close()

    def get_chat_history(
        self,
        limit: int = 50,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取聊天记录

        Args:
            limit: 最大返回数量
            session_id: 会话ID（可选）

        Returns:
            聊天记录列表
        """
        session = self.get_session()
        try:
            query = session.query(ChatHistory)
            if session_id:
                query = query.filter_by(session_id=session_id)

            chats = query.order_by(
                ChatHistory.created_at.desc()
            ).limit(limit).all()

            return [c.to_dict() for c in chats]
        finally:
            session.close()

    def clear_chat_history(self, session_id: Optional[str] = None) -> int:
        """清空聊天记录

        Args:
            session_id: 会话ID（可选），为None时清空所有

        Returns:
            删除的记录数
        """
        session = self.get_session()
        try:
            query = session.query(ChatHistory)
            if session_id:
                query = query.filter_by(session_id=session_id)

            count = query.count()
            query.delete()
            session.commit()

            return count
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"清空聊天记录失败: {str(e)}")
        finally:
            session.close()

    # ============ Preference 操作 ============

    def save_preference(self, key: str, value: Any) -> None:
        """保存偏好设置

        Args:
            key: 键
            value: 值（会被序列化为JSON）
        """
        session = self.get_session()
        try:
            # 查找是否已存在
            pref = session.query(Preference).filter_by(key=key).first()
            if pref:
                pref.value = value
            else:
                pref = Preference(key=key, value=value)
                session.add(pref)

            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"保存偏好设置失败: {str(e)}")
        finally:
            session.close()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """获取偏好设置

        Args:
            key: 键
            default: 默认值

        Returns:
            值，如果不存在则返回默认值
        """
        session = self.get_session()
        try:
            pref = session.query(Preference).filter_by(key=key).first()
            return pref.value if pref else default
        finally:
            session.close()

    def get_all_preferences(self) -> Dict[str, Any]:
        """获取所有偏好设置

        Returns:
            偏好设置字典
        """
        session = self.get_session()
        try:
            prefs = session.query(Preference).all()
            return {p.key: p.value for p in prefs}
        finally:
            session.close()
