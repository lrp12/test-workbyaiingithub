#!/usr/bin/env python3
"""
智能依赖扫描脚本
自动分析Python文件中的import语句，更新requirements-ai.txt
"""
import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

STANDARD_LIBS = {
    # Python 3.11 完整标准库列表（200+模块）
    'builtins', '__builtin__', '__builtins__', 'string', 're', 'difflib', 'textwrap', 
    'unicodedata', 'stringprep', 'readline', 'rlcompleter', 'struct', 'codecs', 
    'binascii', 'base64', 'binhex', 'quopri', 'uu', 'xdrlib', 'datetime', 'calendar', 
    'collections', 'collections.abc', 'heapq', 'bisect', 'array', 'weakref', 'types', 
    'copy', 'pprint', 'reprlib', 'enum', 'dataclasses', 'numbers', 'math', 'cmath', 
    'decimal', 'fractions', 'random', 'statistics', 'itertools', 'functools', 
    'operator', 'pathlib', 'os', 'os.path', 'fileinput', 'stat', 'filecmp', 
    'tempfile', 'glob', 'fnmatch', 'linecache', 'shutil', 'pickle', 'pickletools', 
    'shelve', 'marshal', 'dbm', 'sqlite3', 'zlib', 'gzip', 'bz2', 'lzma', 
    'zipfile', 'tarfile', 'csv', 'configparser', 'netrc', 'plistlib', 'hashlib', 
    'hmac', 'secrets', 'io', 'time', 'argparse', 'getopt', 'logging', 
    'logging.config', 'logging.handlers', 'getpass', 'curses', 'curses.textpad', 
    'curses.ascii', 'curses.panel', 'platform', 'errno', 'ctypes', 'ctypes.wintypes', 
    'msvcrt', 'threading', 'multiprocessing', 'concurrent.futures', 'subprocess', 
    'sched', 'queue', 'asyncio', 'socket', 'ssl', 'select', 'selectors', 'asyncore', 
    'asynchat', 'signal', 'mmap', 'email', 'email.mime', 'json', 'mailcap', 
    'mailbox', 'mimetypes', 'html', 'html.parser', 'html.entities', 
    'xml.etree.ElementTree', 'xml.dom', 'xml.dom.minidom', 'xml.dom.pulldom', 
    'xml.sax', 'xml.parsers.expat', 'xmlrpc.client', 'xmlrpc.server', 'webbrowser', 
    'cgi', 'cgitb', 'wsgiref', 'urllib', 'urllib.request', 'urllib.parse', 
    'urllib.error', 'urllib.response', 'urllib.robotparser', 'http', 'http.client', 
    'http.server', 'http.cookies', 'http.cookiejar', 'ftplib', 'poplib', 'imaplib', 
    'nntplib', 'smtplib', 'smtpd', 'telnetlib', 'uuid', 'socketserver', 'ipaddress', 
    'wave', 'colorsys', 'gettext', 'locale', 'turtle', 'cmd', 'shlex', 'tkinter', 
    'tkinter.ttk', 'tkinter.tix', 'tkinter.scrolledtext', 'tkinter.constants', 
    'pydoc', 'doctest', 'unittest', 'unittest.mock', 'test', 'test.support', 'bdb', 
    'faulthandler', 'pdb', 'timeit', 'trace', 'tracemalloc', 'cProfile', 
    'profile', 'pstats', 'sys', 'sysconfig', '__main__', 'warnings', 'abc', 
    'atexit', 'traceback', '__future__', 'gc', 'inspect', 'site', 'code', 
    'codeop', 'zipimport', 'pkgutil', 'modulefinder', 'runpy', 'importlib',
}

# 常见第三方库推荐版本
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
    """从Python文件中提取所有import的顶级模块"""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import_matches = re.findall(r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9._]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9._]*)*)', content, re.MULTILINE)
        for match in import_matches:
            modules = [m.strip() for m in match.split(',')]
            for module in modules:
                top_module = module.split('.')[0]
                if top_module and not top_module.startswith('_'):
                    imports.add(top_module)
        
        from_matches = re.findall(r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9._]*)\s+import', content, re.MULTILINE)
        for module in from_matches:
            top_module = module.split('.')[0]
            if top_module and not top_module.startswith('_'):
                imports.add(top_module)
        
    except Exception as e:
        print(f"⚠️  读取文件失败 {file_path}: {e}", file=sys.stderr)
    
    return imports

def scan_directory(scan_path):
    """扫描目录下所有Python文件"""
    all_imports = set()
    python_files = list(Path(scan_path).rglob("*.py"))
    skip_dirs = {'.git', '__pycache__', 'venv', '.venv', '.ai', 'kimi', '.github', 'dist', 'build', '.pytest_cache'}
    
    print(f"🔍 开始扫描: {scan_path}")
    print(f"📊 找到 {len(python_files)} 个Python文件")
    
    for py_file in python_files:
        if any(skip_dir in str(py_file.parents) for skip_dir in skip_dirs):
            continue
        
        imports = extract_imports(py_file)
        if imports:
            rel_path = py_file.relative_to(scan_path)
            print(f"  📄 {rel_path}: {', '.join(sorted(imports))}")
        all_imports.update(imports)
    
    print(f"\n📊 总计发现 {len(all_imports)} 个不同的顶级模块")
    return all_imports

def filter_third_party(imports):
    """过滤出第三方库"""
    third_party = []
    print(f"\n🔍 开始过滤标准库...")
    print(f"📦 原始模块列表: {sorted(imports)}")
    
    for imp in imports:
        if imp.startswith('_'):
            print(f"  ⏭️  跳过内置模块: {imp}")
            continue
        
        is_stdlib = imp in STANDARD_LIBS
        if is_stdlib:
            print(f"  🏛️  标准库: {imp}")
        else:
            third_party.append(imp)
            print(f"  ✅ 第三方库: {imp}")
    
    return sorted(set(third_party))

def generate_requirements(third_party_libs, output_file):
    """生成requirements文件"""
    if not third_party_libs:
        print("\n⚠️  未检测到需要的外部依赖，跳过更新")
        return
    
    lines = [
        "# AI工作流依赖（自动生成）",
        f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "#"
    ]
    
    for lib in sorted(third_party_libs):
        if lib in COMMON_PACKAGES:
            lines.append(COMMON_PACKAGES[lib])
        else:
            lines.append(lib)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"\n✅ 依赖文件已更新: {output_file}")
    print(f"📦 共检测到 {len(third_party_libs)} 个第三方库")

def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(description='智能扫描Python依赖')
    parser.add_argument('--scan-path', required=True, help='要扫描的目录路径')
    parser.add_argument('--output', required=True, help='输出的requirements文件路径')
    args = parser.parse_args()
    
    if not os.path.isdir(args.scan_path):
        print(f"❌ 错误: 扫描路径不存在 - {args.scan_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        all_imports = scan_directory(args.scan_path)
        third_party = filter_third_party(all_imports)
        generate_requirements(third_party, args.output)
        print(f"\n🎉 依赖扫描完成！")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 执行失败: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

