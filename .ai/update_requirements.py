#!/usr/bin/env python3
"""
自动扫描Python项目中的第三方依赖
Kimi AI工作流专用
"""
import ast
import sys
from pathlib import Path
from typing import Set, List
import subprocess

# Python 3.11标准库列表（用于排除）
STDLIB_MODULES = {
    'abc', 'argparse', 'ast', 'asyncio', 'base64', 'bisect', 'builtins',
    'collections', 'concurrent', 'configparser', 'contextlib', 'csv',
    'dataclasses', 'datetime', 'decimal', 'dis', 'enum', 'fileinput',
    'functools', 'glob', 'hashlib', 'heapq', 'hmac', 'html', 'http',
    'importlib', 'inspect', 'io', 'itertools', 'json', 'logging',
    'math', 'numbers', 'operator', 'os', 'pathlib', 'pickle', 'platform',
    'pprint', 'queue', 'random', 're', 'secrets', 'socket', 'sqlite3',
    'statistics', 'string', 'subprocess', 'sys', 'textwrap', 'threading',
    'time', 'types', 'typing', 'urllib', 'uuid', 'warnings', 'weakref',
    'xml', 'zipfile', 'zoneinfo'
}

def scan_imports(scan_path: str) -> Set[str]:
    """扫描目录下所有Python文件的import语句"""
    imports = set()
    path = Path(scan_path)
    
    for py_file in path.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), str(py_file))
            
            for node in ast.walk(tree):
                # import xxx
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name.split('.')[0]
                        if module not in STDLIB_MODULES:
                            imports.add(module)
                
                # from xxx import
                elif isinstance(node, ast.FromImport):
                    if node.module:
                        module = node.module.split('.')[0]
                        if module not in STDLIB_MODULES:
                            imports.add(module)
        
        except Exception:
            # 跳过无法解析的文件
            continue
    
    return imports

def get_package_versions(packages: Set[str]) -> List[str]:
    """获取包的版本信息"""
    result = []
    
    for package in sorted(packages):
        try:
            # 尝试获取已安装版本
            info = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', package],
                capture_output=True,
                text=True
            )
            
            if info.returncode == 0:
                # 解析pip show输出
                for line in info.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(': ')[1]
                        result.append(f"{package}=={version}")
                        break
            else:
                # 如果未安装，只写包名（不推荐，会警告）
                print(f"警告: {package} 未安装，无法锁定版本", file=sys.stderr)
                result.append(f"{package}")
        
        except Exception as e:
            print(f"获取 {package} 版本失败: {e}", file=sys.stderr)
    
    return result

def update_requirements_file(output_path: str, packages: List[str]):
    """更新requirements文件"""
    path = Path(output_path)
    
    # 读取现有文件（如果存在）
    existing = set()
    if path.exists():
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    existing.add(line.split('==')[0])
    
    # 合并新发现的包
    all_packages = set(packages)
    
    # 写入文件
    with open(path, 'w') as f:
        f.write("# AI工作流依赖（自动扫描生成）\n")
        f.write("# 生成时间: {}\n".format(__import__('datetime').datetime.now().isoformat()))
        f.write("# 可直接运行: pip install -r {}\n\n".format(path.name))
        
        for pkg in sorted(all_packages):
            f.write(f"{pkg}\n")
    
    print(f"✅ 已更新: {path} ({len(all_packages)} 个包)")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='自动扫描Python依赖')
    parser.add_argument('--scan-path', default='.', help='扫描目录路径')
    parser.add_argument('--output', default='requirements-ai.txt', help='输出文件路径')
    args = parser.parse_args()
    
    # 扫描import
    print(f"正在扫描: {args.scan_path}")
    imports = scan_imports(args.scan_path)
    print(f"发现第三方库: {imports}")
    
    # 获取版本
    versioned = get_package_versions(imports)
    
    # 更新文件
    update_requirements_file(args.output, versioned)

if __name__ == "__main__":
    main()
