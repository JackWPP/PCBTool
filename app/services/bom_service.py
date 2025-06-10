import pandas as pd
import io
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ..models.conversation import Conversation
from ..models.task import Task
from ..models.user import User
from ..schemas.task import BOMAnalysisRequest
from ..core.exceptions import TaskError, NotFoundError
from datetime import datetime


class BOMService:
    """BOM分析服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_bom(
        self, 
        conversation: Conversation, 
        user: User, 
        request: BOMAnalysisRequest
    ) -> Dict[str, Any]:
        """分析BOM数据"""
        
        # 创建任务记录
        task = Task(
            user_id=user.id,
            conversation_id=conversation.id,
            task_type="bom_analysis",
            status="running",
            input_data={"selected_website": request.selected_website}
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        try:
            # 从会话结果中获取BOM数据
            if not conversation.results or "BOM文件" not in conversation.results:
                raise TaskError("未找到BOM数据，请先进行图片分析")
            
            bom_content = conversation.results["BOM文件"]
            
            # 解析CSV数据
            bom_data = self._extract_csv_from_content(bom_content)
            
            if bom_data is None:
                raise TaskError("无法解析BOM数据")
            
            # 根据选择的网站进行价格计算
            device_details = self._calculate_prices(bom_data, request.selected_website)
            
            # 计算总价
            total_price = sum(item["总价"] for item in device_details)
            
            result = {
                "selected_website": request.selected_website,
                "device_details": device_details,
                "total_price": total_price,
                "device_count": len(device_details)
            }
            
            # 更新任务状态
            task.status = "completed"
            task.progress = 100.0
            task.result_data = result
            self.db.commit()
            
            return result
            
        except Exception as e:
            # 更新任务状态为失败
            task.status = "failed"
            task.error_message = str(e)
            self.db.commit()
            raise TaskError(f"BOM分析失败: {str(e)}")
    
    def _extract_csv_from_content(self, content: str) -> Optional[pd.DataFrame]:
        """从内容中提取CSV数据"""
        try:
            # 查找CSV块
            start_index = content.find('```csv')
            if start_index == -1:
                return None
            
            end_index = content.find('```', start_index + len('```csv'))
            if end_index == -1:
                return None
            
            csv_content = content[start_index + len('```csv'):end_index].strip()
            
            # 解析CSV
            df = pd.read_csv(io.StringIO(csv_content))
            
            # 添加价格列（如果不存在）
            if 'price' not in df.columns:
                df['price'] = 0
            
            return df
            
        except Exception:
            return None
    
    def _calculate_prices(self, bom_data: pd.DataFrame, selected_website: str) -> List[Dict[str, Any]]:
        """根据选择的网站计算价格"""
        device_details = []
        
        for _, row in bom_data.iterrows():
            price = row.get('price', 0)
            quantity = row.get('数量', 1)
            
            # 根据网站应用不同的价格策略
            if selected_website == "华秋商城":
                price = price * 0.9  # 9折
            elif selected_website == "立创商城":
                price = price * 0.95  # 95折
            elif selected_website == "德捷电子":
                price = price * 1.05  # 加价5%
            elif selected_website == "云汉芯城":
                price = price * 0.92  # 92折
            elif selected_website == "PCBWay":
                price = price * 1.1  # 加价10%
            
            device_details.append({
                "器件名称": row.get('元器件型号', '未知'),
                "单价": round(price, 2),
                "数量": quantity,
                "总价": round(price * quantity, 2)
            })
        
        return device_details
    
    def get_supported_websites(self) -> List[str]:
        """获取支持的网站列表"""
        return ["立创商城", "华秋商城", "德捷电子", "云汉芯城", "PCBWay"]
    
    def update_bom_prices(
        self, 
        conversation_id: int, 
        user_id: int, 
        price_updates: Dict[str, float]
    ) -> Dict[str, Any]:
        """更新BOM价格"""
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        
        if not conversation:
            raise NotFoundError("会话不存在")
        
        # 更新价格数据
        if conversation.results and "bom_analysis" in conversation.results:
            bom_result = conversation.results["bom_analysis"]
            device_details = bom_result.get("device_details", [])
            
            for device in device_details:
                device_name = device.get("器件名称")
                if device_name in price_updates:
                    device["单价"] = price_updates[device_name]
                    device["总价"] = device["单价"] * device["数量"]
            
            # 重新计算总价
            total_price = sum(item["总价"] for item in device_details)
            bom_result["total_price"] = total_price
            
            self.db.commit()
            return bom_result
        
        raise TaskError("未找到BOM分析结果")
