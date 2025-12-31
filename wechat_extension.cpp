// wechat_extension.cpp
// 微信消息处理的C++扩展模块

#include "wechat_extension.h"
#include <iostream>
#include <string>
#include <fstream>
#include <chrono>
#include <mutex>

// 全局变量
static WeChatExtensionConfig g_config;
static WeChatExtensionStatus g_status;
static std::mutex g_mutex;
static std::ofstream g_log_file;

// 辅助函数：获取当前时间字符串
std::string get_current_time() {
    auto now = std::chrono::system_clock::now();
    auto now_time_t = std::chrono::system_clock::to_time_t(now);
    char time_str[20];
    std::strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", std::localtime(&now_time_t));
    return std::string(time_str);
}

// 辅助函数：写日志
void write_log(const std::string& message, bool is_error = false) {
    std::lock_guard<std::mutex> lock(g_mutex);
    
    if (g_config.enable_logging) {
        std::string log_message = "[" + get_current_time() + "] " + 
                                 (is_error ? "[ERROR] " : "[INFO] ") + message;
        
        // 同时输出到控制台和文件
        std::cout << log_message << std::endl;
        
        if (g_log_file.is_open()) {
            g_log_file << log_message << std::endl;
            g_log_file.flush();
        }
    }
}

// 初始化扩展
extern "C" __declspec(dllexport) bool initialize_extension(const WeChatExtensionConfig* config) {
    std::lock_guard<std::mutex> lock(g_mutex);
    
    try {
        // 初始化配置
        if (config != nullptr) {
            g_config = *config;
        } else {
            // 默认配置
            g_config.enable_logging = true;
            g_config.enable_auto_reply = false;
            g_config.max_message_length = 1024;
            g_config.log_file = "wechat_extension.log";
        }
        
        // 打开日志文件
        if (g_config.enable_logging) {
            g_log_file.open(g_config.log_file, std::ios::out | std::ios::app);
            if (!g_log_file.is_open()) {
                std::cerr << "无法打开日志文件：" << g_config.log_file << std::endl;
                return false;
            }
        }
        
        // 初始化状态
        g_status.is_initialized = true;
        g_status.is_logging_enabled = g_config.enable_logging;
        g_status.message_count = 0;
        g_status.version = "v1.0";
        
        write_log("微信消息处理C++扩展模块已初始化");
        return true;
    } catch (const std::exception& e) {
        std::cerr << "初始化扩展失败：" << e.what() << std::endl;
        return false;
    }
}

// 处理微信消息
extern "C" __declspec(dllexport) void process_wechat_message(const char* sender, const char* content, int msg_type) {
    std::lock_guard<std::mutex> lock(g_mutex);
    
    try {
        std::string sender_str(sender ? sender : "未知发送者");
        std::string content_str(content ? content : "");
        
        // 增加消息计数
        g_status.message_count++;
        
        // 转换消息类型
        std::string msg_type_str;
        switch (msg_type) {
            case MSG_TYPE_TEXT:
                msg_type_str = "文本";
                break;
            case MSG_TYPE_IMAGE:
                msg_type_str = "图片";
                break;
            case MSG_TYPE_VOICE:
                msg_type_str = "语音";
                break;
            case MSG_TYPE_VIDEO:
                msg_type_str = "视频";
                break;
            case MSG_TYPE_FILE:
                msg_type_str = "文件";
                break;
            default:
                msg_type_str = "未知";
        }
        
        // 日志记录
        std::string log_msg = "收到消息 - 发送者: " + sender_str + ", 类型: " + msg_type_str + ", 内容: " + content_str;
        write_log(log_msg);
        
        // 打印消息信息
        std::cout << "[C++] 收到微信消息：" << std::endl;
        std::cout << "  发送者：" << sender_str << std::endl;
        std::cout << "  类型：" << msg_type_str << std::endl;
        std::cout << "  内容：" << content_str << std::endl;
        
        // 简单的消息响应示例
        if (g_config.enable_auto_reply) {
            if (content_str.find("hello") != std::string::npos || content_str.find("你好") != std::string::npos) {
                std::cout << "  [C++] 自动回复：你好！我是微信消息处理助手。" << std::endl;
            }
        }
        
        // 这里可以添加更多的C++处理逻辑
        // 例如：
        // 1. 消息存储到数据库
        // 2. 消息分析和处理
        // 3. 调用其他C++库进行处理
        // 4. 触发其他系统操作
        
    } catch (const std::exception& e) {
        write_log("处理消息失败：" + std::string(e.what()), true);
    }
}

// 获取扩展信息
extern "C" __declspec(dllexport) const char* get_extension_info() {
    return "微信消息处理C++扩展模块 v1.0";
}

// 获取扩展状态
extern "C" __declspec(dllexport) void get_extension_status(WeChatExtensionStatus* status) {
    if (status != nullptr) {
        std::lock_guard<std::mutex> lock(g_mutex);
        *status = g_status;
    }
}

// 配置扩展
extern "C" __declspec(dllexport) bool configure_extension(const WeChatExtensionConfig* config) {
    if (config == nullptr) {
        return false;
    }
    
    std::lock_guard<std::mutex> lock(g_mutex);
    
    try {
        // 关闭旧的日志文件
        if (g_log_file.is_open()) {
            g_log_file.close();
        }
        
        // 更新配置
        g_config = *config;
        g_status.is_logging_enabled = g_config.enable_logging;
        
        // 打开新的日志文件
        if (g_config.enable_logging) {
            g_log_file.open(g_config.log_file, std::ios::out | std::ios::app);
            if (!g_log_file.is_open()) {
                std::cerr << "无法打开日志文件：" << g_config.log_file << std::endl;
                return false;
            }
        }
        
        write_log("微信消息处理C++扩展模块已重新配置");
        return true;
    } catch (const std::exception& e) {
        write_log("配置扩展失败：" + std::string(e.what()), true);
        return false;
    }
}

// 关闭扩展
extern "C" __declspec(dllexport) void shutdown_extension() {
    std::lock_guard<std::mutex> lock(g_mutex);
    
    write_log("微信消息处理C++扩展模块正在关闭");
    
    // 关闭日志文件
    if (g_log_file.is_open()) {
        g_log_file.close();
    }
    
    // 重置状态
    g_status.is_initialized = false;
    g_status.is_logging_enabled = false;
    
    std::cout << "微信消息处理C++扩展模块已关闭" << std::endl;
}

// 获取支持的消息类型列表
extern "C" __declspec(dllexport) int get_supported_message_types(int* types) {
    if (types != nullptr) {
        types[0] = MSG_TYPE_TEXT;
        types[1] = MSG_TYPE_IMAGE;
        types[2] = MSG_TYPE_VOICE;
        types[3] = MSG_TYPE_VIDEO;
        types[4] = MSG_TYPE_FILE;
    }
    return 5; // 返回支持的消息类型数量
}
