from typing import Dict, Any, AsyncGenerator
from sqlalchemy.orm import Session
from ..models.conversation import Conversation
from ..models.task import Task
from ..models.user import User
from ..utils.api_client import dify_client
from ..core.exceptions import TaskError


class CodeService:
    """代码生成服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_code(
        self,
        conversation: Conversation,
        user: User
    ) -> AsyncGenerator[str, None]:
        """生成电路代码"""
        
        # 创建任务记录
        task = Task(
            user_id=user.id,
            conversation_id=conversation.id,
            task_type="code_generation",
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
            
            requirement_document = conversation.results.get("需求文档", "")
            bom_data = conversation.results.get("BOM文件", "")
            
            if not requirement_document and not bom_data:
                raise TaskError("缺少需求文档或BOM数据")
            
            # 生成代码
            full_code = ""
            
            async for code_chunk in dify_client.generate_code(
                requirement_document=requirement_document,
                bom_csv=bom_data,
                user_id=str(user.id),
                conversation_id=str(conversation.id)
            ):
                full_code += code_chunk
                yield code_chunk
            
            # 更新任务状态
            task.status = "completed"
            task.progress = 100.0
            task.result_data = {"generated_code": full_code}
            self.db.commit()
            
            # 更新会话结果
            if not conversation.results:
                conversation.results = {}
            conversation.results["generated_code"] = full_code
            self.db.commit()
            
        except Exception as e:
            # 更新任务状态为失败
            task.status = "failed"
            task.error_message = str(e)
            self.db.commit()
            raise TaskError(f"代码生成失败: {str(e)}")
    
    def get_code_template(self, code_type: str = "arduino") -> str:
        """获取代码模板"""
        templates = {
            "arduino": """
// Arduino电路控制代码
#include <Arduino.h>

void setup() {
    Serial.begin(9600);
    // 初始化代码
}

void loop() {
    // 主循环代码
}
""",
            "raspberry_pi": """
# Raspberry Pi电路控制代码
import RPi.GPIO as GPIO
import time

# GPIO设置
GPIO.setmode(GPIO.BCM)

def setup():
    # 初始化代码
    pass

def main_loop():
    # 主循环代码
    while True:
        time.sleep(1)

if __name__ == "__main__":
    setup()
    try:
        main_loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
""",
            "python": """
# Python电路仿真代码
import numpy as np
import matplotlib.pyplot as plt

def simulate_circuit():
    # 电路仿真代码
    pass

if __name__ == "__main__":
    simulate_circuit()
"""
        }
        
        return templates.get(code_type, templates["arduino"])
    
    def validate_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """验证生成的代码"""
        try:
            if language == "python":
                # 简单的Python语法检查
                compile(code, '<string>', 'exec')
                return {"valid": True, "message": "代码语法正确"}
            else:
                # 对于其他语言，只做基本检查
                if not code.strip():
                    return {"valid": False, "message": "代码为空"}
                return {"valid": True, "message": "代码格式正确"}
                
        except SyntaxError as e:
            return {"valid": False, "message": f"语法错误: {str(e)}"}
        except Exception as e:
            return {"valid": False, "message": f"验证失败: {str(e)}"}
    
    def format_code(self, code: str, language: str = "python") -> str:
        """格式化代码"""
        try:
            if language == "python":
                # 简单的Python代码格式化
                lines = code.split('\n')
                formatted_lines = []
                indent_level = 0
                
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        formatted_lines.append("")
                        continue
                    
                    # 处理缩进
                    if stripped.endswith(':'):
                        formatted_lines.append('    ' * indent_level + stripped)
                        indent_level += 1
                    elif stripped in ['else:', 'elif', 'except:', 'finally:']:
                        indent_level -= 1
                        formatted_lines.append('    ' * indent_level + stripped)
                        indent_level += 1
                    else:
                        if stripped.startswith(('return', 'break', 'continue', 'pass')):
                            formatted_lines.append('    ' * indent_level + stripped)
                        else:
                            formatted_lines.append('    ' * indent_level + stripped)
                
                return '\n'.join(formatted_lines)
            else:
                return code
                
        except Exception:
            return code
