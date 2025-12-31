#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视觉AI模型主程序
支持微信集成和独立运行模式
"""

import argparse
import sys
import os
import logging
from typing import Optional

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入模型和微信读取器
try:
    from rule_based_visual_ai import RuleBasedVisualAIModel as VisualAIModel
    from wechat_reader import WeChatReader
    logger.info("成功导入所需模块")
except ImportError as e:
    logger.error(f"导入模块失败: {e}")
    sys.exit(1)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='视觉AI模型主程序',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --mode wechat                # 微信集成模式
  python main.py --mode interactive           # 交互式聊天模式
  python main.py --mode interactive -i cat.jpg # 交互式模式下分析图像
  python main.py --mode test                  # 测试模型功能
        """)
    
    parser.add_argument('--mode', '-m', 
                      choices=['wechat', 'interactive', 'test'],
                      default='wechat',
                      help='运行模式: wechat(微信集成), interactive(交互式聊天), test(测试模型)')
    parser.add_argument('--image', '-i', 
                      type=str,
                      help='要分析的图像路径（仅在interactive模式下使用）')
    parser.add_argument('--debug', '-d', 
                      action='store_true',
                      help='启用调试模式，显示更详细的日志信息')
    
    return parser.parse_args()


def setup_logging(debug: bool) -> None:
    """设置日志级别
    
    Args:
        debug: 是否启用调试模式
    """
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("调试模式已启用")
    else:
        logging.getLogger().setLevel(logging.INFO)


class InteractiveChat:
    """交互式聊天类"""
    
    def __init__(self, image_path: Optional[str] = None):
        """初始化交互式聊天
        
        Args:
            image_path: 要分析的图像路径
        """
        self.image_path = image_path
        self.ai_model = None
        
    def load_model(self) -> bool:
        """加载AI模型
        
        Returns:
            bool: 是否成功加载模型
        """
        try:
            self.ai_model = VisualAIModel()
            logger.info(f"✅ 视觉AI模型已加载，使用设备: {self.ai_model.device}")
            print(f"✅ 视觉AI模型已加载，使用设备: {self.ai_model.device}")
            return True
        except Exception as e:
            logger.error(f"❌ 加载视觉AI模型失败: {e}")
            print(f"❌ 加载视觉AI模型失败: {e}")
            return False
    
    def analyze_initial_image(self) -> None:
        """分析初始图像（如果提供）"""
        if not self.image_path:
            return
        
        if os.path.exists(self.image_path):
            logger.info(f"\n正在分析图像: {self.image_path}")
            print(f"\n正在分析图像: {self.image_path}")
            
            try:
                result = self.ai_model.analyze_image(self.image_path)
                logger.info(f"图像分析结果: {result}")
                print(f"图像分析结果: {result}")
            except Exception as e:
                logger.error(f"❌ 分析图像失败: {e}")
                print(f"❌ 分析图像失败: {e}")
        else:
            logger.error(f"❌ 图像文件不存在: {self.image_path}")
            print(f"❌ 图像文件不存在: {self.image_path}")
    
    def start_chat(self) -> int:
        """开始交互式聊天
        
        Returns:
            int: 退出码
        """
        print("=== 视觉AI模型交互式聊天 ===")
        print("输入 'exit' 或 'quit' 退出程序")
        print("输入 'reset' 重置聊天历史")
        print("输入 'help' 查看帮助信息")
        print("=" * 50)
        
        # 加载模型
        if not self.load_model():
            return 1
        
        # 分析初始图像
        self.analyze_initial_image()
        
        # 开始聊天循环
        try:
            while True:
                user_input = input("\n你: ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    logger.info("用户请求退出程序")
                    print("再见！")
                    break
                elif user_input.lower() == 'reset':
                    self.ai_model.reset_chat_history()
                    logger.info("聊天历史已重置")
                    print("✅ 聊天历史已重置")
                    continue
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif not user_input:
                    continue
                
                # 生成回复
                try:
                    response = self.ai_model.chat(user_input)
                    logger.info(f"AI回复: {response[:50]}...")
                    print(f"AI: {response}")
                except Exception as e:
                    logger.error(f"❌ 处理请求时出错: {e}")
                    print(f"❌ 处理请求时出错: {e}")
        
        except KeyboardInterrupt:
            logger.info("收到键盘中断信号，退出程序")
            print("\n再见！")
        except Exception as e:
            logger.error(f"❌ 聊天过程中发生未预期错误: {e}")
            print(f"❌ 聊天过程中发生未预期错误: {e}")
            return 1
        
        return 0
    
    def _show_help(self) -> None:
        """显示帮助信息"""
        help_text = """
可用命令:
  exit/quit    - 退出程序
  reset        - 重置聊天历史
  help         - 显示此帮助信息
        """
        print(help_text)


class WeChatMode:
    """微信模式类"""
    
    def __init__(self):
        """初始化微信模式"""
        self.wechat_reader = None
    
    def run(self) -> int:
        """运行微信模式
        
        Returns:
            int: 退出码
        """
        print("=== 视觉AI模型微信集成模式 ===")
        logger.info("启动微信集成模式")
        
        try:
            # 创建微信读取器实例
            self.wechat_reader = WeChatReader()
            logger.info("成功创建微信读取器实例")
            
            # 登录微信
            if not self.wechat_reader.login():
                logger.error("微信登录失败")
                return 1
            
            # 开始监听消息
            logger.info("开始监听微信消息")
            self.wechat_reader.start_listening()
            
            return 0
        
        except KeyboardInterrupt:
            logger.info("收到键盘中断信号，正在退出微信模式")
            print("\n正在退出...")
            if self.wechat_reader:
                self.wechat_reader.logout()
            return 0
        
        except Exception as e:
            logger.error(f"❌ 微信模式运行失败: {e}")
            print(f"❌ 微信模式运行失败: {e}")
            if self.wechat_reader:
                self.wechat_reader.logout()
            return 1


class TestMode:
    """测试模式类"""
    
    def run(self) -> int:
        """运行测试模式
        
        Returns:
            int: 退出码
        """
        print("=== 视觉AI模型测试模式 ===")
        logger.info("启动测试模式")
        
        try:
            # 尝试导入测试模块
            try:
                from test_visual_ai import test_visual_ai_model
                logger.info("成功导入测试模块")
                
                # 运行测试
                success = test_visual_ai_model()
                logger.info(f"测试完成，结果: {'成功' if success else '失败'}")
                return 0 if success else 1
            
            except ImportError:
                # 如果没有专门的测试模块，运行简单测试
                logger.warning("未找到test_visual_ai模块，运行简单测试")
                return self._run_simple_test()
                
        except Exception as e:
            logger.error(f"❌ 运行测试失败: {e}")
            print(f"❌ 运行测试失败: {e}")
            return 1
    
    def _run_simple_test(self) -> int:
        """运行简单测试
        
        Returns:
            int: 退出码
        """
        print("正在运行简单测试...")
        
        try:
            # 创建模型实例
            ai_model = VisualAIModel()
            print(f"✅ 模型创建成功，使用设备: {ai_model.device}")
            
            # 测试聊天功能
            response = ai_model.chat("你好")
            print(f"✅ 聊天测试通过: {response[:30]}...")
            
            # 测试图像分析（使用虚拟路径）
            response = ai_model.analyze_image("test_image.jpg")
            print(f"✅ 图像分析测试通过: {response[:30]}...")
            
            # 测试聊天历史重置
            result = ai_model.reset_chat_history()
            print(f"✅ 聊天历史重置测试通过: {result}")
            
            print("\n🎉 所有测试通过！")
            logger.info("简单测试全部通过")
            return 0
            
        except Exception as e:
            print(f"❌ 简单测试失败: {e}")
            logger.error(f"简单测试失败: {e}")
            return 1


def main():
    """主函数"""
    try:
        # 解析命令行参数
        args = parse_args()
        
        # 设置日志级别
        setup_logging(args.debug)
        
        logger.info(f"启动视觉AI模型主程序，运行模式: {args.mode}")
        
        # 根据模式选择运行方式
        mode_handlers = {
            'wechat': WeChatMode,
            'interactive': InteractiveChat,
            'test': TestMode
        }
        
        # 创建模式处理器实例
        if args.mode == 'interactive':
            mode_instance = mode_handlers[args.mode](args.image)
        else:
            mode_instance = mode_handlers[args.mode]()
        
        # 运行模式
        return_code = mode_instance.run()
        
        logger.info(f"程序退出，返回码: {return_code}")
        return return_code
        
    except Exception as e:
        logger.error(f"❌ 主程序运行失败: {e}")
        print(f"❌ 主程序运行失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
