#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关键词匹配模块，支持精确匹配、模糊匹配和正则表达式匹配
"""

import re
import logging

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MatchType:
    """匹配类型枚举"""
    EXACT = "exact"      # 精确匹配
    FUZZY = "fuzzy"      # 模糊匹配
    REGEX = "regex"      # 正则表达式匹配

class KeywordRule:
    """关键词规则类"""
    
    def __init__(self, keyword, response, match_type=MatchType.EXACT, priority=0):
        """初始化关键词规则
        
        Args:
            keyword: 关键词
            response: 回复内容
            match_type: 匹配类型，默认为精确匹配
            priority: 优先级，数值越大优先级越高
        """
        self.keyword = keyword
        self.response = response
        self.match_type = match_type
        self.priority = priority
        # 预编译正则表达式，提高匹配效率
        self.regex_pattern = re.compile(keyword) if match_type == MatchType.REGEX else None

class KeywordMatcher:
    """关键词匹配器类"""
    
    def __init__(self):
        """初始化关键词匹配器"""
        self.rules = []
    
    def add_rule(self, keyword, response, match_type=MatchType.EXACT, priority=0):
        """添加关键词规则
        
        Args:
            keyword: 关键词
            response: 回复内容
            match_type: 匹配类型
            priority: 优先级
        """
        rule = KeywordRule(keyword, response, match_type, priority)
        self.rules.append(rule)
        # 按优先级排序，优先级高的规则先匹配
        self.rules.sort(key=lambda x: x.priority, reverse=True)
        logger.info(f"添加关键词规则: {keyword} (类型: {match_type}, 优先级: {priority})")
    
    def add_rules_from_config(self, config):
        """从配置中添加批量规则
        
        Args:
            config: 规则配置列表，每个元素包含keyword, response, match_type, priority
        """
        for rule_config in config:
            self.add_rule(**rule_config)
    
    def match(self, text):
        """匹配文本，返回第一个匹配的规则
        
        Args:
            text: 要匹配的文本
            
        Returns:
            匹配到的规则对象，如果没有匹配则返回None
        """
        for rule in self.rules:
            if self._is_match(rule, text):
                logger.info(f"匹配到规则: {rule.keyword} (类型: {rule.match_type})")
                return rule
        return None
    
    def _is_match(self, rule, text):
        """检查文本是否匹配规则
        
        Args:
            rule: 规则对象
            text: 要匹配的文本
            
        Returns:
            bool: 是否匹配
        """
        if rule.match_type == MatchType.EXACT:
            return text == rule.keyword
        elif rule.match_type == MatchType.FUZZY:
            return rule.keyword in text
        elif rule.match_type == MatchType.REGEX:
            return rule.regex_pattern.search(text) is not None
        return False
    
    def get_all_rules(self):
        """获取所有规则
        
        Returns:
            规则列表
        """
        return self.rules
    
    def clear_rules(self):
        """清除所有规则"""
        self.rules = []
        logger.info("已清除所有关键词规则")
