#!/usr/bin/env python3
"""
PCB工具快速测试脚本
用于验证系统的基本功能和并发能力
"""

import asyncio
import sys
import os
import time

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from test_client import PCBToolClient
    from concurrent_test import run_load_test
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所有依赖包: pip install -r requirements.txt")
    sys.exit(1)


async def quick_health_check():
    """快速健康检查"""
    print("🔍 执行健康检查...")
    
    try:
        async with PCBToolClient() as client:
            health = await client.health_check()
            print(f"✅ 服务健康状态: {health['status']}")
            return True
    except Exception as e:
        print(f"❌ 健康检查失败: {str(e)}")
        print("请确保服务已启动: python -m uvicorn app.main:app --reload")
        return False


async def quick_functionality_test():
    """快速功能测试"""
    print("\n🧪 执行功能测试...")
    
    try:
        # 创建测试用户
        username = f"quicktest_{int(time.time())}"
        email = f"{username}@test.com"
        password = "testpass123"
        
        async with PCBToolClient() as client:
            # 注册
            user = await client.register(username, email, password)
            print(f"✅ 用户注册成功: {user['username']}")
            
            # 登录
            login_result = await client.login(username, password)
            print(f"✅ 用户登录成功")
            
            # 创建会话
            conversation = await client.create_conversation("快速测试会话")
            print(f"✅ 会话创建成功: ID {conversation['id']}")
            
            # 文本分析（简化版本，不依赖外部API）
            print("✅ 基本功能测试通过")
            
            return True
            
    except Exception as e:
        print(f"❌ 功能测试失败: {str(e)}")
        return False


async def quick_concurrent_test():
    """快速并发测试"""
    print("\n⚡ 执行并发测试（3个用户）...")
    
    try:
        result = await run_load_test(3)
        
        if result["success_rate"] >= 0.8:
            print(f"✅ 并发测试通过: 成功率 {result['success_rate']*100:.1f}%")
            return True
        else:
            print(f"⚠️ 并发测试警告: 成功率仅 {result['success_rate']*100:.1f}%")
            return False
            
    except Exception as e:
        print(f"❌ 并发测试失败: {str(e)}")
        return False


async def main():
    """主测试流程"""
    print("🚀 PCB工具快速测试开始")
    print("="*40)
    
    # 健康检查
    if not await quick_health_check():
        return False
    
    # 功能测试
    if not await quick_functionality_test():
        return False
    
    # 并发测试
    if not await quick_concurrent_test():
        return False
    
    print("\n" + "="*40)
    print("🎉 所有测试通过！系统运行正常")
    print("\n📊 API文档地址: http://localhost:8000/docs")
    print("🔧 Redoc文档地址: http://localhost:8000/redoc")
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试过程中发生未知错误: {str(e)}")
        sys.exit(1)
