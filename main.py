import os
os.environ['TIKA_SERVER_JAR'] = "/xiaoya/tika-server-standard-3.2.3.jar"
import tika
try:
    import tika.tika
    tika.tika.TikaClientOnly = False  # 确保不是客户端模式
    tika.tika.TikaServerJar = "/xiaoya/tika-server-standard-3.2.3.jar"
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
import tokouriapi
import asyncio
from flask import Response
import json
import pdftomd
import mdtohtml
from flask import Flask, request, send_file, abort
import ppttotxt
import compress_sklearn
import compress_cleancollection
import time
import urllib.parse



app = flask.Flask(__name__)
app.secret_key = os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


BASE_DIRECTORY = os.path.abspath("./download")
os.makedirs(BASE_DIRECTORY, exist_ok=True)
def is_safe_path(base_directory, requested_path):

    requested_abs_path = os.path.abspath(requested_path)
    base_abs_path = os.path.abspath(base_directory)

    return requested_abs_path.startswith(base_abs_path + os.sep) or requested_abs_path == base_abs_path



@app.route('/get_file', methods=['GET'])
def get_file():

    filepath = request.args.get('filepath')

    if not filepath:
        abort(400, description="Missing 'filepath' parameter.")

    full_requested_path = os.path.join(BASE_DIRECTORY, filepath)

    if not is_safe_path(BASE_DIRECTORY, full_requested_path):
        app.logger.warning(f"Blocked attempt to access path outside base directory: {full_requested_path}")
        abort(403, description="Access denied. Path traversal detected.")

    if not os.path.exists(full_requested_path):
        abort(404, description=f"File not found: {filepath}")

    if not os.path.isfile(full_requested_path):
        abort(400, description=f"Path is not a file: {filepath}")

    try:
        return send_file(full_requested_path, as_attachment=False) 
    except Exception as e:
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
    conn = get_db_connection_2()  
    conn.execute("PRAGMA busy_timeout = 30000") 
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT filename FROM course WHERE fileid = ?", (fileid,))
        row = cursor.fetchone()
        if row:
            return row['filename'] 
        else:
            return None 
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


def extract_extension(filename):
    match = re.search(r'\.([^.]+)$', filename)
    if match:
        return match.group(1)
    else:
        return None  

class User(UserMixin):
    def __init__(self, user_id, username, token=None):
        self.id = user_id
        self.username = username
        self.token = token


@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT id, username, token FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        loaded_user = User(user['id'], user['username'])
        loaded_user.token = user['token'] 
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

    if response.status_code == 200:
        return True
    else:
        return False

def base64_encode_url(url: str) -> str:
    encoded = base64.b64encode(url.encode('utf-8')).decode('ascii')
    return quote(encoded, safe='')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('partials/home.html')

@app.route('/acount')
def acount():
    if not current_user.is_authenticated:
        return render_template('partials/acount.html', nickename=None, realname=None, imgurl="/static/default.png")

    
    if hasattr(current_user, 'token') and current_user.token:
        token = current_user.token
    else:
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

    else:
        print("头像获取失败")
        return render_template('partials/acount.html', nickename=None, realname=None, imgurl="/static/default.png")






@app.route('/about')
def about():
    return render_template('partials/about.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
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
            pass
        else:
            new_token = playwrightlogin.login(username, password, "2")
            if new_token is None:
                conn.close()
                return '<div class="alert alert-danger">智慧理工大账号验证失败</div>', 400

            conn.execute('UPDATE users SET token = ? WHERE id = ?', (new_token, user['id']))
            conn.commit()
            token = new_token

        conn.close()

        user_obj = User(user['id'], user['username'], token)
        login_user(user_obj)
        
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
    if hasattr(current_user, 'token') and current_user.token:
        token = current_user.token
    else:
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
        flash('请先登录')
        return redirect(url_for('login'))


@app.route('/digital_course/<kecheng>')
@login_required
def digital_course(kecheng):
    if hasattr(current_user, 'token') and current_user.token:
        token = current_user.token
    else:
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
            todb = [
                (file_item['id'], file_item['name'])
                for chapter in chapters
                if 'files' in chapter and isinstance(chapter['files'], list)
                for file_item in chapter['files']
                if file_item.get('type') == 6
            ]           
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
    if hasattr(current_user, 'token') and current_user.token:
        token = current_user.token
    else:
        conn = get_db_connection()
        user_record = conn.execute('SELECT token FROM users WHERE id = ?', (current_user.id,)).fetchone()
        conn.close()
        if user_record:
            token = user_record['token']
        else:
            token = None

    if token:
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
        preview_url = 'http://xiaoya.xn--estn41aqtae4v.xyz/get_file?filepath=' + file_id+'/'+filename
        preview_url_with_filename = preview_url + '&fullfilename=' + filename 

        base64_encoded_bytes = base64.b64encode(preview_url_with_filename.encode('utf-8'))
        base64_encoded_str = base64_encoded_bytes.decode('utf-8')
        url_encoded = urllib.parse.quote(base64_encoded_str, safe='')
        preview_url_kk = 'http://kkfile.xn--estn41aqtae4v.xyz/onlinePreview?url=' + url_encoded
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
        conn = get_db_connection()
        user_record = conn.execute('SELECT token FROM users WHERE id = ?', (current_user.id,)).fetchone()
        conn.close()
        if user_record:
            token = user_record['token']
        else:
            token = None
    
    print(f"开始处理AI分析，file_id: {file_id}")
    
    conn_2 = get_db_connection_2()
    cursor = conn_2.cursor()

    cursor.execute("SELECT node FROM course WHERE fileid = ?", (file_id,))
    existing_result = cursor.fetchone()
    if existing_result is not None and existing_result['node'] is not None and existing_result['node'].strip() != '':
        conn_2.close()
        print(f"找到已有分析结果，file_id: {file_id}")
        return render_template('partials/ai_analysis.html', re=existing_result['node'])
    
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
    
    conn_2 = get_db_connection_2()
    cursor = conn_2.cursor()
    cursor.execute("INSERT OR REPLACE INTO course (fileid, filename, note, node) VALUES (?, ?, '', ?)", (file_id, filename, result))
    conn_2.commit()
    conn_2.close()
    
    print(f"AI分析完成并已保存，file_id: {file_id}")
    return render_template('partials/ai_analysis.html', re=result)

    



@app.route('/mistake')
def mistake():
    return render_template('partials/mistake.html')

if __name__ == '__main__':

    init_db() 
    new_table()
    app.run(debug=True, host='0.0.0.0', port=5088)
