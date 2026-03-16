# 智慧理工大课程学习助手

这是一个基于Flask开发的Web应用程序，旨在帮助学生更高效地管理和学习智慧理工大的在线课程资源。系统提供了课程管理、资料预览、AI分析等功能。

## 功能特性

- **用户认证系统**：支持用户登录、登出，自动获取智慧理工大学习平台的认证Token
- **课程管理**：展示用户的数字课程列表
- **资料预览**：支持课程资料在线预览（PDF格式）
- **AI分析**：对课程资料进行AI分析，自动生成Markdown格式的学习摘要
- **数学公式渲染**：支持LaTeX数学公式的渲染显示
- **响应式界面**：采用HTMX实现动态内容加载

## 技术栈

- **后端**: Python, Flask
- **前端**: HTML, CSS, JavaScript, HTMX
- **数据库**: SQLite3
- **AI分析**: 通过Doubao API进行PDF内容分析
- **文档转换**: PDF转Markdown工具
- **样式**: Bootstrap框架

## 项目结构

```
.
├── doubao/
│   └── test.py
├── static/
│   └── style.css
├── templates/
│   ├── partials/
│   │   ├── about.html
│   │   ├── ai_analysis.html
│   │   ├── complete_profile.html
│   │   ├── dashboard.html
│   │   ├── digital_course.html
│   │   ├── home.html
│   │   ├── login.html
│   │   ├── mistake.html
│   │   ├── preview.html
│   │   ├── register.html
│   │   └── preview.html
│   ├── base.html
│   └── index.html
├── acquire_course.py          # 获取课程信息
├── acquire_digitalcourse.py   # 获取数字课程资源
├── coze.py
├── main.py                   # 主应用入口
├── mdtohtml.py               # Markdown转HTML工具
├── output_alt.md
├── output_with_math.html
├── pdf_download.py           # PDF下载工具
├── pdftomd.py                # PDF转Markdown工具
├── playwrightlogin.py        # Playwright登录模块
├── seleniumlogin.py          # Selenium登录模块
├── sharefile.py
├── todoubao.py               # Doubao AI接口
├── topdf.py                  # 转PDF工具
├── video.py
├── 完蛋了.py
└── README.md                 # 项目说明文档
```

## 安装与运行

1. 确保已安装Python 3.x环境
2. 安装依赖包：
   ```bash
   pip install flask flask-login flask-wtf wtforms requests volcenginesdkarkruntime
   ```
   安装 tika-server-standard-3.2.3.jar
3. 初始化数据库并启动应用：
   ```bash
   python main.py
   ```
4. 访问 http://127.0.0.1:5088 查看应用

## 主要功能模块说明

### 用户认证
- 使用Playwright或Selenium模拟登录智慧理工大学习平台
- 自动获取和维护认证Token
- 数据库存储用户信息和Token

### 课程获取
- [acquire_course.py](file:///e:%5C%E6%A1%8C%E9%9D%A2%5C3s%E9%A1%B9%E7%9B%AE%5C%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%BB%A1%5Cacquire_course.py) 和 [acquire_digitalcourse.py](file:///e:%5C%E6%A1%8C%E9%9D%A2%5C3s%E9%A1%B9%E7%9B%AE%5C%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%BB%A1%5Cacquire_digitalcourse.py) 分别负责获取课程列表和课程资源
- 通过API调用获取用户课程信息

### 文件处理
- [pdf_download.py](file:///e:%5C%E6%A1%8C%E9%9D%A2%5C3s%E9%A1%B9%E7%9B%AE%5C%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%BB%A1%5Cpdf_download.py) 负责下载课程相关文件
- [topdf.py](file:///e:%5C%E6%A1%8C%E9%9D%A2%5C3s%E9%A1%B9%E7%9B%AE%5C%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%BB%A1%5Ctopdf.py) 提供PDF转换功能
- [pdftomd.py](file:///e:%5C%E6%A1%8C%E9%9D%A2%5C3s%E9%A1%B9%E7%9B%AE%5C%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%BB%A1%5Cpdftomd.py) 实现PDF到Markdown的转换

### AI分析
- [todoubao.py](file:///e:%5C%E6%A1%8C%E9%9D%A2%5C3s%E9%A1%B9%E7%9B%AE%5C%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%BB%A1%5Ctodoubao.py) 调用DoubaoAPI对课程资料进行AI分析
- [mdtohtml.py](file:///e:%5C%E6%A1%8C%E9%9D%A2%5C3s%E9%A1%B9%E7%9B%AE%5C%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%BB%A1%5Cmdtohtml.py) 将Markdown转换为带样式的HTML

## 页面说明

- **首页** ([templates/index.html](file:///e:%5C%E6%A1%8C%E9%9D%A2%5C3s%E9%A1%B9%E7%9B%AE%5C%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%BB%A1%5Ctemplates%5Cindex.html)): 应用入口页面
- **登录页** ([templates/partials/login.html](file:///e:%5C%E6%A1%8C%E9%9D%A2%5C3s%E9%A1%B9%E7%9B%AE%5C%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%BB%A1%5Ctemplates%5Cpartials%5Clogin.html)): 用户登录界面
- **仪表盘** ([templates/partials/dashboard.html](file:///e:%5C%E6%A1%8C%E9%9D%A2%5C3s%E9%A1%B9%E7%9B%AE%5C%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%BB%A1%5Ctemplates%5Cpartials%5Cdashboard.html)): 展示用户课程列表
- **数字课程页** ([templates/partials/digital_course.html](file:///e:%5C%E6%A1%8C%E9%9D%A2%5C3s%E9%A1%B9%E7%9B%AE%5C%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%BB%A1%5Ctemplates%5Cpartials%5Cdigital_course.html)): 显示课程资源结构
- **预览页** ([templates/partials/preview.html](file:///e:%5C%E6%A1%8C%E9%9D%A2%5C3s%E9%A1%B9%E7%9B%AE%5C%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%BB%A1%5Ctemplates%5Cpartials%5Cpreview.html)): 在线预览课程资料
- **AI分析页** ([templates/partials/ai_analysis.html](file:///e:%5C%E6%A1%8C%E9%9D%A2%5C3s%E9%A1%B9%E7%9B%AE%5C%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%BB%A1%5Ctemplates%5Cpartials%5Cai_analysis.html)): 显示AI生成的学习摘要

## 注意事项

- 运行前确保网络连接正常，部分功能需要访问外部API
- 初次运行会自动创建SQLite数据库文件[koitoyuu.db](file:///e:%5C%E6%A1%8C%E9%9D%A2%5C3s%E9%A1%B9%E7%9B%AE%5C%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%BB%A1%5Ckoitoyuu.db)
- 需要有效的智慧理工大学习平台账号才能使用全部功能
- AI分析功能依赖外部API，可能产生费用

## 开发与维护

本项目采用模块化设计，便于功能扩展和维护。如需添加新功能，建议按照现有架构模式进行开发：

1. 在[main.py](file:///e:%5C%E6%A1%8C%E9%9D%A2%5C3s%E9%A1%B9%E7%9B%AE%5C%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%BB%A1%5Cmain.py)中添加路由和控制器
2. 在[templates/partials](file:///e:%5C%E6%A1%8C%E9%9D%A2%5C3s%E9%A1%B9%E7%9B%AE%5C%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%BB%A1%5Ctemplates%5Cpartials)中添加对应的页面模板
3. 如需要新功能模块，在根目录创建相应.py文件
