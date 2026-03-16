import subprocess
import os
import shutil # 用于查找可执行文件
from pathlib import Path
import mimetypes

def find_libreoffice_executable():
    """尝试查找 LibreOffice 的可执行文件路径 (soffice 或 loffice)"""
    possible_names = ['loffice', 'soffice'] # Linux/macOS 通常用 loffice, Windows 用 soffice
    for name in possible_names:
        exe_path = shutil.which(name)
        if exe_path:
            print(f"找到 LibreOffice 可执行文件: {exe_path}")
            return exe_path
    return None

def is_convertible_file(file_path):
    """
    检查文件是否为可以转换为PDF的类型
    对于没有扩展名的文件，使用多种方法尝试识别
    """
    # 获取文件扩展名
    ext = file_path.suffix.lower()
    
    # 常见的LibreOffice支持的文件类型
    supported_exts = {
        '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',  # Office类型
        '.odt', '.ods', '.odp', '.odg', '.odf',            # OpenDocument类型
        '.rtf', '.txt', '.csv',                            # 文本和表格类型
        '.html', '.htm', '.epub', '.xml'                   # 其他文档类型
    }
    
    if ext in supported_exts:
        return True
    
    # 对于没有扩展名或未知扩展名的文件，尝试使用mimetype检测
    mime_type, _ = mimetypes.guess_type(str(file_path))
    
    if mime_type:
        # 检查是否为文档类型
        if mime_type.startswith(('text/', 'application/msword', 'application/vnd.', 'application/rtf')):
            return True
    
    # 如果无法通过mimetype识别，可以尝试读取文件头来判断
    # 这里我们简单地对没有扩展名但可能是文档的文件返回True，让LibreOffice尝试转换
    if not ext:
        # 检查文件大小，避免对空文件或非常小的文件尝试转换
        if file_path.stat().st_size > 100:  # 文件大于100字节
            return True

    return False

def convert_to_pdf_lightweight(input_path_str, output_dir_str=None, force_convert=True, delete_source=True):
    """
    使用 LibreOffice (soffice/loffice) 进行转换。
    支持单个文件或整个目录的转换。
    force_convert: 强制转换，即使不能确定文件类型也尝试转换
    delete_source: 转换成功后删除源文件
    """
    # 尝试查找 LibreOffice 可执行文件
    libreoffice_exe = find_libreoffice_executable()
    if not libreoffice_exe:
        print("错误: 找不到 LibreOffice 的可执行文件 (soffice 或 loffice)。")
        print("请确保 LibreOffice 已安装并且其可执行文件路径已被添加到系统的 PATH 环境变量中。")
        return

    input_path = Path(input_path_str)
    output_dir = Path(output_dir_str) if output_dir_str else input_path.parent

    if not input_path.exists():
        print(f"错误: 输入路径不存在 {input_path}")
        return

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 处理单个文件
    if input_path.is_file():
        # 对于没有后缀名的文件，我们默认尝试转换
        should_convert = force_convert or is_convertible_file(input_path)
        
        if not should_convert:
            print(f"跳过不可转换的文件: {input_path}")
            return

        # 对于单个文件，直接转换到目标目录
        cmd = [
            libreoffice_exe,
            "--headless",       # 无头模式，不显示 UI (在 Windows 上可能也需要 --invisible)
            "--invisible",      # Windows 上可能需要这个参数确保完全不可见
            "--nodefault",      # 不创建默认文档
            "--nolockcheck",    # 不检查文件锁定
            "--nologo",         # 不显示启动画面
            "--norestore",      # 禁止恢复
            "--convert-to", "pdf",
            "--outdir", str(output_dir),
            str(input_path)
        ]
        print(f"正在转换 ({Path(libreoffice_exe).stem}): {input_path.name} -> 目录 '{output_dir}'")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120) # 添加超时
            expected_pdf_name = f"{input_path.stem}.pdf"
            expected_full_path = output_dir / expected_pdf_name
            if expected_full_path.exists():
                print(f"  -> 成功: 已生成 {expected_full_path}")
                # 如果转换成功且设置了删除源文件标志，则删除原文件
                if delete_source:
                    input_path.unlink()
                    print(f"  -> 源文件已删除: {input_path}")
            else:
                print(f"  -> 警告: 未在预期位置找到 {expected_full_path}")
                if result.stdout:
                    print(f"     stdout: {result.stdout}")
                if result.stderr:
                    print(f"     stderr: {result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"  -> 错误: 转换失败 {input_path.name}")
            print(f"     Return code: {e.returncode}")
            if e.stdout:
                print(f"     stdout: {e.stdout}")
            if e.stderr:
                print(f"     stderr: {e.stderr}")
        except subprocess.TimeoutExpired:
            print(f"  -> 错误: 转换超时 {input_path.name}")


    # 处理目录
    elif input_path.is_dir():
        # 对于目录，我们获取所有文件并尝试转换
        all_files = [f for f in input_path.rglob("*") if f.is_file()]
        
        if not all_files:
            print(f"在目录 '{input_path}' 中未找到任何文件。")
            return

        print(f"在 '{input_path}' 中找到 {len(all_files)} 个文件，开始转换...")

        for file_path in all_files:
            # 检查是否应该尝试转换此文件
            if not force_convert and not is_convertible_file(file_path):
                print(f"跳过不可转换的文件: {file_path}")
                continue

            # 计算相对于输入根目录的路径，以便在输出目录中重建相同的子目录结构
            relative_path = file_path.relative_to(input_path)
            # 构造目标 PDF 文件在输出目录中的父目录
            target_pdf_dir = output_dir / relative_path.parent
            target_pdf_dir.mkdir(parents=True, exist_ok=True) # 确保子目录存在

            cmd = [
                libreoffice_exe,
                "--headless",
                "--invisible",
                "--nodefault",
                "--nolockcheck",
                "--nologo",
                "--norestore",
                "--convert-to", "pdf",
                "--outdir", str(target_pdf_dir), # 输出到计算出的子目录
                str(file_path)
            ]
            print(f"正在转换 ({Path(libreoffice_exe).stem}): {relative_path} -> {target_pdf_dir}")
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120) # 添加超时
                expected_pdf_name = f"{file_path.stem}.pdf"
                expected_full_path = target_pdf_dir / expected_pdf_name
                if expected_full_path.exists():
                    print(f"  -> 成功: 已生成 {expected_full_path}")
                    # 如果转换成功且设置了删除源文件标志，则删除原文件
                    if delete_source:
                        file_path.unlink()
                        print(f"  -> 源文件已删除: {file_path}")
                else:
                    print(f"  -> 警告: 未在预期位置找到 {expected_full_path}")
                    if result.stdout:
                        print(f"     stdout: {result.stdout}")
                    if result.stderr:
                        print(f"     stderr: {result.stderr}")
            except subprocess.CalledProcessError as e:
                print(f"  -> 错误: 转换失败 {file_path.name}")
                print(f"     Return code: {e.returncode}")
                if e.stdout:
                    print(f"     stdout: {e.stdout}")
                if e.stderr:
                    print(f"     stderr: {e.stderr}")
            except subprocess.TimeoutExpired:
                print(f"  -> 错误: 转换超时 {file_path.name}")

# # --- 示例用法 ---
# if __name__ == "__main__":
#     input_path = "./input" # 指向你的输入文件或包含输入文件的目录
#     output_directory = "./output_pdfs" # 指向你希望存放输出 PDF 文件的目录

#     convert_to_pdf_lightweight(input_path, output_directory, delete_source=True)
#     print("\n转换流程结束。")

