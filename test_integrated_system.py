#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试集成系统
"""

print("=== 测试集成系统 ===")

try:
    print("1. 导入model_handler...")
    from model_handler import model_handler, initialize_default_models
    print("✅ model_handler导入成功")
except Exception as e:
    print(f"❌ model_handler导入失败: {e}")
    exit(1)

try:
    print("\n2. 初始化默认模型...")
    success = initialize_default_models()
    print(f"✅ 默认模型初始化 {'成功' if success else '失败'}")
except Exception as e:
    print(f"❌ 默认模型初始化失败: {e}")
    exit(1)

try:
    print("\n3. 测试文本模型处理...")
    success, result = model_handler.process("你好，你能做什么？", "text")
    print(f"✅ 文本模型处理 {'成功' if success else '失败'}")
    if success:
        print(f"   结果: {result}")
except Exception as e:
    print(f"❌ 文本模型处理失败: {e}")

try:
    print("\n4. 测试视觉AI模型处理...")
    # 使用不存在的图像文件进行测试
    success, result = model_handler.process("这是一张猫的图片", "visual_ai", image_path="cat.jpg")
    print(f"✅ 视觉AI模型处理 {'成功' if success else '失败'}")
    if success:
        print(f"   结果: {result}")
except Exception as e:
    print(f"❌ 视觉AI模型处理失败: {e}")

try:
    print("\n5. 测试图像模型处理...")
    # 使用不存在的图像文件进行测试
    success, result = model_handler.process("cat.jpg", "image")
    print(f"✅ 图像模型处理 {'成功' if success else '失败'}")
    if success:
        print(f"   结果: {result}")
except Exception as e:
    print(f"❌ 图像模型处理失败: {e}")

print("\n=== 测试完成 ===")
