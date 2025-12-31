#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试脚本，用于测试法律智能客服系统各个模块的功能
"""

import os
import sys
import logging
from loguru import logger

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置环境变量，指定配置文件路径
os.environ["CONFIG_PATH"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "legal_chatbot", "config", "config.yaml")

def test_config():
    """测试配置文件加载功能"""
    logger.info("开始测试配置文件加载功能")
    
    try:
        from legal_chatbot.utils.config import get_config
        
        # 测试加载配置
        project_name = get_config("base.project_name", "default_name")
        logger.info(f"项目名称: {project_name}")
        
        # 测试加载嵌套配置
        model_name = get_config("training.pretrained_model.name", "default_model")
        logger.info(f"预训练模型名称: {model_name}")
        
        # 测试加载不存在的配置
        non_existent = get_config("non_existent.key", "default_value")
        logger.info(f"不存在的配置项，返回默认值: {non_existent}")
        
        logger.info("配置文件加载测试通过")
        return True
    except Exception as e:
        logger.error(f"配置文件加载测试失败: {e}")
        return False

def test_logger():
    """测试日志系统功能"""
    logger.info("开始测试日志系统功能")
    
    try:
        from legal_chatbot.utils.logger import setup_logger
        
        # 测试设置日志级别
        setup_logger(level="DEBUG")
        
        # 测试不同级别的日志
        logger.debug("这是一条DEBUG级别的日志")
        logger.info("这是一条INFO级别的日志")
        logger.warning("这是一条WARNING级别的日志")
        logger.error("这是一条ERROR级别的日志")
        logger.critical("这是一条CRITICAL级别的日志")
        
        logger.info("日志系统测试通过")
        return True
    except Exception as e:
        logger.error(f"日志系统测试失败: {e}")
        return False

def test_entity_recognizer():
    """测试实体识别模块"""
    logger.info("开始测试实体识别模块")
    
    try:
        from legal_chatbot.preprocessing.entity_recognizer import EntityRecognizer
        
        # 初始化实体识别器
        recognizer = EntityRecognizer()
        
        # 测试实体识别功能
        test_text = "根据中华人民共和国刑法第一条，为了惩罚犯罪，保护人民，根据宪法，结合我国同犯罪作斗争的具体经验及实际情况，制定本法。"
        entities = recognizer.get_all_entities(test_text)
        
        logger.info(f"测试文本: {test_text}")
        logger.info(f"识别到的实体数量: {len(entities)}")
        for entity in entities:
            logger.info(f"实体: {entity}")
        
        logger.info("实体识别模块测试通过")
        return True
    except Exception as e:
        logger.error(f"实体识别模块测试失败: {e}")
        return False

def test_relation_extractor():
    """测试关系抽取模块"""
    logger.info("开始测试关系抽取模块")
    
    try:
        from legal_chatbot.preprocessing.relation_extractor import RelationExtractor
        
        # 初始化关系抽取器
        extractor = RelationExtractor()
        
        # 测试关系抽取功能
        test_text = "根据中华人民共和国刑法第一条，为了惩罚犯罪，保护人民，根据宪法，结合我国同犯罪作斗争的具体经验及实际情况，制定本法。"
        relations = extractor.get_all_relations(test_text)
        
        logger.info(f"测试文本: {test_text}")
        logger.info(f"抽取到的关系数量: {len(relations)}")
        for relation in relations:
            logger.info(f"关系: {relation}")
        
        logger.info("关系抽取模块测试通过")
        return True
    except Exception as e:
        logger.error(f"关系抽取模块测试失败: {e}")
        return False

def test_chatbot_handler():
    """测试智能客服处理器"""
    logger.info("开始测试智能客服处理器")
    
    try:
        from legal_chatbot.chatbot.chatbot_handler import ChatbotHandler
        
        # 初始化智能客服处理器
        chatbot = ChatbotHandler()
        
        # 测试健康检查功能
        health_status = chatbot.health_check()
        logger.info(f"健康检查状态: {health_status}")
        
        # 测试简单查询处理
        test_query = "什么是刑法？"
        response = chatbot.handle_query(test_query)
        logger.info(f"测试查询: {test_query}")
        logger.info(f"回答: {response['answer']}")
        logger.info(f"来源数量: {len(response['sources'])}")
        logger.info(f"查询类型: {response['query_type']}")
        logger.info(f"置信度: {response['confidence']}")
        
        logger.info("智能客服处理器测试通过")
        return True
    except Exception as e:
        logger.error(f"智能客服处理器测试失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("开始测试法律智能客服系统")
    
    # 测试结果统计
    results = {
        "config": False,
        "logger": False,
        "entity_recognizer": False,
        "relation_extractor": False,
        "chatbot_handler": False
    }
    
    # 运行测试
    results["config"] = test_config()
    results["logger"] = test_logger()
    results["entity_recognizer"] = test_entity_recognizer()
    results["relation_extractor"] = test_relation_extractor()
    results["chatbot_handler"] = test_chatbot_handler()
    
    # 输出测试结果
    logger.info("\n===== 系统测试结果 =====")
    for test_name, result in results.items():
        status = "通过" if result else "失败"
        logger.info(f"{test_name}: {status}")
    
    # 计算通过率
    passed = sum(results.values())
    total = len(results)
    logger.info(f"\n测试通过率: {passed}/{total} ({passed/total*100:.2f}%)")
    
    if passed == total:
        logger.info("所有测试通过！")
        return 0
    else:
        logger.error(f"有 {total - passed} 个测试失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
