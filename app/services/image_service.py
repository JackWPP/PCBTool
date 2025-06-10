import asyncio
from typing import Dict, Any, AsyncGenerator
from sqlalchemy.orm import Session
from PIL import Image
from ..models.user import User
from ..models.conversation import Conversation
from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate
from ..utils.api_client import dify_client
from ..utils.file_utils import save_upload_file
from ..core.exceptions import TaskError, FileUploadError


class ImageService:
    """图片处理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def process_image_analysis(
        self,
        conversation: Conversation,
        user: User,
        image_file,
        text_input: str = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """处理图片分析任务"""
        
        # 创建任务记录
        task = Task(
            user_id=user.id,
            conversation_id=conversation.id,
            task_type="image_analysis",
            status="running",
            input_data={
                "text_input": text_input or "请输入您的需求"
            }
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        try:
            # 保存上传的图片
            if image_file:
                file_path, filename = await save_upload_file(
                    image_file, user.id, conversation.id
                )
                
                # 上传到Dify
                image_id = await dify_client.upload_file(file_path, str(user.id))
                if not image_id:
                    raise TaskError("图片上传到Dify失败")
                
                inputs = {
                    "image": {
                        "transfer_method": "local_file",
                        "upload_file_id": image_id,
                        "type": "image"
                    }
                }
            else:
                inputs = {}
            
            if text_input:
                inputs["text_in"] = text_input
            
            # 处理工作流
            results = {"BOM文件": "", "需求文档": ""}
            
            async for event_data in dify_client.process_workflow(inputs, str(user.id)):
                event_type = event_data.get("event")
                
                if event_type == "node_started":
                    title = event_data.get('data', {}).get('title', '未知节点')
                    yield {
                        "type": "progress",
                        "message": f"▷ 正在处理节点：{title}",
                        "task_id": task.id
                    }
                
                elif event_type == "node_finished":
                    data = event_data.get('data', {})
                    status = data.get('status', 'unknown')
                    elapsed_time = data.get('elapsed_time', 0)
                    status_icon = "✓" if status == "succeeded" else "✗"
                    yield {
                        "type": "progress",
                        "message": f"{status_icon} 节点状态：{status} | 耗时：{elapsed_time:.1f}s",
                        "task_id": task.id
                    }
                
                elif event_type == "workflow_finished":
                    outputs = event_data.get("data", {}).get("outputs", {})
                    results.update({k: v or "" for k, v in outputs.items()})
            
            # 更新任务状态
            task.status = "completed"
            task.progress = 100.0
            task.result_data = results
            self.db.commit()
            
            # 更新会话结果
            conversation.results = conversation.results or {}
            conversation.results.update(results)
            self.db.commit()
            
            yield {
                "type": "completed",
                "message": "处理完成",
                "task_id": task.id,
                "results": results
            }
            
        except Exception as e:
            # 更新任务状态为失败
            task.status = "failed"
            task.error_message = str(e)
            self.db.commit()
            
            yield {
                "type": "error",
                "message": f"处理失败: {str(e)}",
                "task_id": task.id
            }
            raise TaskError(f"图片分析失败: {str(e)}")
    
    def validate_image(self, image_file) -> bool:
        """验证图片文件"""
        try:
            # 检查文件类型
            if not image_file.content_type.startswith('image/'):
                raise FileUploadError("请上传图片文件")
            
            # 尝试打开图片验证格式
            image = Image.open(image_file.file)
            image.verify()
            
            # 重置文件指针
            image_file.file.seek(0)
            return True
            
        except Exception as e:
            raise FileUploadError(f"无效的图片文件: {str(e)}")
    
    def get_task_progress(self, task_id: int, user_id: int) -> Dict[str, Any]:
        """获取任务进度"""
        task = self.db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()
        
        if not task:
            raise TaskError("任务不存在")
        
        return {
            "task_id": task.id,
            "status": task.status,
            "progress": task.progress,
            "result_data": task.result_data,
            "error_message": task.error_message
        }
