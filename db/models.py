"""
数据库模型

定义SQLite数据表结构，用于数据持久化
"""
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text, JSON,
    ForeignKey, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional
import uuid

Base = declarative_base()


class Dataset(Base):
    """上传的数据集元数据"""
    __tablename__ = 'datasets'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)  # 文件名
    file_path = Column(String, nullable=False)  # 实际文件路径
    upload_time = Column(DateTime, default=datetime.now, index=True)
    rows = Column(Integer)  # 行数
    columns = Column(Integer)  # 列数
    column_names = Column(JSON)  # 列名列表
    size_mb = Column(Float)  # 文件大小(MB)
    is_active = Column(Boolean, default=True, index=True)  # 是否当前选中
    metadata = Column(JSON, default=dict)  # 其他元数据

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'file_path': self.file_path,
            'upload_time': self.upload_time.isoformat() if self.upload_time else None,
            'rows': self.rows,
            'columns': self.columns,
            'column_names': self.column_names,
            'size_mb': self.size_mb,
            'is_active': self.is_active,
            'metadata': self.metadata or {}
        }


class Analysis(Base):
    """分析结果缓存"""
    __tablename__ = 'analyses'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey('datasets.id'), index=True)
    analysis_type = Column(String, nullable=False, index=True)  # 'statistics', 'prediction', 'risk', 'ai'
    result = Column(JSON, nullable=False)  # 分析结果（JSON格式）
    created_at = Column(DateTime, default=datetime.now, index=True)
    status = Column(String, default='completed')  # 'completed', 'failed'

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'dataset_id': self.dataset_id,
            'analysis_type': self.analysis_type,
            'result': self.result or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'status': self.status
        }


class Report(Base):
    """生成的报告"""
    __tablename__ = 'reports'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey('datasets.id'), index=True)
    title = Column(String)
    content = Column(Text, nullable=False)  # Markdown内容
    created_at = Column(DateTime, default=datetime.now, index=True)
    file_path = Column(String)  # 导出的文件路径

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'dataset_id': self.dataset_id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'file_path': self.file_path
        }


class ChatHistory(Base):
    """聊天记录"""
    __tablename__ = 'chat_history'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now, index=True)
    session_id = Column(String, index=True)  # 会话ID，用于分组

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'session_id': self.session_id
        }


class Task(Base):
    """异步任务状态"""
    __tablename__ = 'tasks'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_type = Column(String, nullable=False, index=True)  # 'ai_analysis', 'prediction', 'report'
    status = Column(String, default='pending', index=True)  # 'pending', 'running', 'completed', 'failed', 'cancelled'
    progress = Column(Integer, default=0)  # 0-100
    result = Column(JSON)  # 任务结果
    error = Column(Text)  # 错误信息
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, index=True)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'task_type': self.task_type,
            'status': self.status,
            'progress': self.progress,
            'result': self.result or {},
            'error': self.error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Preference(Base):
    """用户偏好设置"""
    __tablename__ = 'preferences'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
