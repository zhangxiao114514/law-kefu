#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视觉AI模型类
支持图像识别、分类和交互式聊天功能
"""

import torch
import torchvision.transforms as transforms
from PIL import Image
import cv2
import numpy as np
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VisualAIModel:
    """视觉AI模型类"""
    
    def __init__(self):
        """初始化模型"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"使用设备: {self.device}")
        
        # 初始化图像分类模型
        self.image_classifier = self._load_image_classifier()
        
        # 初始化图像描述模型
        self.image_captioner = self._load_image_captioner()
        
        # 初始化聊天模型
        self.chat_model, self.chat_tokenizer = self._load_chat_model()
        
        # 图像预处理转换
        self.image_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                std=[0.229, 0.224, 0.225])
        ])
        
        # 历史对话记录
        self.chat_history = []
    
    def _load_image_classifier(self):
        """加载图像分类模型"""
        try:
            logger.info("正在加载图像分类模型...")
            classifier = pipeline("image-classification", 
                                model="google/vit-base-patch16-224",
                                device=self.device)
            logger.info("图像分类模型加载成功")
            return classifier
        except Exception as e:
            logger.error(f"加载图像分类模型失败: {e}")
            return None
    
    def _load_image_captioner(self):
        """加载图像描述生成模型"""
        try:
            logger.info("正在加载图像描述生成模型...")
            captioner = pipeline("image-to-text", 
                                model="Salesforce/blip-image-captioning-base",
                                device=self.device)
            logger.info("图像描述生成模型加载成功")
            return captioner
        except Exception as e:
            logger.error(f"加载图像描述生成模型失败: {e}")
            return None
    
    def _load_chat_model(self):
        """加载聊天模型"""
        try:
            logger.info("正在加载聊天模型...")
            # 使用轻量级的中文聊天模型
            model_name = "THUDM/chatglm3-6b"
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained(model_name, 
                                                        trust_remote_code=True,
                                                        device_map="auto")
            model = model.eval()
            logger.info("聊天模型加载成功")
            return model, tokenizer
        except Exception as e:
            logger.error(f"加载聊天模型失败: {e}")
            # 回退到英文模型
            try:
                logger.info("尝试加载英文聊天模型...")
                model_name = "microsoft/DialoGPT-medium"
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(model_name)
                model = model.eval()
                logger.info("英文聊天模型加载成功")
                return model, tokenizer
            except Exception as e2:
                logger.error(f"加载英文聊天模型失败: {e2}")
                return None, None
    
    def classify_image(self, image_path):
        """对图像进行分类"""
        if not self.image_classifier:
            return "图像分类模型不可用"
        
        try:
            logger.info(f"正在分类图像: {image_path}")
            results = self.image_classifier(image_path)
            
            # 格式化结果
            classification_result = "图像分类结果：\n"
            for result in results[:3]:  # 只返回前3个结果
                classification_result += f"- {result['label']}: {result['score']:.4f}\n"
            
            return classification_result.strip()
        except Exception as e:
            logger.error(f"图像分类失败: {e}")
            return f"图像分类失败: {str(e)}"
    
    def describe_image(self, image_path):
        """生成图像描述"""
        if not self.image_captioner:
            return "图像描述模型不可用"
        
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
        if not self.chat_model or not self.chat_tokenizer:
            return "聊天模型不可用"
        
        try:
            logger.info(f"正在处理聊天消息: {message}")
            
            # 如果提供了图像，先分析图像
            image_analysis = ""
            if image_path:
                image_analysis = self.analyze_image(image_path)
                logger.info(f"图像分析结果: {image_analysis}")
            
            # 构建对话上下文
            if image_analysis:
                full_message = f"用户发送了一张图片，图片分析结果：{image_analysis}\n用户的问题或评论：{message}"
            else:
                full_message = message
            
            # 添加到历史对话
            self.chat_history.append(full_message)
            
            # 构建输入
            input_text = "\n".join(self.chat_history)
            
            # 生成回复
            if "chatglm" in self.chat_model.config._name_or_path.lower():
                # ChatGLM模型处理
                response, _ = self.chat_model.chat(self.chat_tokenizer, full_message, history=[])
            else:
                # 其他模型处理
                inputs = self.chat_tokenizer.encode(input_text + self.chat_tokenizer.eos_token, return_tensors="pt")
                outputs = self.chat_model.generate(inputs, max_length=1024, pad_token_id=self.chat_tokenizer.eos_token_id)
                response = self.chat_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # 添加到历史对话
            self.chat_history.append(f"AI: {response}")
            
            # 限制历史对话长度
            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]
            
            return response
        except Exception as e:
            logger.error(f"聊天处理失败: {e}")
            return f"聊天处理失败: {str(e)}"
    
    def process_image(self, image_path, task="analyze"):
        """处理图像，根据任务类型返回结果"""
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
    print(f"使用设备: {ai_model.device}")
    
    # 测试分类功能
    # test_image = "test.jpg"
    # if os.path.exists(test_image):
    #     print("\n=== 测试图像分类 ===")
    #     result = ai_model.classify_image(test_image)
    #     print(result)
    #     
    #     print("\n=== 测试图像描述 ===")
    #     result = ai_model.describe_image(test_image)
    #     print(result)
    #     
    #     print("\n=== 测试图像综合分析 ===")
    #     result = ai_model.analyze_image(test_image)
    #     print(result)
    # else:
    #     print(f"测试图像 {test_image} 不存在")
    
    # 测试聊天功能
    print("\n=== 测试聊天功能 ===")
    response = ai_model.chat("你好，你能做什么？")
    print(f"AI: {response}")
    
    response = ai_model.chat("解释一下什么是计算机视觉")
    print(f"AI: {response}")
