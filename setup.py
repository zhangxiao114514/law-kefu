from cx_Freeze import setup, Executable
import sys
import os

# 包含的文件和目录
include_files = [
    ('legal_chatbot', 'legal_chatbot'),
]

# 隐藏导入
hidden_imports = [
    'itchat',
    'torch',
    'transformers',
    'numpy',
    'pandas',
    'scikit-learn',
    'nltk',
    'spacy',
    'jieba',
    'requests',
    'beautifulsoup4',
    'lxml',
    'twisted',
    'scrapy',
    'scrapy-splash',
    'fastapi',
    'uvicorn',
    'pydantic',
    'redis',
    'pymongo',
    'loguru',
    'python-dotenv',
    'click',
    'tqdm',
    'lexnlp',
    'Pillow',
    'opencv-python'
]

# 排除不需要的模块
excludes = [
    'tkinter',
    'matplotlib',
    'PyQt5',
    'PyQt6',
    'jupyter',
    'notebook'
]

# 设置执行文件
setup(
    name="VisualAIChatbot",
    version="1.0",
    description="Visual AI Chatbot with WeChat Integration",
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
            "build_exe": "build\visual_ai_chatbot",
            "optimize": 0,
            "packages": ["torch", "transformers"]
        }
    }
)
