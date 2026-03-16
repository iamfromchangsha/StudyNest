import base64
from Crypto.Cipher import DES
from Crypto.Util.Padding import unpad
import requests
import json
import pickle
from urllib.parse import urlparse


def decrypt_file_url(encrypted_url):
    try:
        # 定义密钥和初始化向量（必须是8字节）
        key = b'94374647'
        iv = b'99526255'
        
        # 替换URL安全的Base64字符为标准字符
        base64_str = encrypted_url.replace('_', '+').replace('*', '/').replace('-', '=')
        
        # 解码Base64字符串
        encrypted_bytes = base64.b64decode(base64_str)
        
        # 创建DES解密器（CBC模式）
        cipher = DES.new(key, DES.MODE_CBC, iv)
        
        # 解密数据并移除填充
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        decrypted_data = unpad(decrypted_bytes, DES.block_size)
        
        # 转换为UTF-8字符串
        return decrypted_data.decode('utf-8')
    except Exception as e:
        print(f'URL解密失败: {e}')
        return encrypted_url

def huoquyuanma(url,token):
    headers = {
        'Authorization': 'Bearer '+token,
        'Cookie':'WT-prd-rememberme=false; WT-prd-language=zh-CN; WT-prd-access-token='+token+'; WT-prd-login-schoolId=f8d0cbf5d0d5aed8d698612d4212b7a9; WT-prd-refresh-token=5b7472731c074b6a9d4ea4d19ab2b8bb; WT-prd-refresh-token-state-v2=0; WT-prd-teaching-schoolId=0',
        'Referer':'https://whut.ai-augmented.com',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }

    
    
  
    ref = requests.get(url,headers=headers)
    print(ref.text)
    ref = json.loads(ref.text)
    ref = ref['data']['url']
    return ref
def main(token,file_id):
    session = requests.Session()
    randomma_url = 'https://whut.ai-augmented.com/api/jx-iresource/resource/queryResource?node_id='+str(file_id)
    headers = {
        'Authorization': 'Bearer '+token,
        'Cookie':'WT-prd-rememberme=false; WT-prd-language=zh-CN; WT-prd-access-token='+token+'; WT-prd-login-schoolId=f8d0cbf5d0d5aed8d698612d4212b7a9; WT-prd-refresh-token=5b7472731c074b6a9d4ea4d19ab2b8bb; WT-prd-refresh-token-state-v2=0; WT-prd-teaching-schoolId=0',
        'Referer':'https://whut.ai-augmented.com',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    randomma = requests.get(randomma_url,headers=headers)
    randomma = json.loads(randomma.text)
    randomma = randomma['data']
    parsed_url = urlparse(randomma)
    path_parts = parsed_url.path.split('/')
    file_uurl = path_parts[-1]
    url = 'https://whut.ai-augmented.com/api/jx-oresource/cloud/file_url/'+str(file_uurl)+'?encryption_status=1&filename='+str(file_uurl)+'.pptx'

    print(url)
    encrypted_url = huoquyuanma(url,token)
    #encrypted_url = "jVCVOu87R2yKqUZ8FAlxi4TXxIJpHMbY2dCW3xQmdPPYYxE9YizuKaGwIqJgBMECizScBO670fH*T4FOvRRiVt*f_8hpe3GCw5f6LJh_DtBQfKSNi2VJaS3BJ3FS*ZtycM7WNLQRhTKZXwk3fe15elQKmnXGSUIb8YlwEriVNqQMJ7Jgb6*oigcx0tb3wUl*reuIIXaKCA_037yRBQK8tJ3SWnPOAgXFC9XYUZlvC9roQ5S9qi096RvljVdU85Xr4jLM17mNq4A6wKCZBQrLzpwcFr8XiGwzrlbMTTqQud4hDJoMXzi417yQcP8W4xtbSrL0GVqFISN7bo3IGc4*jVr581EBySLIEgoWw9b4KnFJt4E0CuwTFIEJxJiN3YErMQ70J6DH96HymyhpLrP2kjNjTGzZMN_HUuo8imZGxm3Yp7FyxzRTkQ-="
    decrypted_url = decrypt_file_url(encrypted_url)
    print(decrypted_url)
    return decrypted_url
    # print(f"解密后的URL: {decrypted_url}")
    # ress = session.get('https://vip.ow365.cn/owview/p/pv.aspx?PowerPointView=ReadingView&WOPISrc='+decrypted_url)
    # response = session.get(decrypted_url)
    # with open(str(file_name), 'wb') as f:
    #     f.write(response.content)

# decrypt_file_url('https://whut.ai-augmented.com/cloud/file_access/6880708511207051206')