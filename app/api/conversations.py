import logging
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..models.conversation import Conversation
from ..schemas.conversation import ConversationCreate, Conversation as ConversationSchema, ConversationWithFiles
from ..services.image_service import ImageService
from ..core.deps import get_current_active_user, check_conversation_owner
from ..core.exceptions import create_http_exception, NotFoundError, ValidationError
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["会话管理"])


@router.post("/", response_model=ConversationSchema, summary="创建新会话")
async def create_conversation(
    conversation_create: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建新的对话会话
    """
    try:
        conversation = Conversation(
            user_id=current_user.id,
            title=conversation_create.title or "新对话",
            description=conversation_create.description,
            status="active"
        )
        
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation
    
    except Exception as e:
        logger.error(f"创建会话失败: {str(e)}", exc_info=True)
        raise create_http_exception(ValidationError(f"创建会话失败: {str(e)}"))


@router.get("/", response_model=List[ConversationSchema], summary="获取用户会话列表")
async def get_conversations(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的所有会话
    """
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return conversations


@router.get("/{conversation_id}", response_model=ConversationWithFiles, summary="获取会话详情")
async def get_conversation(
    conversation: Conversation = Depends(check_conversation_owner)
):
    """
    获取指定会话的详细信息
    """
    return conversation


@router.post("/{conversation_id}/upload-image", summary="上传图片")
async def upload_image(
    conversation_id: int,
    image: UploadFile = File(...),
    text_input: str = Form(None),
    current_user: User = Depends(get_current_active_user),
    conversation: Conversation = Depends(check_conversation_owner),
    db: Session = Depends(get_db)
):
    """
    上传图片到指定会话
    """
    try:
        image_service = ImageService(db)
        
        # 验证图片
        image_service.validate_image(image)
        
        async def generate_progress():
            async for progress_data in image_service.process_image_analysis(
                conversation, current_user, image, text_input
            ):
                yield f"data: {json.dumps(progress_data, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate_progress(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "*"
            }
        )
    
    except Exception as e:
        logger.error(f"图片上传失败: {str(e)}", exc_info=True)
        raise create_http_exception(ValidationError(f"图片上传失败: {str(e)}"))


@router.post("/{conversation_id}/analyze-text", summary="分析文本")
async def analyze_text(
    conversation_id: int,
    text_input: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    conversation: Conversation = Depends(check_conversation_owner),
    db: Session = Depends(get_db)
):
    """
    仅分析文本输入
    """
    try:
        image_service = ImageService(db)
        
        async def generate_progress():
            async for progress_data in image_service.process_image_analysis(
                conversation, current_user, None, text_input
            ):
                yield f"data: {json.dumps(progress_data, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate_progress(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "*"
            }
        )
    
    except Exception as e:
        logger.error(f"文本分析失败: {str(e)}", exc_info=True)
        raise create_http_exception(ValidationError(f"文本分析失败: {str(e)}"))


@router.get("/{conversation_id}/results", summary="获取会话结果")
async def get_conversation_results(
    conversation: Conversation = Depends(check_conversation_owner)
):
    """
    获取会话的处理结果
    """
    return {
        "conversation_id": conversation.id,
        "results": conversation.results or {},
        "status": conversation.status
    }


@router.delete("/{conversation_id}", summary="删除会话")
async def delete_conversation(
    conversation: Conversation = Depends(check_conversation_owner),
    db: Session = Depends(get_db)
):
    """
    删除指定会话
    """
    try:
        db.delete(conversation)
        db.commit()
        return {"message": "会话已删除"}
    
    except Exception as e:
        logger.error(f"删除会话失败: {str(e)}", exc_info=True)
        raise create_http_exception(ValidationError(f"删除会话失败: {str(e)}"))
