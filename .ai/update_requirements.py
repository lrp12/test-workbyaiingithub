#!/usr/bin/env python3
"""
智能依赖扫描脚本
自动分析Python文件中的import语句，更新requirements-ai.txt
"""

import os
import re
import sys
from pathlib import Path
import argparse

# Python标准库列表（用于过滤，避免将内置库加入requirements）
STANDARD_LIBS = {
    'os', 'sys', 'time', 'datetime', 'json', 're', 'math', 'random', 'string',
    'pathlib', 'subprocess', 'threading', 'multiprocessing', 'collections',
    'itertools', 'functools', 'typing', 'inspect', 'hashlib', 'base64',
    'csv', 'io', 'pickle', 'sqlite3', 'uuid', 'warnings', 'logging',
    'argparse', 'configparser', 'html', 'http', 'urllib', 'ftplib',
    'smtplib', 'email', 'xml', 'zipfile', 'tarfile', 'gzip', 'bz2',
    'lzma', 'shutil', 'tempfile', 'mimetypes', 'getpass', 'secrets',
    'hmac', 'ssl', 'socket', 'select', 'asyncio', 'concurrent', 'ctypes',
    'decimal', 'fractions', 'numbers', 'statistics', 'typing', 'enum',
    'dataclasses', 'contextlib', 'dataclasses', 'enum', 'pprint',
    'textwrap', 'stringprep', 'fnmatch', 'glob', 'linecache', 'traceback',
    'cProfile', 'profile', 'pstats', 'timeit', 'trace', 'doctest'
}

# 常见第三方库及其推荐版本
COMMON_PACKAGES = {
    'requests': 'requests>=2.31.0',
    'pytest': 'pytest==7.4.3',
    'radon': 'radon==6.0.1',
    'numpy': 'numpy>=1.24.0',
    'pandas': 'pandas>=2.0.0',
    'beautifulsoup4': 'beautifulsoup4>=4.12.0',
    'lxml': 'lxml>=4.9.0',
    'scrapy': 'scrapy>=2.9.0',
    'selenium': 'selenium>=4.10.0',
    'flask': 'flask>=2.3.0',
    'django': 'django>=4.2.0',
    'fastapi': 'fastapi>=0.100.0',
    'pydantic': 'pydantic>=2.0.0',
    'sqlalchemy': 'sqlalchemy>=2.0.0',
}


def extract_imports(file_path):
    """从Python文件中提取所有import的库"""
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配 import xxx
        import_matches = re.findall(r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*', content, re.MULTILINE)
        imports.update(import_matches)
        
        # 匹配 from xxx import
        from_matches = re.findall(r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import', content, re.MULTILINE)
        imports.update(from_matches)
        
    except Exception as e:
        print(f"⚠️  读取文件失败 {file_path}: {e}", file=sys.stderr)
    
    return imports


def scan_directory(scan_path):
    """扫描目录下所有Python文件"""
    all_imports = set()
    python_files = list(Path(scan_path).rglob("*.py"))
    
    print(f"🔍 扫描Python文件: 找到 {len(python_files)} 个文件")
    
    for py_file in python_files:
        # 跳过虚拟环境、缓存和隐藏目录
        if any(skip in str(py_file) for skip in ['.git', '__pycache__', 'venv', '.venv', '.ai']):
            continue
        
        imports = extract_imports(py_file)
        if imports:
            print(f"  📄 {py_file.relative_to(scan_path)}: {', '.join(imports)}")
        all_imports.update(imports)
    
    return all_imports


def filter_third_party(imports):
    """过滤出第三方库"""
    third_party = []
    for imp in imports:
        if imp not in STANDARD_LIBS and not imp.startswith('_'):
            third_party.append(imp)
    return sorted(third_party)


def generate_requirements(third_party_libs, output_file):
    """生成requirements文件"""
    lines = ["# AI工作流依赖（自动生成）", "# 更新时间: " + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ""]
    
    for lib in third_party_libs:
        # 如果有预设版本，使用预设；否则只写库名
        if lib in COMMON_PACKAGES:
            lines.append(COMMON_PACKAGES[lib])
        else:
            lines.append(lib)
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"\n✅ 依赖文件已更新: {output_file}")
    print(f"📦 检测到 {len(third_party_libs)} 个第三方库:")
    for lib in third_party_libs:
        print(f"   - {lib}")


def main():
    parser = argparse.ArgumentParser(description='智能扫描Python依赖')
    parser.add_argument('--scan-path', required=True, help='要扫描的目录路径')
    parser.add_argument('--output', required=True, help='输出的requirements文件路径')
    args = parser.parse_args()
    
    if not os.path.isdir(args.scan_path):
        print(f"❌ 错误: 扫描路径不存在 - {args.scan_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"📂 开始扫描目录: {args.scan_path}")
    
    # 1. 扫描所有import
    all_imports = scan_directory(args.scan_path)
    print(f"\n📊 总计发现 {len(all_imports)} 个不同的 import")
    
    # 2. 过滤第三方库
    third_party = filter_third_party(all_imports)
    
    if not third_party:
        print("⚠️  未检测到需要的外部依赖")
        return
    
    # 3. 生成requirements文件
    generate_requirements(third_party, args.output)


if __name__ == '__main__':
    main()