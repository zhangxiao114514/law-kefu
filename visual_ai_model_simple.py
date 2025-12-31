#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版视觉AI模型
只使用transformers的核心功能，不依赖复杂的torch和numpy操作
"""

import logging
from transformers import pipeline

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VisualAIModel:
    """简化版视觉AI模型类"""
    
    def __init__(self):
        """初始化模型"""
        logger.info("初始化简化版视觉AI模型...")
        
        # 历史对话记录
        self.chat_history = []
        
        # 标记是否已加载模型
        self.models_loaded = False
        
        # 尝试加载模型
        self._load_models()
    
    def _load_models(self):
        """加载必要的模型"""
        try:
            logger.info("正在加载文本生成模型...")
            # 使用轻量级的文本生成模型
            self.text_generator = pipeline("text-generation", model="gpt2", 
                                         max_new_tokens=100, 
                                         truncation=True)
            logger.info("文本生成模型加载成功")
            
            logger.info("正在加载图像分类模型...")
            # 使用轻量级的图像分类模型
            self.image_classifier = pipeline("image-classification", 
                                           model="google/vit-base-patch16-224",
                                           top_k=3)
            logger.info("图像分类模型加载成功")
            
            logger.info("正在加载图像描述模型...")
            # 使用轻量级的图像描述模型
            self.image_captioner = pipeline("image-to-text", 
                                          model="Salesforce/blip-image-captioning-base",
                                          max_new_tokens=50)
            logger.info("图像描述模型加载成功")
            
            self.models_loaded = True
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            self.models_loaded = False
    
    def classify_image(self, image_path):
        """对图像进行分类"""
        if not self.models_loaded:
            return "模型未加载"
        
        try:
            logger.info(f"正在分类图像: {image_path}")
            results = self.image_classifier(image_path)
            
            # 格式化结果
            classification_result = "图像分类结果：\n"
            for result in results:
                classification_result += f"- {result['label']}: {result['score']:.4f}\n"
            
            return classification_result.strip()
        except Exception as e:
            logger.error(f"图像分类失败: {e}")
            return f"图像分类失败: {str(e)}"
    
    def describe_image(self, image_path):
        """生成图像描述"""
        if not self.models_loaded:
            return "模型未加载"
        
        try:
            logger.info(f"正在生成图像描述: {image_path}")
            results = self.image_captioner(image_path)
            description = results[0]["generated_text"]
            return f"图像描述：{description}"
        except Exception as e:
            logger.error(f"生成图像描述失败: {e}")
            return f"生成图像描述失败: {str(e)}"
    
    def analyze_image(self, image_path):
        """综合分析图像"""
        if not self.models_loaded:
            return "模型未加载"
        
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
    
    def chat(self, message, image_path=None):
        """与模型聊天，支持图像输入"""
        if not self.models_loaded:
            return "模型未加载"
        
        try:
            logger.info(f"正在处理聊天消息: {message}")
            
            # 如果提供了图像，先分析图像
            image_analysis = ""
            if image_path:
                image_analysis = self.analyze_image(image_path)
                logger.info(f"图像分析结果: {image_analysis}")
            
            # 构建对话上下文
            if image_analysis:
                prompt = f"用户发送了一张图片，图片分析结果：{image_analysis}\n用户的问题或评论：{message}\nAI的回答："
            else:
                # 构建历史对话
                history = "\n".join(self.chat_history[-3:])  # 只保留最近3轮对话
                prompt = f"{history}\n用户：{message}\nAI："
            
            # 生成回复
            response = self.text_generator(prompt)[0]["generated_text"]
            
            # 提取AI的回复部分
            if "AI：" in response:
                response = response.split("AI：")[-1].strip()
            
            # 添加到历史对话
            self.chat_history.append(f"用户：{message}")
            self.chat_history.append(f"AI：{response}")
            
            # 限制历史对话长度
            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]
            
            return response
        except Exception as e:
            logger.error(f"聊天处理失败: {e}")
            return f"聊天处理失败: {str(e)}"
    
    def process_image(self, image_path, task="analyze"):
        """处理图像，根据任务类型返回结果"""
        if not self.models_loaded:
            return "模型未加载"
        
        try:
            logger.info(f"正在处理图像 {image_path}，任务：{task}")
            
            if task == "classify":
                return self.classify_image(image_path)
            elif task == "describe":
                return self.describe_image(image_path)
            elif task == "analyze":
                return self.analyze_image(image_path)
            else:
                return f"未知任务类型: {task}"
        except Exception as e:
            logger.error(f"处理图像失败: {e}")
            return f"处理图像失败: {str(e)}"
    
    def reset_chat_history(self):
        """重置聊天历史"""
        self.chat_history = []
        logger.info("聊天历史已重置")
        return "聊天历史已重置"

# 测试代码
if __name__ == "__main__":
    # 创建模型实例
    ai_model = VisualAIModel()
    
    print("视觉AI模型已初始化")
    print(f"模型加载状态: {'成功' if ai_model.models_loaded else '失败'}")
    
    # 测试聊天功能
    if ai_model.models_loaded:
        print("\n=== 测试聊天功能 ===")
        response = ai_model.chat("你好，你能做什么？")
        print(f"问: 你好，你能做什么？")
        print(f"答: {response}")
