#!/usr/bin/env python3
import asyncio
from pathlib import Path
from spider import AShareSpider
from filter import VolumeFilter
from exporter import CsvExporter

async def main():
    spider = AShareSpider()
    raw = await spider.fetch_all()
    filtered = VolumeFilter.gt(raw, 3.0)
    CsvExporter.save(filtered, Path("output/量比大于3.csv"))
    print(f"已导出 {len(filtered)} 只股票")

if __name__ == "__main__":
    asyncio.run(main())