#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版打包脚本
只包含核心功能，不包含复杂的深度学习依赖
"""

import sys
from cx_Freeze import setup, Executable

# 包含的文件和目录
include_files = [
    ('legal_chatbot', 'legal_chatbot'),
]

# 隐藏导入 - 只包含最核心的依赖
hidden_imports = [
    'itchat',
    'requests',
    'jieba',
    'PIL',  # Pillow的正确模块名是PIL
    'cv2'   # opencv-python的正确模块名是cv2
]

# 排除不需要的模块
excludes = [
    'torch',
    'transformers',
    'datasets',
    'evaluate',
    'accelerate',
    'fastapi',
    'uvicorn',
    'pydantic',
    'redis',
    'pymongo',
    'twisted',
    'scrapy',
    'scrapy-splash',
    'scikit-learn',
    'nltk',
    'spacy',
    'lexnlp',
    'matplotlib',
    'PyQt5',
    'PyQt6',
    'tkinter',
    'jupyter',
    'notebook'
]

# 设置执行文件
setup(
    name="VisualAIChatbot",
    version="1.0",
    description="Visual AI Chatbot with WeChat Integration (Simplified Version)",
    executables=[Executable(
        "main.py",
        base=None,  # 使用console模式
        target_name="visual_ai_chatbot.exe",
        icon=None
    )],
    options={
        "build_exe": {
            "include_files": include_files,
            "includes": hidden_imports,
            "excludes": excludes,
            "build_exe": "build\visual_ai_chatbot_simple",
            "optimize": 0,
        }
    }
)
