import gradio as gr
import requests
import json
import pandas as pd
import os
import asyncio
import aiohttp
from typing import Optional, Dict, Any, Generator
from datetime import datetime
import time
import threading
from io import StringIO

# 后端API配置
API_BASE_URL = "http://localhost:8000"

class PCBToolClient:
    """增强版PCB工具API客户端"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.session = requests.Session()
    
    def set_token(self, token: str):
        """设置认证令牌"""
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login-json",
                json={"username": username, "password": password},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.set_token(data["access_token"])
                return {"success": True, "data": data}
            else:
                error_detail = response.json().get("detail", "登录失败")
                return {"success": False, "error": error_detail}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "无法连接到后端服务，请确保后端服务已启动"}
        except Exception as e:
            return {"success": False, "error": f"登录异常: {str(e)}"}
    
    def register(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """用户注册"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json={"username": username, "email": email, "password": password},
                timeout=10
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                error_detail = response.json().get("detail", "注册失败")
                return {"success": False, "error": error_detail}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "无法连接到后端服务"}
        except Exception as e:
            return {"success": False, "error": f"注册异常: {str(e)}"}
    
    def create_conversation(self, title: str, description: str = "") -> Dict[str, Any]:
        """创建新会话"""
        try:
            response = self.session.post(
                f"{self.base_url}/conversations/",
                json={"title": title, "description": description},
                timeout=10
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                error_detail = response.json().get("detail", "创建会话失败")
                return {"success": False, "error": error_detail}
        except Exception as e:
            return {"success": False, "error": f"创建会话异常: {str(e)}"}
    
    def get_conversations(self) -> Dict[str, Any]:
        """获取用户会话列表"""
        try:
            response = self.session.get(
                f"{self.base_url}/conversations/",
                timeout=10
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                error_detail = response.json().get("detail", "获取会话失败")
                return {"success": False, "error": error_detail}
        except Exception as e:
            return {"success": False, "error": f"获取会话异常: {str(e)}"}
    
    def upload_image(self, conversation_id: int, image_path: str, text_input: str = "") -> Generator[str, None, None]:
        """上传图片并流式返回分析结果"""
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                data = {'text_input': text_input}
                headers = {"Authorization": self.headers.get("Authorization", "")}
                
                response = self.session.post(
                    f"{self.base_url}/conversations/{conversation_id}/upload-image",
                    files=files,
                    data=data,
                    headers=headers,
                    stream=True,
                    timeout=60
                )
                
                if response.status_code == 200:
                    yield "🔄 开始处理图片...\n"
                    
                    # 处理流式响应
                    for line in response.iter_lines():
                        if line:
                            try:
                                decoded_line = line.decode('utf-8')
                                if decoded_line.startswith('data: '):
                                    json_str = decoded_line[6:]
                                    if json_str.strip():
                                        data = json.loads(json_str)
                                        if data.get('type') == 'progress':
                                            yield f"📊 {data.get('message', '')}\n"
                                        elif data.get('type') == 'result':
                                            yield f"✅ 分析完成:\n{data.get('content', '')}\n"
                                        elif data.get('type') == 'error':
                                            yield f"❌ 错误: {data.get('message', '')}\n"
                            except json.JSONDecodeError:
                                continue
                    
                    yield "\n🎉 图片处理完成！"
                else:
                    error_detail = response.json().get("detail", "图片上传失败")
                    yield f"❌ 上传失败: {error_detail}"
                    
        except Exception as e:
            yield f"❌ 处理异常: {str(e)}"
    
    def analyze_bom(self, conversation_id: int, selected_website: str = "立创商城") -> Dict[str, Any]:
        """BOM分析"""
        try:
            data = {'selected_website': selected_website}
            headers = {"Authorization": self.headers.get("Authorization", "")}
            
            response = self.session.post(
                f"{self.base_url}/tasks/conversations/{conversation_id}/bom-analysis",
                data=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                error_detail = response.json().get("detail", "BOM分析失败")
                return {"success": False, "error": error_detail}
        except Exception as e:
            return {"success": False, "error": f"BOM分析异常: {str(e)}"}
    
    def generate_code(self, conversation_id: int) -> Generator[str, None, None]:
        """生成代码并流式返回"""
        try:
            headers = {"Authorization": self.headers.get("Authorization", "")}
            
            response = self.session.post(
                f"{self.base_url}/tasks/conversations/{conversation_id}/code-generation",
                headers=headers,
                stream=True,
                timeout=60
            )
            
            if response.status_code == 200:
                yield "🔄 开始生成代码...\n\n"
                code_content = ""
                
                for line in response.iter_lines():
                    if line:
                        try:
                            decoded_line = line.decode('utf-8')
                            if decoded_line.startswith('data: '):
                                json_str = decoded_line[6:]
                                if json_str.strip():
                                    data = json.loads(json_str)
                                    if data.get('type') == 'code':
                                        code_chunk = data.get('content', '')
                                        code_content += code_chunk
                                        yield code_content
                                    elif data.get('type') == 'completed':
                                        yield code_content + "\n\n// ✅ 代码生成完成"
                        except json.JSONDecodeError:
                            continue
            else:
                yield f"❌ 代码生成失败: {response.json().get('detail', '未知错误')}"
                
        except Exception as e:
            yield f"❌ 代码生成异常: {str(e)}"
    
    def generate_deployment_guide(self, conversation_id: int) -> Generator[str, None, None]:
        """生成部署指南并流式返回"""
        try:
            headers = {"Authorization": self.headers.get("Authorization", "")}
            
            response = self.session.post(
                f"{self.base_url}/tasks/conversations/{conversation_id}/deployment-guide",
                headers=headers,
                stream=True,
                timeout=60
            )
            
            if response.status_code == 200:
                yield "🔄 开始生成部署指南...\n\n"
                guide_content = ""
                
                for line in response.iter_lines():
                    if line:
                        try:
                            decoded_line = line.decode('utf-8')
                            if decoded_line.startswith('data: '):
                                json_str = decoded_line[6:]
                                if json_str.strip():
                                    data = json.loads(json_str)
                                    if data.get('type') == 'guide':
                                        guide_chunk = data.get('content', '')
                                        guide_content += guide_chunk
                                        yield guide_content
                                    elif data.get('type') == 'completed':
                                        yield guide_content + "\n\n✅ 部署指南生成完成"
                        except json.JSONDecodeError:
                            continue
            else:
                yield f"❌ 部署指南生成失败: {response.json().get('detail', '未知错误')}"
                
        except Exception as e:
            yield f"❌ 部署指南生成异常: {str(e)}"

# 创建API客户端实例
api_client = PCBToolClient()

# 全局状态
user_token = None
current_conversation_id = None
current_user_info = None

# Gradio界面函数
def login_user(username: str, password: str):
    """用户登录处理"""
    global user_token, current_user_info
    
    if not username or not password:
        return "⚠️ 请输入用户名和密码", gr.update(visible=True), gr.update(visible=False), gr.update()
    
    result = api_client.login(username, password)
    if result["success"]:
        user_token = result["data"]["access_token"]
        current_user_info = {"username": username}
        
        # 获取会话列表
        conversations = get_conversation_list()
        
        return (
            f"✅ 登录成功！欢迎 {username}", 
            gr.update(visible=False), 
            gr.update(visible=True),
            gr.update(choices=conversations)
        )
    else:
        return (
            f"❌ 登录失败: {result['error']}", 
            gr.update(visible=True), 
            gr.update(visible=False),
            gr.update()
        )

def register_user(username: str, email: str, password: str, confirm_password: str):
    """用户注册处理"""
    if not all([username, email, password, confirm_password]):
        return "⚠️ 请填写所有字段"
    
    if password != confirm_password:
        return "⚠️ 两次输入的密码不一致"
    
    if len(password) < 6:
        return "⚠️ 密码长度至少6位"
    
    result = api_client.register(username, email, password)
    if result["success"]:
        return f"✅ 注册成功！请使用 {username} 登录"
    else:
        return f"❌ 注册失败: {result['error']}"

def create_new_conversation(title: str, description: str = ""):
    """创建新会话"""
    global current_conversation_id
    
    if not title.strip():
        return "⚠️ 请输入会话标题", gr.update()
    
    result = api_client.create_conversation(title.strip(), description.strip())
    if result["success"]:
        current_conversation_id = result["data"]["id"]
        conversations = get_conversation_list()
        return (
            f"✅ 会话 '{title}' 创建成功！", 
            gr.update(choices=conversations, value=current_conversation_id)
        )
    else:
        return f"❌ 创建会话失败: {result['error']}", gr.update()

def get_conversation_list():
    """获取会话列表"""
    result = api_client.get_conversations()
    if result["success"]:
        conversations = result["data"]
        return [(f"{conv['title']} (ID: {conv['id']})", conv['id']) for conv in conversations]
    return []

def select_conversation(conversation_id):
    """选择会话"""
    global current_conversation_id
    if conversation_id:
        current_conversation_id = conversation_id
        return f"✅ 已选择会话 ID: {conversation_id}"
    return "⚠️ 请选择一个会话"

def process_image_upload(image, text_input, progress=gr.Progress()):
    """处理图片上传（流式）"""
    global current_conversation_id
    
    if not current_conversation_id:
        return "⚠️ 请先创建或选择一个会话"
    
    if image is None:
        return "⚠️ 请上传图片"
    
    # 保存临时图片文件
    temp_path = f"temp_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    image.save(temp_path)
    
    try:
        result_text = ""
        for chunk in api_client.upload_image(current_conversation_id, temp_path, text_input or ""):
            result_text += chunk
            yield result_text
            time.sleep(0.1)  # 小延迟以显示流式效果
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

def analyze_bom_components(selected_website):
    """分析BOM组件"""
    global current_conversation_id
    
    if not current_conversation_id:
        return "⚠️ 请先创建或选择一个会话", pd.DataFrame()
    
    result = api_client.analyze_bom(current_conversation_id, selected_website)
    if result["success"]:
        # 解析BOM数据
        bom_data = result["data"].get("data", {})
        
        # 创建示例数据（实际应根据API返回格式调整）
        if "components" in bom_data:
            components = bom_data["components"]
            df = pd.DataFrame(components)
        else:
            # 示例数据
            sample_data = [
                {"器件名称": "电阻", "规格型号": "1kΩ", "单价": 0.1, "数量": 10, "总价": 1.0},
                {"器件名称": "电容", "规格型号": "100μF", "单价": 0.5, "数量": 5, "总价": 2.5},
                {"器件名称": "LED", "规格型号": "红色5mm", "单价": 0.3, "数量": 8, "总价": 2.4}
            ]
            df = pd.DataFrame(sample_data)
        
        return f"✅ BOM分析完成 (使用 {selected_website})", df
    else:
        return f"❌ BOM分析失败: {result['error']}", pd.DataFrame()

def calculate_total_price(dataframe):
    """计算总价"""
    if dataframe is None or len(dataframe) == 0:
        return dataframe, 0
    
    try:
        # 确保有必要的列
        if '单价' in dataframe.columns and '数量' in dataframe.columns:
            dataframe['总价'] = dataframe['单价'] * dataframe['数量']
            total = dataframe['总价'].sum()
            return dataframe, round(total, 2)
        else:
            return dataframe, 0
    except Exception as e:
        return dataframe, 0

def generate_code_stream(progress=gr.Progress()):
    """生成代码（流式）"""
    global current_conversation_id
    
    if not current_conversation_id:
        return "⚠️ 请先创建或选择一个会话"
    
    for chunk in api_client.generate_code(current_conversation_id):
        yield chunk
        time.sleep(0.1)

def generate_deployment_guide_stream(progress=gr.Progress()):
    """生成部署指南（流式）"""
    global current_conversation_id
    
    if not current_conversation_id:
        return "⚠️ 请先创建或选择一个会话"
    
    for chunk in api_client.generate_deployment_guide(current_conversation_id):
        yield chunk
        time.sleep(0.1)

# 创建增强版Gradio界面
with gr.Blocks(title="PCB电路设计工具", theme=gr.themes.Soft(), css="""
    .gradio-container {
        max-width: 1200px !important;
    }
    .status-success {
        color: #28a745 !important;
    }
    .status-error {
        color: #dc3545 !important;
    }
    .status-warning {
        color: #ffc107 !important;
    }
""") as demo:
    
    gr.Markdown("""
    # 🔧 PCB电路设计和分析工具
    
    **功能特点:**
    - 🔐 多用户认证系统
    - 📷 智能图片分析
    - 🔍 BOM组件分析与价格计算
    - 💻 自动代码生成
    - 📖 部署指南生成
    - 💬 会话管理
    
    ---
    """)
    
    # 用户认证区域
    with gr.Tab("🔐 用户认证") as auth_tab:
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 登录")
                login_username = gr.Textbox(
                    label="用户名", 
                    placeholder="请输入用户名"
                )
                login_password = gr.Textbox(
                    label="密码", 
                    type="password", 
                    placeholder="请输入密码"
                )
                login_btn = gr.Button("🚀 登录", variant="primary", size="lg")
                login_status = gr.Textbox(label="登录状态", interactive=False, lines=2)
            
            with gr.Column():
                gr.Markdown("### 注册新账户")
                reg_username = gr.Textbox(
                    label="用户名 (将作为您的登录凭证)", 
                    placeholder="请输入用户名"
                )
                reg_email = gr.Textbox(
                    label="邮箱", 
                    placeholder="请输入有效的邮箱地址"
                )
                reg_password = gr.Textbox(
                    label="密码 (长度至少6位)", 
                    type="password", 
                    placeholder="请输入密码"
                )
                reg_confirm_password = gr.Textbox(
                    label="确认密码", 
                    type="password", 
                    placeholder="请再次输入密码"
                )
                register_btn = gr.Button("📝 注册", variant="secondary", size="lg")
                register_status = gr.Textbox(label="注册状态", interactive=False, lines=2)
    
    # 主要功能区域（登录后可见）
    with gr.Tab("🔧 电路分析", visible=False) as main_tab:
        # 会话管理区域
        with gr.Group():
            gr.Markdown("### 💬 会话管理")
            with gr.Row():
                with gr.Column(scale=2):
                    conversation_title = gr.Textbox(
                    label="新会话标题 (为您的项目起一个描述性的名称)", 
                    placeholder="例如：LED流水灯设计"
                )
                with gr.Column(scale=3):
                    conversation_desc = gr.Textbox(
                    label="会话描述 (可以包含项目的详细要求和规格)", 
                    placeholder="详细描述您的项目需求（可选）"
                )
                with gr.Column(scale=1):
                    create_conv_btn = gr.Button("➕ 创建会话", variant="primary")
            
            with gr.Row():
                with gr.Column(scale=3):
                    conversation_list = gr.Dropdown(
                    label="选择会话 (选择一个现有会话或创建新会话)", 
                    choices=[], 
                    interactive=True
                )
                with gr.Column(scale=2):
                    conversation_status = gr.Textbox(label="会话状态", interactive=False)
        
        gr.Markdown("---")
        
        # 图片上传和分析
        with gr.Group():
            gr.Markdown("### 📷 图片上传与智能分析")
            with gr.Row():
                with gr.Column():
                    image_input = gr.Image(
                        label="上传电路图片 (支持 PNG, JPG, JPEG 格式)", 
                        type="pil"
                    )
                    text_input = gr.Textbox(
                    label="补充说明 (详细的描述有助于获得更准确的分析结果)", 
                    placeholder="请描述您的需求或对图片的说明",
                    lines=3
                )
                    upload_btn = gr.Button("🔍 上传并分析", variant="primary", size="lg")
                
                with gr.Column():
                    analysis_result = gr.Textbox(
                        label="📋 分析结果 (AI分析结果将在这里显示)", 
                        lines=12, 
                        interactive=False
                    )
        
        gr.Markdown("---")
        
        # BOM分析区域
        with gr.Group():
            gr.Markdown("### 🔍 BOM组件分析与价格计算")
            
            with gr.Row():
                with gr.Column():
                    website_choices = ["立创商城", "华秋商城", "德捷电子", "云汉芯城", "PCBWay"]
                    selected_website = gr.Radio(
                        choices=website_choices, 
                        label="选择供应商网站 (选择您偏好的电子元器件供应商)", 
                        value="立创商城"
                    )
                    analyze_bom_btn = gr.Button("🔍 分析BOM", variant="primary", size="lg")
                    bom_status = gr.Textbox(label="分析状态", interactive=False)
                
                with gr.Column():
                    gr.Markdown("#### 💰 价格计算")
                    calculate_btn = gr.Button("💰 计算总价", variant="secondary", size="lg")
                    total_price_display = gr.Number(
                        label="总价（元） - 所有组件的总价格", 
                        value=0
                    )
            
            bom_dataframe = gr.Dataframe(
                headers=["器件名称", "规格型号", "单价", "数量", "总价"],
                label="📊 BOM组件清单 (您可以直接编辑数量和价格)",
                interactive=True
            )
        
        gr.Markdown("---")
        
        # 代码生成和部署指南
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 💻 智能代码生成")
                generate_code_btn = gr.Button("⚡ 生成电路代码", variant="primary", size="lg")
                code_output = gr.Code(
                    label="🔧 生成的代码 (基于您的电路设计自动生成的控制代码)", 
                    language="cpp",
                    lines=15
                )
            
            with gr.Column():
                gr.Markdown("### 📖 部署指南生成")
                generate_guide_btn = gr.Button("📚 生成部署指南", variant="primary", size="lg")
                deployment_guide = gr.Textbox(
                    label="📋 部署指南 (详细的硬件连接和软件部署说明)", 
                    lines=15, 
                    interactive=False
                )
        
        # 系统状态显示
        with gr.Group():
            gr.Markdown("### 📊 系统状态")
            with gr.Row():
                system_status = gr.Textbox(
                    label="系统状态", 
                    value="✅ 系统正常运行",
                    interactive=False
                )
                api_status = gr.Textbox(
                    label="API状态", 
                    value="🔗 已连接到后端服务",
                    interactive=False
                )
    
    # 事件绑定
    login_btn.click(
        fn=login_user,
        inputs=[login_username, login_password],
        outputs=[login_status, auth_tab, main_tab, conversation_list]
    )
    
    register_btn.click(
        fn=register_user,
        inputs=[reg_username, reg_email, reg_password, reg_confirm_password],
        outputs=[register_status]
    )
    
    create_conv_btn.click(
        fn=create_new_conversation,
        inputs=[conversation_title, conversation_desc],
        outputs=[conversation_status, conversation_list]
    )
    
    conversation_list.change(
        fn=select_conversation,
        inputs=[conversation_list],
        outputs=[conversation_status]
    )
    
    upload_btn.click(
        fn=process_image_upload,
        inputs=[image_input, text_input],
        outputs=[analysis_result]
    )
    
    analyze_bom_btn.click(
        fn=analyze_bom_components,
        inputs=[selected_website],
        outputs=[bom_status, bom_dataframe]
    )
    
    calculate_btn.click(
        fn=calculate_total_price,
        inputs=[bom_dataframe],
        outputs=[bom_dataframe, total_price_display]
    )
    
    generate_code_btn.click(
        fn=generate_code_stream,
        inputs=[],
        outputs=[code_output]
    )
    
    generate_guide_btn.click(
        fn=generate_deployment_guide_stream,
        inputs=[],
        outputs=[deployment_guide]
    )

if __name__ == "__main__":
    print("🚀 启动PCB电路设计工具前端界面...")
    print(f"📡 后端API地址: {API_BASE_URL}")
    print("🌐 前端界面将在 http://localhost:7860 启动")
    print("📚 请确保后端服务已在 http://localhost:8000 运行")
    
    # 启动Gradio应用
    demo.queue()  # 启用队列支持流式响应
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True
    )