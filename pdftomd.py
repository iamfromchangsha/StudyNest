import fitz  # PyMuPDF
from markdownify import markdownify as md

def pdf_to_markdown_alternative(pdf_path):
    """
    将 PDF 文件转换为 Markdown 格式的字符串 (备用方法：HTML -> Markdown)，不包含图片的 Base64 编码。

    Args:
        pdf_path (str): 输入 PDF 文件的路径。

    Returns:
        str: 转换后的 Markdown 文本。如果发生错误，则返回空字符串。
    """
    try:
        doc = fitz.open(pdf_path)  # 打开PDF文档
        full_markdown_text = ""

        for page_num in range(doc.page_count):
            page = doc[page_num]
            # 提取页面的 HTML 内容
            page_html = page.get_text("html")
            # 将 HTML 转换为 Markdown，同时忽略 <img> 标签
            # strip=['img'] 会移除 img 标签及其内容
            page_markdown = md(page_html, strip=['img']) 
            full_markdown_text += page_markdown
            # 可选：在页面之间添加分隔符
            # full_markdown_text += "\n---\n"

        doc.close()  # 关闭文档
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

# # --- 使用示例 ---
# if __name__ == "__main__":
#     pdf_file_path = "./output_pdfs/6795079840325179263.pdf"  # 替换为你的PDF文件路径

#     result_md = pdf_to_markdown_alternative(pdf_file_path)

#     if result_md:
#         print("--- 转换成功 (备用方法, 无图片) ---")
#         print(result_md[:500]) # 打印前500个字符作为预览
#         print("...")
        
#         # 可选：将结果保存到文件
#         with open("output_alt_no_img.md", "w", encoding="utf-8") as f:
#             f.write(result_md)
#         print("\n转换完成，结果已保存到 output_alt_no_img.md")
#     else:
#         print("--- 转换失败，请检查上面的错误信息 ---")

# a = pdf_to_markdown_alternative("./output_pdfs/6795079840325179263.pdf")  # 示例调用
# print(a)