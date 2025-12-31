#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动回复管理器，整合关键词匹配、信息获取和多轮对话管理
"""

import logging
from keyword_matcher import KeywordMatcher, MatchType
from conversation_manager import ConversationManager
from info_fetcher import InfoFetcher, InfoSourceType
from info_updater import InfoUpdater
from info_fetcher import InfoCache

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoReplyManager:
    """自动回复管理器类"""
    
    def __init__(self):
        """初始化自动回复管理器"""
        # 初始化各个模块
        self.keyword_matcher = KeywordMatcher()
        self.conversation_manager = ConversationManager()
        self.info_fetcher = InfoFetcher()
        self.info_cache = InfoCache()
        self.info_updater = InfoUpdater(self.info_cache)
        
        # 默认回复
        self.default_response = "抱歉，我暂时无法理解您的意思，请换个方式提问。"
        
        logger.info("自动回复管理器初始化完成")
    
    def add_reply_rule(self, keyword, response, match_type=MatchType.EXACT, priority=0):
        """添加回复规则
        
        Args:
            keyword: 关键词
            response: 回复内容
            match_type: 匹配类型
            priority: 优先级
        """
        self.keyword_matcher.add_rule(keyword, response, match_type, priority)
    
    def add_reply_rules_from_config(self, config):
        """从配置中添加批量回复规则
        
        Args:
            config: 规则配置列表
        """
        self.keyword_matcher.add_rules_from_config(config)
    
    def add_info_source(self, name, source_config, update_interval=3600, on_update=None):
        """添加信息源
        
        Args:
            name: 信息源名称
            source_config: 信息源配置
            update_interval: 更新间隔，单位为秒
            on_update: 更新后的回调函数
            
        Returns:
            bool: 是否添加成功
        """
        # 创建获取函数
        def fetch_func():
            return self.info_fetcher.fetch(source_config)
        
        # 添加更新任务
        return self.info_updater.add_task(name, fetch_func, update_interval, name, on_update)
    
    def start_info_updates(self):
        """启动所有信息源的自动更新"""
        self.info_updater.start_all_tasks()
    
    def stop_info_updates(self):
        """停止所有信息源的自动更新"""
        self.info_updater.stop_all_tasks()
    
    def get_cached_info(self, info_name):
        """获取缓存的信息
        
        Args:
            info_name: 信息名称
            
        Returns:
            缓存的信息
        """
        return self.info_cache.get(info_name)
    
    def handle_message(self, user_id, message_content):
        """处理用户消息并生成回复
        
        Args:
            user_id: 用户ID
            message_content: 消息内容
            
        Returns:
            回复内容
        """
        try:
            # 验证输入参数
            if not self._validate_input_params(user_id, message_content):
                logger.error("输入参数验证失败")
                return self.default_response
            
            logger.info(f"处理用户 {user_id} 的消息: {message_content}")
            
            # 添加用户消息到对话历史
            self.conversation_manager.add_user_message(user_id, message_content)
            
            # 检查是否有匹配的关键词规则
            matched_rule = self.keyword_matcher.match(message_content)
            
            if matched_rule:
                # 生成回复
                response = self._generate_response_from_rule(matched_rule, user_id, message_content)
            else:
                # 检查是否需要处理多轮对话
                response = self._handle_multi_turn_conversation(user_id, message_content)
            
            # 如果没有生成回复，使用默认回复
            if not response:
                response = self.default_response
            
            # 验证回复内容
            response = self._validate_response(response)
            
            # 添加机器人回复到对话历史
            self.conversation_manager.add_bot_message(user_id, response)
            
            logger.info(f"生成回复: {response}")
            return response
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            return self.default_response
    
    def _validate_input_params(self, user_id, message_content):
        """验证输入参数
        
        Args:
            user_id: 用户ID
            message_content: 消息内容
            
        Returns:
            bool: 参数是否有效
        """
        if not user_id or not isinstance(user_id, str):
            logger.error("无效的用户ID")
            return False
        
        if message_content is None:
            logger.error("消息内容不能为空")
            return False
        
        if not isinstance(message_content, str):
            message_content = str(message_content)
        
        return True
    
    def _validate_response(self, response):
        """验证回复内容
        
        Args:
            response: 回复内容
            
        Returns:
            str: 验证后的回复内容
        """
        if not response:
            logger.warning("回复内容为空，使用默认回复")
            return self.default_response
        
        if not isinstance(response, str):
            try:
                response = str(response)
            except Exception as e:
                logger.error(f"回复内容转换为字符串失败: {e}")
                return self.default_response
        
        # 限制回复长度
        max_response_length = 500
        if len(response) > max_response_length:
            logger.warning(f"回复内容过长，截断为 {max_response_length} 字符")
            response = response[:max_response_length] + "..."
        
        return response
    
    def _generate_response_from_rule(self, rule, user_id, message_content):
        """根据匹配的规则生成回复
        
        Args:
            rule: 匹配的规则
            user_id: 用户ID
            message_content: 消息内容
            
        Returns:
            回复内容
        """
        response = rule.response
        
        # 检查回复中是否包含需要替换的变量
        if "{info:" in response:
            # 提取信息名称
            import re
            info_matches = re.findall(r"\{info:(\w+)\}", response)
            for info_name in info_matches:
                # 获取缓存的信息
                info = self.get_cached_info(info_name)
                if info:
                    # 替换变量
                    response = response.replace(f"{{info:{info_name}}}", str(info))
        
        # 检查回复中是否包含对话状态控制
        if "{state:" in response:
            # 提取状态名称
            import re
            state_matches = re.findall(r"\{state:(\w+)\}", response)
            for state in state_matches:
                # 更新对话状态
                self.conversation_manager.update_conversation_state(user_id, state)
                # 移除状态控制标记
                response = response.replace(f"{{state:{state}}}", "")
        
        return response
    
    def _handle_multi_turn_conversation(self, user_id, message_content):
        """处理多轮对话
        
        Args:
            user_id: 用户ID
            message_content: 消息内容
            
        Returns:
            回复内容
        """
        # 获取当前对话状态
        conversation = self.conversation_manager.get_conversation(user_id)
        current_state = conversation.current_state
        
        # 根据当前状态处理对话
        # 这里可以扩展各种对话状态的处理逻辑
        if current_state == "init":
            # 初始状态，没有特殊处理
            return None
        
        # 默认返回None，使用默认回复
        return None
    
    def set_default_response(self, response):
        """设置默认回复
        
        Args:
            response: 默认回复内容
        """
        self.default_response = response
        logger.info(f"设置默认回复: {response}")
    
    def reset_conversation(self, user_id):
        """重置用户对话
        
        Args:
            user_id: 用户ID
        """
        self.conversation_manager.reset_conversation(user_id)
    
    def get_system_status(self):
        """获取系统状态
        
        Returns:
            系统状态字典
        """
        return {
            "keyword_rule_count": len(self.keyword_matcher.get_all_rules()),
            "active_conversation_count": self.conversation_manager.get_conversation_count(),
            "info_source_count": self.info_updater.get_task_count(),
            "cache_info": self.info_cache.get_cache_info()
        }
