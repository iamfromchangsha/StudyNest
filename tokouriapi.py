import requests
import json

baseurl = "https://api.kourichat.com/v1/chat/completions"
headers = {"Authorization": "Bearer sk-kouri-aO12bhIupWw5u0WlqK2LYUfdlNKJBeOYDIXeijpXLZS2LnTI"}

def chat_with_ai(content, model="longcat-flash-thinking", temperature=0.7, max_tokens=10000):

    messages = [
        {
            "role": "system", 
            "content": "你是一位专业的课程分析师，仔细阅读并理解上传的课件内容。你的任务是提炼出文档的核心内容，生成一份结构清晰、内容准确的Markdown格式总结。具体要求：1. 提取关键信息：识别并总结课件中的核心概念、重要定义、关键论点、主要步骤或流程、重要的数据和结论等。2. 保持逻辑结构：如果原文档有明确的章节划分，请在总结中保留相应的Markdown标题层级。3. 使用Markdown格式：总结内容必须使用标准Markdown语法。4. 语言精炼：总结应言简意赅，用自己的话复述原文内容，避免大段摘抄原文。5. 完整覆盖：确保总结涵盖课件的主要知识点，形成一个完整的知识体系概览。6. 忽略无关元素：可以忽略页眉、页脚、装饰性图片、版权信息等非核心内容。7. 数学公式处理：使用$$符号包裹LaTeX数学公式。"
        },
        {
            "role": "user", 
            "content": content + "\n\n请以专业老师的角度给出知识点总结。请以标准格式的形式返回内容。使用$$符号包裹latex数学公式。"
        }
    ]
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    try:
        result = requests.post(baseurl, headers=headers, json=payload, timeout=200) 
        result.raise_for_status()  
        
        response_data = result.json()
        if "choices" in response_data and len(response_data["choices"]) > 0:
            return response_data["choices"][0]["message"]["content"]
        else:
            return "分析失败：无法获取有效响应"
            
    except requests.exceptions.Timeout:
        print("API请求超时")
        return "分析失败：请求超时，请稍后重试"
    except requests.RequestException as e:
        print(f"API请求失败: {e}")
        return f"分析失败：{str(e)}"
    except json.JSONDecodeError as e:
        print(f"响应解析失败: {e}")
        return f"分析失败：响应格式错误"
