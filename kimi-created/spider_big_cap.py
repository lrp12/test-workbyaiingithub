#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大市值股票爬虫
过滤条件：流通市值 > 1亿
"""

import json
import time
import random
import logging
from datetime import datetime
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

from filter import Filter
from exporter import Exporter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BigCapSpider:
    """大市值股票爬虫"""
    
    def __init__(self):
        self.name = "big_cap_spider"
        self.base_url = "https://example.com/big-cap-stocks"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        self.filter = Filter()
        self.exporter = Exporter()
        
    def fetch_page(self, page: int = 1) -> str:
        """获取网页内容"""
        url = f"{self.base_url}?page={page}"
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"请求失败: {e}")
            return ""
    
    def parse_stocks(self, html: str) -> List[Dict]:
        """解析股票列表"""
        soup = BeautifulSoup(html, 'html.parser')
        stocks = []
        
        # 根据实际网页结构调整选择器
        rows = soup.select("table.stock-table tbody tr")
        for row in rows:
            try:
                code = row.select_one("td.code").text.strip()
                name = row.select_one("td.name").text.strip()
                price = float(row.select_one("td.price").text.strip())
                change_pct = float(row.select_one("td.change").text.strip().rstrip('%'))
                market_cap = float(row.select_one("td.market-cap").text.strip())  # 流通市值（亿）
                
                stock = {
                    "code": code,
                    "name": name,
                    "price": price,
                    "change_pct": change_pct,
                    "market_cap": market_cap,
                    "timestamp": datetime.now().isoformat()
                }
                stocks.append(stock)
            except (AttributeError, ValueError) as e:
                logger.warning(f"解析行失败: {e}")
                continue
                
        return stocks
    
    def filter_big_cap(self, stocks: List[Dict]) -> List[Dict]:
        """过滤流通市值 > 1亿的股票"""
        return [s for s in stocks if s.get("market_cap", 0) > 1.0]
    
    def run(self, max_pages: int = 5) -> None:
        """运行爬虫"""
        logger.info("开始爬取大市值股票...")
        all_stocks = []
        
        for page in range(1, max_pages + 1):
            logger.info(f"正在爬取第 {page} 页...")
            html = self.fetch_page(page)
            if not html:
                continue
                
            stocks = self.parse_stocks(html)
            big_cap_stocks = self.filter_big_cap(stocks)
            all_stocks.extend(big_cap_stocks)
            
            # 随机延迟，避免被封
            time.sleep(random.uniform(1, 3))
        
        # 去重
        seen = set()
        unique_stocks = []
        for s in all_stocks:
            key = s["code"]
            if key not in seen:
                seen.add(key)
                unique_stocks.append(s)
        
        logger.info(f"共获取 {len(unique_stocks)} 只大市值股票")
        
        # 导出数据
        self.exporter.export_to_json(unique_stocks, "big_cap_stocks.json")
        self.exporter.export_to_csv(unique_stocks, "big_cap_stocks.csv")
        
        logger.info("大市值股票爬虫运行完成")


if __name__ == "__main__":
    spider = BigCapSpider()
    spider.run()