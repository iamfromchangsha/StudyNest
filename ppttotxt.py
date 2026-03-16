
from tika import parser

def ppt_to_txt(file_path):
    result = parser.from_file(file_path, serverEndpoint="http://localhost:9998")

    text = result.get("content", "").strip()
    if text: 
        output_path = file_path.replace(".ppt", ".txt").replace(".pptx", ".txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"\n📄 文字已保存到: {output_path}")
        return text
    else:
        print("⚠️ 未提取到任何文字")
        return ""
    
if __name__ == "__main__":
    md=ppt_to_txt(file_path)
    print(md)
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(md)
