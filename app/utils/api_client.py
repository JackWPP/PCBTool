import httpx
import json
from typing import Dict, Any, Optional, AsyncGenerator
from ..config import settings
from ..core.exceptions import ExternalAPIError


class DifyAPIClient:
    """Dify API客户端"""
    
    def __init__(self):
        self.api_url = settings.api_url_dify
        self.upload_url = settings.upload_url_dify
        self.api_key = settings.api_key_dify
        self.code_api_key = settings.code_api_key_dify
        self.code_api_url = settings.code_api_url_dify
    
    async def upload_file(self, file_path: str, user_id: str) -> Optional[str]:
        """上传文件到Dify"""
        try:
            async with httpx.AsyncClient() as client:
                with open(file_path, "rb") as f:
                    files = {"file": f}
                    data = {"user": user_id}
                    headers = {"Authorization": f"Bearer {self.api_key}"}
                    
                    response = await client.post(
                        self.upload_url,
                        headers=headers,
                        files=files,
                        data=data,
                        timeout=60.0
                    )
                    response.raise_for_status()
                    return response.json().get("id")
        except Exception as e:
            raise ExternalAPIError(f"文件上传失败: {str(e)}")
    
    async def process_workflow(
        self,
        inputs: Dict[str, Any],
        user_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """处理工作流（流式响应）"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "text/event-stream",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": inputs,
            "response_mode": "streaming",
            "user": user_id
        }
        
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=120.0
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if not line or line == ": ping":
                            continue
                        
                        if line.startswith("data:"):
                            json_str = line[5:].strip()
                            if json_str:
                                try:
                                    event_data = json.loads(json_str)
                                    yield event_data
                                except json.JSONDecodeError:
                                    continue
        except httpx.HTTPError as e:
            raise ExternalAPIError(f"工作流处理失败: {str(e)}")
    
    async def generate_code(
        self,
        requirement_document: str,
        bom_csv: str,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """生成代码（流式响应）"""
        headers = {
            "Authorization": f"Bearer {self.code_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": {
                "requirement_document": requirement_document,
                "bom_list": bom_csv
            },
            "query": "请根据需求文档和BOM列表生成相应的代码",
            "response_mode": "streaming",
            "user": user_id,
            "conversation_id": conversation_id or ""
        }
        
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    self.code_api_url,
                    headers=headers,
                    json=payload,
                    timeout=120.0
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line and line.startswith('data:'):
                            json_str = line.split('data: ')[1]
                            try:
                                event_data = json.loads(json_str)
                                event_type = event_data.get('event')
                                
                                if event_type in ['message', 'agent_message']:
                                    answer = event_data.get('answer', '')
                                    if answer:
                                        yield answer
                                elif event_type == 'message_end':
                                    break
                                elif event_type == 'error':
                                    raise ExternalAPIError(f"API错误: {event_data.get('message')}")
                            except json.JSONDecodeError:
                                continue
        except httpx.HTTPError as e:
            raise ExternalAPIError(f"代码生成失败: {str(e)}")


class AlibabaAPIClient:
    """阿里云API客户端"""
    
    def __init__(self):
        self.base_url = settings.alibaba_base_url
        self.api_key = settings.alibaba_api_key
    
    async def generate_deployment_guide(
        self,
        requirement_doc: str,
        bom_data: str
    ) -> AsyncGenerator[str, None]:
        """生成部署指南"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""【部署指南生成提示】
基于以下需求文档：
{requirement_doc}

以及BOM数据：
{bom_data}

请生成500字左右的详细部署指南，说明部署步骤、环境要求及注意事项，并尽量优化部署方案和提示细节。"""
        
        payload = {
            "model": "qwen-max",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "top_p": 0.7,
            "max_tokens": 4096,
            "stream": True
        }
        
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=120.0
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            json_str = line[5:].strip()
                            if json_str == "[DONE]":
                                break
                            try:
                                chunk_data = json.loads(json_str)
                                choices = chunk_data.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
        except httpx.HTTPError as e:
            raise ExternalAPIError(f"部署指南生成失败: {str(e)}")


# 全局API客户端实例
dify_client = DifyAPIClient()
alibaba_client = AlibabaAPIClient()
