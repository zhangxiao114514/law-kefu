#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试C++扩展功能
"""

import ctypes
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_cpp_extension():
    """测试C++扩展功能"""
    logger.info("开始测试C++扩展功能")
    
    try:
        # 加载C++扩展
        extension = ctypes.CDLL('./wechat_extension.dll')
        logger.info("成功加载C++扩展")
        
        # 初始化扩展
        extension.initialize_extension.argtypes = None
        extension.initialize_extension.restype = ctypes.c_bool
        
        result = extension.initialize_extension(None)
        if result:
            logger.info("成功初始化C++扩展")
        else:
            logger.error("初始化C++扩展失败")
            return
        
        # 获取扩展信息
        extension.get_extension_info.argtypes = None
        extension.get_extension_info.restype = ctypes.c_char_p
        
        info = extension.get_extension_info()
        if info:
            logger.info(f"C++扩展信息: {info.decode('utf-8')}")
        
        # 测试消息处理功能
        extension.process_wechat_message.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
        extension.process_wechat_message.restype = None
        
        # 测试文本消息
        logger.info("测试处理文本消息")
        extension.process_wechat_message(
            "测试用户".encode('utf-8'), 
            "你好，这是一条测试消息".encode('utf-8'), 
            0  # MSG_TYPE_TEXT
        )
        
        # 测试图片消息
        logger.info("测试处理图片消息")
        extension.process_wechat_message(
            "测试用户".encode('utf-8'), 
            "图片消息内容".encode('utf-8'), 
            1  # MSG_TYPE_IMAGE
        )
        
        # 测试语音消息
        logger.info("测试处理语音消息")
        extension.process_wechat_message(
            "测试用户".encode('utf-8'), 
            "语音消息内容".encode('utf-8'), 
            2  # MSG_TYPE_VOICE
        )
        
        # 关闭扩展
        extension.shutdown_extension.argtypes = None
        extension.shutdown_extension.restype = None
        
        extension.shutdown_extension()
        logger.info("成功关闭C++扩展")
        
        logger.info("C++扩展功能测试完成")
        
    except Exception as e:
        logger.error(f"测试C++扩展功能时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_cpp_extension()
