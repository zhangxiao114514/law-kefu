// wechat_extension.h
// 微信消息处理C++扩展模块头文件
// 定义了Python与C++之间的接口

#ifndef WECHAT_EXTENSION_H
#define WECHAT_EXTENSION_H

#include <string>
#include <vector>

// 消息类型枚举
enum WeChatMsgType {
    MSG_TYPE_TEXT = 0,      // 文本消息
    MSG_TYPE_IMAGE = 1,     // 图片消息
    MSG_TYPE_VOICE = 2,     // 语音消息
    MSG_TYPE_VIDEO = 3,     // 视频消息
    MSG_TYPE_FILE = 4,      // 文件消息
    MSG_TYPE_UNKNOWN = 5    // 未知消息类型
};

// 扩展配置结构体
struct WeChatExtensionConfig {
    bool enable_logging;     // 是否启用日志
    bool enable_auto_reply;  // 是否启用自动回复
    int max_message_length;  // 最大消息长度
    std::string log_file;    // 日志文件路径
};

// 扩展状态结构体
struct WeChatExtensionStatus {
    bool is_initialized;     // 是否已初始化
    bool is_logging_enabled; // 是否启用日志
    int message_count;       // 处理的消息数量
    std::string version;     // 扩展版本
};

// 导出函数声明
extern "C" {
    // 初始化扩展
    __declspec(dllexport) bool initialize_extension(const WeChatExtensionConfig* config);
    
    // 处理微信消息
    __declspec(dllexport) void process_wechat_message(const char* sender, const char* content, int msg_type);
    
    // 获取扩展信息
    __declspec(dllexport) const char* get_extension_info();
    
    // 获取扩展状态
    __declspec(dllexport) void get_extension_status(WeChatExtensionStatus* status);
    
    // 配置扩展
    __declspec(dllexport) bool configure_extension(const WeChatExtensionConfig* config);
    
    // 关闭扩展
    __declspec(dllexport) void shutdown_extension();
    
    // 获取支持的消息类型列表
    __declspec(dllexport) int get_supported_message_types(int* types);
}

#endif // WECHAT_EXTENSION_H
