import os
from typing import Optional


class Settings:
    """应用配置"""
    
    # 数据库配置
    database_url: str = "sqlite:///./pcb_tool.db"
    
    # JWT配置
    secret_key: str = "dev-secret-key-change-in-production-12345678901234567890"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Dify API配置
    api_url_dify: str = "https://genshinimpact.site/v1/workflows/run"
    upload_url_dify: str = "https://genshinimpact.site/v1/files/upload"
    api_key_dify: str = ""
    code_api_key_dify: str = ""
    code_api_url_dify: str = "https://genshinimpact.site/v1/chat-messages"
      # 阿里云API配置
    alibaba_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    alibaba_api_key: str = ""
    
    # Redis配置
    redis_url: Optional[str] = None
    
    # 文件配置
    upload_dir: str = "uploads"
    max_file_size: int = 10485760  # 10MB
    
    # 日志配置
    log_level: str = "INFO"
    
    # 应用配置
    app_name: str = "PCB Tool Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    
    def __init__(self):
        """从环境变量加载配置"""
        # 加载.env文件
        self._load_env_file()
          # 从环境变量更新配置
        self.database_url = os.getenv("DATABASE_URL", self.database_url)
        self.secret_key = os.getenv("SECRET_KEY", self.secret_key)
        self.algorithm = os.getenv("ALGORITHM", self.algorithm)
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", self.access_token_expire_minutes))
        
        self.api_url_dify = os.getenv("API_URL_DIFY", self.api_url_dify)
        self.upload_url_dify = os.getenv("UPLOAD_URL_DIFY", self.upload_url_dify)
        self.api_key_dify = os.getenv("API_KEY_DIFY", self.api_key_dify)
        self.code_api_key_dify = os.getenv("CODE_API_KEY_DIFY", self.code_api_key_dify)
        self.code_api_url_dify = os.getenv("CODE_API_URL_DIFY", self.code_api_url_dify)
        
        self.alibaba_base_url = os.getenv("ALIBABA_BASE_URL", self.alibaba_base_url)
        self.alibaba_api_key = os.getenv("ALIBABA_API_KEY", self.alibaba_api_key)
        
        self.redis_url = os.getenv("REDIS_URL", self.redis_url)
        
        self.upload_dir = os.getenv("UPLOAD_DIR", self.upload_dir)
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", self.max_file_size))
        
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
    
    def _load_env_file(self):
        """手动加载.env文件"""
        env_file = ".env"
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value


# 创建全局配置实例
settings = Settings()

# 确保上传目录存在
os.makedirs(settings.upload_dir, exist_ok=True)
