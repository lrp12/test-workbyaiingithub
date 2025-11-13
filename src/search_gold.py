import requests, re, datetime, os, logging, time, random
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SOURCES = [
    ('https://www.kitco.com/gold-price-today/', r'Gold Price Per Ounce</span>.*?>([\d,]+\.\d+)'),
    ('https://goldprice.org/', r'id="gpotickerPrice".*?>([\d,]+\.\d+)'),
    ('https://www.gold.org/data/gold-price', r'"value":\s*([\d.]+)'),
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def fetch_one(url, pattern):
    try:
        time.sleep(random.uniform(0.3, 0.7))
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        m = re.search(pattern, r.text, re.S)
        if m:
            return float(m.group(1).replace(',', ''))
    except Exception as e:
        logging.debug(f'{url} 失败: {e}')
    return None

def fetch_gold_price():
    with ThreadPoolExecutor(max_workers=len(SOURCES)) as ex:
        futures = {ex.submit(fetch_one, url, pat): url for url, pat in SOURCES}
        for fut in as_completed(futures):
            price = fut.result()
            if price:
                return price
    return None

def main():
    price = fetch_gold_price()
    if price is None:
        logging.error('全网获取金价失败')
        return
    os.makedirs('src', exist_ok=True)
    with open('src/gold.txt', 'w', encoding='utf-8') as f:
        f.write(f'{datetime.date.today()} 金价: {price} USD/oz\n')
    logging.info(f'已写入金价: {price} USD/oz')

if __name__ == '__main__':
    main()
