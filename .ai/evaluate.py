#!/usr/bin/env python3
"""
评估代码质量，返回JSON分数
Kimi优化专用评估器
"""
import subprocess
import json
import sys
import time
from pathlib import Path

def evaluate_code(file_path: str):
    """评估代码并返回分数"""
    results = {
        "file": file_path,
        "timestamp": time.time(),
        "tests": {},
        "complexity": {},
        "score": 0
    }
    
    # 语法检查
    try:
        with open(file_path, 'r') as f:
            compile(f.read(), file_path, 'exec')
        results["syntax"] = {"valid": True}
    except SyntaxError as e:
        results["syntax"] = {"valid": False, "error": str(e)}
        return results
    
    # 运行测试
    if Path("pytest.ini").exists() or list(Path.cwd().glob("test_*.py")):
        try:
            start = time.time()
            result = subprocess.run(
                ["pytest", "--cov", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60
            )
            results["tests"] = {
                "passed": result.returncode == 0,
                "duration": time.time() - start,
            }
        except Exception as e:
            results["tests"]["error"] = str(e)
    
    # 复杂度分析
    try:
        result = subprocess.run(
            ["radon", "cc", "-a", "-s", file_path],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            scores = [int(line.split()[-1]) for line in result.stdout.split('\n') if 'Average' in line]
            results["complexity"]["average"] = scores[0] if scores else 0
    except Exception as e:
        results["complexity"]["error"] = str(e)
    
    # 计算总分
    score = 100
    if not results["syntax"]["valid"]: score = 0
    elif not results["tests"].get("passed", True): score -= 30
    else: score += 10
    
    if results["complexity"].get("average", 0) > 15: score -= 20
    
    results["score"] = max(0, min(100, score))
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "缺少文件路径"}, ensure_ascii=False))
        sys.exit(1)
    
    result = evaluate_code(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
