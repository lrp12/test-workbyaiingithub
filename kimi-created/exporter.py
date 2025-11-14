import csv
from pathlib import Path
from typing import List
from spider import Stock

class CsvExporter:
    @staticmethod
    def save(stocks: List[Stock], path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["代码", "名称", "量比"])
            for s in stocks:
                writer.writerow([s.code, s.name, s.volume_ratio])