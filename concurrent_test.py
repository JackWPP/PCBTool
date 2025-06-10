import asyncio
import time
import random
from test_client import PCBToolClient


class ConcurrentTester:
    """并发测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000", num_users: int = 5):
        self.base_url = base_url
        self.num_users = num_users
        self.results = []
    
    async def simulate_user_session(self, user_id: int):
        """模拟用户会话"""
        start_time = time.time()
        session_results = {
            "user_id": user_id,
            "start_time": start_time,
            "operations": [],
            "errors": [],
            "success": True
        }
        
        try:
            async with PCBToolClient(self.base_url) as client:
                # 注册和登录
                username = f"concurrent_user_{user_id}_{int(time.time())}"
                email = f"{username}@test.com"
                password = "testpassword123"
                
                # 注册
                register_start = time.time()
                await client.register(username, email, password, f"并发测试用户{user_id}")
                session_results["operations"].append({
                    "operation": "register",
                    "duration": time.time() - register_start,
                    "success": True
                })
                
                # 登录
                login_start = time.time()
                await client.login(username, password)
                session_results["operations"].append({
                    "operation": "login",
                    "duration": time.time() - login_start,
                    "success": True
                })
                
                # 创建多个会话
                conversations = []
                for i in range(random.randint(2, 4)):
                    conv_start = time.time()
                    conversation = await client.create_conversation(
                        f"用户{user_id}的会话{i+1}",
                        f"这是用户{user_id}创建的第{i+1}个测试会话"
                    )
                    conversations.append(conversation)
                    session_results["operations"].append({
                        "operation": "create_conversation",
                        "duration": time.time() - conv_start,
                        "success": True
                    })
                
                # 并发执行文本分析
                analysis_tasks = []
                for conversation in conversations:
                    task = self.perform_text_analysis(
                        client, 
                        conversation['id'], 
                        f"用户{user_id}的电路分析请求，会话{conversation['id']}"
                    )
                    analysis_tasks.append(task)
                
                # 等待所有分析完成
                analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
                
                for i, result in enumerate(analysis_results):
                    if isinstance(result, Exception):
                        session_results["errors"].append(f"分析任务{i}失败: {str(result)}")
                        session_results["success"] = False
                    else:
                        session_results["operations"].append(result)
                
                # 随机延时模拟真实用户行为
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
        except Exception as e:
            session_results["errors"].append(f"会话执行失败: {str(e)}")
            session_results["success"] = False
        
        session_results["total_duration"] = time.time() - start_time
        session_results["end_time"] = time.time()
        
        return session_results
    
    async def perform_text_analysis(self, client: PCBToolClient, conversation_id: int, text: str):
        """执行文本分析"""
        start_time = time.time()
        try:
            results = await client.analyze_text(conversation_id, text)
            return {
                "operation": "text_analysis",
                "conversation_id": conversation_id,
                "duration": time.time() - start_time,
                "success": True,
                "result_count": len(results)
            }
        except Exception as e:
            return {
                "operation": "text_analysis",
                "conversation_id": conversation_id,
                "duration": time.time() - start_time,
                "success": False,
                "error": str(e)
            }
    
    async def run_concurrent_test(self):
        """运行并发测试"""
        print(f"开始并发测试，模拟 {self.num_users} 个用户...")
        
        # 创建用户任务
        user_tasks = []
        for i in range(self.num_users):
            task = self.simulate_user_session(i + 1)
            user_tasks.append(task)
        
        # 并发执行所有用户会话
        start_time = time.time()
        results = await asyncio.gather(*user_tasks, return_exceptions=True)
        total_duration = time.time() - start_time
        
        # 分析结果
        successful_users = 0
        total_operations = 0
        failed_operations = 0
        total_errors = 0
        
        for result in results:
            if isinstance(result, Exception):
                print(f"用户会话异常: {str(result)}")
                continue
            
            if result["success"]:
                successful_users += 1
            
            total_operations += len(result["operations"])
            failed_operations += len([op for op in result["operations"] if not op.get("success", True)])
            total_errors += len(result["errors"])
            
            print(f"用户 {result['user_id']}: {'成功' if result['success'] else '失败'} "
                  f"(耗时: {result['total_duration']:.2f}s, "
                  f"操作: {len(result['operations'])}, "
                  f"错误: {len(result['errors'])})")
        
        # 输出测试摘要
        print("\n" + "="*50)
        print("并发测试摘要")
        print("="*50)
        print(f"总用户数: {self.num_users}")
        print(f"成功用户数: {successful_users}")
        print(f"成功率: {successful_users/self.num_users*100:.1f}%")
        print(f"总测试时间: {total_duration:.2f}s")
        print(f"总操作数: {total_operations}")
        print(f"失败操作数: {failed_operations}")
        print(f"总错误数: {total_errors}")
        print(f"平均每用户耗时: {total_duration/self.num_users:.2f}s")
        
        return {
            "total_users": self.num_users,
            "successful_users": successful_users,
            "success_rate": successful_users/self.num_users,
            "total_duration": total_duration,
            "total_operations": total_operations,
            "failed_operations": failed_operations,
            "total_errors": total_errors,
            "results": results
        }


async def run_load_test(num_users: int = 5, base_url: str = "http://localhost:8000"):
    """运行负载测试"""
    tester = ConcurrentTester(base_url, num_users)
    return await tester.run_concurrent_test()


async def run_stress_test():
    """运行压力测试"""
    print("开始压力测试...")
    
    # 逐渐增加用户数量
    user_counts = [3, 5, 8, 10, 15]
    
    for user_count in user_counts:
        print(f"\n测试 {user_count} 个并发用户...")
        
        try:
            result = await run_load_test(user_count)
            
            if result["success_rate"] < 0.8:  # 成功率低于80%
                print(f"警告: 在 {user_count} 个用户时成功率降至 {result['success_rate']*100:.1f}%")
                break
            
            # 等待系统恢复
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"压力测试在 {user_count} 个用户时失败: {str(e)}")
            break
    
    print("压力测试完成")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "stress":
            asyncio.run(run_stress_test())
        elif sys.argv[1] == "load":
            user_count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            asyncio.run(run_load_test(user_count))
        else:
            print("用法: python concurrent_test.py [stress|load] [用户数]")
    else:
        # 默认运行基本并发测试
        asyncio.run(run_load_test(5))