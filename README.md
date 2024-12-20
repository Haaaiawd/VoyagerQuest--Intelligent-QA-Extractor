# VoyagerQuest: Intelligent QA Extractor

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

智能问答对生成工具 - 基于火山引擎API的长文本QA处理系统

## 💡 功能特性

- 🚀 自动文本分块处理，支持超长文本
- 🎯 智能生成相关问答对，适合教育培训场景
- 🔄 支持自定义起始位置，断点续传
- 📦 JSON格式存储，方便后续处理
- 🛠 提供完整测试用例和处理工具

## 📦 安装指南

1. 克隆仓库
```bash
git clone https://github.com/yourusername/VoyagerQuest.git
cd VoyagerQuest
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入你的API密钥
```

## 🚀 快速开始

### 基础用法

```python
python start_generate_qa.py
```

### 自定义处理

```python
# 指定起始切片位置
python start_generate_qa.py --start-index 5

# 合并生成的文件
python merge_qa_files.py
```

## 📖 API文档

### generate_qa.py

主要功能模块，包含以下核心方法：

- `split_text(text, chunk_size=2000)`: 文本分块
- `generate_qa_pairs(input_file, output_folder, start_index=0)`: 生成QA对
- `call_volcano_api(text_chunk)`: 调用API

### merge_qa_files.py

结果处理工具：

- `merge_qa_files(input_folder, output_file)`: 合并JSON文件

## 📝 输入输出示例

### 输入文本格式
```text
这是一段长文本内容...
```

### 输出JSON格式
```json
[
    {
        "instruction": "问题1",
        "output": "答案1",
        "system": "你是一个占卜和算命解释专家..."
    }
]
```

## 🔧 配置说明

在 `.env` 文件中配置以下参数：

```properties
VOLC_ACCESSKEY=your_access_key
VOLC_SECRETKEY=your_secret_key
ENDPOINT_ID=your_endpoint_id
```

## ⚙️ 进阶配置

### 性能优化

- 建议单个文本块大小：2000字符
- 并发处理：支持断点续传
- 内存优化：分批处理大文件

### 错误处理

- API调用失败自动重试
- 文本解析异常捕获
- JSON格式校验

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 开源协议

本项目采用 MIT 协议 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [火山引擎](https://www.volcengine.com/) - 提供API支持
- [Python](https://www.python.org/) - 编程语言支持
