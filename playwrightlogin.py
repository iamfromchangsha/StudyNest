# 请注意：需要先安装 playwright 和相关浏览器驱动
# pip install playwright
# playwright install chromium # (或其他你需要的浏览器, 如 firefox, webkit)

from playwright.sync_api import sync_playwright # 1. 导入 Playwright 同步 API
import re # 用于构建 URL 模式 (如果需要)

def login(account, password, a_xuanze):
    """
    使用 Playwright 登录并获取 WT-prd-access-token。

    Args:
        account (str): 用户名/账号。
        password (str): 密码。
        a_xuanze (str): 登录方式选择 ('1' 或 '2')。

    Returns:
        str or None: 成功则返回 access token，失败则返回 None。
    """
    # 2. 使用 with 语句管理 Playwright 上下文
    with sync_playwright() as p:
        # 3. 创建浏览器实例 (可选择是否 headless)
        browser = p.chromium.launch(
            headless=True, # 设置为 False 以有头模式运行，可以看到浏览器界面
            args=[
                "--disable-images", # 禁用图片加载 (Playwright 方式)
                # "--disable-stylesheets", # Playwright 似乎没有直接禁用 CSS 的 CLI arg，
                                        # 但可以在页面加载后执行 JS 来隐藏样式表
            ]
        )

        # 4. 创建新的浏览器上下文 (相当于 Selenium 的 window/tab)
        context = browser.new_context(
            # 也可以在这里设置初始视口大小等
            viewport={'width': 1920, 'height': 1080}, # 模拟最大化窗口
        )

        # 5. 创建新页面
        page = context.new_page()

        # 6. 根据 a_xuanze 选择登录 URL 和元素定位
        if a_xuanze == '1':
            login_url = 'https://infra.ai-augmented.com/app/auth/oauth2/login?response_type=code&state=e5v03n&client_id=xy_client_whut&redirect_uri=https://whut.ai-augmented.com/api/jw-starcmooc/user/authorCallback&school=10497&lang=zh_CN'
            account_selector = '#account'
            password_selector = '#password'
            login_button_selector = 'button.ant-btn.css-lxdosa.ant-btn-primary'
        elif a_xuanze == '2':
            login_url = 'https://infra.ai-augmented.com/api/auth/cas/casDirectLogin?schoolCertify=10497'
            account_selector = '#un'
            password_selector = '#pd'
            login_button_selector = '#index_login_btn'
        else:
            print(f"无效的 a_xuanze 值: {a_xuanze}")
            browser.close()
            return None

        # 7. 访问登录页面
        page.goto(login_url)

        # 8. 填写用户名和密码
        page.locator(account_selector).fill(account)
        page.locator(password_selector).fill(password)

        # 9. 点击登录按钮
        # 使用 click() 时，Playwright 会自动等待元素可点击
        page.locator(login_button_selector).click()

        # 10. 尝试关闭可能弹出的模态框 (如果存在)
        # 使用 expect_not_to_be_attached 或 wait_for_timeout 都可以
        # wait_for_timeout 是固定等待，不如等待元素消失精确
        # page.wait_for_timeout(3000) # 原来的 time.sleep(3) -> page.wait_for_timeout(3000)

        # 更好的方式是尝试等待关闭按钮出现并点击，然后等待其消失
        close_button_selector = 'span.anticon.anticon-close.ant-modal-close-icon'
        try:
            close_button = page.locator(close_button_selector)
            # 检查元素是否存在并可见
            if close_button.is_visible(timeout=5000): # 等待最多 5 秒看是否有关闭按钮
                close_button.click()
                # 等待该按钮不再附加到 DOM 中
                close_button.wait_for(state='detached', timeout=5000)
                print("Modal closed.")
        except Exception as e:
            # 如果在指定时间内没有找到按钮，或者点击/等待失败，则忽略
            print(f"No modal found or error closing it: {e}")

        # 11. 等待页面跳转或状态改变，确保登录成功
        # 可以根据登录成功后可能出现的 URL 特征或元素来判断
        # 这里暂时用一个较短的等待，实际情况可能需要更复杂的逻辑
        page.wait_for_timeout(6000) # 等待 3 秒让页面状态稳定
        
        # 检查是否存在"继续登录"按钮，如果存在则点击
        continue_login_button = page.locator('button:has-text("继续登录")')
        if continue_login_button.count() > 0 and continue_login_button.is_visible():
            continue_login_button.click()
            print("点击了'继续登录'按钮")

        # 12. 获取 Cookies
        # Playwright 需要知道要获取哪个域名下的 cookies
        # 假设 access token 存在主域名下，获取页面当前 URL 的 cookies
        cookies = context.cookies(page.url) # 使用当前页面 URL 作为域名参考
        print("All Cookies:", cookies)

        # 13. 提取 access token
        access_token_value = None
        for cookie in cookies:
            if cookie['name'] == 'WT-prd-access-token':
                access_token_value = cookie['value']
                break

        # 14. 关闭浏览器 (在 with 语句结束时自动发生)
        browser.close()

        print("Access Token:", access_token_value)
        return access_token_value

# --- 示例调用 ---
# login('1023007126', 'linyuxiang1540', '2') # 取消注释并修改参数以测试