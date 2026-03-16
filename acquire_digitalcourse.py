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
    
    # 1. 找到root节点（顶级目录）
    root = next((item for item in items if item['name'] == 'root'), None)
    if not root:
        return [], None
    root_id = root['id']  # root的唯一标识，用于判断直接子节点（章节）
    
    # 2. 区分章节（目录）和文件（任务等）
    chapters = []  # 章节：type=1且是root的直接子节点（parent_id=root_id）
    materials = []  # 文件：type!=1（如type=7/8）
    
    for item in items:
        # 跳过root自身
        if item['id'] == root_id:
            continue
        
        item_type = item.get('type', 0)
        parent_id = item.get('parent_id', '')
        
        # 章节判定：type=1（目录类型）且父节点是root（直接子节点）
        if item_type == 1 and parent_id == root_id:
            chapters.append({
                'id': item['id'],
                'name': item['name'],
                'updated_at': item.get('updated_at', ''),
                'sort_position': item.get('sort_position', 0)  # 用于排序的位置字段
            })
        
        # 文件判定：type!=1（非目录类型，如任务、资料等）
        elif item_type != 1:
            materials.append({
                'id': item['id'],
                'name': item['name'],
                'parent_id': parent_id,
                'type': item_type  # 保留文件类型
            })
    
    # 3. 处理无章节的情况：创建默认章节
    has_default_chapter = False
    if not chapters:
        chapters.append({
            'id': 'default_chapter',
            'name': '默认文件夹',
            'updated_at': '',
            'sort_position': 0
        })
        has_default_chapter = True
    
    # 4. 按sort_position排序章节（原数据中章节有明确的位置编号）
    chapters.sort(key=lambda x: x['sort_position'])
    
    # 5. 建立章节与文件的映射（按parent_id匹配）
    chapter_files = {
        chapter['id']: {
            'name': chapter['name'],
            'files': [],
            'updated_at': chapter['updated_at']
        } for chapter in chapters
    }
    
    # 分配文件到对应章节
    for material in materials:
        parent_id = material['parent_id']
        # 若文件的父节点是章节，则归入对应章节
        if parent_id in chapter_files:
            chapter_files[parent_id]['files'].append({
                'id': material['id'],
                'name': material['name'],
                'type': material['type']
            })
        # 如果没有匹配到章节，但有默认章节，则放入默认章节
        elif has_default_chapter:
            chapter_files['default_chapter']['files'].append({
                'id': material['id'],
                'name': material['name'],
                'type': material['type']
            })
    
    # 6. 格式化结果（提取日期部分）
    result = [
        {
            'id': cid,
            'name': cdata['name'],
            'files': cdata['files'],
            'updated_at': cdata['updated_at'].split('T')[0] if 'T' in cdata['updated_at'] else cdata['updated_at']
        } for cid, cdata in chapter_files.items()]
    
    return result, root_id
    



'''
def get_course_resource(group_id,token):
    headers = {
        'Authorization': 'Bearer '+token,
        'Cookie':'WT-prd-rememberme=false; WT-prd-language=zh-CN; WT-prd-access-token='+token+'; WT-prd-login-schoolId=f8d0cbf5d0d5aed8d698612d4212b7a9; WT-prd-refresh-token=5b7472731c074b6a9d4ea4d19ab2b8bb; WT-prd-refresh-token-state-v2=0; WT-prd-teaching-schoolId=0',
        'Referer':'https://whut.ai-augmented.com',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    url = 'https://whut.ai-augmented.com/api/jx-iresource/resource/queryCourseResources?group_id='+group_id
    response = requests.get(url,headers=headers)
    response = json.loads(response.text)
    data = response['data']
    print(data)
    changjie_name = []
    changjie_path = []
    changjie_id = []
    Misaka_Mikoto_name = []
    Misaka_Mikoto_path = []
    Misaka_Mikoto_id = []
    Misaka_Mikoto_parent_id = []
    for Shirai_Kuroko in data:
        if Shirai_Kuroko['name'] =='root':
            root = []
            root.append(Shirai_Kuroko['path'])
            length = len(Shirai_Kuroko['path'])
       
        if len(Shirai_Kuroko['path'])>length + 2 and len(Shirai_Kuroko['path'])<2 * length + 5:
            
            changjie_name.append(Shirai_Kuroko['name'])
           
            changjie_path.append(Shirai_Kuroko['path'])
            
            changjie_id.append(Shirai_Kuroko['id'])
        if len(Shirai_Kuroko['path'])>2 * length + 5:
           
            Misaka_Mikoto_name.append(Shirai_Kuroko['name'])
            
            Misaka_Mikoto_path.append(Shirai_Kuroko['path'])    
           
            Misaka_Mikoto_id.append(Shirai_Kuroko['id'])
            
            Misaka_Mikoto_parent_id.append(Shirai_Kuroko['parent_id'])

    Misaka_Mikoto_i = []
    changjie_j = []
    for i in range(len(Misaka_Mikoto_parent_id)):
        for j in range(len(changjie_id)):
            if Misaka_Mikoto_parent_id[i] == changjie_id[j]:
                Misaka_Mikoto_i.append(i)
                changjie_j.append(j)
                print(Misaka_Mikoto_name[i],Misaka_Mikoto_path[i],Misaka_Mikoto_id[i])
    
    print(Misaka_Mikoto_i,changjie_j)
    print(changjie_name,changjie_path,changjie_id)
    chapter_files = {name: [] for name in changjie_name}
    for index, chapter in enumerate(changjie_j):
        if chapter < len(changjie_name):  # 确保章节编号在范围内
            chapter_name = changjie_name[chapter]
            chapter_files[chapter_name].append(index)

    for chapter, files in chapter_files.items():
        formatted_files = ', '.join(Misaka_Mikoto_name[file_index] for file_index in files)
        print(f"{chapter}: Files [{formatted_files}]")



    return data

get_course_resource('6630748833959681934','346031390f5c470b8417e5d5a13875dd')
'''


