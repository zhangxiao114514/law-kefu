# 法律智能客服系统

一个基于AI的法律智能客服系统，支持微信集成、图像分析和自然语言处理，为用户提供法律相关的智能问答服务。

## 功能特性

### 核心功能
- 🤖 **智能问答**：基于深度学习模型的法律知识问答
- 💬 **微信集成**：支持微信公众号/个人号接入
- 📷 **图像分析**：支持法律文书、合同等图像的智能分析
- 🔍 **关键词匹配**：基于规则的快速关键词识别
- 📚 **法律知识库**：集成多种法律数据源

### 技术栈
- **后端框架**：Python 3.10+
- **微信集成**：itchat
- **深度学习**：PyTorch、Transformers
- **图像处理**：OpenCV、Pillow
- **网络爬虫**：Scrapy
- **API服务**：FastAPI

## 快速开始

### 安装依赖

```bash
# 安装基本依赖
pip install -r requirements.txt

# 安装法律领域特定模型（可选）
python -m spacy download zh_core_web_sm
```

### 运行系统

```bash
# 微信集成模式
python main.py --mode wechat

# 交互式聊天模式
python main.py --mode interactive

# 测试模式
python main.py --mode test
```

## 项目结构

```
kefu/
├── legal_chatbot/       # 法律聊天机器人核心模块
│   ├── chatbot/         # 聊天机器人实现
│   ├── config/          # 配置文件
│   ├── preprocessing/   # 数据预处理
│   ├── spider/          # 法律数据爬虫
│   ├── training/        # 模型训练
│   └── utils/           # 工具函数
├── src/                 # 核心源代码
│   ├── main.py          # 主程序入口
│   ├── model_handler.py # 模型处理器
│   ├── visual_ai_model.py # 视觉AI模型
│   └── wechat_reader.py # 微信消息读取器
├── tests/               # 测试文件
├── docs/                # 文档
├── requirements.txt     # 依赖列表
└── README.md            # 项目说明
```

## 配置说明

### 基本配置

编辑 `legal_chatbot/config/config.yaml` 文件，配置以下参数：

```yaml
# 微信配置
wechat:
  auto_login: true
  hot_reload: true

# 模型配置
model:
  device: "cuda"  # cpu 或 cuda
  model_path: "models/legal_chatbot"

# 日志配置
logging:
  level: "INFO"
  file_path: "logs/legal_chatbot.log"
```

## 模块说明

### 1. 微信集成模块

- **功能**：处理微信消息的接收和发送
- **核心文件**：`wechat_reader.py`
- **支持消息类型**：文本、图像、语音

### 2. 视觉AI模型

- **功能**：分析法律相关图像，提取关键信息
- **核心文件**：`visual_ai_model.py`
- **支持图像类型**：合同、法律文书、身份证等

### 3. 模型处理器

- **功能**：加载和管理深度学习模型
- **核心文件**：`model_handler.py`
- **支持模型**：BERT、GPT等预训练模型

## 开发指南

### 环境要求

- Python 3.10+
- CUDA 11.7+ (可选，用于GPU加速)
- 至少8GB内存

### 测试

```bash
# 运行系统集成测试
python test_system.py

# 运行组件测试
python test_integrated_system.py
```

### 代码规范

- 遵循PEP 8规范
- 使用Type Hint
- 编写单元测试

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

- 项目地址：https://github.com/zhangxiao114514/law-kefu
- 作者：Zhang Xiao
