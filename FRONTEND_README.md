# PCB电路设计工具 - 前端界面

## 📋 项目概述

这是一个基于FastAPI后端和Gradio前端的PCB电路设计和分析工具。该工具提供了完整的电路设计流程，从图片分析到代码生成，再到部署指南。

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装Python 3.8+：

```bash
python --version
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动应用

#### 方法一：使用启动脚本（推荐）

双击运行 `start_full_app.bat` 文件，这将自动启动后端和前端服务。

#### 方法二：手动启动

**启动后端服务：**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**启动前端界面：**
```bash
# 基础版前端
python frontend_new.py

# 或增强版前端（推荐）
python frontend_enhanced.py
```

### 4. 访问应用

- **前端界面**: http://localhost:7860
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 🎯 功能特性

### 🔐 用户认证系统
- 用户注册和登录
- JWT令牌认证
- 多用户支持

### 💬 会话管理
- 创建和管理项目会话
- 会话历史记录
- 项目组织和分类

### 📷 智能图片分析
- 上传电路图片
- AI驱动的电路识别
- 组件检测和分析
- 流式结果显示

### 🔍 BOM分析与价格计算
- 自动生成物料清单(BOM)
- 多供应商价格对比
  - 立创商城
  - 华秋商城
  - 德捷电子
  - 云汉芯城
  - PCBWay
- 实时价格计算
- 可编辑的组件清单

### 💻 智能代码生成
- 基于电路设计自动生成控制代码
- 支持多种编程语言
- 流式代码生成
- 代码优化建议

### 📖 部署指南生成
- 自动生成硬件连接指南
- 软件部署说明
- 调试和测试步骤
- 故障排除指南

## 🖥️ 界面说明

### 用户认证页面
- **登录**: 使用已有账户登录
- **注册**: 创建新用户账户

### 主功能页面

#### 会话管理区域
- 创建新的项目会话
- 选择现有会话
- 查看会话状态

#### 图片分析区域
- 上传电路图片（支持PNG, JPG, JPEG）
- 添加文字描述
- 查看AI分析结果

#### BOM分析区域
- 选择供应商网站
- 查看组件清单
- 编辑数量和价格
- 计算总成本

#### 代码生成区域
- 生成电路控制代码
- 实时代码预览
- 代码语法高亮

#### 部署指南区域
- 生成详细部署说明
- 硬件连接图
- 软件配置步骤

## 🔧 技术架构

### 前端技术栈
- **Gradio**: 快速构建机器学习界面
- **Python**: 主要编程语言
- **Requests**: HTTP客户端库
- **Pandas**: 数据处理
- **AsyncIO**: 异步编程支持

### 后端技术栈
- **FastAPI**: 现代Python Web框架
- **SQLAlchemy**: ORM数据库操作
- **JWT**: 用户认证
- **Uvicorn**: ASGI服务器

### 数据库
- **SQLite**: 轻量级数据库（开发环境）
- 支持PostgreSQL/MySQL（生产环境）

## 📁 文件结构

```
PCBTool/
├── app/                          # 后端应用
│   ├── api/                      # API路由
│   ├── core/                     # 核心功能
│   ├── models/                   # 数据模型
│   ├── schemas/                  # 数据模式
│   ├── services/                 # 业务逻辑
│   └── utils/                    # 工具函数
├── frontend_new.py               # 基础前端界面
├── frontend_enhanced.py          # 增强前端界面（推荐）
├── start_full_app.bat           # 启动脚本
├── requirements.txt             # 依赖列表
└── README.md                    # 项目说明
```

## 🔄 API接口说明

### 认证接口
- `POST /auth/register` - 用户注册
- `POST /auth/login-json` - 用户登录
- `GET /auth/me` - 获取当前用户信息

### 会话接口
- `POST /conversations/` - 创建会话
- `GET /conversations/` - 获取会话列表
- `GET /conversations/{id}` - 获取会话详情

### 任务接口
- `POST /conversations/{id}/upload-image` - 上传图片
- `POST /tasks/conversations/{id}/bom-analysis` - BOM分析
- `POST /tasks/conversations/{id}/code-generation` - 代码生成
- `POST /tasks/conversations/{id}/deployment-guide` - 部署指南

## 🐛 故障排除

### 常见问题

1. **无法连接到后端服务**
   - 确保后端服务已启动（端口8000）
   - 检查防火墙设置
   - 验证API_BASE_URL配置

2. **图片上传失败**
   - 检查图片格式（支持PNG, JPG, JPEG）
   - 确保图片大小合理（<10MB）
   - 验证用户已登录

3. **BOM分析无结果**
   - 确保已上传并分析图片
   - 检查会话是否正确选择
   - 验证网络连接

4. **代码生成失败**
   - 确保会话中有有效的电路数据
   - 检查后端服务状态
   - 查看控制台错误信息

### 日志查看

- **后端日志**: 查看控制台输出或 `app.log` 文件
- **前端日志**: 查看浏览器控制台

## 🔒 安全注意事项

1. **生产环境部署**
   - 修改默认密钥和配置
   - 启用HTTPS
   - 配置适当的CORS策略
   - 使用生产级数据库

2. **用户数据保护**
   - 定期备份数据库
   - 实施访问控制
   - 监控异常活动

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看LICENSE文件了解详情。

## 📞 支持与反馈

如果您遇到问题或有改进建议，请：

1. 查看本文档的故障排除部分
2. 检查GitHub Issues
3. 创建新的Issue描述问题
4. 联系开发团队

---

**祝您使用愉快！** 🎉