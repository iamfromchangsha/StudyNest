import fitz  # PyMuPDF
from markdownify import markdownify as md

def pdf_to_markdown_alternative(pdf_path):

    try:
        doc = fitz.open(pdf_path)  
        full_markdown_text = ""

        for page_num in range(doc.page_count):
            page = doc[page_num]
            page_html = page.get_text("html")
            page_markdown = md(page_html, strip=['img']) 
            full_markdown_text += page_markdown

        doc.close()  
        return full_markdown_text

    except FileNotFoundError:
        print(f"错误：找不到文件 '{pdf_path}'")
        return ""
    except fitz.FileDataError as e:
        print(f"错误：PDF 文件损坏或格式错误 - {e}")
        return ""
    except Exception as e:
        print(f"转换过程中发生未知错误: {type(e).__name__}: {e}")
        import traceback
        print("详细错误堆栈信息:")
        traceback.print_exc()
        return ""
