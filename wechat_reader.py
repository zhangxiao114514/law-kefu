#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信消息读取模块
"""

import itchat
from itchat.content import *
import logging
import ctypes
import os
import time
import shutil
from rule_based_visual_ai import RuleBasedVisualAIModel as VisualAIModel
from message_type_identifier import MessageTypeIdentifier, MessageType
from auto_reply_manager import AutoReplyManager
from model_handler import model_handler, initialize_default_models

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WeChatReader:
    """微信消息读取器类"""
    
    # 配置常量
    TEMP_MEDIA_DIR = os.path.join(os.getcwd(), 'temp_media')
    MAX_TEMP_FILE_AGE = 3600  # 临时文件最大保留时间（秒）
    
    def __init__(self):
        """初始化"""
        # 初始化itchat
        self.itchat = itchat.new_instance()
        # 初始化消息类型识别器
        self.message_identifier = MessageTypeIdentifier()
        # 初始化自动回复管理器
        self.auto_reply_manager = AutoReplyManager()
        # 初始化模型处理器
        initialize_default_models()
        # 初始化C++扩展
        self.cpp_extension = None
        self.msg_type_map = {
            'Text': 0,      # MSG_TYPE_TEXT
            'Picture': 1,   # MSG_TYPE_IMAGE
            'Voice': 2,     # MSG_TYPE_VOICE
            'Video': 3,     # MSG_TYPE_VIDEO
            'Attachment': 4 # MSG_TYPE_FILE
        }
        
        # 创建临时目录
        self._ensure_temp_dir_exists()
        # 清理旧的临时文件
        self._cleanup_old_temp_files()
        # 注册消息处理函数
        self._register_message_handlers()
        # 尝试加载C++扩展
        self._load_cpp_extension()
        
        logger.info("微信消息读取器初始化完成")
    
    def _ensure_temp_dir_exists(self):
        """确保临时目录存在"""
        try:
            if not os.path.exists(self.TEMP_MEDIA_DIR):
                os.makedirs(self.TEMP_MEDIA_DIR)
                logger.info(f"已创建临时目录: {self.TEMP_MEDIA_DIR}")
        except Exception as e:
            logger.error(f"创建临时目录失败: {e}")
    
    def _cleanup_old_temp_files(self):
        """清理旧的临时文件"""
        try:
            current_time = time.time()
            removed_files = 0
            
            for file_name in os.listdir(self.TEMP_MEDIA_DIR):
                file_path = os.path.join(self.TEMP_MEDIA_DIR, file_name)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > self.MAX_TEMP_FILE_AGE:
                        os.remove(file_path)
                        removed_files += 1
            
            if removed_files > 0:
                logger.info(f"已清理 {removed_files} 个旧的临时文件")
        except Exception as e:
            logger.error(f"清理旧临时文件失败: {e}")
    
    def _load_cpp_extension(self):
        """加载C++扩展"""
        try:
            # 尝试加载C++动态链接库
            dll_path = os.path.join(os.getcwd(), 'wechat_extension.dll')
            if not os.path.exists(dll_path):
                logger.warning(f"C++扩展文件不存在: {dll_path}")
                return
            
            self.cpp_extension = ctypes.CDLL(dll_path)
            logger.info("成功加载C++扩展")
            
            # 设置函数参数类型和返回类型
            self.cpp_extension.initialize_extension.argtypes = [ctypes.c_void_p]
            self.cpp_extension.initialize_extension.restype = ctypes.c_bool
            
            self.cpp_extension.process_wechat_message.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
            self.cpp_extension.process_wechat_message.restype = None
            
            self.cpp_extension.get_extension_info.argtypes = None
            self.cpp_extension.get_extension_info.restype = ctypes.c_char_p
            
            self.cpp_extension.shutdown_extension.argtypes = None
            self.cpp_extension.shutdown_extension.restype = None
            
            # 初始化扩展
            result = self.cpp_extension.initialize_extension(None)
            if result:
                logger.info("成功初始化C++扩展")
                # 获取扩展信息
                info = self.cpp_extension.get_extension_info()
                if info:
                    logger.info(f"C++扩展信息: {info.decode('utf-8')}")
            else:
                logger.error("初始化C++扩展失败")
                self.cpp_extension = None
        except Exception as e:
            logger.warning(f"未能加载C++扩展: {e}")
            self.cpp_extension = None
    
    def _register_message_handlers(self):
        """注册消息处理函数"""
        # 注册所有消息类型的处理函数
        message_types = [TEXT, PICTURE, VOICE, VIDEO, ATTACHMENT]
        
        @self.itchat.msg_register(message_types, isFriendChat=True, isGroupChat=True)
        def message_handler(msg):
            self._handle_message(msg)
        
        # 消息类型映射，将itchat常量转换为可读名称
        msg_type_names = {
            TEXT: '文本',
            PICTURE: '图片',
            VOICE: '语音',
            VIDEO: '视频',
            ATTACHMENT: '附件'
        }
        logger.info(f"已注册消息处理器，支持类型: {[msg_type_names.get(t, str(t)) for t in message_types]}")
    
    def _validate_message(self, msg):
        """验证消息的有效性
        
        Args:
            msg: 原始消息对象
            
        Returns:
            bool: 消息是否有效
        """
        required_fields = ['Type', 'FromUserName', 'Content', 'User']
        for field in required_fields:
            if field not in msg:
                logger.error(f"消息缺少必填字段: {field}")
                return False
        
        return True
    
    def _download_media_file(self, msg):
        """下载媒体文件
        
        Args:
            msg: 原始消息对象
            
        Returns:
            str: 下载后的文件路径，失败返回None
        """
        try:
            file_name = msg.get('FileName', 'unknown_file')
            logger.info(f"正在下载媒体文件: {file_name}")
            
            # 获取文件后缀
            _, file_suffix = os.path.splitext(file_name)
            if not file_suffix:
                # 根据消息类型猜测后缀
                if msg['Type'] == 'Picture':
                    file_suffix = '.jpg'
                elif msg['Type'] == 'Voice':
                    file_suffix = '.mp3'
                elif msg['Type'] == 'Video':
                    file_suffix = '.mp4'
                else:
                    file_suffix = '.unknown'
            
            # 生成唯一的临时文件路径
            timestamp = int(time.time() * 1000)  # 毫秒级时间戳
            random_suffix = os.urandom(4).hex()  # 4字节随机十六进制字符串
            temp_file_name = f"{timestamp}_{random_suffix}{file_suffix}"
            file_path = os.path.join(self.TEMP_MEDIA_DIR, temp_file_name)
            
            # 调用itchat的下载方法
            msg['Text'](file_path)
            
            if os.path.exists(file_path):
                logger.info(f"成功下载媒体文件到: {file_path}")
                return file_path
            else:
                logger.error(f"下载后文件不存在: {file_path}")
                return None
        except Exception as e:
            logger.error(f"下载媒体文件失败: {e}")
            return None
    
    def _generate_response(self, msg, sender, content, identified_type):
        """生成回复
        
        Args:
            msg: 原始消息对象
            sender: 发送者ID
            content: 消息内容
            identified_type: 识别的消息类型
            
        Returns:
            str: 回复内容，None表示不回复
        """
        try:
            # 首先尝试使用自动回复管理器获取回复
            response = self.auto_reply_manager.handle_message(sender, content)
            
            if response:
                logger.info(f"使用自动回复生成回复")
                return response
            
            # 如果自动回复管理器没有生成回复，使用模型处理器
            logger.info(f"使用模型处理器生成回复")
            
            if identified_type == MessageType.TEXT:
                # 文本消息处理
                model_type = "text"
                input_data = content
                success, result = model_handler.process(input_data, model_type)
            elif identified_type in [MessageType.PICTURE, MessageType.VOICE, MessageType.VIDEO]:
                # 媒体消息处理
                model_type = "visual_ai"
                
                # 下载媒体文件
                file_path = self._download_media_file(msg)
                if not file_path:
                    return "抱歉，下载媒体文件失败。"
                
                try:
                    # 使用模型生成回复
                    success, result = model_handler.process("分析一下这张图片", model_type, image_path=file_path)
                finally:
                    # 确保临时文件被删除
                    if os.path.exists(file_path):
                        os.remove(file_path)
            else:
                # 其他类型消息处理
                model_type = "text"
                input_data = f"收到{identified_type}类型的消息"
                success, result = model_handler.process(input_data, model_type)
            
            if success:
                return str(result) if isinstance(result, dict) else result
            else:
                logger.error(f"模型处理失败: {result}")
                return "抱歉，我现在无法为您生成回复，请稍后重试。"
        except Exception as e:
            logger.error(f"生成回复失败: {e}")
            return "抱歉，处理您的消息时发生错误。"
    
    def _send_response(self, msg, response):
        """发送回复
        
        Args:
            msg: 原始消息对象
            response: 回复内容
            
        Returns:
            bool: 发送是否成功
        """
        try:
            # 验证回复内容
            if not isinstance(response, str) or len(response.strip()) == 0:
                logger.warning(f"无效的回复内容: {response}")
                return False
            
            # 发送回复
            self.itchat.send_msg(response, toUserName=msg['FromUserName'])
            logger.info(f"已发送回复: {response[:50]}... 给 {msg['FromUserName']}")
            return True
        except Exception as e:
            logger.error(f"发送回复失败: {e}")
            return False
    
    def _handle_message(self, msg):
        """处理接收到的消息"""
        try:
            logger.debug(f"收到原始消息: {msg}")
            
            # 验证消息基本信息
            if not self._validate_message(msg):
                return
            
            # 提取消息信息
            original_msg_type = msg['Type']
            sender = msg['FromUserName']
            content = msg['Content']
            nick_name = msg['User']['NickName'] if 'NickName' in msg['User'] else sender
            
            # 使用消息类型识别器识别消息类型
            identified_type, confidence = self.message_identifier.recognize(msg)
            
            # 打印消息信息
            print(f"\n[原始类型: {original_msg_type}] [识别类型: {identified_type}] [置信度: {confidence:.2f}] 来自 {nick_name}")
            if identified_type == MessageType.TEXT:
                print(f"内容: {content}")
            else:
                file_name = msg.get('FileName', '未知文件名')
                print(f"文件名: {file_name}")
            
            # 处理消息并生成回复
            response = self._generate_response(msg, sender, content, identified_type)
            
            # 发送回复
            if response:
                self._send_response(msg, response)
            
            # 如果C++扩展可用，调用C++处理函数
            if self.cpp_extension:
                try:
                    # 将Python字符串转换为C字符串
                    nick_name_c = nick_name.encode('utf-8')
                    content_c = content.encode('utf-8')
                    msg_type_c = self.msg_type_map.get(original_msg_type, 0)
                    
                    # 调用C++函数处理消息
                    self.cpp_extension.process_wechat_message(nick_name_c, content_c, msg_type_c)
                except Exception as e:
                    logger.error(f"调用C++扩展失败: {e}")
        except Exception as e:
            logger.error(f"处理消息时发生异常: {e}")
    
    def login(self):
        """登录微信"""
        logger.info("正在登录微信...")
        try:
            # 登录微信，使用二维码扫描登录
            self.itchat.auto_login(hotReload=True, enableCmdQR=True)
            logger.info("微信登录成功")
            return True
        except Exception as e:
            logger.error(f"微信登录失败: {e}")
            return False
    
    def start_listening(self):
        """开始监听消息"""
        logger.info("开始监听微信消息...")
        print("微信消息读取已启动，按Ctrl+C停止")
        try:
            # 开始运行itchat
            self.itchat.run()
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在退出...")
            self.logout()
        except Exception as e:
            logger.error(f"监听消息时发生异常: {e}")
            self.logout()
    
    def logout(self):
        """退出登录"""
        logger.info("正在退出微信...")
        
        # 关闭C++扩展
        if self.cpp_extension:
            try:
                self.cpp_extension.shutdown_extension()
                logger.info("成功关闭C++扩展")
            except Exception as e:
                logger.error(f"关闭C++扩展时出错: {e}")
            finally:
                self.cpp_extension = None
        
        # 退出微信
        try:
            self.itchat.logout()
            logger.info("微信已退出")
        except Exception as e:
            logger.error(f"微信退出失败: {e}")
        
        # 清理临时文件
        try:
            shutil.rmtree(self.TEMP_MEDIA_DIR)
            logger.info(f"已删除临时目录: {self.TEMP_MEDIA_DIR}")
        except Exception as e:
            logger.error(f"删除临时目录失败: {e}")
