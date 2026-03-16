from pptx import Presentation

def extract_text_from_pptx(file_path):

    try:
        prs = Presentation(file_path)
        text_runs = []

        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text_runs.append(shape.text)
        
        return "\n".join(text_runs)
    
    except Exception as e:
        raise RuntimeError(f"无法读取PPTX文件 {file_path}: {e}")
    

