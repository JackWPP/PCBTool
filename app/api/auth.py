from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.user import UserCreate, User, Token, UserLogin
from ..services.auth_service import AuthService
from ..utils.security import create_access_token
from ..config import settings
from ..core.exceptions import create_http_exception, AuthenticationError, ValidationError
from ..core.deps import get_current_active_user

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=User, summary="用户注册")
async def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    注册新用户
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.create_user(user_create)
        return user
    except (ValidationError, AuthenticationError) as e:
        raise create_http_exception(e)


@router.post("/login", response_model=Token, summary="用户登录")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    用户登录，返回访问令牌
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.authenticate_user(form_data.username, form_data.password)
        
        if not user:
            raise AuthenticationError("用户名或密码错误")
        
        if not user.is_active:
            raise AuthenticationError("用户账户已被禁用")
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    except (ValidationError, AuthenticationError) as e:
        raise create_http_exception(e)


@router.post("/login-json", response_model=Token, summary="JSON格式登录")
async def login_json(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    JSON格式用户登录
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.authenticate_user(user_login.username, user_login.password)
        
        if not user:
            raise AuthenticationError("用户名或密码错误")
        
        if not user.is_active:
            raise AuthenticationError("用户账户已被禁用")
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    except (ValidationError, AuthenticationError) as e:
        raise create_http_exception(e)


@router.get("/me", response_model=User, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前登录用户的信息
    """
    return current_user
