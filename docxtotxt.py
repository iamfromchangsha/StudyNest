from docx import Document

def extract_text_from_docx(file_path):
    """
    从 .docx 文件中提取所有文本内容。

    参数:
        file_path (str): DOCX 文件的路径。

    返回:
        str: 文档中所有段落文本，用换行符 '\n' 连接。
    """
    try:
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return "\n".join(full_text)
    
    except Exception as e:
        raise RuntimeError(f"无法读取DOCX文件 {file_path}: {e}")