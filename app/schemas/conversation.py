from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class ConversationBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    results: Optional[Dict[str, Any]] = None


class ConversationInDB(ConversationBase):
    id: int
    user_id: int
    status: str
    results: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Conversation(ConversationInDB):
    pass


class ConversationFileBase(BaseModel):
    filename: str
    original_name: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None


class ConversationFileCreate(ConversationFileBase):
    conversation_id: int
    file_path: str


class ConversationFile(ConversationFileBase):
    id: int
    conversation_id: int
    file_path: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationWithFiles(Conversation):
    files: List[ConversationFile] = []
