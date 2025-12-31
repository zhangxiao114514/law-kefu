#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息类型识别系统
能够准确识别不同类型的消息内容，支持多种常见消息类型的识别
"""

import logging
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MessageType:
    """消息类型常量定义"""
    TEXT = "TEXT"
    PICTURE = "PICTURE"
    VOICE = "VOICE"
    VIDEO = "VIDEO"
    FILE = "FILE"
    MAP = "MAP"
    CARD = "CARD"
    NOTE = "NOTE"
    SHARING = "SHARING"
    FRIENDS = "FRIENDS"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


class BaseMessageRecognizer(ABC):
    """消息识别器基类"""
    
    @abstractmethod
    def recognize(self, message: Dict[str, Any]) -> Tuple[bool, float]:
        """
        识别消息类型
        
        Args:
            message: 消息字典
            
        Returns:
            Tuple[bool, float]: (是否匹配该类型, 匹配置信度)
        """
        pass
    
    @abstractmethod
    def get_type(self) -> str:
        """
        获取识别器对应的消息类型
        
        Returns:
            str: 消息类型
        """
        pass


class TextMessageRecognizer(BaseMessageRecognizer):
    """文本消息识别器"""
    
    def recognize(self, message: Dict[str, Any]) -> Tuple[bool, float]:
        """识别文本消息"""
        # 检查是否有明确的类型标记
        msg_type = message.get("Type", "")
        
        # 如果有明确的Text类型标记，直接返回最高置信度
        if msg_type in ["Text", "text"]:
            return True, 1.0
            
        # 如果有明确的非Text类型标记，直接返回不匹配
        if msg_type:
            return False, 0.0
        
        # 检查是否有文件名，有文件名的一般不是纯文本消息
        file_name = message.get("FileName", "")
        if file_name:
            return False, 0.0
        
        # 进一步检查内容是否为纯文本
        content = message.get("Content", "")
        if isinstance(content, str) and len(content) > 0:
            # 检查是否包含特殊标记
            special_patterns = [
                r"<msg>", r"<a href=", r"<location x=", r"<appmsg",
                r"<contactcard", r"<sysmsg", r"<img", r"<voice", r"<video"
            ]
            for pattern in special_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return False, 0.0
            return True, 0.9
        return False, 0.0
    
    def get_type(self) -> str:
        return MessageType.TEXT


class PictureMessageRecognizer(BaseMessageRecognizer):
    """图片消息识别器"""
    
    def recognize(self, message: Dict[str, Any]) -> Tuple[bool, float]:
        """识别图片消息"""
        msg_type = message.get("Type", "")
        if msg_type in ["Picture", "picture"]:
            return True, 1.0
        
        # 检查文件名和扩展名
        file_name = message.get("FileName", "").lower()
        if file_name:
            # 检查文件扩展名
            img_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"]
            for ext in img_extensions:
                if file_name.endswith(ext):
                    return True, 0.9
        
        # 检查是否包含图片相关标记
        content = message.get("Content", "")
        if isinstance(content, str):
            if re.search(r"<img", content, re.IGNORECASE) or re.search(r"ImageFlag", content, re.IGNORECASE) or re.search(r"cdnurl", content, re.IGNORECASE):
                return True, 0.85
        return False, 0.0
    
    def get_type(self) -> str:
        return MessageType.PICTURE


class VoiceMessageRecognizer(BaseMessageRecognizer):
    """语音消息识别器"""
    
    def recognize(self, message: Dict[str, Any]) -> Tuple[bool, float]:
        """识别语音消息"""
        msg_type = message.get("Type", "")
        if msg_type in ["Recording", "recording", "Voice", "voice"]:
            return True, 1.0
        
        # 检查文件名和扩展名
        file_name = message.get("FileName", "").lower()
        if file_name:
            # 检查文件扩展名
            voice_extensions = [".mp3", ".wav", ".amr", ".silk", ".ogg", ".aac"]
            for ext in voice_extensions:
                if file_name.endswith(ext):
                    return True, 0.9
        
        # 检查内容是否包含语音标记
        content = message.get("Content", "")
        if isinstance(content, str) and re.search(r"<voice", content, re.IGNORECASE):
            return True, 0.85
        return False, 0.0
    
    def get_type(self) -> str:
        return MessageType.VOICE


class VideoMessageRecognizer(BaseMessageRecognizer):
    """视频消息识别器"""
    
    def recognize(self, message: Dict[str, Any]) -> Tuple[bool, float]:
        """识别视频消息"""
        msg_type = message.get("Type", "")
        if msg_type in ["Video", "video"]:
            return True, 1.0
        
        # 检查文件名和扩展名
        file_name = message.get("FileName", "").lower()
        if file_name:
            # 检查文件扩展名
            video_extensions = [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm"]
            for ext in video_extensions:
                if file_name.endswith(ext):
                    return True, 0.9
        
        # 检查内容是否包含视频标记
        content = message.get("Content", "")
        if isinstance(content, str) and re.search(r"<video", content, re.IGNORECASE):
            return True, 0.85
        return False, 0.0
    
    def get_type(self) -> str:
        return MessageType.VIDEO


class FileMessageRecognizer(BaseMessageRecognizer):
    """文件消息识别器"""
    
    def recognize(self, message: Dict[str, Any]) -> Tuple[bool, float]:
        """识别文件消息"""
        msg_type = message.get("Type", "")
        if msg_type in ["Attachment", "attachment"]:
            return True, 1.0
        # 检查是否包含文件相关标记
        content = message.get("Content", "")
        if isinstance(content, str) and re.search(r"<appmsg.*?fileext", content, re.IGNORECASE):
            return True, 0.85
        return False, 0.0
    
    def get_type(self) -> str:
        return MessageType.FILE


class MapMessageRecognizer(BaseMessageRecognizer):
    """地图消息识别器"""
    
    def recognize(self, message: Dict[str, Any]) -> Tuple[bool, float]:
        """识别地图消息"""
        msg_type = message.get("Type", "")
        if msg_type in ["Map", "map"]:
            return True, 1.0
        # 检查内容是否包含地图标记
        content = message.get("Content", "")
        if isinstance(content, str) and re.search(r"<location x=", content, re.IGNORECASE):
            return True, 0.9
        return False, 0.0
    
    def get_type(self) -> str:
        return MessageType.MAP


class CardMessageRecognizer(BaseMessageRecognizer):
    """名片消息识别器"""
    
    def recognize(self, message: Dict[str, Any]) -> Tuple[bool, float]:
        """识别名片消息"""
        msg_type = message.get("Type", "")
        if msg_type in ["Card", "card"]:
            return True, 1.0
        # 检查内容是否包含名片标记
        content = message.get("Content", "")
        if isinstance(content, str) and re.search(r"<contactcard", content, re.IGNORECASE):
            return True, 0.9
        return False, 0.0
    
    def get_type(self) -> str:
        return MessageType.CARD


class SharingMessageRecognizer(BaseMessageRecognizer):
    """分享消息识别器"""
    
    def recognize(self, message: Dict[str, Any]) -> Tuple[bool, float]:
        """识别分享消息"""
        msg_type = message.get("Type", "")
        if msg_type in ["Sharing", "sharing"]:
            return True, 1.0
        # 检查内容是否包含分享标记
        content = message.get("Content", "")
        if isinstance(content, str) and re.search(r"<a href=", content, re.IGNORECASE):
            return True, 0.85
        return False, 0.0
    
    def get_type(self) -> str:
        return MessageType.SHARING


class NoteMessageRecognizer(BaseMessageRecognizer):
    """通知消息识别器"""
    
    def recognize(self, message: Dict[str, Any]) -> Tuple[bool, float]:
        """识别通知消息"""
        msg_type = message.get("Type", "")
        if msg_type in ["Note", "note"]:
            return True, 1.0
        # 检查内容是否包含通知标记
        content = message.get("Content", "")
        if isinstance(content, str) and re.search(r"<sysmsg" or r"<note", content, re.IGNORECASE):
            return True, 0.8
        return False, 0.0
    
    def get_type(self) -> str:
        return MessageType.NOTE


class FriendsMessageRecognizer(BaseMessageRecognizer):
    """好友请求消息识别器"""
    
    def recognize(self, message: Dict[str, Any]) -> Tuple[bool, float]:
        """识别好友请求消息"""
        msg_type = message.get("Type", "")
        if msg_type in ["Friends", "friends"]:
            return True, 1.0
        return False, 0.0
    
    def get_type(self) -> str:
        return MessageType.FRIENDS


class SystemMessageRecognizer(BaseMessageRecognizer):
    """系统消息识别器"""
    
    def recognize(self, message: Dict[str, Any]) -> Tuple[bool, float]:
        """识别系统消息"""
        msg_type = message.get("Type", "")
        if msg_type in ["System", "system"]:
            return True, 1.0
        # 检查内容是否包含系统消息标记
        content = message.get("Content", "")
        if isinstance(content, str) and re.search(r"<sysmsg" or r"系统消息", content, re.IGNORECASE):
            return True, 0.8
        return False, 0.0
    
    def get_type(self) -> str:
        return MessageType.SYSTEM


class MessageTypeIdentifier:
    """消息类型识别器主类"""
    
    def __init__(self):
        """初始化消息类型识别器"""
        self.recognizers: List[BaseMessageRecognizer] = []
        self._register_default_recognizers()
    
    def _register_default_recognizers(self):
        """注册默认的消息识别器"""
        # 按优先级注册识别器
        self.recognizers.extend([
            TextMessageRecognizer(),
            PictureMessageRecognizer(),
            VoiceMessageRecognizer(),
            VideoMessageRecognizer(),
            FileMessageRecognizer(),
            MapMessageRecognizer(),
            CardMessageRecognizer(),
            SharingMessageRecognizer(),
            NoteMessageRecognizer(),
            FriendsMessageRecognizer(),
            SystemMessageRecognizer()
        ])
    
    def register_recognizer(self, recognizer: BaseMessageRecognizer):
        """
        注册自定义消息识别器
        
        Args:
            recognizer: 消息识别器实例
        """
        self.recognizers.append(recognizer)
    
    def recognize(self, message: Dict[str, Any]) -> Tuple[str, float]:
        """
        识别消息类型
        
        Args:
            message: 消息字典
            
        Returns:
            Tuple[str, float]: (消息类型, 置信度)
        """
        best_type = MessageType.UNKNOWN
        best_confidence = 0.0
        
        for recognizer in self.recognizers:
            try:
                is_match, confidence = recognizer.recognize(message)
                if is_match and confidence > best_confidence:
                    best_type = recognizer.get_type()
                    best_confidence = confidence
            except Exception as e:
                logger.error(f"{recognizer.get_type()}识别器出错: {e}")
        
        return best_type, best_confidence
    
    def batch_recognize(self, messages: List[Dict[str, Any]]) -> List[Tuple[str, float]]:
        """
        批量识别消息类型
        
        Args:
            messages: 消息字典列表
            
        Returns:
            List[Tuple[str, float]]: 消息类型和置信度列表
        """
        results = []
        for message in messages:
            results.append(self.recognize(message))
        return results
    
    def get_supported_types(self) -> List[str]:
        """
        获取支持的消息类型
        
        Returns:
            List[str]: 支持的消息类型列表
        """
        return [recognizer.get_type() for recognizer in self.recognizers] + [MessageType.UNKNOWN]
