#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金价抓取脚本（修订版）
Author : Reviewer
Date   : 2024-05-XX
Desc   : 抓取伦敦现货黄金（XAU）最新报价，失败时输出详细错误信息。
"""

import sys
import json
import time
import logging
import requests
from datetime import datetime

# ========== 配置区域 ==========
# 日志：同时输出到控制台与文件，方便排查
LOG_FMT = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FMT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("gold_price.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("GoldPrice")

# 备选 API（优先使用第一个，失败自动切换）
API_LIST = [
    {
        "name": "GoldAPI",
        "url": "https://www.goldapi.io/api/XAU/USD",
        "headers": {"x-access-token": "goldapi-KEY_PLACEHOLDER"},
        "price_path": ["price"],          # 响应中价格的字段路径
        "timeout": 8
    },
    {
        "name": "Metals-API",
        "url": "https://metals-api.com/api/latest",
        "params": {"access_key": "METALS_KEY_PLACEHOLDER", "base": "XAU", "symbols": "USD"},
        "price_path": ["rates", "USD"],
        "timeout": 8
    }
]

# 重试次数与间隔
MAX_RETRY = 3
RETRY_DELAY = 2   # 秒
# ==============================


def fetch_price(api_conf, retry=0):
    """
    根据单个 API 配置抓取金价
    :param api_conf: 单条 API 配置 dict
    :param retry: 当前重试次数
    :return: (float|None, str)  价格，错误信息
    """
    try:
        logger.info("【%s】请求开始，retry=%s", api_conf["name"], retry)
        kw = {"timeout": api_conf["timeout"]}

        # 构造请求参数
        if "headers" in api_conf:
            kw["headers"] = api_conf["headers"]
        if "params" in api_conf:
            kw["params"] = api_conf["params"]

        resp = requests.get(api_conf["url"], **kw)
        logger.debug("【%s】HTTP %s", api_conf["name"], resp.status_code)

        # 非 200 直接抛异常
        resp.raise_for_status()

        data = resp.json()

        # 按路径提取价格
        price = data
        for key in api_conf["price_path"]:
            price = price[key]

        price = float(price)
        logger.info("【%s】成功获取价格：%s USD/oz", api_conf["name"], price)
        return price, ""

    except (requests.exceptions.RequestException, ValueError, KeyError, TypeError) as exc:
        # 记录详细异常信息
        logger.exception("【%s】抓取失败：%s", api_conf["name"], exc)
        err_detail = f"{api_conf['name']} -> {type(exc).__name__}: {exc}"
        return None, err_detail


def get_gold_price():
    """
    遍历 API_LIST，直到成功获取金价
    :return: (float|None, list)  价格，所有错误信息列表
    """
    errors = []
    for api in API_LIST:
        for attempt in range(MAX_RETRY):
            price, err = fetch_price(api, retry=attempt)
            if price is not None:
                return price, errors
            errors.append(err)
            time.sleep(RETRY_DELAY)
    return None, errors


def main():
    logger.info("========== 金价抓取任务启动 @ %s ==========", datetime.now())
    price, errors = get_gold_price()

    if price is None:
        logger.error("全部 API 均失败，详细错误如下：")
        for idx, e in enumerate(errors, 1):
            logger.error("  [%s] %s", idx, e)
        # 以非 0 退出码告知外部失败
        sys.exit(2)
    else:
        logger.info("最终金价：%.2f USD/oz", price)
        # 如有后续流程，可在此继续处理 price
        # 例如写数据库、推送消息等
        print(json.dumps({"gold_usd_oz": price, "ts": datetime.now().isoformat()}))


if __name__ == "__main__":
    main()
