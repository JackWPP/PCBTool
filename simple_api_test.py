#!/usr/bin/env python3
"""简化的阿里云API测试"""

import requests
import json
import os

print("🔍 开始阿里云API测试...")

# 读取.env文件
def load_env():
    env_vars = {}
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except Exception as e:
        print(f"❌ 读取.env文件失败: {e}")
        return {}
    return env_vars

env_vars = load_env()
base_url = env_vars.get("ALIBABA_BASE_URL", "")
api_key = env_vars.get("ALIBABA_API_KEY", "")

print(f"🌐 Base URL: {base_url}")
print(f"🔑 API Key: {api_key[:10]}..." if api_key else "❌ 未找到API Key")

if not base_url or not api_key:
    print("❌ 配置不完整，退出测试")
    exit(1)

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
    print("📡 发送API请求...")
    response = requests.post(
        f"{base_url}/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
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
    print(f"❌ 请求失败: {str(e)}")

print("✅ 测试完成")
