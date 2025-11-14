from typing import List
from spider import Stock

class VolumeFilter:
    @staticmethod
    def gt(stocks: List[Stock], threshold: float) -> List[Stock]:
        return [s for s in stocks if s.volume_ratio > threshold]