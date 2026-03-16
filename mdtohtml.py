import re
import markdown

def markdown_to_html_with_style_and_math(markdown_text):

    # --- 预处理：将LaTeX标准标记转换为MathJax能识别的格式 ---
    # 处理行内公式 $...$ 转换为 \(...\)
    processed_text = re.sub(r'\$(.*?)\$', r'\\(\1\\)', markdown_text)
    
    # 处理独立行的块级公式 $$...$$ 转换为 \[...\]
    processed_text = re.sub(r'^\$\$(.*?)\$\$$', r'\\[\1\\]', processed_text, flags=re.MULTILINE)
    
    # --- 预处理：确保标题前后有换行 ---
    lines = processed_text.split('\n')
    final_lines = []
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if re.match(r'^#{1,6} ', stripped_line):  # 匹配标题行
            # 如果不是第一行且前一行非空，则加空行
            if i > 0 and final_lines[-1].strip() != "":
                final_lines.append("")
            final_lines.append(stripped_line)
            # 如果不是最后一行且下一行非空且不是另一个标题，则加空行
            if i + 1 < len(lines) and lines[i+1].strip() != "" and not re.match(r'^#{1,6} ', lines[i+1].strip()):
                final_lines.append("")
        else:
            final_lines.append(line)
    processed_text = "\n".join(final_lines)

    # --- Markdown 转换 ---
    # 'extra' 包含 tables, fenced_code_blocks, header_id 等
    # 'codehilite' 用于代码高亮
    # 'toc' 用于生成目录 (可选)
    # 'nl2br' 将换行符转换为 <br> (有时有用，但需注意与表格的兼容性)
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'tables', 'toc', 'nl2br'])
    html_body = md.convert(processed_text)

    html_body = re.sub(r'<em>(.*?)</em>', r'\1', html_body)

    # --- 添加全局样式 ---
    style = """
    <style>
    body {
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 1000px;
        margin: 0 auto;
        padding: 20px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    table, th, td {
        border: 1px solid #ddd;
    }
    th, td {
        padding: 10px;
        text-align: left;
    }
    th {
        background-color: #f2f2f2;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;
    }
    h1 {
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
    }
    h2 {
        border-bottom: 1px solid #bdc3c7;
        padding-bottom: 8px;
    }
    pre {
        background-color: #2c3e50;
        color: #ecf0f1;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
        margin: 15px 0;
    }
    code {
        background-color: #ecf0f1;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: monospace;
    }
    blockquote {
        border-left: 4px solid #3498db;
        padding-left: 15px;
        margin-left: 0;
        color: #7f8c8d;
        font-style: italic;
    }
    /* MathJax 默认居中显示独立公式 */
    .MathJax_Display {
        text-align: center;
    }
    </style>
    """

    # --- 添加 MathJax 配置和 CDN 链接 ---
    mathjax_config = """
    <script>
      window.MathJax = {
        tex: {
          inlineMath: [['\\(', '\\)']],     // 行内公式定界符
          displayMath: [['\\[', '\\]']],   // 块级公式定界符
          processEscapes: true,
          processEnvironments: true
        },
        svg: {
          fontCache: 'global' // 使用全局字体缓存
        }
      };
    </script>
    <script type="text/javascript" id="MathJax-script" async
      src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js">
    </script>
    """

    # 将样式、MathJax 配置和内容组合在一起
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Markdown to HTML with Math</title>
    {style}
    {mathjax_config}
</head>
<body>
    {html_body}
</body>
</html>"""

    return full_html