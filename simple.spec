# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('legal_chatbot', 'legal_chatbot')],
    hiddenimports=['itchat', 'torch', 'transformers', 'numpy', 'pandas', 'scikit-learn', 'nltk', 'spacy', 'jieba', 'requests', 'beautifulsoup4', 'lxml', 'twisted', 'scrapy', 'scrapy-splash', 'fastapi', 'uvicorn', 'pydantic', 'redis', 'pymongo', 'loguru', 'python-dotenv', 'click', 'tqdm', 'lexnlp', 'Pillow', 'opencv-python'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='visual_ai_chatbot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
