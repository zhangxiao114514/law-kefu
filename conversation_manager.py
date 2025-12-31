#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多轮对话管理模块，支持上下文连贯回复
"""

import logging
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConversationState:
    """对话状态类"""
    
    def __init__(self, user_id):
        """初始化对话状态
        
        Args:
            user_id: 用户ID
        """
        self.user_id = user_id
        self.messages = []  # 对话历史记录
        self.current_state = "init"  # 当前对话状态
        self.context_data = {}  # 上下文数据，用于存储对话过程中的临时信息
        self.last_active_time = datetime.now()  # 最后活跃时间
    
    def add_message(self, sender, content, message_type="text"):
        """添加消息到对话历史
        
        Args:
            sender: 发送者，可以是"user"或"bot"
            content: 消息内容
            message_type: 消息类型，默认为"text"
        """
        message = {
            "sender": sender,
            "content": content,
            "type": message_type,
            "timestamp": datetime.now()
        }
        self.messages.append(message)
        self.last_active_time = datetime.now()
        # 限制对话历史长度，最多保留50条消息
        if len(self.messages) > 50:
            self.messages.pop(0)
    
    def get_recent_messages(self, count=10):
        """获取最近的对话消息
        
        Args:
            count: 要获取的消息数量
            
        Returns:
            最近的消息列表
        """
        return self.messages[-count:]
    
    def update_state(self, new_state):
        """更新对话状态
        
        Args:
            new_state: 新的对话状态
        """
        self.current_state = new_state
        self.last_active_time = datetime.now()
    
    def set_context_data(self, key, value):
        """设置上下文数据
        
        Args:
            key: 数据键
            value: 数据值
        """
        self.context_data[key] = value
        self.last_active_time = datetime.now()
    
    def get_context_data(self, key, default=None):
        """获取上下文数据
        
        Args:
            key: 数据键
            default: 默认值，如果键不存在则返回默认值
            
        Returns:
            上下文数据值
        """
        return self.context_data.get(key, default)
    
    def clear_context_data(self):
        """清除上下文数据"""
        self.context_data.clear()
    
    def is_expired(self, timeout_minutes=30):
        """检查对话是否过期
        
        Args:
            timeout_minutes: 超时时间，单位为分钟
            
        Returns:
            bool: 是否过期
        """
        return datetime.now() - self.last_active_time > timedelta(minutes=timeout_minutes)

class ConversationManager:
    """对话管理器类"""
    
    def __init__(self, timeout_minutes=30):
        """初始化对话管理器
        
        Args:
            timeout_minutes: 对话超时时间，单位为分钟
        """
        self.conversations = {}  # 用户ID到对话状态的映射
        self.timeout_minutes = timeout_minutes
    
    def get_conversation(self, user_id):
        """获取用户的对话状态
        
        Args:
            user_id: 用户ID
            
        Returns:
            对话状态对象
        """
        if user_id not in self.conversations or self.conversations[user_id].is_expired(self.timeout_minutes):
            # 如果用户不存在或对话已过期，创建新的对话状态
            self.conversations[user_id] = ConversationState(user_id)
            logger.info(f"为用户 {user_id} 创建新的对话状态")
        return self.conversations[user_id]
    
    def add_user_message(self, user_id, content, message_type="text"):
        """添加用户消息
        
        Args:
            user_id: 用户ID
            content: 消息内容
            message_type: 消息类型
        """
        conversation = self.get_conversation(user_id)
        conversation.add_message("user", content, message_type)
        logger.info(f"添加用户 {user_id} 消息: {content}")
    
    def add_bot_message(self, user_id, content, message_type="text"):
        """添加机器人消息
        
        Args:
            user_id: 用户ID
            content: 消息内容
            message_type: 消息类型
        """
        conversation = self.get_conversation(user_id)
        conversation.add_message("bot", content, message_type)
        logger.info(f"添加机器人回复 {user_id}: {content}")
    
    def update_conversation_state(self, user_id, new_state):
        """更新对话状态
        
        Args:
            user_id: 用户ID
            new_state: 新的对话状态
        """
        conversation = self.get_conversation(user_id)
        conversation.update_state(new_state)
        logger.info(f"更新用户 {user_id} 对话状态为: {new_state}")
    
    def set_context_data(self, user_id, key, value):
        """设置上下文数据
        
        Args:
            user_id: 用户ID
            key: 数据键
            value: 数据值
        """
        conversation = self.get_conversation(user_id)
        conversation.set_context_data(key, value)
        logger.info(f"设置用户 {user_id} 上下文数据: {key} = {value}")
    
    def get_context_data(self, user_id, key, default=None):
        """获取上下文数据
        
        Args:
            user_id: 用户ID
            key: 数据键
            default: 默认值
            
        Returns:
            上下文数据值
        """
        conversation = self.get_conversation(user_id)
        return conversation.get_context_data(key, default)
    
    def get_recent_messages(self, user_id, count=10):
        """获取最近的对话消息
        
        Args:
            user_id: 用户ID
            count: 要获取的消息数量
            
        Returns:
            最近的消息列表
        """
        conversation = self.get_conversation(user_id)
        return conversation.get_recent_messages(count)
    
    def reset_conversation(self, user_id):
        """重置对话
        
        Args:
            user_id: 用户ID
        """
        if user_id in self.conversations:
            del self.conversations[user_id]
            logger.info(f"已重置用户 {user_id} 的对话")
    
    def clear_expired_conversations(self):
        """清除所有过期的对话"""
        expired_users = []
        for user_id, conversation in self.conversations.items():
            if conversation.is_expired(self.timeout_minutes):
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del self.conversations[user_id]
            logger.info(f"已清除用户 {user_id} 的过期对话")
        
        return len(expired_users)
    
    def get_conversation_count(self):
        """获取当前活跃对话数量
        
        Returns:
            活跃对话数量
        """
        return len(self.conversations)
