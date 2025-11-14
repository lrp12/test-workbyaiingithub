#!/usr/bin/env bash
# 一键部署京东金价监控桌面方案
set -e

DIR="gold-monitor"
mkdir -p "$DIR"/logs "$DIR"/data

cat > "$DIR"/gold_price.py <<'PY'
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

CONFIG_FILE = "config.json"
LOG_FILE = "logs/gold_price.log"
HISTORY_FILE = "data/price_history.json"

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
PY

cat > "$DIR"/config.json <<'JSON'
{
  "threshold": 0.5,
  "interval": 60,
  "app_key": "YOUR_JD_APP_KEY",
  "secret": "YOUR_JD_SECRET"
}
JSON

cat > "$DIR"/run_gold.bat <<'BAT'
@echo off
cd /d "%~dp0"
python gold_price.py
pause
BAT

cat > "$DIR"/run_gold.sh <<'SH'
#!/usr/bin/env bash
cd "$(dirname "$0")"
python3 gold_price.py
SH

cat > "$DIR"/setup.bat <<'SETUP_BAT'
@echo off
echo 安装依赖...
python -m pip install requests win10toast --user
echo 安装完成，双击 run_gold.bat 启动监控
pause
SETUP_BAT

cat > "$DIR"/setup.sh <<'SETUP_SH'
#!/usr/bin/env bash
echo "安装依赖..."
python3 -m pip install requests --user
echo "安装完成，执行 ./run_gold.sh 启动监控"
SETUP_SH

touch "$DIR"/logs/gold_price.log
echo "[]" > "$DIR"/data/price_history.json

chmod +x "$DIR"/*.sh

echo "部署完成，目录：$DIR"
echo "Windows: 先运行 setup.bat，再运行 run_gold.bat"
echo "Linux/Mac: 先运行 ./setup.sh，再运行 ./run_gold.sh"
