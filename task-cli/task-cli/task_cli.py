#!/usr/bin/env python3
"""Task CLI: 一个简单的命令行任务管理工具，支持打印九九乘法表到1.txt"""

import argparse
import os
import sys
from datetime import datetime


def print_multiplication_table():
    """将九九乘法表写入1.txt文件"""
    with open("1.txt", "w", encoding="utf-8") as f:
        for i in range(1, 10):
            for j in range(1, i + 1):
                f.write(f"{j}×{i}={i*j:2} ")
            f.write("\n")
    print("九九乘法表已写入 1.txt")


def main():
    parser = argparse.ArgumentParser(description="Task CLI 工具")
    parser.add_argument(
        "--multiplication-table",
        action="store_true",
        help="生成九九乘法表到1.txt"
    )
    args = parser.parse_args()

    if args.multiplication_table:
        print_multiplication_table()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()