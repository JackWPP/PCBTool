import asyncio
import aiohttp
import json
import time
from typing import List, Dict
import base64


class PCBToolClient:
    """PCB工具API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.token = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def register(self, username: str, email: str, password: str, full_name: str = None):
        """注册用户"""
        data = {
            "username": username,
            "email": email,
            "password": password,
            "full_name": full_name or username
        }
        
        async with self.session.post(f"{self.base_url}/auth/register", json=data) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                error = await resp.text()
                raise Exception(f"注册失败: {error}")
    
    async def login(self, username: str, password: str):
        """登录用户"""
        data = {
            "username": username,
            "password": password
        }
        
        async with self.session.post(f"{self.base_url}/auth/login-json", json=data) as resp:
            if resp.status == 200:
                result = await resp.json()
                self.token = result["access_token"]
                return result
            else:
                error = await resp.text()
                raise Exception(f"登录失败: {error}")
    
    def _get_headers(self):
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    async def create_conversation(self, title: str = None, description: str = None):
        """创建会话"""
        data = {}
        if title:
            data["title"] = title
        if description:
            data["description"] = description
        
        async with self.session.post(
            f"{self.base_url}/conversations/",
            json=data,
            headers=self._get_headers()
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                error = await resp.text()
                raise Exception(f"创建会话失败: {error}")
    
    async def analyze_text(self, conversation_id: int, text_input: str):
        """分析文本"""
        data = aiohttp.FormData()
        data.add_field('text_input', text_input)
        
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        async with self.session.post(
            f"{self.base_url}/conversations/{conversation_id}/analyze-text",
            data=data,
            headers=headers
        ) as resp:
            if resp.status == 200:
                # 处理流式响应
                results = []
                async for line in resp.content:
                    if line:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            try:
                                data = json.loads(line_str[6:])
                                results.append(data)
                            except json.JSONDecodeError:
                                pass
                return results
            else:
                error = await resp.text()
                raise Exception(f"文本分析失败: {error}")
    
    async def get_conversation_results(self, conversation_id: int):
        """获取会话结果"""
        async with self.session.get(
            f"{self.base_url}/conversations/{conversation_id}/results",
            headers=self._get_headers()
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                error = await resp.text()
                raise Exception(f"获取会话结果失败: {error}")
    
    async def health_check(self):
        """健康检查"""
        async with self.session.get(f"{self.base_url}/health") as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                error = await resp.text()
                raise Exception(f"健康检查失败: {error}")


async def test_basic_functionality():
    """测试基本功能"""
    print("开始基本功能测试...")
    
    async with PCBToolClient() as client:
        try:
            # 健康检查
            health = await client.health_check()
            print(f"✓ 健康检查通过: {health}")
            
            # 注册用户
            username = f"testuser_{int(time.time())}"
            email = f"{username}@test.com"
            user = await client.register(username, email, "testpassword123", "测试用户")
            print(f"✓ 用户注册成功: {user['username']}")
            
            # 登录
            login_result = await client.login(username, "testpassword123")
            print(f"✓ 登录成功: {login_result['token_type']}")
            
            # 创建会话
            conversation = await client.create_conversation("测试会话", "这是一个测试会话")
            print(f"✓ 会话创建成功: {conversation['id']}")
            
            # 文本分析
            analysis_results = await client.analyze_text(conversation['id'], "请分析这个简单的LED电路")
            print(f"✓ 文本分析完成: 收到 {len(analysis_results)} 个响应")
            
            # 获取会话结果
            results = await client.get_conversation_results(conversation['id'])
            print(f"✓ 获取会话结果成功: {results['status']}")
            
            return True
            
        except Exception as e:
            print(f"✗ 基本功能测试失败: {str(e)}")
            return False


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())