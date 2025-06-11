import gradio as gr
import requests
import json
import pandas as pd
import os
from typing import Optional, Dict, Any
import asyncio
import aiohttp
from datetime import datetime

# 后端API配置
API_BASE_URL = "http://localhost:8000"
API_HEADERS = {"Content-Type": "application/json"}

# 全局变量存储用户状态
user_token = None
current_conversation_id = None

class PCBToolAPI:
    """PCB工具API客户端"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
    
    def set_token(self, token: str):
        """设置认证令牌"""
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login-json",
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                self.set_token(data["access_token"])
                return {"success": True, "data": data}
            else:
                return {"success": False, "error": response.json().get("detail", "登录失败")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def register(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """用户注册"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/register",
                json={"username": username, "email": email, "password": password},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.json().get("detail", "注册失败")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_conversation(self, title: str, description: str = "") -> Dict[str, Any]:
        """创建新会话"""
        try:
            response = requests.post(
                f"{self.base_url}/conversations/",
                json={"title": title, "description": description},
                headers=self.headers
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.json().get("detail", "创建会话失败")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_conversations(self) -> Dict[str, Any]:
        """获取用户会话列表"""
        try:
            response = requests.get(
                f"{self.base_url}/conversations/",
                headers=self.headers
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.json().get("detail", "获取会话失败")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def upload_image(self, conversation_id: int, image_path: str, text_input: str = "") -> Dict[str, Any]:
        """上传图片到指定会话"""
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                data = {'text_input': text_input}
                headers = {"Authorization": self.headers.get("Authorization", "")}
                
                response = requests.post(
                    f"{self.base_url}/conversations/{conversation_id}/upload-image",
                    files=files,
                    data=data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    return {"success": True, "data": "图片上传成功"}
                else:
                    return {"success": False, "error": response.json().get("detail", "图片上传失败")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_bom(self, conversation_id: int, selected_website: str = "立创商城") -> Dict[str, Any]:
        """BOM分析"""
        try:
            data = {'selected_website': selected_website}
            headers = {"Authorization": self.headers.get("Authorization", "")}
            
            response = requests.post(
                f"{self.base_url}/tasks/conversations/{conversation_id}/bom-analysis",
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.json().get("detail", "BOM分析失败")}
        except Exception as e:
            return {"success": False, "error": str(e)}

# 创建API客户端实例
api_client = PCBToolAPI()

# Gradio界面函数
def login_user(username: str, password: str):
    """用户登录处理"""
    global user_token
    
    if not username or not password:
        return "请输入用户名和密码", gr.update(visible=True), gr.update(visible=False)
    
    result = api_client.login(username, password)
    if result["success"]:
        user_token = result["data"]["access_token"]
        return f"登录成功！欢迎 {username}", gr.update(visible=False), gr.update(visible=True)
    else:
        return f"登录失败: {result['error']}", gr.update(visible=True), gr.update(visible=False)

def register_user(username: str, email: str, password: str, confirm_password: str):
    """用户注册处理"""
    if not all([username, email, password, confirm_password]):
        return "请填写所有字段"
    
    if password != confirm_password:
        return "两次输入的密码不一致"
    
    result = api_client.register(username, email, password)
    if result["success"]:
        return f"注册成功！请使用 {username} 登录"
    else:
        return f"注册失败: {result['error']}"

def create_new_conversation(title: str, description: str = ""):
    """创建新会话"""
    global current_conversation_id
    
    if not title:
        return "请输入会话标题", gr.update()
    
    result = api_client.create_conversation(title, description)
    if result["success"]:
        current_conversation_id = result["data"]["id"]
        conversations = get_conversation_list()
        return f"会话 '{title}' 创建成功！", gr.update(choices=conversations, value=current_conversation_id)
    else:
        return f"创建会话失败: {result['error']}", gr.update()

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
    current_conversation_id = conversation_id
    return f"已选择会话 ID: {conversation_id}"

def process_image_upload(image, text_input):
    """处理图片上传"""
    global current_conversation_id
    
    if not current_conversation_id:
        return "请先创建或选择一个会话"
    
    if image is None:
        return "请上传图片"
    
    # 保存临时图片文件
    temp_path = f"temp_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    image.save(temp_path)
    
    try:
        result = api_client.upload_image(current_conversation_id, temp_path, text_input or "")
        if result["success"]:
            return "图片上传并分析成功！"
        else:
            return f"图片处理失败: {result['error']}"
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

def analyze_bom_components(selected_website):
    """分析BOM组件"""
    global current_conversation_id
    
    if not current_conversation_id:
        return "请先创建或选择一个会话", pd.DataFrame()
    
    result = api_client.analyze_bom(current_conversation_id, selected_website)
    if result["success"]:
        # 这里需要根据实际返回的数据结构来解析
        bom_data = result["data"].get("data", {})
        if "components" in bom_data:
            df = pd.DataFrame(bom_data["components"])
            return "BOM分析完成", df
        else:
            return "BOM分析完成，但没有找到组件数据", pd.DataFrame()
    else:
        return f"BOM分析失败: {result['error']}", pd.DataFrame()

def calculate_total_price(dataframe):
    """计算总价"""
    if dataframe is None or len(dataframe) == 0:
        return dataframe, 0
    
    try:
        # 假设dataframe有'单价'和'数量'列
        if '单价' in dataframe.columns and '数量' in dataframe.columns:
            dataframe['总价'] = dataframe['单价'] * dataframe['数量']
            total = dataframe['总价'].sum()
            return dataframe, total
        else:
            return dataframe, 0
    except Exception as e:
        return dataframe, 0

# 创建Gradio界面
with gr.Blocks(title="PCB电路设计工具", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🔧 PCB电路设计和分析工具")
    gr.Markdown("基于FastAPI后端的多用户PCB设计平台")
    
    # 用户认证区域
    with gr.Tab("用户登录"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 登录")
                login_username = gr.Textbox(label="用户名", placeholder="请输入用户名")
                login_password = gr.Textbox(label="密码", type="password", placeholder="请输入密码")
                login_btn = gr.Button("登录", variant="primary")
                login_status = gr.Textbox(label="登录状态", interactive=False)
            
            with gr.Column():
                gr.Markdown("## 注册")
                reg_username = gr.Textbox(label="用户名", placeholder="请输入用户名")
                reg_email = gr.Textbox(label="邮箱", placeholder="请输入邮箱")
                reg_password = gr.Textbox(label="密码", type="password", placeholder="请输入密码")
                reg_confirm_password = gr.Textbox(label="确认密码", type="password", placeholder="请再次输入密码")
                register_btn = gr.Button("注册", variant="secondary")
                register_status = gr.Textbox(label="注册状态", interactive=False)
    
    # 主要功能区域（登录后可见）
    with gr.Tab("电路分析", visible=False) as main_tab:
        # 会话管理
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 会话管理")
                conversation_title = gr.Textbox(label="新会话标题", placeholder="输入会话标题")
                conversation_desc = gr.Textbox(label="会话描述", placeholder="输入会话描述（可选）")
                create_conv_btn = gr.Button("创建新会话")
                
                conversation_list = gr.Dropdown(label="选择会话", choices=[], interactive=True)
                conversation_status = gr.Textbox(label="会话状态", interactive=False)
        
        gr.Markdown("---")
        
        # 图片上传和分析
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 📷 图片上传与分析")
                image_input = gr.Image(label="上传电路图片", type="pil")
                text_input = gr.Textbox(label="补充说明", placeholder="请描述您的需求或对图片的说明")
                upload_btn = gr.Button("上传并分析", variant="primary")
            
            with gr.Column():
                gr.Markdown("### 📋 分析结果")
                analysis_result = gr.Textbox(label="分析结果", lines=10, interactive=False)
        
        gr.Markdown("---")
        
        # BOM分析
        with gr.Row():
            gr.Markdown("### 🔍 BOM组件分析")
        
        with gr.Row():
            with gr.Column():
                website_choices = ["立创商城", "华秋商城", "德捷电子", "云汉芯城", "PCBWay"]
                selected_website = gr.Radio(
                    choices=website_choices, 
                    label="选择供应商网站", 
                    value="立创商城"
                )
                analyze_bom_btn = gr.Button("分析BOM", variant="primary")
                bom_status = gr.Textbox(label="分析状态", interactive=False)
            
            with gr.Column():
                calculate_btn = gr.Button("计算总价")
                total_price_display = gr.Number(label="总价（元）", value=0)
        
        with gr.Row():
            bom_dataframe = gr.Dataframe(
                headers=["器件名称", "规格型号", "单价", "数量", "总价"],
                label="BOM组件清单",
                interactive=True
            )
        
        gr.Markdown("---")
        
        # 代码生成和部署指南
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 💻 代码生成")
                generate_code_btn = gr.Button("生成电路代码", variant="primary")
                code_output = gr.Code(label="生成的代码", language="cpp")
            
            with gr.Column():
                gr.Markdown("### 📖 部署指南")
                generate_guide_btn = gr.Button("生成部署指南", variant="primary")
                deployment_guide = gr.Textbox(label="部署指南", lines=10, interactive=False)
    
    # 事件绑定
    login_btn.click(
        fn=login_user,
        inputs=[login_username, login_password],
        outputs=[login_status, gr.update(), main_tab]
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

if __name__ == "__main__":
    # 启动Gradio应用
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )