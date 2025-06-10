from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class TaskBase(BaseModel):
    task_type: str
    input_data: Optional[Dict[str, Any]] = None


class TaskCreate(TaskBase):
    conversation_id: int


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[float] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TaskInDB(TaskBase):
    id: int
    user_id: int
    conversation_id: int
    status: str
    progress: float
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Task(TaskInDB):
    pass


class TaskProgress(BaseModel):
    task_id: int
    status: str
    progress: float
    message: Optional[str] = None


class ImageAnalysisRequest(BaseModel):
    text_input: Optional[str] = None


class BOMAnalysisRequest(BaseModel):
    selected_website: str = "立创商城"


class CodeGenerationRequest(BaseModel):
    pass  # 使用会话中的数据


class DeploymentGuideRequest(BaseModel):
    pass  # 使用会话中的数据
