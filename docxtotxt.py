from docx import Document

def extract_text_from_docx(file_path):
    
    try:
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return "\n".join(full_text)
    
    except Exception as e:
        raise RuntimeError(f"无法读取DOCX文件 {file_path}: {e}")
