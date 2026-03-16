import requests
import json


def fetch_course_resources(group_id, token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Cookie': f'WT-prd-rememberme=false; WT-prd-language=zh-CN; WT-prd-access-token={token}; WT-prd-login-schoolId=f8d0cbf5d0d5aed8d698612d4212b7a9; WT-prd-refresh-token=5b7472731c074b6a9d4ea4d19ab2b8bb; WT-prd-refresh-token-state-v2=0; WT-prd-teaching-schoolId=0',
        'Referer': 'https://whut.ai-augmented.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    url = f'https://whut.ai-augmented.com/api/jx-iresource/resource/queryCourseResources?group_id={group_id}'
    response = requests.get(url, headers=headers)
    print(response.json())
    return response.json()

def process_resources(data):
    if not data or 'data' not in data:
        return [], None
    
    items = data['data']

    root = next((item for item in items if item['name'] == 'root'), None)
    if not root:
        return [], None
    root_id = root['id']  
    
    chapters = []  
    materials = []  
    
    for item in items:
        if item['id'] == root_id:
            continue
        
        item_type = item.get('type', 0)
        parent_id = item.get('parent_id', '')
        
        if item_type == 1 and parent_id == root_id:
            chapters.append({
                'id': item['id'],
                'name': item['name'],
                'updated_at': item.get('updated_at', ''),
                'sort_position': item.get('sort_position', 0) 
            })
        
        elif item_type != 1:
            materials.append({
                'id': item['id'],
                'name': item['name'],
                'parent_id': parent_id,
                'type': item_type  
            })
    
    has_default_chapter = False
    if not chapters:
        chapters.append({
            'id': 'default_chapter',
            'name': '默认文件夹',
            'updated_at': '',
            'sort_position': 0
        })
        has_default_chapter = True
    
    chapters.sort(key=lambda x: x['sort_position'])
    
    chapter_files = {
        chapter['id']: {
            'name': chapter['name'],
            'files': [],
            'updated_at': chapter['updated_at']
        } for chapter in chapters
    }
    
    for material in materials:
        parent_id = material['parent_id']
        if parent_id in chapter_files:
            chapter_files[parent_id]['files'].append({
                'id': material['id'],
                'name': material['name'],
                'type': material['type']
            })
        elif has_default_chapter:
            chapter_files['default_chapter']['files'].append({
                'id': material['id'],
                'name': material['name'],
                'type': material['type']
            })
    
    result = [
        {
            'id': cid,
            'name': cdata['name'],
            'files': cdata['files'],
            'updated_at': cdata['updated_at'].split('T')[0] if 'T' in cdata['updated_at'] else cdata['updated_at']
        } for cid, cdata in chapter_files.items()]
    
    return result, root_id
    



