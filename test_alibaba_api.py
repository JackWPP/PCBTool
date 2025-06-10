#!/usr/bin/env python3
"""阿里云API测试脚本"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_alibaba_api():
    """测试阿里云API"""
    
    base_url = os.getenv("ALIBABA_BASE_URL")
    api_key = os.getenv("ALIBABA_API_KEY")
    
    print(f"🔗 测试阿里云API...")
    print(f"🌐 Base URL: {base_url}")
    print(f"🔑 API Key: {api_key[:10]}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen-max",
        "messages": [
            {
                "role": "user", 
                "content": "你好，请简单回复测试成功"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            print(f"✅ 状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"🎉 API调用成功!")
                
                if "choices" in result and result["choices"]:
                    content = result["choices"][0]["message"]["content"]
                    print(f"📝 回复: {content}")
                else:
                    print(f"📄 完整响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            else:
                print(f"❌ API调用失败: {response.status_code}")
                print(f"📄 错误信息: {response.text}")
                
    except Exception as e:
        print(f"❌ 网络连接失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_alibaba_api())
