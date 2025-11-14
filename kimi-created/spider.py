import asyncio
import json
import time
from typing import List, Dict
import requests
from fake_useragent import UserAgent
from pydantic import BaseModel

class Stock(BaseModel):
    code: str
    name: str
    volume_ratio: float

class AShareSpider:
    def __init__(self, max_concurrent: int = 10):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_all(self) -> List[Stock]:
        codes = self._get_all_codes()
        tasks = [self._fetch_one(code) for code in codes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if isinstance(r, Stock)]

    def _get_all_codes(self) -> List[str]:
        url = "http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=5000&fs=m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23"
        headers = {"User-Agent": self.ua.random}
        resp = self.session.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return [item["f12"] for item in data["data"]["diff"]]

    async def _fetch_one(self, code: str) -> Stock:
        async with self.semaphore:
            await asyncio.sleep(0.1)
            url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={self._market(code)}.{code}&fields=f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65,f66,f67,f68,f69,f70,f71,f72,f73,f74,f75,f76,f77,f78,f79,f80,f81,f82,f83,f84,f85,f86,f87,f88,f89,f90,f91,f92,f93,f94,f95,f96,f97,f98,f99,f100,f101,f102,f103,f104,f105,f106,f107,f108,f109,f110,f111,f112,f113,f114,f115,f116,f117,f118,f119,f120,f121,f122,f123,f124,f125,f126,f127,f128,f129,f130,f131,f132,f133,f134,f135,f136,f137,f138,f139,f140,f141,f142,f143,f144,f145,f146,f147,f148,f149,f150,f151,f152,f153,f154,f155,f156,f157,f158,f159,f160,f161,f162,f163,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f193,f194,f195,f196,f197,f198,f199,f200"
            headers = {"User-Agent": self.ua.random}
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(None, lambda: self.session.get(url, headers=headers, timeout=10))
            resp.raise_for_status()
            data = resp.json()
            item = data["data"]
            return Stock(
                code=code,
                name=item["f58"],
                volume_ratio=float(item.get("f184", 0))
            )

    def _market(self, code: str) -> int:
        return 1 if code.startswith("6") else 0