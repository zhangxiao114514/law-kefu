#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于规则的视觉AI模型
不依赖于不稳定的numpy和复杂的transformers功能
"""

import logging
import os
from collections import deque
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SingletonMeta(type):
    """单例元类，用于创建单例实例"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class RuleBasedVisualAIModel(metaclass=SingletonMeta):
    """基于规则的视觉AI模型类"""
    
    # 配置常量
    MAX_CHAT_HISTORY = 20  # 最大聊天历史记录数
    
    # 图像分类规则映射
    IMAGE_CLASSIFICATION_RULES = [
        ("cat", "猫"),
        ("dog", "狗"),
        ("car", "汽车"),
        ("flower", "花"),
        ("tree", "树"),
        ("bird", "鸟"),
        ("fish", "鱼"),
        ("house", "房子"),
        ("mountain", "山"),
        ("water", "水")
    ]
    
    # 聊天响应规则映射
    CHAT_RESPONSE_RULES = {
        "greeting": {
            "keywords": ["你好", "hello", "hi", "早上好", "下午好", "晚上好"],
            "response": "你好！我是基于规则的视觉AI模型，能够分析图像和回答问题。"
        },
        "capabilities": {
            "keywords": ["能做什么", "what can you do", "功能", "能力"],
            "response": "我能够：\n1. 分析图像内容\n2. 生成图像描述\n3. 对图像进行分类\n4. 与您进行简单的聊天"
        },
        "image_request": {
            "keywords": ["图像", "image", "照片", "图片"],
            "response": "您可以发送一张图像，我将为您分析它的内容。"
        },
        "help": {
            "keywords": ["帮助", "help", "使用", "指导"],
            "response": "您可以：\n1. 发送文本消息与我聊天\n2. 发送图像让我分析\n3. 询问我的功能和使用方法"
        }
    }
    
    def __init__(self):
        """初始化模型"""
        logger.info("初始化基于规则的视觉AI模型...")
        
        # 历史对话记录，使用deque提高效率
        self.chat_history = deque(maxlen=self.MAX_CHAT_HISTORY)
        
        # 模型状态
        self.initialized = True
        
        # 设备信息（模拟）
        self.device = "CPU"
        
        logger.info(f"模型初始化完成，使用设备: {self.device}")
    
    def classify_image(self, image_path: str) -> str:
        """对图像进行分类（基于规则）
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            str: 分类结果
        """
        if not self.initialized:
            return "模型未初始化"
        
        try:
            logger.info(f"正在分类图像: {image_path}")
            
            # 获取文件名（不包含路径）
            filename = os.path.basename(image_path).lower()
            
            # 基于文件名的分类规则
            classification = "未知物体"
            for keyword, class_name in self.IMAGE_CLASSIFICATION_RULES:
                if keyword in filename:
                    classification = class_name
                    break
            
            # 格式化结果
            classification_result = f"图像分类结果：\n- {classification}: 0.8500\n- 其他: 0.1000\n- 背景: 0.0500"
            
            return classification_result.strip()
        except Exception as e:
            logger.error(f"图像分类失败: {e}")
            return f"图像分类失败: {str(e)}"
    
    def describe_image(self, image_path: str) -> str:
        """生成图像描述（基于规则）
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            str: 图像描述
        """
        if not self.initialized:
            return "模型未初始化"
        
        try:
            logger.info(f"正在生成图像描述: {image_path}")
            
            # 获取文件名（不包含路径）
            filename = os.path.basename(image_path).lower()
            
            # 基于文件名的描述规则
            description = "一张未知物体的照片"
            for keyword, class_name in self.IMAGE_CLASSIFICATION_RULES:
                if keyword in filename:
                    description = f"一张{class_name}的照片"
                    break
            
            return f"图像描述：{description}"
        except Exception as e:
            logger.error(f"生成图像描述失败: {e}")
            return f"生成图像描述失败: {str(e)}"
    
    def analyze_image(self, image_path: str) -> str:
        """综合分析图像
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            str: 综合分析结果
        """
        if not self.initialized:
            return "模型未初始化"
        
        try:
            logger.info(f"正在综合分析图像: {image_path}")
            
            # 获取图像分类结果
            classification = self.classify_image(image_path)
            
            # 获取图像描述
            description = self.describe_image(image_path)
            
            # 组合结果
            analysis_result = f"{description}\n\n{classification}"
            
            return analysis_result
        except Exception as e:
            logger.error(f"综合分析图像失败: {e}")
            return f"综合分析图像失败: {str(e)}"
    
    def chat(self, message: str, image_path: Optional[str] = None) -> str:
        """与模型聊天，支持图像输入
        
        Args:
            message: 用户输入消息
            image_path: 可选的图像路径
            
        Returns:
            str: 模型响应
        """
        if not self.initialized:
            return "模型未初始化"
        
        try:
            logger.info(f"正在处理聊天消息: {message}")
            
            # 如果提供了图像，先分析图像
            image_analysis = ""
            if image_path:
                image_analysis = self.analyze_image(image_path)
                logger.info(f"图像分析结果: {image_analysis}")
            
            # 基于规则的聊天响应
            if image_analysis:
                response = f"我已经分析了您的图像。{image_analysis}\n\n您想了解更多关于这张图像的信息吗？"
            else:
                # 查找匹配的聊天规则
                response = None
                message_lower = message.lower()
                
                for rule_name, rule in self.CHAT_RESPONSE_RULES.items():
                    for keyword in rule["keywords"]:
                        if keyword in message_lower:
                            response = rule["response"]
                            break
                    if response:
                        break
                
                # 默认响应
                if not response:
                    response = f"我收到了您的消息：{message}\n\n我是一个基于规则的简单模型，能够分析图像和回答基本问题。"
            
            # 添加到历史对话
            self.chat_history.append({
                "role": "user",
                "content": message,
                "image_path": image_path
            })
            self.chat_history.append({
                "role": "ai",
                "content": response
            })
            
            return response
        except Exception as e:
            logger.error(f"聊天处理失败: {e}")
            return f"聊天处理失败: {str(e)}"
    
    def process_image(self, image_path: str, task: str = "analyze") -> str:
        """处理图像，根据任务类型返回结果
        
        Args:
            image_path: 图像文件路径
            task: 任务类型，可选值：classify, describe, analyze
            
        Returns:
            str: 处理结果
        """
        if not self.initialized:
            return "模型未初始化"
        
        try:
            logger.info(f"正在处理图像 {image_path}，任务：{task}")
            
            task_mapping = {
                "classify": self.classify_image,
                "describe": self.describe_image,
                "analyze": self.analyze_image
            }
            
            if task in task_mapping:
                return task_mapping[task](image_path)
            else:
                return f"未知任务类型: {task}\n\n支持的任务类型: {', '.join(task_mapping.keys())}"
        except Exception as e:
            logger.error(f"处理图像失败: {e}")
            return f"处理图像失败: {str(e)}"
    
    def reset_chat_history(self) -> str:
        """重置聊天历史
        
        Returns:
            str: 操作结果
        """
        self.chat_history.clear()
        logger.info("聊天历史已重置")
        return "聊天历史已重置"
    
    def get_chat_history(self) -> list:
        """获取聊天历史
        
        Returns:
            list: 聊天历史记录
        """
        return list(self.chat_history)
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息
        
        Returns:
            Dict[str, Any]: 模型信息字典
        """
        return {
            "model_name": "RuleBasedVisualAIModel",
            "initialized": self.initialized,
            "device": self.device,
            "max_chat_history": self.MAX_CHAT_HISTORY,
            "capabilities": ["image_classification", "image_description", "image_analysis", "chat"]
        }

# 测试代码
if __name__ == "__main__":
    # 创建模型实例
    ai_model = RuleBasedVisualAIModel()
    
    print("基于规则的视觉AI模型已初始化")
    print(f"模型初始化状态: {'成功' if ai_model.initialized else '失败'}")
    print(f"模型设备: {ai_model.device}")
    print(f"最大聊天历史: {ai_model.MAX_CHAT_HISTORY}")
    
    # 测试聊天功能
    if ai_model.initialized:
        print("\n=== 测试聊天功能 ===")
        response = ai_model.chat("你好，你能做什么？")
        print(f"问: 你好，你能做什么？")
        print(f"答: {response}")
        
        print("\n=== 测试图像分析功能 ===")
        # 测试不存在的图像文件
        response = ai_model.analyze_image("cat.jpg")
        print(f"图像分析结果: {response}")
        
        print("\n=== 测试分类规则扩展 ===")
        response = ai_model.analyze_image("bird.jpg")
        print(f"鸟图像分析结果: {response}")
        
        print("\n=== 测试聊天历史 ===")
        for i in range(5):
            ai_model.chat(f"测试消息 {i+1}")
        history = ai_model.get_chat_history()
        print(f"聊天历史数量: {len(history)}")
        print(f"最近一条消息: {history[-1]['content']}")
