import os
import uuid
import aiofiles
from typing import Optional
from fastapi import UploadFile
from pathlib import Path
from datetime import datetime
from ..config import settings
from ..core.exceptions import FileUploadError


def generate_unique_filename(original_filename: str) -> str:
    """生成唯一的文件名"""
    file_extension = Path(original_filename).suffix
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{file_extension}"


def get_user_upload_dir(user_id: int) -> Path:
    """获取用户专用的上传目录"""
    user_dir = Path(settings.upload_dir) / f"user_{user_id}"
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def get_conversation_upload_dir(user_id: int, conversation_id: int) -> Path:
    """获取会话专用的上传目录"""
    conv_dir = get_user_upload_dir(user_id) / f"conversation_{conversation_id}"
    conv_dir.mkdir(parents=True, exist_ok=True)
    return conv_dir


async def save_upload_file(
    upload_file: UploadFile,
    user_id: int,
    conversation_id: Optional[int] = None
) -> tuple[str, str]:
    """
    保存上传的文件
    返回 (文件路径, 生成的文件名)
    """
    # 检查文件大小
    if upload_file.size and upload_file.size > settings.max_file_size:
        raise FileUploadError(f"文件大小超过限制 ({settings.max_file_size} bytes)")
    
    # 确定保存目录
    if conversation_id:
        save_dir = get_conversation_upload_dir(user_id, conversation_id)
    else:
        save_dir = get_user_upload_dir(user_id)
    
    # 生成唯一文件名
    unique_filename = generate_unique_filename(upload_file.filename)
    file_path = save_dir / unique_filename
    
    try:
        # 异步保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            content = await upload_file.read()
            await f.write(content)
        
        return str(file_path), unique_filename
    
    except Exception as e:
        # 清理可能已创建的文件
        if file_path.exists():
            file_path.unlink()
        raise FileUploadError(f"文件保存失败: {str(e)}")


def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    except Exception:
        return False


def get_file_type(filename: str) -> str:
    """根据文件扩展名确定文件类型"""
    extension = Path(filename).suffix.lower()
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    document_extensions = {'.pdf', '.doc', '.docx', '.txt', '.md', '.csv', '.xlsx', '.xls'}
    
    if extension in image_extensions:
        return "image"
    elif extension in document_extensions:
        return "document"
    else:
        return "other"


def clean_old_files(user_id: int, days_old: int = 30) -> int:
    """清理用户的旧文件"""
    user_dir = get_user_upload_dir(user_id)
    current_time = datetime.now()
    deleted_count = 0
    
    for file_path in user_dir.rglob("*"):
        if file_path.is_file():
            file_age = current_time - datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_age.days > days_old:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception:
                    pass
    
    return deleted_count
