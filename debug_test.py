import asyncio
import httpx
import json
from app.utils.api_client import dify_client

async def test_dify_api():
    """测试Dify API连接性"""
    try:
        # 简单的工作流测试
        inputs = {"text_in": "测试输入"}
        user_id = "test_user"
        
        print("🔄 开始测试 Dify 工作流...")
        
        event_count = 0
        async for event_data in dify_client.process_workflow(inputs, user_id):
            event_count += 1
            event_type = event_data.get("event", "unknown")
            print(f"📨 事件 {event_count}: {event_type}")
            print(f"   数据: {json.dumps(event_data, ensure_ascii=False, indent=2)}")
            
            if event_count > 10:  # 避免无限循环
                print("⚠️ 超过10个事件，停止测试")
                break
        
        print(f"✅ 测试完成，共收到 {event_count} 个事件")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_file_upload():
    """测试文件上传"""
    try:
        print("📁 测试文件上传功能...")
        
        # 创建一个测试文件
        test_file_path = "test_image.txt"
        with open(test_file_path, "w") as f:
            f.write("测试图片内容")
        
        upload_result = await dify_client.upload_file(test_file_path, "test_user")
        print(f"📤 上传结果: {upload_result}")
        
    except Exception as e:
        print(f"❌ 上传测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_api_connectivity():
    """测试API连通性"""
    try:
        print("🌐 测试API连通性...")
        
        # 测试基本连通性
        async with httpx.AsyncClient() as client:
            # 测试Dify API
            response = await client.get("https://genshinimpact.site", timeout=10.0)
            print(f"🔗 Dify基础连接: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 连通性测试失败: {str(e)}")

if __name__ == "__main__":
    print("🚀 开始调试测试...")
    asyncio.run(test_api_connectivity())
    asyncio.run(test_file_upload())
    asyncio.run(test_dify_api())
