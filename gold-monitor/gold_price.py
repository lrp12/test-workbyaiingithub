#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import time
import datetime
import logging
import os
import sys
import requests
from win10toast import ToastNotifier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
LOG_FILE = os.path.join(BASE_DIR, "logs", "gold_price.log")
HISTORY_FILE = os.path.join(BASE_DIR, "data", "price_history.json")

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(data):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def fetch_jd_gold_price():
    url = "https://api.jd.com/routerjson"
    params = {
        "method": "jingdong.gold.price.get",
        "app_key": "YOUR_APP_KEY",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "v": "2.0",
        "format": "json",
        "sign": "YOUR_SIGN"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logging.error("获取京东金价失败: %s", e)
        return None

def notify(price, change):
    toaster = ToastNotifier()
    title = "京东金价监控"
    msg = f"当前金价: {price} 元/克，变动: {change:.2f} 元/克"
    toaster.show_toast(title, msg, duration=10)

def main():
    cfg = load_config()
    threshold = cfg.get("threshold", 0.5)
    interval = cfg.get("interval", 60)
    history = load_history()
    last_price = history[-1]["price"] if history else None

    while True:
        data = fetch_jd_gold_price()
        if not data:
            time.sleep(interval)
            continue
        price = data.get("price", 0)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {"time": now, "price": price}
        history.append(record)
        save_history(history)

        if last_price:
            change = price - last_price
            if abs(change) >= threshold:
                notify(price, change)
                logging.info("价格变动超过阈值: %.2f", change)
        last_price = price
        logging.info("记录金价: %.2f 元/克", price)
        time.sleep(interval)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("用户中断，程序退出")
        sys.exit(0)

requests
win10toast
