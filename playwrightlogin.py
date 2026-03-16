

from playwright.sync_api import sync_playwright
import re 
def login(account, password, a_xuanze):

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-images", 
            ]
        )

        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
        )

        page = context.new_page()

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

        page.goto(login_url)

        page.locator(account_selector).fill(account)
        page.locator(password_selector).fill(password)

        page.locator(login_button_selector).click()

       
        close_button_selector = 'span.anticon.anticon-close.ant-modal-close-icon'
        try:
            close_button = page.locator(close_button_selector)
            if close_button.is_visible(timeout=5000):
                close_button.click()
                close_button.wait_for(state='detached', timeout=5000)
                print("Modal closed.")
        except Exception as e:
            print(f"No modal found or error closing it: {e}")

        page.wait_for_timeout(6000) 
        
        continue_login_button = page.locator('button:has-text("继续登录")')
        if continue_login_button.count() > 0 and continue_login_button.is_visible():
            continue_login_button.click()
            print("点击了'继续登录'按钮")

        cookies = context.cookies(page.url) 
        print("All Cookies:", cookies)

        access_token_value = None
        for cookie in cookies:
            if cookie['name'] == 'WT-prd-access-token':
                access_token_value = cookie['value']
                break

        browser.close()

        print("Access Token:", access_token_value)
        return access_token_value

