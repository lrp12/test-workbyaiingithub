gold-monitor/gold_price.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import logging
import requests
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import threading

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

CONFIG_FILE = BASE_DIR / "config.json"
HISTORY_FILE = DATA_DIR / "price_history.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "gold_price.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("GoldMonitor")

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

cfg = load_config()
API_LIST = cfg["api_list"]
MAX_RETRY = cfg["max_retry"]
RETRY_DELAY = cfg["retry_delay"]
CHECK_INTERVAL = cfg["check_interval"]
THRESHOLD = cfg["threshold"]

def fetch_price(api_conf):
    for attempt in range(MAX_RETRY):
        try:
            kw = {"timeout": api_conf["timeout"]}
            if "headers" in api_conf:
                kw["headers"] = api_conf["headers"]
            if "params" in api_conf:
                kw["params"] = api_conf["params"]
            resp = requests.get(api_conf["url"], **kw)
            resp.raise_for_status()
            data = resp.json()
            price = data
            for key in api_conf["price_path"]:
                price = price[key]
            return float(price), ""
        except Exception as exc:
            err = f"{api_conf['name']} -> {type(exc).__name__}: {exc}"
            logger.debug(err)
            if attempt < MAX_RETRY - 1:
                time.sleep(RETRY_DELAY)
    return None, err

def get_gold_price():
    errors = []
    with ThreadPoolExecutor(max_workers=len(API_LIST)) as executor:
        future_to_api = {executor.submit(fetch_price, api): api for api in API_LIST}
        for future in as_completed(future_to_api):
            price, err = future.result()
            if price is not None:
                return price, errors
            errors.append(err)
    return None, errors

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(entry):
    hist = load_history()
    hist.append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(hist[-1000:], f, ensure_ascii=False, indent=2)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("京东金价监控")
        self.geometry("320x160")
        self.resizable(False, False)
        self.iconify()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.last_price = None
        self.alert_queue = queue.Queue()
        self.build_ui()
        self.after(1000, self.scheduled_update)
        self.after(100, self.process_alerts)

    def build_ui(self):
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="当前金价 (USD/oz)").pack(pady=4)
        self.price_var = tk.StringVar(value="--")
        ttk.Label(frm, textvariable=self.price_var, font=("Arial", 24, "bold")).pack(pady=4)
        self.status_var = tk.StringVar(value="等待更新...")
        ttk.Label(frm, textvariable=self.status_var, font=("Arial", 10)).pack(pady=4)

    def scheduled_update(self):
        threading.Thread(target=self.update_price, daemon=True).start()
        self.after(CHECK_INTERVAL * 1000, self.scheduled_update)

    def update_price(self):
        price, errors = get_gold_price()
        if price is None:
            self.status_var.set("获取失败")
            logger.error("All APIs failed: %s", errors)
            return
        self.price_var.set(f"{price:.2f}")
        ts = datetime.now().isoformat(timespec="seconds")
        self.status_var.set(f"更新于 {ts.split('T')[1]}")
        save_history({"ts": ts, "price": price})
        if self.last_price is not None and abs(price - self.last_price) >= THRESHOLD:
            self.alert_queue.put((price, self.last_price))
        self.last_price = price
        logger.info("Updated price: %.2f", price)

    def process_alerts(self):
        try:
            while True:
                new, old = self.alert_queue.get_nowait()
                diff = new - old
                sign = "↑" if diff > 0 else "↓"
                msg = f"金价变动 {sign} {abs(diff):.2f} USD/oz\n当前：{new:.2f}"
                messagebox.showwarning("金价提醒", msg)
                logger.warning("Alert: %s", msg)
        except queue.Empty:
            pass
        self.after(100, self.process_alerts)

    def on_close(self):
        self.withdraw()

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()

gold-monitor/config.json
{
  "api_list": [
    {
      "name": "GoldAPI",
      "url": "https://www.goldapi.io/api/XAU/USD",
      "headers": {"x-access-token": "goldapi-KEY_PLACEHOLDER"},
      "price_path": ["price"],
      "timeout": 8
    },
    {
      "name": "Metals-API",
      "url": "https://metals-api.com/api/latest",
      "params": {"access_key": "METALS_KEY_PLACEHOLDER", "base": "XAU", "symbols": "USD"},
      "price_path": ["rates", "USD"],
      "timeout": 8
    }
  ],
  "max_retry": 3,
  "retry_delay": 2,
  "check_interval": 60,
  "threshold": 5.0
}

gold-monitor/run_gold.bat
@echo off
cd /d "%~dp0"
python gold_price.py
pause

gold-monitor/run_gold.sh
#!/bin/bash
cd "$(dirname "$0")"
python3 gold_price.py

gold-monitor/setup.bat
@echo off
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat
echo Installing dependencies...
pip install -U pip requests
echo Setup complete. Run run_gold.bat to start.

gold-monitor/setup.sh
#!/bin/bash
set -e
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "Installing dependencies..."
pip install -U pip requests
echo "Setup complete. Run ./run_gold.sh to start."

gold-monitor/logs/gold_price.log

gold-monitor/data/price_history.json
[]
