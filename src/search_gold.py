import requests, re, datetime, os, logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_gold_price():
    url = 'https://www.kitco.com/gold-price-today/'
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logging.error(f'网络请求失败: {e}')
        return None
    match = re.search(r'Gold Price Per Ounce</span>.*?>([\d,]+\.\d+)', resp.text, re.S)
    if match:
        return float(match.group(1).replace(',', ''))
    logging.error('未解析到金价')
    return None

def main():
    price = fetch_gold_price()
    if price is None:
        logging.error('获取金价失败')
        return
    os.makedirs('src', exist_ok=True)
    with open('src/o.txt', 'w', encoding='utf-8') as f:
        f.write(f'{datetime.date.today()} 金价: {price} USD/oz\n')
    logging.info(f'已写入金价: {price} USD/oz')

if __name__ == '__main__':
    main()
