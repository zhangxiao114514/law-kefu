#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息更新管理器，用于管理信息的定时更新和手动更新
"""

import logging
import threading
import time
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InfoUpdateTask:
    """信息更新任务类"""
    
    def __init__(self, name, fetch_func, update_interval, cache_key, cache, on_update=None):
        """初始化更新任务
        
        Args:
            name: 任务名称
            fetch_func: 获取信息的函数
            update_interval: 更新间隔，单位为秒
            cache_key: 缓存键
            cache: 缓存对象
            on_update: 更新后的回调函数
        """
        self.name = name
        self.fetch_func = fetch_func
        self.update_interval = update_interval
        self.cache_key = cache_key
        self.cache = cache
        self.on_update = on_update
        self.last_update_time = None
        self.is_running = False
        self.thread = None
    
    def run(self):
        """执行更新任务"""
        try:
            logger.info(f"执行更新任务: {self.name}")
            # 调用获取函数获取最新信息
            result = self.fetch_func()
            if result is not None:
                # 将结果存入缓存，过期时间设置为更新间隔
                self.cache.set(self.cache_key, result, expire_time=self.update_interval)
                self.last_update_time = datetime.now()
                logger.info(f"更新任务完成: {self.name}")
                # 调用回调函数
                if self.on_update:
                    self.on_update(self.name, result)
        except Exception as e:
            logger.error(f"更新任务失败: {self.name}, 错误: {e}")
    
    def start(self):
        """启动定时更新任务"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            logger.info(f"启动定时更新任务: {self.name}，更新间隔: {self.update_interval}秒")
    
    def stop(self):
        """停止定时更新任务"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        logger.info(f"停止定时更新任务: {self.name}")
    
    def _run_loop(self):
        """定时更新循环"""
        while self.is_running:
            self.run()
            # 等待更新间隔
            time.sleep(self.update_interval)
    
    def get_status(self):
        """获取任务状态
        
        Returns:
            任务状态字典
        """
        return {
            "name": self.name,
            "update_interval": self.update_interval,
            "last_update_time": self.last_update_time.isoformat() if self.last_update_time else None,
            "is_running": self.is_running,
            "cache_key": self.cache_key
        }

class InfoUpdater:
    """信息更新管理器类"""
    
    def __init__(self, cache):
        """初始化信息更新管理器
        
        Args:
            cache: 缓存对象
        """
        self.cache = cache
        self.tasks = {}  # 任务名称到任务对象的映射
        self.lock = threading.Lock()
    
    def add_task(self, name, fetch_func, update_interval, cache_key, on_update=None):
        """添加更新任务
        
        Args:
            name: 任务名称
            fetch_func: 获取信息的函数
            update_interval: 更新间隔，单位为秒
            cache_key: 缓存键
            on_update: 更新后的回调函数
        """
        with self.lock:
            if name in self.tasks:
                logger.warning(f"更新任务已存在: {name}")
                return False
            
            task = InfoUpdateTask(name, fetch_func, update_interval, cache_key, self.cache, on_update)
            self.tasks[name] = task
            logger.info(f"添加更新任务: {name}")
            return True
    
    def remove_task(self, name):
        """移除更新任务
        
        Args:
            name: 任务名称
        """
        with self.lock:
            if name in self.tasks:
                task = self.tasks[name]
                task.stop()
                del self.tasks[name]
                logger.info(f"移除更新任务: {name}")
                return True
            else:
                logger.warning(f"更新任务不存在: {name}")
                return False
    
    def start_task(self, name):
        """启动更新任务
        
        Args:
            name: 任务名称
        """
        with self.lock:
            if name in self.tasks:
                self.tasks[name].start()
                return True
            else:
                logger.warning(f"更新任务不存在: {name}")
                return False
    
    def stop_task(self, name):
        """停止更新任务
        
        Args:
            name: 任务名称
        """
        with self.lock:
            if name in self.tasks:
                self.tasks[name].stop()
                return True
            else:
                logger.warning(f"更新任务不存在: {name}")
                return False
    
    def start_all_tasks(self):
        """启动所有更新任务"""
        with self.lock:
            for name, task in self.tasks.items():
                task.start()
            logger.info(f"已启动所有 {len(self.tasks)} 个更新任务")
    
    def stop_all_tasks(self):
        """停止所有更新任务"""
        with self.lock:
            for name, task in self.tasks.items():
                task.stop()
            logger.info(f"已停止所有更新任务")
    
    def run_task(self, name):
        """手动运行一次更新任务
        
        Args:
            name: 任务名称
        """
        with self.lock:
            if name in self.tasks:
                self.tasks[name].run()
                return True
            else:
                logger.warning(f"更新任务不存在: {name}")
                return False
    
    def run_all_tasks(self):
        """手动运行所有更新任务"""
        with self.lock:
            for name, task in self.tasks.items():
                task.run()
            logger.info(f"已手动运行所有 {len(self.tasks)} 个更新任务")
    
    def get_task_status(self, name):
        """获取任务状态
        
        Args:
            name: 任务名称
            
        Returns:
            任务状态字典
        """
        with self.lock:
            if name in self.tasks:
                return self.tasks[name].get_status()
            else:
                logger.warning(f"更新任务不存在: {name}")
                return None
    
    def get_all_tasks_status(self):
        """获取所有任务状态
        
        Returns:
            所有任务状态的字典
        """
        with self.lock:
            status = {}
            for name, task in self.tasks.items():
                status[name] = task.get_status()
            return status
    
    def get_task_count(self):
        """获取任务数量
        
        Returns:
            任务数量
        """
        with self.lock:
            return len(self.tasks)
