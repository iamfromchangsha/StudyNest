import subprocess
import os
import shutil 
from pathlib import Path
import mimetypes

def find_libreoffice_executable():
    possible_names = ['loffice', 'soffice'] 
    for name in possible_names:
        exe_path = shutil.which(name)
        if exe_path:
            print(f"找到 LibreOffice 可执行文件: {exe_path}")
            return exe_path
    return None

def is_convertible_file(file_path):

    ext = file_path.suffix.lower()
    
    supported_exts = {
        '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',  
        '.odt', '.ods', '.odp', '.odg', '.odf',           
        '.rtf', '.txt', '.csv',                          
        '.html', '.htm', '.epub', '.xml'                
    }
    
    if ext in supported_exts:
        return True
    
    mime_type, _ = mimetypes.guess_type(str(file_path))
    
    if mime_type:
        if mime_type.startswith(('text/', 'application/msword', 'application/vnd.', 'application/rtf')):
            return True
    
    if not ext:
        if file_path.stat().st_size > 100: 
            return True

    return False

def convert_to_pdf_lightweight(input_path_str, output_dir_str=None, force_convert=True, delete_source=True):

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

    output_dir.mkdir(parents=True, exist_ok=True)

    if input_path.is_file():
        should_convert = force_convert or is_convertible_file(input_path)
        
        if not should_convert:
            print(f"跳过不可转换的文件: {input_path}")
            return

        cmd = [
            libreoffice_exe,
            "--headless",      
            "--invisible",      
            "--nodefault",    
            "--nolockcheck",   
            "--nologo",       
            "--norestore",      
            "--convert-to", "pdf",
            "--outdir", str(output_dir),
            str(input_path)
        ]
        print(f"正在转换 ({Path(libreoffice_exe).stem}): {input_path.name} -> 目录 '{output_dir}'")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120) 
            expected_pdf_name = f"{input_path.stem}.pdf"
            expected_full_path = output_dir / expected_pdf_name
            if expected_full_path.exists():
                print(f"  -> 成功: 已生成 {expected_full_path}")
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


    elif input_path.is_dir():
        all_files = [f for f in input_path.rglob("*") if f.is_file()]
        
        if not all_files:
            print(f"在目录 '{input_path}' 中未找到任何文件。")
            return

        print(f"在 '{input_path}' 中找到 {len(all_files)} 个文件，开始转换...")

        for file_path in all_files:
            if not force_convert and not is_convertible_file(file_path):
                print(f"跳过不可转换的文件: {file_path}")
                continue

            relative_path = file_path.relative_to(input_path)
            target_pdf_dir = output_dir / relative_path.parent
            target_pdf_dir.mkdir(parents=True, exist_ok=True)

            cmd = [
                libreoffice_exe,
                "--headless",
                "--invisible",
                "--nodefault",
                "--nolockcheck",
                "--nologo",
                "--norestore",
                "--convert-to", "pdf",
                "--outdir", str(target_pdf_dir),
                str(file_path)
            ]
            print(f"正在转换 ({Path(libreoffice_exe).stem}): {relative_path} -> {target_pdf_dir}")
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120) 
                expected_pdf_name = f"{file_path.stem}.pdf"
                expected_full_path = target_pdf_dir / expected_pdf_name
                if expected_full_path.exists():
                    print(f"  -> 成功: 已生成 {expected_full_path}")
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


