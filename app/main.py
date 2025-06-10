from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys
import time
from pathlib import Path

from .config import settings
from .database import create_tables
from .api import auth, conversations, tasks
from .core.exceptions import PCBToolException, create_http_exception

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log")
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    logger.info("正在初始化数据库...")
    create_tables()
    logger.info("数据库初始化完成")
    
    # 确保上传目录存在
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    
    yield
    
    # 应用关闭时的清理工作
    logger.info("应用正在关闭...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="一个支持多用户并发的PCB电路设计和分析工具的后端服务",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理器
@app.exception_handler(PCBToolException)
async def pcb_tool_exception_handler(request: Request, exc: PCBToolException):
    """处理自定义异常"""
    logger.error(f"PCBTool异常: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "type": type(exc).__name__}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理HTTP异常"""
    logger.error(f"HTTP异常: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理通用异常"""
    logger.error(f"未处理异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"}
    )


# 注册路由
app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(tasks.router)


@app.get("/", summary="根路径")
async def root():
    """应用根路径"""
    return {
        "message": "PCB工具后端服务",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": "2025-06-10T20:51:00"
    }


# 添加请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有请求"""
    start_time = time.time()
    
    # 记录请求信息
    logger.info(f"请求开始: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # 记录响应信息
        logger.info(
            f"请求完成: {request.method} {request.url} - "
            f"状态码: {response.status_code} - 耗时: {process_time:.3f}s"
        )
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"请求异常: {request.method} {request.url} - "
            f"耗时: {process_time:.3f}s - 错误: {str(e)}"
        )
        raise


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        workers=1 if settings.debug else 4
    )
