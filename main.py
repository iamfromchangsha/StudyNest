import os

# --- 第一步：设置环境变量 ---
os.environ['TIKA_SERVER_JAR'] = "/xiaoya/tika-server-standard-3.2.3.jar"

# --- 第二步：导入 tika ---
import tika

# --- 第三步：尝试直接修改 tika 内部的 JAR 路径变量 ---
# 这是尝试绕过环境变量读取缓存的一种方式
try:
    import tika.tika
    tika.tika.TikaClientOnly = False  # 确保不是客户端模式
    # 直接修改 TikaServerJar 变量
    tika.tika.TikaServerJar = "/xiaoya/tika-server-standard-3.2.3.jar"
    # 有时还需要重置一些内部状态，但这取决于具体版本
    # tika.tika.ServerEndpoint = None # 尝试重置，让 checkTikaServer 重新计算
    print(f"[DEBUG] Manually set TikaServerJar to: {tika.tika.TikaServerJar}")
except ImportError:
    print("[WARNING] Could not import tika.tika submodule. Direct variable modification might not work.")
except AttributeError as e:
    print(f"[WARNING] Could not set attribute on tika.tika submodule: {e}. Direct variable modification might not work.")

import flask
from flask import request, render_template, flash, redirect, url_for,session,make_response, url_for,jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
import sqlite3
import re
import pptxtotxt
import docxtotxt
from flask_wtf.csrf import generate_csrf
import seleniumlogin
import acquire_course
import acquire_digitalcourse
import requests
import pdf_download
import base64
from urllib.parse import quote
import playwrightlogin
import requests
import topdf
from pathlib import Path
# import todoubao
import tokouriapi
import asyncio
# from volcenginesdkarkruntime import AsyncArk
# from volcenginesdkarkruntime import Ark
# from volcenginesdkarkruntime.types.responses.response_completed_event import ResponseCompletedEvent
# from volcenginesdkarkruntime.types.responses.response_reasoning_summary_text_delta_event import ResponseReasoningSummaryTextDeltaEvent
# from volcenginesdkarkruntime.types.responses.response_output_item_added_event import ResponseOutputItemAddedEvent
# from volcenginesdkarkruntime.types.responses.response_text_delta_event import ResponseTextDeltaEvent
# from volcenginesdkarkruntime.types.responses.response_text_done_event import ResponseTextDoneEvent
from flask import Response
import json
import pdftomd
import mdtohtml
from flask import Flask, request, send_file, abort
import ppttotxt
import compress_sklearn
import compress_cleancollection
# import threading
import time
import urllib.parse
# import multiprocessing



app = flask.Flask(__name__)
app.secret_key = os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


BASE_DIRECTORY = os.path.abspath("./download")
os.makedirs(BASE_DIRECTORY, exist_ok=True) # 如果目录不存在，则创建它

def is_safe_path(base_directory, requested_path):
    """
    检查请求的路径是否在允许的基础目录内，以防止路径遍历。
    """
    # 规范化路径（解析 .. 和 .）
    requested_abs_path = os.path.abspath(requested_path)
    base_abs_path = os.path.abspath(base_directory)

    # 检查规范化后的请求路径是否以基础路径开头
    return requested_abs_path.startswith(base_abs_path + os.sep) or requested_abs_path == base_abs_path



@app.route('/get_file', methods=['GET'])
def get_file():

    filepath = request.args.get('filepath')

    if not filepath:
        # 如果没有提供 filepath 参数
        abort(400, description="Missing 'filepath' parameter.")

    # 构建完整的文件系统路径
    full_requested_path = os.path.join(BASE_DIRECTORY, filepath)

    # 1. 检查路径安全性
    if not is_safe_path(BASE_DIRECTORY, full_requested_path):
        app.logger.warning(f"Blocked attempt to access path outside base directory: {full_requested_path}")
        abort(403, description="Access denied. Path traversal detected.")

    # 2. 检查文件是否存在且是一个文件（而不是目录）
    if not os.path.exists(full_requested_path):
        abort(404, description=f"File not found: {filepath}")

    if not os.path.isfile(full_requested_path):
        abort(400, description=f"Path is not a file: {filepath}")

    # 3. 使用 send_file 安全地发送文件
    try:
        # as_attachment=True 会提示浏览器下载文件
        # as_attachment=False (默认) 尝试在浏览器中打开文件
        return send_file(full_requested_path, as_attachment=False) 
    except Exception as e:
        # 发生其他错误时（如权限不足），返回 500 错误
        app.logger.error(f"Error sending file {full_requested_path}: {e}")
        abort(500, description="An error occurred while processing the file.")

def get_db_connection():
    conn = sqlite3.connect('koitoyuu.db')
    conn.row_factory = sqlite3.Row  
    return conn

def get_db_connection_2():
     conn_2 = sqlite3.connect('courseinformation.db')
     conn_2.row_factory = sqlite3.Row
     return conn_2

def init_db():
    """初始化数据库表（如果不存在）"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            token TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_filename_by_fileid(fileid):
    conn = get_db_connection_2()  # 连接 courseinformation.db
    conn.execute("PRAGMA busy_timeout = 30000")  # 设置30秒超时
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT filename FROM course WHERE fileid = ?", (fileid,))
        row = cursor.fetchone()
        if row:
            return row['filename']  # 因为你设置了 row_factory = sqlite3.Row
        else:
            return None  # 或者抛出异常，或返回默认值
    except Exception as e:
        print(f"查询文件名时出错: {e}")
        return None
    finally:
        conn.close()

def new_table():
    conn_2 = get_db_connection_2()
    conn_2.execute('''
        CREATE TABLE IF NOT EXISTS course (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fileid TEXT UNIQUE NOT NULL, 
            filename TEXT NOT NULL,
            note TEXT NOT NULL,
            node TEXT
        )
    ''')
    conn_2.commit()
    conn_2.close()


def extract_extension(filename):# 提取文件扩展名的函数
    match = re.search(r'\.([^.]+)$', filename)
    if match:
        return match.group(1)
    else:
        return None  # 或者返回空字符串 ''，根据需求

class User(UserMixin):
    def __init__(self, user_id, username, token=None):
        self.id = user_id
        self.username = username
        self.token = token

# @app.route('/user_info')
# def user_info():
#     if current_user.is_authenticated:
#         # 如果用户已登录，尝试获取详细信息
#         token = getattr(current_user, 'token', None) # 使用 getattr 安全获取 token
#         if not token:
#             # 如果当前用户对象没有 token，从数据库加载
#             conn = get_db_connection()
#             user_record = conn.execute('SELECT token FROM users WHERE id = ?', (current_user.id,)).fetchone()
#             conn.close()
#             if user_record:
#                 token = user_record['token']

#         if token:
#             # 尝试获取智慧理工大的用户信息
#             url = "https://whut.ai-augmented.com/api/jw-starcmooc/user/currentUserInfo"
#             headers = {
#                 'Authorization': 'Bearer ' + token,
#                 'Cookie': 'WT-prd-rememberme=false; WT-prd-language=zh-CN; WT-prd-access-token=' + token + '; WT-prd-login-schoolId=f8d0cbf5d0d5aed8d698612d4212b7a9; WT-prd-refresh-token=5b7472731c074b6a9d4ea4d19ab2b8bb; WT-prd-refresh-token-state-v2=0; WT-prd-teaching-schoolId=0',
#                 'Referer': 'https://whut.ai-augmented.com',
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
#             }
#             try:
#                 response = requests.get(url, headers=headers)
#                 if response.status_code == 200:
#                     data = response.json()
#                     result = data.get('result', {})
#                     nickname = result.get('nickname', 'User') # 如果没获取到昵称，默认为 'User'
#                     realname = result.get('realname', '')
#                     head_image_url_raw = result.get('headImageUrl', '') # 获取原始 URL
#                     if head_image_url_raw:
#                         # 构造完整的头像 URL
#                         full_head_url = "https://whut.ai-augmented.com/api/jx-oresource" + head_image_url_raw
#                         # 这里可以选择是否真的去请求一次 full_head_url 获取最终 URL
#                         # 通常直接使用构造好的 URL 即可，除非 API 有特殊重定向逻辑
#                         final_head_url = full_head_url
#                         print(final_head_url)
#                     else:
#                         final_head_url = "/static/default.png" # 如果 API 没有返回头像 URL，使用默认图
#                 else:
#                     # API 请求失败，使用默认值
#                     nickname = current_user.username # 回退到本地用户名
#                     final_head_url = "/static/default.png"
#             except requests.RequestException as e:
#                 # 请求异常，使用默认值
#                 app.logger.error(f"Error fetching user info from API: {e}")
#                 nickname = current_user.username
#                 final_head_url = "/static/default.png"
#         else:
#             # 有用户对象但没有 token，可能是本地注册用户
#             nickname = current_user.username
#             final_head_url = "/static/default.png"
        
#     else:
#         # 用户未登录，渲染未登录状态的 HTML 片段

#     # 返回生成的 HTML 片段

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT id, username, token FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        loaded_user = User(user['id'], user['username'])
        loaded_user.token = user['token']  # 保存token到实例
        return loaded_user
    return None

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

class ProfileForm(FlaskForm):
    whutusername = StringField('智慧理工大账户', validators=[DataRequired(), Length(min=2, max=30)]) 
    whutpassword = PasswordField('密码', validators=[DataRequired()])  
    submit = SubmitField('保存信息')

def test_token(token):
    headers = {
        'Authorization': 'Bearer '+token,
        'Cookie':'WT-prd-rememberme=false; WT-prd-language=zh-CN; WT-prd-access-token='+token+'; WT-prd-login-schoolId=f8d0cbf5d0d5aed8d698612d4212b7a9; WT-prd-refresh-token=5b7472731c074b6a9d4ea4d19ab2b8bb; WT-prd-refresh-token-state-v2=0; WT-prd-teaching-schoolId=0',
        'Referer':'https://whut.ai-augmented.com',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    response = requests.get('https://whut.ai-augmented.com/api/jx-iresource/group/student/groups?time_flag=1', headers=headers)
    # print(response.text)
    if response.status_code == 200:
        return True
    else:
        return False

def base64_encode_url(url: str) -> str:
    encoded = base64.b64encode(url.encode('utf-8')).decode('ascii')
    return quote(encoded, safe='')

# AI_PROMPT = """
# 请扮演一位专业的课程分析师，仔细阅读并理解上传的课件PDF文档。你的任务是提炼出文档的核心内容，生成一份结构清晰、内容准确的 Markdown 格式总结。

# 具体要求如下：
# 1.  **提取关键信息**：识别并总结课件中的核心概念、重要定义、关键论点、主要步骤或流程、重要的数据和结论等。
# 2.  **保持逻辑结构**：如果原文档有明确的章节划分（如标题、小节），请在总结中保留相应的 Markdown 标题层级（#, ##, ###）。
# 3.  **使用 Markdown 格式**：总结内容必须使用标准 Markdown 语法，包括但不限于：
#     *   各级标题 (`#`, `##`, `###`)
#     *   无序列表 (`-`, `*`) 或有序列表 (`1.`, `2.`)
#     *   粗体 (`**bold**`)
#     *   代码块 (`` ``` )
#     *   引用块 (`>`) 
#     *   表格 (如果需要呈现对比数据)
# 4.  **语言精炼**：总结应言简意赅，用自己的话复述原文内容，避免大段摘抄原文。
# 5.  **完整覆盖**：确保总结涵盖课件的主要知识点，形成一个完整的知识体系概览。
# 6.  **忽略无关元素**：可以忽略页眉、页脚、装饰性图片、版权信息等非核心内容。

# 最终输出应是一份可以直接使用的 Markdown 文档，方便用户复习和查阅。
# """

# async def analyze_pdf_with_ai_streaming(pdf_path, api_key='51f1b673-9b5d-4e26-b9a4-5822cf3dfdb2'):
#     """使用AI分析PDF并返回Markdown格式结果，支持流式传输"""
#     client = AsyncArk(
#         base_url='https://ark.cn-beijing.volces.com/api/v3',
#         api_key=api_key,
#     )

#     try:
#         # 上传PDF文件
#         print("Upload pdf file")
#         file = await client.files.create(
#             file=open(pdf_path, "rb"),
#             purpose="user_data"
#         )
#         print(f"File uploaded: {file.id}")

#         # 等待文件处理完成
#         await client.files.wait_for_processing(file.id)
#         print(f"File processed: {file.id}")

#         response = await client.responses.create(
#             model="doubao-seed-1-8-251228",
#             input=[
#                 {"role": "user", "content": [
#                     {
#                         "type": "input_file",
#                         "file_id": file.id  # 引用PDF文件ID
#                     },
#                     {
#                         "type": "input_text",
#                         "text": AI_PROMPT
#                     }
#                 ]},
#             ],
#             stream=True,  # 启用流式传输
#         )

#         # 收集AI响应结果
#         result_text = ""
#         async for event in response:
#             if isinstance(event, ResponseReasoningSummaryTextDeltaEvent):
#                 delta = event.delta
#                 result_text += delta
#                 yield f"data: {json.dumps({'type': 'delta', 'content': delta})}\n\n"
#                 print(f"[AI API返回] {delta}")  # 控制台打印API返回
#             elif isinstance(event, ResponseTextDeltaEvent):
#                 delta = event.delta
#                 result_text += delta
#                 yield f"data: {json.dumps({'type': 'delta', 'content': delta})}\n\n"
#                 print(f"[AI API返回] {delta}")  # 控制台打印API返回
#             elif isinstance(event, ResponseTextDoneEvent):
#                 print("\nOutputTextDone.")
#             elif isinstance(event, ResponseCompletedEvent):
#                 print("Response Completed. Usage = " + event.response.usage.model_dump_json())
#                 yield f"data: {json.dumps({'type': 'done', 'usage': event.response.usage.model_dump_json()})}\n\n"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('partials/home.html')

@app.route('/acount')
def acount():
    # 检查用户是否已认证
    if not current_user.is_authenticated:
        # 用户未登录，传递空值
        return render_template('partials/acount.html', nickename=None, realname=None, imgurl="/static/default.png")

    
    if hasattr(current_user, 'token') and current_user.token:
        token = current_user.token
    else:
        # 从数据库加载token
        conn = get_db_connection()
        user_record = conn.execute('SELECT token FROM users WHERE id = ?', (current_user.id,)).fetchone()
        conn.close()
        if user_record:
            token = user_record['token']
        else:
            token = None
    
    if not token:
        return render_template('partials/acount.html', nickename=None, realname=None, imgurl="/static/default.png")
                
    url = "https://whut.ai-augmented.com/api/jw-starcmooc/user/currentUserInfo"
    headers = {
    'Authorization': 'Bearer '+token,
    'Cookie':'WT-prd-rememberme=false; WT-prd-language=zh-CN; WT-prd-access-token='+token+'; WT-prd-login-schoolId=f8d0cbf5d0d5aed8d698612d4212b7a9; WT-prd-refresh-token=5b7472731c074b6a9d4ea4d19ab2b8bb; WT-prd-refresh-token-state-v2=0; WT-prd-teaching-schoolId=0',
    'Referer':'https://whut.ai-augmented.com',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}
    response = requests.get(url,headers=headers)
    data = response.json()
    result = data['result']
    nickename = result['nickname']
    realname = result['realname']
    id = result['id']
    headImageUrl = result['headImageUrl']
    headImageUrl = "https://whut.ai-augmented.com/api/jx-oresource"+headImageUrl
    response = requests.get(headImageUrl)
    if response.status_code == 200:
        print("头像获取成功")
        final_headurl = response.url
        return render_template('partials/acount.html', nickename=nickename, realname=realname, imgurl=final_headurl)
        # return jsonify({
        #     "logged_in": True,
        #     "nickename": nickename,
        #     "realname": realname,
        #     "imgurl":final_headurl
        # })
    else:
        print("头像获取失败")
        return render_template('partials/acount.html', nickename=None, realname=None, imgurl="/static/default.png")






@app.route('/about')
def about():
    return render_template('partials/about.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegisterForm()
#     if form.validate_on_submit():
#         username = form.username.data
#         password = form.password.data

#         conn = get_db_connection()
#         existing = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
#         if existing:
#             conn.close()
#             return '<div class="alert alert-danger">用户名已存在</div>', 400

#         password_hash = generate_password_hash(password)
#         conn.execute(
#             'INSERT INTO users (username, password_hash) VALUES (?, ?)',
#             (username, password_hash)
#         )
#         conn.commit()
#         conn.close()

#         return '<div class="alert alert-success">注册成功！<a hx-get="/login" hx-target="#content">去登录</a></div>'

#     if form.errors:
#         errors = '<br>'.join([f"{field}: {'; '.join(errs)}" for field, errs in form.errors.items()])
#         return f'<div class="alert alert-danger">输入错误：<br>{errors}</div>', 400

#     return render_template('partials/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # 从数据库加载当前用户的token
        conn = get_db_connection()
        user_record = conn.execute('SELECT token FROM users WHERE id = ?', (current_user.id,)).fetchone()
        conn.close()
        if user_record and user_record['token']:
            course = acquire_course.get_kecheng(user_record['token'], '1')
            data = course.get('data', [])
            html_content = render_template('partials/dashboard.html', courses=data)
            js_script = '<script>document.dispatchEvent(new Event("loginSuccess"));</script>'
            return html_content + js_script
        else:
            # 如果用户没有token，则需要重新登录
            pass
            
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data 

        conn = get_db_connection()
        user = conn.execute('SELECT id, username, password_hash, token FROM users WHERE username = ?', (username,)).fetchone()

        
        if not user:
            conn.execute('INSERT INTO users (username, password_hash, token) VALUES (?, ?, NULL)',
                         (username, password))  
            conn.commit()
            user = conn.execute('SELECT id, username, password_hash, token FROM users WHERE username = ?', (username,)).fetchone()
        else:
            pass

        token = user['token']

        
        if token and test_token(token):  
            # Token有效
            pass
        else:
            # 需要重新获取token
            new_token = playwrightlogin.login(username, password, "2")
            if new_token is None:
                conn.close()
                return '<div class="alert alert-danger">智慧理工大账号验证失败</div>', 400

            # 更新数据库中的token
            conn.execute('UPDATE users SET token = ? WHERE id = ?', (new_token, user['id']))
            conn.commit()
            token = new_token

        conn.close()

        # 登录用户，并将token存储在User对象中
        user_obj = User(user['id'], user['username'], token)
        login_user(user_obj)
        
        # 获取课程信息
        course = acquire_course.get_kecheng(token, '1')
        data = course.get('data', [])
        html_content = render_template('partials/dashboard.html', courses=data)
        js_script = '<script>document.dispatchEvent(new Event("loginSuccess"));</script>'
        return html_content + js_script

    return render_template('partials/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return '<div class="alert alert-info">已退出登录。<a href="/">返回首页</a></div>'

@app.route('/dashboard')
@login_required
def dashboard():
    # 直接使用当前用户的token
    if hasattr(current_user, 'token') and current_user.token:
        token = current_user.token
    else:
        # 如果当前用户没有token，则从数据库加载
        conn = get_db_connection()
        user_record = conn.execute('SELECT token FROM users WHERE id = ?', (current_user.id,)).fetchone()
        conn.close()
        if user_record:
            token = user_record['token']
        else:
            token = None
    
    if token:
        course = acquire_course.get_kecheng(token, '1')
        data = course.get('data', [])
        return render_template('partials/dashboard.html', courses=data)
    else:
        # 如果没有有效的token，重定向到登录页面
        flash('请先登录')
        return redirect(url_for('login'))

    # conn = get_db_connection()
    # user = conn.execute('SELECT profile_complete FROM users WHERE id = ?', (current_user.id,)).fetchone()
    # conn.close()

    # if not user or not user['profile_complete']:
    #     from flask import make_response
    #     resp = make_response('')
    #     resp.headers['HX-Redirect'] = '/complete_profile'
    #     return resp

@app.route('/digital_course/<kecheng>')
@login_required
def digital_course(kecheng):
    # 获取当前用户的token
    if hasattr(current_user, 'token') and current_user.token:
        token = current_user.token
    else:
        # 从数据库加载token
        conn = get_db_connection()
        user_record = conn.execute('SELECT token FROM users WHERE id = ?', (current_user.id,)).fetchone()
        conn.close()
        if user_record:
            token = user_record['token']
        else:
            token = None

    if token:
        data = acquire_digitalcourse.fetch_course_resources(kecheng, token)
        if len(data.get('data', [])) == 0:
            return render_template('partials/mistake.html')
        else:     
            chapters,root_id = acquire_digitalcourse.process_resources(data)
            # print(chapters)
            todb = [
                (file_item['id'], file_item['name'])
                for chapter in chapters
                if 'files' in chapter and isinstance(chapter['files'], list)
                for file_item in chapter['files']
                if file_item.get('type') == 6
            ]           
            # print(todb)
            conn_2 = get_db_connection_2()
            cursor = conn_2.cursor()
            cursor.executemany("INSERT OR IGNORE INTO course (fileid, filename,note) VALUES (?, ?, '')", todb)
            conn_2.commit()
            conn_2.close()

            return render_template('partials/digital_course.html', chapters=chapters, root_id=root_id)
    else:
        flash('请先登录')
        return redirect(url_for('login'))

@app.route('/preview/<file_id>')
@login_required
def preview(file_id):
    # 获取当前用户的token
    if hasattr(current_user, 'token') and current_user.token:
        token = current_user.token
    else:
        # 从数据库加载token
        conn = get_db_connection()
        user_record = conn.execute('SELECT token FROM users WHERE id = ?', (current_user.id,)).fetchone()
        conn.close()
        if user_record:
            token = user_record['token']
        else:
            token = None

    if token:
        # full_path = os.path.join('./output_pdfs', f'{file_id}.pdf')
        filename = get_filename_by_fileid(file_id)
        if filename is None:
            return render_template('partials/mistake.html')
        else:
            url = pdf_download.main(token, file_id)
            session_instance = requests.Session()
            response = session_instance.get(url)
            filepath = f'./download/{file_id}/{filename}'
            os.makedirs(os.path.dirname(filepath), exist_ok=True) 
            with open(filepath, 'wb') as f:
                f.write(response.content)
            # topdf.convert_to_pdf_lightweight("./input", "./output_pdfs")
        preview_url = 'http://xiaoya.xn--estn41aqtae4v.xyz/get_file?filepath=' + file_id+'/'+filename
        preview_url_with_filename = preview_url + '&fullfilename=' + filename 

        base64_encoded_bytes = base64.b64encode(preview_url_with_filename.encode('utf-8'))
        base64_encoded_str = base64_encoded_bytes.decode('utf-8')
        url_encoded = urllib.parse.quote(base64_encoded_str, safe='')
        preview_url_kk = 'http://kkfile.xn--estn41aqtae4v.xyz/onlinePreview?url=' + url_encoded
        # print(preview_url_kk)
        return render_template('partials/preview.html', preview_url=preview_url_kk, file_id=file_id)
    else:
        flash('请先登录')
        return redirect(url_for('login'))

@app.route('/ai_analysis/<file_id>')
@login_required
def ai_analysis(file_id):
    if hasattr(current_user, 'token') and current_user.token:
        token = current_user.token
    else:
        # 从数据库加载token
        conn = get_db_connection()
        user_record = conn.execute('SELECT token FROM users WHERE id = ?', (current_user.id,)).fetchone()
        conn.close()
        if user_record:
            token = user_record['token']
        else:
            token = None
    
    print(f"开始处理AI分析，file_id: {file_id}")
    
    # 统一使用一个数据库连接
    conn_2 = get_db_connection_2()
    cursor = conn_2.cursor()

    # 查询是否有已存在的分析结果
    cursor.execute("SELECT node FROM course WHERE fileid = ?", (file_id,))
    existing_result = cursor.fetchone()
    if existing_result is not None and existing_result['node'] is not None and existing_result['node'].strip() != '':
        conn_2.close()
        print(f"找到已有分析结果，file_id: {file_id}")
        return render_template('partials/ai_analysis.html', re=existing_result['node'])
    
    # 如果记录不存在，关闭当前连接
    conn_2.close()
    
    print(f"未找到已有分析，开始处理新文件，file_id: {file_id}")
    
    filename = get_filename_by_fileid(file_id)
    print(f"获取到的文件名: {filename}")
    
    if filename is None:
        print(f"错误：无法找到file_id {file_id} 对应的文件名")
        return "无法找到对应的文件", 404
        
    file_path = f'./download/{file_id}/{filename}'
    print(f"文件路径: {file_path}")
    
    filestyle = extract_extension(filename)
    print(f"文件类型: {filestyle}")
    
    if filestyle == 'ppt':
        md = ppttotxt.ppt_to_txt(file_path)
        md = compress_cleancollection.summarize(md)
    elif filestyle == 'pptx':
        md = pptxtotxt.extract_text_from_pptx(file_path)
        md = compress_sklearn.summarize(md)
    elif filestyle == 'docx':
        md = docxtotxt.extract_text_from_docx(file_path)
        md = compress_sklearn.summarize(md)
    elif filestyle == 'pdf':
        md = pdftomd.pdf_to_markdown_alternative(file_path)
        md = compress_sklearn.summarize(md)
    else:
        return f"不支持的文件类型: {filestyle}", 400

    print(f"提取文本长度: {len(md)}")
    
    result = tokouriapi.chat_with_ai(md)
    result = mdtohtml.markdown_to_html_with_style_and_math(result)
    
    # 重新建立连接用于插入新结果
    conn_2 = get_db_connection_2()
    cursor = conn_2.cursor()
    cursor.execute("INSERT OR REPLACE INTO course (fileid, filename, note, node) VALUES (?, ?, '', ?)", (file_id, filename, result))
    conn_2.commit()
    conn_2.close()
    
    print(f"AI分析完成并已保存，file_id: {file_id}")
    return render_template('partials/ai_analysis.html', re=result)

    


# 流式AI分析接口
# @app.route('/stream_analyze/<file_id>')
# @login_required
# def stream_analyze(file_id):
#     """流式分析指定ID的PDF文件"""
#     # 获取当前用户的token
#     if not hasattr(current_user, 'token') or not current_user.token:
#         conn = get_db_connection()
#         user_record = conn.execute('SELECT token FROM users WHERE id = ?', (current_user.id,)).fetchone()
#         conn.close()
#         if user_record:
#             current_user.token = user_record['token']
#         else:
#             return Response(json.dumps({'error': '请先登录'}), mimetype='application/json', status=401)

#     # 下载文件
#     url = pdf_download.main(current_user.token, file_id)
#     session = requests.Session()
#     response = session.get(url)
#     file_path = f'./input/{file_id}'
#     with open(file_path, 'wb') as f:
#         f.write(response.content)

#     # 检查文件是否为PDF，如果不是则尝试转换
#     if not file_path.endswith('.pdf'):
#         try:
#             topdf.convert_to_pdf_lightweight("./input", "./output_pdfs")

#             # 检查转换后的PDF是否存在
#             converted_pdf_path = f"./output_pdfs/{file_id}.pdf"
#             if os.path.exists(converted_pdf_path):
#                 file_path = converted_pdf_path
#             else:
#                 # 如果转换失败，返回错误信息
#                 return Response(json.dumps({'error': '无法将将文件转换为PDF格式，AI分析功能需要PDF文件。'}), mimetype='application/json', status=400)
#         except Exception as e:
#             return Response(json.dumps({'error': f'文件转换过程中出现错误: {str(e)}'}), mimetype='application/json', status=400)
    
#     # 获取AI分析结果
#     aitext = todoubao.get_pdf_analysis(file_path)
    
#     # 创建简单的流式响应，发送AI分析结果
#     def generate():
#         # 发送分析结果
#         yield f"data: {json.dumps({'type': 'delta', 'content': aitext})}\n\n"
#         # 发送完成信号
#         yield f"data: {json.dumps({'type': 'done', 'content': 'Analysis completed'})}\n\n"

#     return Response(generate(), mimetype='text/plain')



# # 旧的AI分析路由，用于显示AI分析页面
# @app.route('/analyze_pdf/<file_id>')
# @login_required
# def analyze_pdf(file_id):
#     """显示AI分析页面"""
#     return render_template('partials/ai_analysis.html', file_id=file_id)

@app.route('/mistake')
def mistake():
    return render_template('partials/mistake.html')

if __name__ == '__main__':

    init_db() 
    new_table()
    app.run(debug=True, host='0.0.0.0', port=5088)