from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas.user import TokenData
from ..config import settings
from ..utils.security import verify_token
from ..core.exceptions import AuthenticationError, AuthorizationError

# HTTP Bearer令牌验证
security = HTTPBearer()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """获取当前用户"""
    token = credentials.credentials
    
    try:
        # 验证令牌
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise AuthenticationError("无效的令牌")
        token_data = TokenData(username=username)
    except JWTError:
        raise AuthenticationError("无效的令牌")
    
    # 查找用户
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise AuthenticationError("用户不存在")
    
    if not user.is_active:
        raise AuthenticationError("用户已被禁用")
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise AuthenticationError("用户已被禁用")
    return current_user


def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """获取当前超级用户"""
    if not current_user.is_superuser:
        raise AuthorizationError("需要超级用户权限")
    return current_user


def check_conversation_owner(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """检查会话所有权"""
    from ..models.conversation import Conversation
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise AuthorizationError("无权访问此会话")
    
    return conversation


def check_task_owner(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """检查任务所有权"""
    from ..models.task import Task
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise AuthorizationError("无权访问此任务")
    
    return task
