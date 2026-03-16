import base64
from Crypto.Cipher import DES
from Crypto.Util.Padding import unpad
import requests
import json
import pickle
from urllib.parse import urlparse


def decrypt_file_url(encrypted_url):
    try:
        key = b'94374647'
        iv = b'99526255'
        
        base64_str = encrypted_url.replace('_', '+').replace('*', '/').replace('-', '=')
        
        encrypted_bytes = base64.b64decode(base64_str)
        
        cipher = DES.new(key, DES.MODE_CBC, iv)
        
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        decrypted_data = unpad(decrypted_bytes, DES.block_size)
        
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
    decrypted_url = decrypt_file_url(encrypted_url)
    print(decrypted_url)
    return decrypted_url

