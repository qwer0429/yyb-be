"""
药品导入任务管理模块
使用后台线程处理导入任务，提供任务状态跟踪
"""
import threading
import uuid
import time
from datetime import datetime
from typing import Dict, Optional, Callable, Any
import logging

# Django 数据库连接处理
from django import db

logger = logging.getLogger(__name__)


class ImportTaskManager:
    """
    导入任务管理器
    管理后台导入任务的生命周期和状态
    """
    
    def __init__(self):
        # 任务存储: {task_id: task_info}
        self._tasks: Dict[str, Dict] = {}
        # 任务锁，保证线程安全
        self._lock = threading.Lock()
        # 清理间隔（秒）
        self._cleanup_interval = 3600  # 1小时
        # 任务过期时间（秒）
        self._task_expire_time = 86400  # 24小时
        # 启动清理线程
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """启动后台清理线程，定期清理过期任务"""
        def cleanup_worker():
            while True:
                time.sleep(self._cleanup_interval)
                self._cleanup_expired_tasks()
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("导入任务清理线程已启动")
    
    def _cleanup_expired_tasks(self):
        """清理过期任务"""
        with self._lock:
            current_time = time.time()
            expired_tasks = [
                task_id for task_id, task in self._tasks.items()
                if current_time - task.get('created_at', 0) > self._task_expire_time
            ]
            for task_id in expired_tasks:
                del self._tasks[task_id]
            if expired_tasks:
                logger.info(f"已清理 {len(expired_tasks)} 个过期任务")
    
    def create_task(self, task_type: str = 'import') -> str:
        """
        创建新任务
        
        Args:
            task_type: 任务类型，如 'import', 'preview'
            
        Returns:
            task_id: 任务唯一标识
        """
        task_id = str(uuid.uuid4())
        with self._lock:
            self._tasks[task_id] = {
                'id': task_id,
                'type': task_type,
                'status': 'pending',  # pending, running, completed, failed, cancelled
                'progress': 0,  # 0-100
                'message': '任务等待中',
                'created_at': time.time(),
                'started_at': None,
                'completed_at': None,
                'result': None,
                'error': None,
                'detail': {}  # 存储详细进度信息
            }
        logger.info(f"创建导入任务: {task_id}")
        return task_id
    
    def start_task(self, task_id: str):
        """标记任务开始执行"""
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]['status'] = 'running'
                self._tasks[task_id]['started_at'] = time.time()
                self._tasks[task_id]['message'] = '任务执行中'
                logger.info(f"任务开始执行: {task_id}")
    
    def update_progress(self, task_id: str, progress: int, message: str = None, detail: Dict = None):
        """
        更新任务进度
        
        Args:
            task_id: 任务ID
            progress: 进度百分比 (0-100)
            message: 进度消息
            detail: 详细进度信息
        """
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]['progress'] = min(100, max(0, progress))
                if message:
                    self._tasks[task_id]['message'] = message
                if detail:
                    self._tasks[task_id]['detail'].update(detail)
    
    def complete_task(self, task_id: str, result: Any = None):
        """标记任务完成"""
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]['status'] = 'completed'
                self._tasks[task_id]['progress'] = 100
                self._tasks[task_id]['completed_at'] = time.time()
                self._tasks[task_id]['result'] = result
                self._tasks[task_id]['message'] = '任务完成'
                logger.info(f"任务完成: {task_id}")
    
    def fail_task(self, task_id: str, error: str):
        """标记任务失败"""
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]['status'] = 'failed'
                self._tasks[task_id]['completed_at'] = time.time()
                self._tasks[task_id]['error'] = error
                self._tasks[task_id]['message'] = f'任务失败: {error}'
                logger.error(f"任务失败: {task_id}, 错误: {error}")
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self._lock:
            if task_id in self._tasks:
                if self._tasks[task_id]['status'] in ['pending', 'running']:
                    self._tasks[task_id]['status'] = 'cancelled'
                    self._tasks[task_id]['completed_at'] = time.time()
                    self._tasks[task_id]['message'] = '任务已取消'
                    logger.info(f"任务已取消: {task_id}")
                    return True
        return False
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取任务信息"""
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                # 返回副本，避免外部修改
                return task.copy()
            return None
    
    def get_all_tasks(self, limit: int = 50) -> list:
        """获取所有任务列表"""
        with self._lock:
            tasks = list(self._tasks.values())
            # 按创建时间倒序
            tasks.sort(key=lambda x: x['created_at'], reverse=True)
            return tasks[:limit]
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """
        获取任务状态（简化版，用于API返回）
        """
        task = self.get_task(task_id)
        if not task:
            return None
        
        return {
            'id': task['id'],
            'type': task['type'],
            'status': task['status'],
            'progress': task['progress'],
            'message': task['message'],
            'created_at': datetime.fromtimestamp(task['created_at']).isoformat(),
            'started_at': datetime.fromtimestamp(task['started_at']).isoformat() if task['started_at'] else None,
            'completed_at': datetime.fromtimestamp(task['completed_at']).isoformat() if task['completed_at'] else None,
            'result': task['result'],
            'error': task['error'],
            'detail': task['detail']
        }


# 全局任务管理器实例
task_manager = ImportTaskManager()


def run_in_thread(task_id: str, target_func: Callable, *args, **kwargs):
    """
    在后台线程中运行任务
    
    Args:
        task_id: 任务ID
        target_func: 要执行的函数
        *args, **kwargs: 传递给函数的参数
    """
    def wrapper():
        try:
            task_manager.start_task(task_id)
            result = target_func(task_id, *args, **kwargs)
            task_manager.complete_task(task_id, result)
        except Exception as e:
            logger.error(f"任务执行异常: {task_id}, {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            task_manager.fail_task(task_id, str(e))
    
    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()
    logger.info(f"启动后台线程执行任务: {task_id}")
    return thread


def run_import_in_thread(task_id: str, import_func: Callable, file_data: bytes, file_name: str, *args, **kwargs):
    """
    专门用于导入任务的后台线程包装器
    处理文件数据的序列化，并正确处理 Django 数据库连接
    
    Args:
        task_id: 任务ID
        import_func: 导入函数
        file_data: 文件二进制数据
        file_name: 文件名
    """
    def wrapper():
        import io
        import pandas as pd
        import sys
        
        # 设置日志立即输出
        logger.info(f"[Thread {task_id}] 后台线程启动")
        
        try:
            # 关键：关闭旧的数据库连接，确保后台线程使用自己的连接
            # Django 的数据库连接是线程本地的，必须在新线程中重新建立
            db.connections.close_all()
            logger.info(f"[Thread {task_id}] 数据库连接已重置")
            
            task_manager.start_task(task_id)
            
            # 从字节流重建文件对象
            logger.info(f"[Thread {task_id}] 开始解析Excel文件")
            excel_file = pd.ExcelFile(io.BytesIO(file_data))
            logger.info(f"[Thread {task_id}] Excel文件解析完成，包含sheets: {excel_file.sheet_names}")
            
            # 执行导入
            logger.info(f"[Thread {task_id}] 开始执行导入函数")
            result = import_func(task_id, excel_file, file_name, *args, **kwargs)
            logger.info(f"[Thread {task_id}] 导入函数执行完成，结果: {result}")
            task_manager.complete_task(task_id, result)
            
        except Exception as e:
            error_msg = f"[Thread {task_id}] 导入任务执行异常: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            task_manager.fail_task(task_id, str(e))
        finally:
            # 任务完成后关闭数据库连接
            db.connections.close_all()
            logger.info(f"[Thread {task_id}] 数据库连接已关闭")
    
    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()
    logger.info(f"启动后台导入线程: {task_id}")
    return thread
