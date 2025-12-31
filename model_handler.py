#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型处理模块，用于与自训练模型交互
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from rule_based_visual_ai import RuleBasedVisualAIModel as VisualAIModel

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


class ModelInterface(ABC):
    """模型接口抽象类"""
    
    @abstractmethod
    def process(self, input_data: Any, **kwargs) -> Tuple[bool, Any]:
        """处理输入数据并返回结果
        
        Args:
            input_data: 输入数据
            **kwargs: 额外参数
            
        Returns:
            Tuple[bool, Any]: (成功标志, 处理结果或错误信息)
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Any) -> Tuple[bool, str]:
        """验证输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            Tuple[bool, str]: (验证通过标志, 错误信息)
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息
        
        Returns:
            Dict[str, Any]: 模型信息字典
        """
        pass


class BaseModelAdapter(ModelInterface):
    """基础模型适配器，实现通用模型功能"""
    
    def __init__(self, model_type: str, model_path: Optional[str] = None):
        """初始化模型适配器
        
        Args:
            model_type: 模型类型
            model_path: 模型路径
        """
        self.model_type = model_type
        self.model_path = model_path
        self.model = None
        self.loaded = False
        self.load_time = 0
        
        # 加载模型
        self._load_model()
    
    def _load_model(self):
        """加载模型"""
        try:
            # 加载VisualAIModel单例实例
            start_time = time.time()
            self.model = VisualAIModel()  # 使用单例模式
            self.load_time = time.time() - start_time
            self.loaded = True
            logger.info(f"成功加载{self.model_type}模型，耗时: {self.load_time:.2f}秒")
        except Exception as e:
            logger.error(f"加载{self.model_type}模型失败: {e}")
            self.loaded = False
    
    def validate_input(self, input_data: Any) -> Tuple[bool, str]:
        """验证输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            Tuple[bool, str]: (验证通过标志, 错误信息)
        """
        if input_data is None:
            return False, "输入数据不能为空"
        
        if not isinstance(input_data, (str, bytes)):
            return False, "输入数据必须是字符串或字节流"
        
        if isinstance(input_data, str) and len(input_data.strip()) == 0:
            return False, "输入文本不能为空"
        
        return True, ""
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息
        
        Returns:
            Dict[str, Any]: 模型信息字典
        """
        return {
            "model_type": self.model_type,
            "model_path": self.model_path,
            "loaded": self.loaded,
            "load_time": self.load_time
        }


class MultiPurposeModelAdapter(BaseModelAdapter):
    """多用途模型适配器，支持文本、图像和视觉AI功能"""
    
    def __init__(self, model_path: Optional[str] = None):
        """初始化多用途模型适配器
        
        Args:
            model_path: 模型路径
        """
        super().__init__("multi_purpose", model_path)
    
    def process(self, input_data: Any, **kwargs) -> Tuple[bool, Any]:
        """处理输入数据
        
        Args:
            input_data: 输入数据，可以是文本或图像路径
            **kwargs: 额外参数
            
        Returns:
            Tuple[bool, Any]: (成功标志, 处理结果或错误信息)
        """
        # 验证输入
        is_valid, error_msg = self.validate_input(input_data)
        if not is_valid:
            return False, error_msg
        
        # 检查模型是否加载
        if not self.loaded:
            return False, "模型未加载"
        
        try:
            # 根据输入类型和参数选择处理方式
            image_path = kwargs.get("image_path")
            if image_path:
                # 处理带有图像的请求
                result = self.model.chat(input_data, image_path=image_path)
                logger.info(f"视觉AI模型处理成功")
            else:
                # 检查是否是图像分析请求
                if kwargs.get("task") == "analyze_image" or isinstance(input_data, str) and input_data.endswith((".jpg", ".jpeg", ".png", ".bmp")):
                    result = self.model.analyze_image(input_data)
                    logger.info(f"图像分析处理成功")
                else:
                    # 普通文本处理
                    result = self.model.chat(input_data)
                    logger.info(f"文本处理成功: {input_data[:50]}...")
            
            return True, result
        except Exception as e:
            error_msg = f"模型处理失败: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def validate_input(self, input_data: Any) -> Tuple[bool, str]:
        """验证输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            Tuple[bool, str]: (验证通过标志, 错误信息)
        """
        if input_data is None:
            return False, "输入数据不能为空"
        
        if not isinstance(input_data, (str, bytes)):
            return False, "输入数据必须是字符串或字节流"
        
        if isinstance(input_data, str):
            if len(input_data.strip()) == 0:
                return False, "输入文本不能为空"
            
            if len(input_data) > 1000:
                return False, "输入文本长度不能超过1000字符"
        
        return True, ""
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息
        
        Returns:
            Dict[str, Any]: 模型信息字典
        """
        info = super().get_model_info()
        info.update({
            "capabilities": ["image_classification", "image_description", "chat", "image_analysis"]
        })
        return info


class ModelHandler:
    """模型处理器，管理不同类型的模型"""
    
    def __init__(self):
        """初始化模型处理器"""
        self.models: Dict[str, ModelInterface] = {}
        self.default_model = None
        
        logger.info("模型处理器初始化完成")
    
    def register_model(self, model_type: str, model: ModelInterface, is_default: bool = False):
        """注册模型
        
        Args:
            model_type: 模型类型
            model: 模型实例
            is_default: 是否设置为默认模型
        """
        self.models[model_type] = model
        if is_default:
            self.default_model = model_type
        
        logger.info(f"已注册模型类型: {model_type}, 是否默认: {is_default}")
    
    def get_model(self, model_type: Optional[str] = None) -> Optional[ModelInterface]:
        """获取模型实例
        
        Args:
            model_type: 模型类型
            
        Returns:
            Optional[ModelInterface]: 模型实例
        """
        if model_type and model_type in self.models:
            return self.models[model_type]
        
        if self.default_model and self.default_model in self.models:
            return self.models[self.default_model]
        
        # 返回第一个可用模型
        return next(iter(self.models.values()), None) if self.models else None
    
    def process(self, input_data: Any, model_type: Optional[str] = None, **kwargs) -> Tuple[bool, Any]:
        """处理输入数据
        
        Args:
            input_data: 输入数据
            model_type: 模型类型
            **kwargs: 额外参数
            
        Returns:
            Tuple[bool, Any]: (成功标志, 处理结果或错误信息)
        """
        # 获取模型
        model = self.get_model(model_type)
        if not model:
            return False, "未找到匹配的模型"
        
        # 调用模型处理
        return model.process(input_data, **kwargs)
    
    def validate_input(self, input_data: Any, model_type: Optional[str] = None) -> Tuple[bool, str]:
        """验证输入数据
        
        Args:
            input_data: 输入数据
            model_type: 模型类型
            
        Returns:
            Tuple[bool, str]: (验证通过标志, 错误信息)
        """
        # 获取模型
        model = self.get_model(model_type)
        if not model:
            return False, "未找到匹配的模型"
        
        # 调用模型验证
        return model.validate_input(input_data)
    
    def get_model_info(self, model_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取模型信息
        
        Args:
            model_type: 模型类型
            
        Returns:
            Optional[Dict[str, Any]]: 模型信息字典
        """
        model = self.get_model(model_type)
        if not model:
            return None
        
        return model.get_model_info()
    
    def get_all_model_info(self) -> Dict[str, Dict[str, Any]]:
        """获取所有模型信息
        
        Returns:
            Dict[str, Dict[str, Any]]: 所有模型信息
        """
        return {
            model_type: model.get_model_info() 
            for model_type, model in self.models.items()
        }
    
    def is_model_available(self, model_type: Optional[str] = None) -> bool:
        """检查模型是否可用
        
        Args:
            model_type: 模型类型
            
        Returns:
            bool: 模型是否可用
        """
        model = self.get_model(model_type)
        if not model:
            return False
        
        info = model.get_model_info()
        return info.get("loaded", False)


# 创建全局模型处理器实例
model_handler = ModelHandler()

# 初始化并注册默认模型
def initialize_default_models():
    """初始化并注册默认模型"""
    try:
        # 创建多用途模型适配器（作为默认模型）
        multi_purpose_model = MultiPurposeModelAdapter()
        
        # 注册模型，支持多种类型
        model_handler.register_model("visual_ai", multi_purpose_model, is_default=True)
        model_handler.register_model("text", multi_purpose_model)
        model_handler.register_model("image", multi_purpose_model)
        model_handler.register_model("multi_purpose", multi_purpose_model)
        
        logger.info("默认模型初始化完成")
        return True
    except Exception as e:
        logger.error(f"初始化默认模型失败: {e}")
        return False


if __name__ == "__main__":
    # 测试模型处理器
    initialize_default_models()
    
    # 测试文本模型
    success, result = model_handler.process("你好，这是一个测试", "text")
    print(f"文本模型测试结果: 成功={success}, 结果={result}")
    
    # 测试图像模型
    success, result = model_handler.process("test_image.jpg", "image")
    print(f"图像模型测试结果: 成功={success}, 结果={result}")
    
    # 测试视觉AI模型
    success, result = model_handler.process("分析一下这张图片", "visual_ai", image_path="test_image.jpg")
    print(f"视觉AI模型测试结果: 成功={success}, 结果={result}")
