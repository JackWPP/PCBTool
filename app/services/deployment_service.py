from typing import Dict, Any, AsyncGenerator
from sqlalchemy.orm import Session
import os
from gtts import gTTS
import glob
import time
from ..models.conversation import Conversation
from ..models.task import Task
from ..models.user import User
from ..utils.api_client import alibaba_client
from ..core.exceptions import TaskError


class DeploymentService:
    """部署指南服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_deployment_guide(
        self,
        conversation: Conversation,
        user: User
    ) -> AsyncGenerator[str, None]:
        """生成部署指南"""
        
        # 创建任务记录
        task = Task(
            user_id=user.id,
            conversation_id=conversation.id,
            task_type="deployment_guide",
            status="running",
            input_data={}
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        try:
            # 检查是否有必要的数据
            if not conversation.results:
                raise TaskError("未找到会话数据，请先进行图片分析")
            
            requirement_doc = conversation.results.get("需求文档", "")
            bom_data = conversation.results.get("BOM文件", "")
            
            if not requirement_doc and not bom_data:
                raise TaskError("缺少需求文档或BOM数据")
            
            # 生成部署指南
            full_guide = ""
            
            async for guide_chunk in alibaba_client.generate_deployment_guide(
                requirement_doc=requirement_doc,
                bom_data=bom_data
            ):
                full_guide += guide_chunk
                yield guide_chunk
            
            # 更新任务状态
            task.status = "completed"
            task.progress = 100.0
            task.result_data = {"deployment_guide": full_guide}
            self.db.commit()
            
            # 更新会话结果
            if not conversation.results:
                conversation.results = {}
            conversation.results["deployment_guide"] = full_guide
            self.db.commit()
            
        except Exception as e:
            # 更新任务状态为失败
            task.status = "failed"
            task.error_message = str(e)
            self.db.commit()
            raise TaskError(f"部署指南生成失败: {str(e)}")
    
    def text_to_speech(self, text: str, user_id: int) -> str:
        """文本转语音"""
        try:
            if not text.strip():
                raise TaskError("文本内容为空")
            
            # 使用中文语音
            tts = gTTS(text=text, lang='zh-CN')
            
            # 生成唯一文件名
            timestamp = str(int(time.time()))
            filename = f"speech_{user_id}_{timestamp}.mp3"
            filepath = os.path.join("uploads", f"user_{user_id}", filename)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 保存音频文件
            tts.save(filepath)
            
            # 清理旧的音频文件
            self._cleanup_old_audio_files(user_id)
            
            return filepath
            
        except Exception as e:
            raise TaskError(f"语音生成失败: {str(e)}")
    
    def _cleanup_old_audio_files(self, user_id: int, keep_count: int = 5):
        """清理旧的音频文件"""
        try:
            user_dir = os.path.join("uploads", f"user_{user_id}")
            if not os.path.exists(user_dir):
                return
            
            # 获取所有音频文件
            audio_files = glob.glob(os.path.join(user_dir, "speech_*.mp3"))
            
            # 按修改时间排序
            audio_files.sort(key=os.path.getmtime, reverse=True)
            
            # 删除多余的文件
            for old_file in audio_files[keep_count:]:
                try:
                    os.remove(old_file)
                except Exception:
                    pass
                    
        except Exception:
            pass
    
    def get_deployment_template(self, deployment_type: str = "general") -> str:
        """获取部署模板"""
        templates = {
            "general": """
# 电路部署指南

## 1. 环境准备
- 确保工作环境安全，避免静电干扰
- 准备必要的工具和测试设备
- 检查所有元器件的完整性

## 2. 硬件安装
- 按照电路图进行元器件焊接
- 注意极性和方向
- 确保连接牢固可靠

## 3. 软件配置
- 安装必要的驱动程序
- 上传控制代码
- 进行基本功能测试

## 4. 调试步骤
- 检查电源电压
- 测试各模块功能
- 排查可能的问题

## 5. 注意事项
- 遵循安全操作规范
- 定期维护和检查
- 记录重要参数和设置
""",
            "arduino": """
# Arduino项目部署指南

## 1. 开发环境设置
- 安装Arduino IDE
- 安装必要的库文件
- 配置开发板和端口

## 2. 硬件连接
- 按照接线图连接电路
- 检查电源和信号线
- 确保无短路现象

## 3. 代码上传
- 编译代码检查语法
- 选择正确的开发板型号
- 上传代码到Arduino

## 4. 测试调试
- 打开串口监视器
- 观察输出信息
- 调整参数优化性能

## 5. 部署运行
- 断开USB连接
- 使用外部电源供电
- 监控运行状态
""",
            "raspberry_pi": """
# Raspberry Pi项目部署指南

## 1. 系统准备
- 安装Raspberry Pi OS
- 更新系统和软件包
- 安装Python依赖库

## 2. GPIO配置
- 启用必要的接口
- 设置GPIO权限
- 测试GPIO功能

## 3. 代码部署
- 上传项目代码
- 设置执行权限
- 配置开机自启动

## 4. 网络配置
- 配置WiFi连接
- 设置静态IP
- 配置远程访问

## 5. 监控维护
- 设置系统监控
- 配置日志记录
- 定期备份重要数据
"""
        }
        
        return templates.get(deployment_type, templates["general"])
    
    def create_deployment_checklist(self, conversation: Conversation) -> Dict[str, Any]:
        """创建部署检查清单"""
        checklist = {
            "pre_deployment": [
                "检查所有元器件是否齐全",
                "验证电路设计的正确性",
                "准备必要的工具和设备",
                "确保工作环境安全"
            ],
            "hardware_setup": [
                "按照电路图进行连接",
                "检查电源电压和电流",
                "验证信号连接的正确性",
                "测试各模块的独立功能"
            ],
            "software_deployment": [
                "安装必要的软件和驱动",
                "上传和验证控制代码",
                "配置系统参数",
                "进行功能测试"
            ],
            "final_testing": [
                "进行完整的系统测试",
                "验证所有功能正常",
                "记录测试结果",
                "制作使用说明"
            ],
            "maintenance": [
                "定期检查连接状态",
                "监控系统运行参数",
                "备份重要配置和数据",
                "制定维护计划"
            ]
        }
        
        return {
            "conversation_id": conversation.id,
            "checklist": checklist,
            "created_at": time.time()
        }
