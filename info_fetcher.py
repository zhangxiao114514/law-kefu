#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息自动获取模块，支持从网页、API接口获取实时信息
"""

import logging
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InfoSourceType:
    """信息源类型枚举"""
    WEB_PAGE = "web_page"  # 网页
    API = "api"            # API接口

class InfoFetcher:
    """信息获取器类"""
    
    def __init__(self, timeout=10):
        """初始化信息获取器
        
        Args:
            timeout: 请求超时时间，单位为秒
        """
        self.timeout = timeout
        # 创建会话，提高请求效率
        self.session = requests.Session()
    
    def fetch_from_web_page(self, url, selector=None, headers=None):
        """从网页获取信息
        
        Args:
            url: 网页URL
            selector: CSS选择器，用于提取特定内容，如果为None则返回整个页面内容
            headers: 请求头
            
        Returns:
            提取的网页内容
        """
        try:
            logger.info(f"从网页获取信息: {url}")
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()  # 检查请求是否成功
            
            if selector:
                # 使用BeautifulSoup解析HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                elements = soup.select(selector)
                content = '\n'.join([elem.get_text(strip=True) for elem in elements])
                logger.info(f"成功提取网页内容，共 {len(elements)} 个元素")
                return content
            else:
                logger.info("成功获取整个网页内容")
                return response.text
        except Exception as e:
            logger.error(f"从网页获取信息失败: {e}")
            return None
    
    def fetch_from_api(self, url, method="GET", params=None, data=None, json_data=None, headers=None, auth=None):
        """从API接口获取信息
        
        Args:
            url: API URL
            method: HTTP方法，默认为GET
            params: URL参数
            data: POST表单数据
            json_data: POST JSON数据
            headers: 请求头
            auth: 认证信息
            
        Returns:
            API返回的数据（已解析为字典）
        """
        try:
            logger.info(f"从API获取信息: {url} (方法: {method})")
            
            # 根据方法类型发送请求
            if method.upper() == "GET":
                response = self.session.get(url, params=params, headers=headers, auth=auth, timeout=self.timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, params=params, data=data, json=json_data, headers=headers, auth=auth, timeout=self.timeout)
            else:
                logger.error(f"不支持的HTTP方法: {method}")
                return None
            
            response.raise_for_status()  # 检查请求是否成功
            
            # 解析JSON响应
            result = response.json()
            logger.info("成功获取并解析API数据")
            return result
        except Exception as e:
            logger.error(f"从API获取信息失败: {e}")
            return None
    
    def fetch(self, source_config):
        """根据配置从信息源获取信息
        
        Args:
            source_config: 信息源配置，包含type, url等字段
            
        Returns:
            获取的信息
        """
        source_type = source_config.get("type")
        url = source_config.get("url")
        
        if not source_type or not url:
            logger.error("信息源配置不完整，缺少type或url字段")
            return None
        
        if source_type == InfoSourceType.WEB_PAGE:
            selector = source_config.get("selector")
            headers = source_config.get("headers")
            return self.fetch_from_web_page(url, selector, headers)
        elif source_type == InfoSourceType.API:
            method = source_config.get("method", "GET")
            params = source_config.get("params")
            data = source_config.get("data")
            json_data = source_config.get("json_data")
            headers = source_config.get("headers")
            auth = source_config.get("auth")
            return self.fetch_from_api(url, method, params, data, json_data, headers, auth)
        else:
            logger.error(f"不支持的信息源类型: {source_type}")
            return None

class InfoCache:
    """信息缓存类，用于存储和管理获取的信息"""
    
    def __init__(self):
        """初始化信息缓存"""
        self.cache = {}
    
    def set(self, key, value, expire_time=None):
        """设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            expire_time: 过期时间，单位为秒，如果为None则永不过期
        """
        cache_item = {
            "value": value,
            "timestamp": datetime.now(),
            "expire_time": expire_time
        }
        self.cache[key] = cache_item
        logger.info(f"设置缓存: {key}，过期时间: {expire_time}秒")
    
    def get(self, key):
        """获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果缓存不存在或已过期则返回None
        """
        if key not in self.cache:
            logger.info(f"缓存不存在: {key}")
            return None
        
        cache_item = self.cache[key]
        # 检查缓存是否过期
        if cache_item["expire_time"] is not None:
            elapsed = (datetime.now() - cache_item["timestamp"]).total_seconds()
            if elapsed > cache_item["expire_time"]:
                logger.info(f"缓存已过期: {key}")
                del self.cache[key]  # 删除过期缓存
                return None
        
        logger.info(f"获取缓存: {key}")
        return cache_item["value"]
    
    def delete(self, key):
        """删除缓存
        
        Args:
            key: 缓存键
        """
        if key in self.cache:
            del self.cache[key]
            logger.info(f"删除缓存: {key}")
    
    def clear(self):
        """清除所有缓存"""
        self.cache.clear()
        logger.info("已清除所有缓存")
    
    def get_cache_info(self):
        """获取缓存信息
        
        Returns:
            缓存信息字典，包含缓存数量和每个缓存的状态
        """
        info = {
            "total_count": len(self.cache),
            "items": {}
        }
        
        for key, item in self.cache.items():
            elapsed = (datetime.now() - item["timestamp"]).total_seconds()
            info["items"][key] = {
                "timestamp": item["timestamp"].isoformat(),
                "expire_time": item["expire_time"],
                "elapsed_seconds": round(elapsed, 2),
                "is_expired": elapsed > item["expire_time"] if item["expire_time"] is not None else False
            }
        
        return info
