import requests
import httpx
import asyncio

def test_basic_connectivity():
    """测试基础网络连接"""
    print("🌐 测试基础网络连接...")
    
    # 测试HTTP连接
    try:
        response = requests.get("http://www.baidu.com", timeout=10)
        print(f"✅ HTTP连接正常: {response.status_code}")
    except Exception as e:
        print(f"❌ HTTP连接失败: {str(e)}")
    
    # 测试HTTPS连接
    try:
        response = requests.get("https://www.baidu.com", timeout=10)
        print(f"✅ HTTPS连接正常: {response.status_code}")
    except Exception as e:
        print(f"❌ HTTPS连接失败: {str(e)}")
    
    # 测试目标API域名
    try:
        response = requests.get("https://genshinimpact.site", timeout=10)
        print(f"✅ 目标API域名可达: {response.status_code}")
    except Exception as e:
        print(f"❌ 目标API域名不可达: {str(e)}")

async def test_async_connectivity():
    """测试异步HTTP连接"""
    print("🔄 测试异步HTTP连接...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://www.baidu.com")
            print(f"✅ 异步HTTPS连接正常: {response.status_code}")
    except Exception as e:
        print(f"❌ 异步HTTPS连接失败: {str(e)}")

def test_api_endpoints():
    """测试API端点连接"""
    print("🔗 测试API端点...")
    
    # Dify工作流API
    dify_url = "https://genshinimpact.site/v1/workflows/run"
    try:
        response = requests.post(dify_url, 
                               headers={"Authorization": "Bearer test"}, 
                               json={"test": "data"}, 
                               timeout=10)
        print(f"📡 Dify工作流API: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"❌ Dify工作流API失败: {str(e)}")
    
    # Dify上传API
    upload_url = "https://genshinimpact.site/v1/files/upload"
    try:
        response = requests.get(upload_url, timeout=10)
        print(f"📤 Dify上传API: {response.status_code}")
    except Exception as e:
        print(f"❌ Dify上传API失败: {str(e)}")
      # 阿里云API
    alibaba_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    try:
        response = requests.get(alibaba_url, timeout=10)
        print(f"🚀 阿里云API: {response.status_code}")
    except Exception as e:
        print(f"❌ 阿里云API失败: {str(e)}")

if __name__ == "__main__":
    print("🔍 开始网络连接诊断...")
    test_basic_connectivity()
    print("\n" + "="*50)
    asyncio.run(test_async_connectivity())
    print("\n" + "="*50)
    test_api_endpoints()
    print("\n✅ 网络诊断完成")
