# PCB工具全栈项目

一个完整的PCB电路设计和分析工具，包含FastAPI后端服务和Gradio前端界面。支持多用户并发、用户隔离、会话管理和流式处理，提供现代化的Web界面体验。

## 🌟 功能特性

### 🖥️ 前端界面
- 🎨 **现代化UI**: 基于Gradio 4.x的美观现代界面
- 📱 **响应式设计**: 自适应不同屏幕尺寸
- 🔐 **用户认证**: 完整的登录注册系统
- 💬 **会话管理**: 直观的项目会话管理
- 📷 **图片上传**: 拖拽上传，支持多种格式
- 📊 **实时分析**: 流式响应和进度显示
- 🛠️ **交互式编辑**: 可编辑的BOM清单和参数

### ⚙️ 后端服务
- 🚀 **高性能并发**: 支持15+并发请求处理
- 👥 **用户隔离**: 完整的用户注册、登录和权限管理
- 💬 **会话管理**: 每次请求封装为独立的对话会话
- 🔒 **安全认证**: JWT令牌认证和用户权限控制
- 📁 **文件管理**: 安全的文件上传和用户目录隔离
- 🤖 **AI驱动**: 集成多个AI服务进行电路分析
- 📊 **流式响应**: 实时进度反馈和长时间任务处理
- 💾 **数据持久化**: SQLAlchemy ORM和数据库管理
- 🐳 **容器化部署**: Docker和Docker Compose支持

## 📋 核心功能模块

### 1. 图片分析模块
- 上传PCB电路图片
- AI驱动的电路识别和分析
- 生成BOM清单和需求文档

### 2. BOM分析模块
- 元器件价格查询和比较
- 多个供应商网站价格对比
- 总成本计算和优化建议

### 3. 代码生成模块
- 基于需求文档生成控制代码
- 支持Arduino、Raspberry Pi等平台
- 代码验证和格式化

### 4. 部署指南模块
- 自动生成部署说明
- 文本转语音功能
- 部署检查清单

## 🏗️ 项目结构

```
PCBTool/
├── app/                     # 后端应用
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库配置
│   ├── models/              # 数据模型
│   │   ├── user.py          # 用户模型
│   │   ├── conversation.py  # 会话模型
│   │   └── task.py          # 任务模型
│   ├── schemas/             # Pydantic模式
│   │   ├── user.py          # 用户模式
│   │   ├── conversation.py  # 会话模式
│   │   └── task.py          # 任务模式
│   ├── api/                 # API路由
│   │   ├── auth.py          # 认证API
│   │   ├── conversations.py # 会话管理API
│   │   └── tasks.py         # 任务管理API
│   ├── services/            # 业务逻辑
│   │   ├── auth_service.py      # 认证服务
│   │   ├── image_service.py     # 图片处理服务
│   │   ├── bom_service.py       # BOM分析服务
│   │   ├── code_service.py      # 代码生成服务
│   │   └── deployment_service.py # 部署服务
│   ├── utils/               # 工具函数
│   │   ├── security.py      # 安全工具
│   │   ├── file_utils.py    # 文件工具
│   │   └── api_client.py    # API客户端
│   └── core/                # 核心功能
│       ├── deps.py          # 依赖注入
│       └── exceptions.py    # 异常处理
├── frontend_enhanced.py     # 增强版Gradio前端界面
├── frontend_new.py          # 基础版前端界面
├── start_full_app.bat       # 一键启动脚本
├── FRONTEND_README.md       # 前端使用说明
├── uploads/                 # 用户文件存储
├── tests/                   # 测试文件
├── docker-compose.yml       # Docker编排
├── Dockerfile              # Docker镜像
├── requirements.txt        # Python依赖
├── .env.example           # 环境变量模板
└── README.md              # 项目说明
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd PCBTool

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，配置必要的API密钥和数据库连接
```

### 3. 启动完整应用

#### 🎯 推荐方式：一键启动
```bash
# Windows - 同时启动后端和前端
start_full_app.bat
```

#### 方式二：分别启动
```bash
# 启动后端服务 (端口8000)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端界面 (端口7860)
python frontend_enhanced.py
```

#### 方式三：Docker启动
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 4. 访问应用

启动成功后，访问以下地址：

- **🖥️ 前端界面**: http://localhost:7860 (主要使用入口)
- **📚 API文档**: http://localhost:8000/docs
- **📖 ReDoc**: http://localhost:8000/redoc
- **💚 健康检查**: http://localhost:8000/health

### 5. 验证安装

```bash
# 运行快速测试
python quick_test.py

# 运行并发测试
python concurrent_test.py load 5
```

## 🎨 前端界面功能

### 🔐 用户系统
- 用户注册和登录
- 安全的会话管理
- 个人项目隔离

### 📷 图片分析
- 支持PNG、JPG、JPEG格式
- 拖拽上传，操作简便
- AI智能电路识别
- 实时分析结果显示

### 📊 BOM管理
- 自动组件识别
- 多供应商价格对比
- 可编辑的组件清单
- 自动总价计算

### ⚡ 代码生成
- 基于电路自动生成控制代码
- 支持多种编程语言
- 语法高亮显示
- 一键复制代码

### 📚 部署指南
- 详细的硬件连接说明
- 软件部署步骤
- 完整的实施方案
- 文本转语音功能

## 📖 API文档

启动服务后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## 🔑 主要API端点

### 认证相关
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /auth/me` - 获取用户信息

### 会话管理
- `POST /conversations/` - 创建新会话
- `GET /conversations/` - 获取会话列表
- `GET /conversations/{id}` - 获取会话详情
- `POST /conversations/{id}/upload-image` - 上传图片分析
- `POST /conversations/{id}/analyze-text` - 文本分析
- `GET /conversations/{id}/results` - 获取分析结果

### 任务处理
- `POST /tasks/conversations/{id}/bom-analysis` - BOM分析
- `POST /tasks/conversations/{id}/code-generation` - 代码生成
- `POST /tasks/conversations/{id}/deployment-guide` - 生成部署指南
- `POST /tasks/conversations/{id}/text-to-speech` - 文本转语音

## 🧪 测试

### 基本功能测试
```bash
python test_client.py
```

### 并发测试
```bash
# 测试5个并发用户
python concurrent_test.py load 5

# 压力测试
python concurrent_test.py stress
```

### 完整测试套件
```bash
python quick_test.py
```

## 🔧 配置说明

### 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | 数据库连接URL | `sqlite:///./pcb_tool.db` |
| `SECRET_KEY` | JWT签名密钥 | `your-secret-key-here` |
| `API_KEY_DIFY` | Dify API密钥 | - |
| `NVIDIA_API_KEY` | NVIDIA API密钥 | - |
| `UPLOAD_DIR` | 文件上传目录 | `uploads` |
| `MAX_FILE_SIZE` | 最大文件大小 | `10485760` (10MB) |

### 数据库配置

默认使用SQLite，生产环境建议使用PostgreSQL：

```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/pcb_tool

# MySQL
DATABASE_URL=mysql://user:password@localhost/pcb_tool
```

## 🚀 部署

### Docker部署

```bash
# 单服务部署
docker build -t pcb-tool-backend .
docker run -p 8000:8000 pcb-tool-backend

# 完整服务栈
docker-compose up -d
```

### 生产环境部署

1. 使用PostgreSQL数据库
2. 配置Redis缓存
3. 使用Nginx反向代理
4. 启用HTTPS
5. 配置日志收集

## 📊 性能指标

- **并发用户**: 支持15+并发用户
- **响应时间**: API平均响应时间 < 200ms
- **文件上传**: 支持最大10MB文件
- **内存使用**: 基础内存占用 < 512MB
- **数据库**: 支持大量会话和用户数据

## 🔍 监控和日志

### 健康检查
```bash
curl http://localhost:8000/health
```

### 日志查看
```bash
# Docker日志
docker-compose logs -f pcb-tool-backend

# 本地日志
tail -f app.log
```

## 🤝 开发指南

### 添加新功能

1. 在`models/`中定义数据模型
2. 在`schemas/`中定义Pydantic模式
3. 在`services/`中实现业务逻辑
4. 在`api/`中添加API端点
5. 更新测试用例

### 代码规范

- 使用类型提示
- 添加文档字符串
- 遵循PEP 8规范
- 编写单元测试

## 📄 许可证

[MIT License](LICENSE)

## 🆘 故障排除

### 常见问题

1. **端口占用**: 修改`.env`中的端口配置
2. **依赖安装失败**: 使用Python 3.8+版本
3. **API密钥错误**: 检查`.env`文件配置
4. **数据库连接失败**: 确认数据库服务正常运行

### 获取帮助

- 查看API文档: http://localhost:8000/docs
- 运行健康检查: `python quick_test.py`
- 查看日志文件: `app.log`

---

🎉 **现在您的PCB工具后端服务已经准备就绪！享受高效的电路设计和分析体验吧！**
