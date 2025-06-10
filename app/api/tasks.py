from typing import List
from fastapi import APIRouter, Depends, Form, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
import json
import os

from ..database import get_db
from ..models.user import User
from ..models.conversation import Conversation
from ..schemas.task import (
    Task, TaskCreate, BOMAnalysisRequest, 
    CodeGenerationRequest, DeploymentGuideRequest
)
from ..services.bom_service import BOMService
from ..services.code_service import CodeService
from ..services.deployment_service import DeploymentService
from ..core.deps import get_current_active_user, check_conversation_owner
from ..core.exceptions import create_http_exception, ValidationError, NotFoundError

router = APIRouter(prefix="/tasks", tags=["任务管理"])


@router.post("/conversations/{conversation_id}/bom-analysis", summary="BOM分析")
async def analyze_bom(
    conversation_id: int,
    selected_website: str = Form("立创商城"),
    current_user: User = Depends(get_current_active_user),
    conversation: Conversation = Depends(check_conversation_owner),
    db: Session = Depends(get_db)
):
    """
    分析BOM数据并计算价格
    """
    try:
        bom_service = BOMService(db)
        request = BOMAnalysisRequest(selected_website=selected_website)
        
        result = bom_service.analyze_bom(conversation, current_user, request)
        
        return {
            "success": True,
            "data": result,
            "message": "BOM分析完成"
        }
        
    except Exception as e:
        raise create_http_exception(ValidationError(f"BOM分析失败: {str(e)}"))


@router.post("/conversations/{conversation_id}/code-generation", summary="代码生成")
async def generate_code(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    conversation: Conversation = Depends(check_conversation_owner),
    db: Session = Depends(get_db)
):
    """
    生成电路控制代码
    """
    try:
        code_service = CodeService(db)
        
        async def generate_code_stream():
            async for code_chunk in code_service.generate_code(conversation, current_user):
                yield f"data: {json.dumps({'type': 'code', 'content': code_chunk}, ensure_ascii=False)}\n\n"
            
            yield f"data: {json.dumps({'type': 'completed', 'message': '代码生成完成'}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate_code_stream(),
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
        raise create_http_exception(ValidationError(f"代码生成失败: {str(e)}"))


@router.post("/conversations/{conversation_id}/deployment-guide", summary="生成部署指南")
async def generate_deployment_guide(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    conversation: Conversation = Depends(check_conversation_owner),
    db: Session = Depends(get_db)
):
    """
    生成部署指南
    """
    try:
        deployment_service = DeploymentService(db)
        
        async def generate_guide_stream():
            async for guide_chunk in deployment_service.generate_deployment_guide(conversation, current_user):
                yield f"data: {json.dumps({'type': 'guide', 'content': guide_chunk}, ensure_ascii=False)}\n\n"
            
            yield f"data: {json.dumps({'type': 'completed', 'message': '部署指南生成完成'}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate_guide_stream(),
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
        raise create_http_exception(ValidationError(f"部署指南生成失败: {str(e)}"))


@router.post("/conversations/{conversation_id}/text-to-speech", summary="文本转语音")
async def text_to_speech(
    conversation_id: int,
    text: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    conversation: Conversation = Depends(check_conversation_owner),
    db: Session = Depends(get_db)
):
    """
    将文本转换为语音
    """
    try:
        deployment_service = DeploymentService(db)
        
        audio_path = deployment_service.text_to_speech(text, current_user.id)
        
        if not os.path.exists(audio_path):
            raise NotFoundError("音频文件生成失败")
        
        return FileResponse(
            audio_path,
            media_type="audio/mpeg",
            filename=f"speech_{conversation_id}.mp3"
        )
        
    except Exception as e:
        raise create_http_exception(ValidationError(f"语音生成失败: {str(e)}"))


@router.get("/conversations/{conversation_id}/deployment-checklist", summary="获取部署检查清单")
async def get_deployment_checklist(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    conversation: Conversation = Depends(check_conversation_owner),
    db: Session = Depends(get_db)
):
    """
    获取部署检查清单
    """
    try:
        deployment_service = DeploymentService(db)
        checklist = deployment_service.create_deployment_checklist(conversation)
        
        return {
            "success": True,
            "data": checklist,
            "message": "检查清单获取成功"
        }
        
    except Exception as e:
        raise create_http_exception(ValidationError(f"获取检查清单失败: {str(e)}"))


@router.get("/conversations/{conversation_id}/code-template", summary="获取代码模板")
async def get_code_template(
    conversation_id: int,
    code_type: str = "arduino",
    current_user: User = Depends(get_current_active_user),
    conversation: Conversation = Depends(check_conversation_owner),
    db: Session = Depends(get_db)
):
    """
    获取代码模板
    """
    try:
        code_service = CodeService(db)
        template = code_service.get_code_template(code_type)
        
        return {
            "success": True,
            "data": {
                "template": template,
                "code_type": code_type
            },
            "message": "代码模板获取成功"
        }
        
    except Exception as e:
        raise create_http_exception(ValidationError(f"获取代码模板失败: {str(e)}"))


@router.get("/supported-websites", summary="获取支持的网站列表")
async def get_supported_websites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取支持的元器件采购网站列表
    """
    bom_service = BOMService(db)
    websites = bom_service.get_supported_websites()
    
    return {
        "success": True,
        "data": websites,
        "message": "支持的网站列表获取成功"
    }
