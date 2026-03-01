"""
异步任务管理器

管理后台异步任务，支持进度跟踪和状态更新
"""
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Optional, Dict, Any, List
import threading
import time
from datetime import datetime

from .session_manager import SessionManager
from .models import Task as TaskModel


class TaskManager:
    """异步任务管理器"""

    def __init__(self, session_manager: SessionManager, max_workers: int = 3):
        """初始化任务管理器

        Args:
            session_manager: 会话管理器
            max_workers: 最大工作线程数
        """
        self.session_manager = session_manager
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks: Dict[str, Future] = {}
        self.lock = threading.Lock()

    def submit_task(
        self,
        task_type: str,
        func: Callable,
        *args,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        **kwargs
    ) -> str:
        """提交异步任务

        Args:
            task_type: 任务类型 ('ai_analysis', 'prediction', 'report')
            func: 要执行的函数
            *args: 函数位置参数
            progress_callback: 进度回调函数 (progress_percent, message)
            **kwargs: 函数关键字参数

        Returns:
            任务ID
        """
        # 创建任务记录
        task_id = self._create_task(task_type)

        # 包装函数以支持进度回调
        def wrapped_func():
            return self._run_task(task_id, func, *args, progress_callback=progress_callback, **kwargs)

        # 提交到线程池
        future = self.executor.submit(wrapped_func)

        # 保存Future引用
        with self.lock:
            self.active_tasks[task_id] = future

        return task_id

    def _create_task(self, task_type: str) -> str:
        """创建任务记录

        Args:
            task_type: 任务类型

        Returns:
            任务ID
        """
        session = self.session_manager.get_session()
        try:
            task = TaskModel(
                task_type=task_type,
                status='pending',
                progress=0
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            return task.id
        except Exception as e:
            session.rollback()
            raise Exception(f"创建任务失败: {str(e)}")
        finally:
            session.close()

    def _run_task(
        self,
        task_id: str,
        func: Callable,
        *args,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        **kwargs
    ) -> Any:
        """运行任务并更新状态

        Args:
            task_id: 任务ID
            func: 要执行的函数
            *args: 函数位置参数
            progress_callback: 进度回调
            **kwargs: 函数关键字参数

        Returns:
            函数执行结果
        """
        # 更新状态为 running
        self._update_task_status(task_id, 'running', progress=0)

        try:
            # 如果函数支持进度回调，传入包装函数
            if progress_callback is not None:
                # 创建包装器同时更新数据库
                def db_progress_callback(progress: int, message: str = ""):
                    progress_callback(progress, message)
                    self._update_task_status(task_id, 'running', progress=progress)

                # 检查函数是否接受 progress_callback 参数
                import inspect
                sig = inspect.signature(func)
                if 'progress_callback' in sig.parameters:
                    result = func(*args, progress_callback=db_progress_callback, **kwargs)
                else:
                    result = func(*args, **kwargs)
                    # 模拟进度更新
                    self._update_task_status(task_id, 'running', progress=50)
                    time.sleep(0.5)
                    self._update_task_status(task_id, 'running', progress=100)
            else:
                # 模拟进度更新
                self._update_task_status(task_id, 'running', progress=10)
                result = func(*args, **kwargs)
                self._update_task_status(task_id, 'running', progress=100)

            # 更新状态为 completed
            self._update_task_status(
                task_id,
                'completed',
                progress=100,
                result=self._serialize_result(result)
            )

            return result

        except Exception as e:
            # 更新状态为 failed
            self._update_task_status(
                task_id,
                'failed',
                error=str(e)
            )
            raise

    def _serialize_result(self, result: Any) -> Any:
        """序列化结果以便存储到数据库

        Args:
            result: 要序列化的结果

        Returns:
            可JSON序列化的结果
        """
        # 如果是pandas DataFrame，转换为字典
        if hasattr(result, 'to_dict'):
            return result.to_dict()
        # 如果是带有to_dict方法的对象
        elif hasattr(result, '__dict__'):
            try:
                import json
                return json.loads(json.dumps(result, default=str))
            except:
                return str(result)
        # 其他情况直接返回（假设已经是可JSON序列化的）
        return result

    def _update_task_status(
        self,
        task_id: str,
        status: str,
        progress: int = None,
        result: Any = None,
        error: str = None
    ) -> None:
        """更新任务状态

        Args:
            task_id: 任务ID
            status: 状态
            progress: 进度（0-100）
            result: 结果
            error: 错误信息
        """
        session = self.session_manager.get_session()
        try:
            task = session.query(TaskModel).filter_by(id=task_id).first()
            if task:
                task.status = status
                if progress is not None:
                    task.progress = progress
                if result is not None:
                    task.result = self._serialize_result(result)
                if error is not None:
                    task.error = error
                task.updated_at = datetime.now()
                session.commit()
        except Exception as e:
            session.rollback()
            # 状态更新失败不应该中断任务
            pass
        finally:
            session.close()

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态字典，如果不存在则返回None
        """
        session = self.session_manager.get_session()
        try:
            task = session.query(TaskModel).filter_by(id=task_id).first()
            return task.to_dict() if task else None
        finally:
            session.close()

    def cancel_task(self, task_id: str) -> bool:
        """取消任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功取消
        """
        with self.lock:
            if task_id in self.active_tasks:
                future = self.active_tasks[task_id]
                if future.cancel():
                    self._update_task_status(task_id, 'cancelled')
                    del self.active_tasks[task_id]
                    return True

        # 如果Future无法取消，更新状态为cancelled
        self._update_task_status(task_id, 'cancelled')
        return True

    def list_tasks(
        self,
        task_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """列出任务

        Args:
            task_type: 任务类型（可选）
            status: 状态（可选）
            limit: 最大返回数量

        Returns:
            任务列表
        """
        session = self.session_manager.get_session()
        try:
            query = session.query(TaskModel)
            if task_type:
                query = query.filter_by(task_type=task_type)
            if status:
                query = query.filter_by(status=status)

            tasks = query.order_by(
                TaskModel.created_at.desc()
            ).limit(limit).all()

            return [t.to_dict() for t in tasks]
        finally:
            session.close()

    def cleanup_old_tasks(self, days: int = 7) -> int:
        """清理旧任务

        Args:
            days: 保留天数

        Returns:
            删除的任务数
        """
        from sqlalchemy import and_
        from datetime import timedelta

        session = self.session_manager.get_session()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            query = session.query(TaskModel).filter(
                and_(
                    TaskModel.status.in_(['completed', 'failed', 'cancelled']),
                    TaskModel.updated_at < cutoff_date
                )
            )

            count = query.count()
            query.delete()
            session.commit()

            return count
        except Exception as e:
            session.rollback()
            raise Exception(f"清理旧任务失败: {str(e)}")
        finally:
            session.close()

    def shutdown(self, wait: bool = True):
        """关闭任务管理器

        Args:
            wait: 是否等待所有任务完成
        """
        self.executor.shutdown(wait=wait)
