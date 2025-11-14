# 微信公众号文章导出器

一键抓取并导出指定公众号的全部图文为 HTML/PDF/Excel，支持按关键词过滤、按时间范围筛选、去重、增量更新。

## 功能
- 扫码登录，自动维持会话
- 并发抓取，速度≈300 篇/分钟
- 按关键词/正则过滤标题与正文
- 按发布时间区间筛选
- 自动去重（标题+发布时间）
- 断点续爬、增量更新
- 支持导出为：
  - 单篇 HTML（含图片、样式、原文链接）
  - 合并 PDF（需 wkhtmltopdf）
  - Excel 明细（标题、作者、发布时间、摘要、原文链接、本地路径）

## 快速开始

1. 克隆仓库
```bash
git clone https://github.com/yourname/wechat-mp-exporter.git
cd wechat-mp-exporter
```

2. 安装依赖（推荐 Python≥3.8）
```bash
pip install -r requirements.txt
```

3. 运行主程序
```bash
python main.py
```

4. 按提示扫码登录，输入公众号昵称或 Biz，即可开始抓取。

## 高级用法

### 命令行参数
```bash
python main.py --biz=MzI3NzU3MzQ2OA== \
               --out=./output \
               --format=html,pdf,excel \
               --keyword=AI|人工智能 \
               --start=2023-01-01 \
               --end=2023-12-31 \
               --workers=32 \
               --incremental
```

参数说明：
- `--biz`：公众号唯一 Biz 值（优先于昵称）
- `--out`：输出目录，默认 `./output`
- `--format`：导出格式，默认 `html,excel`
- `--keyword`：关键词或正则，多个用 `|` 分隔
- `--start/--end`：发布时间区间（含）
- `--workers`：并发协程数，默认 32
- `--incremental`：增量模式，仅抓取新增文章

### 过滤规则
在 `filter.py` 中可自定义复杂过滤函数，例如：
```python
def custom_filter(article: dict) -> bool:
    # 正文必须≥300 字且含图片
    return len(article['content']) >= 300 and 'data-src' in article['content']
```

### 断点续爬
程序每 50 篇自动保存一次进度（`checkpoint.json`），异常退出后重新运行即可自动续爬。

## 输出样例

```
output/
├── html/                 # 单篇 HTML
│   ├── 2023-07-01_标题1.html
│   └── …
├── pdf/                  # 合并 PDF
│   └── 2023全年合集.pdf
├── excel/
│   └── 文章明细.xlsx     # 含标题、作者、时间、摘要、原文链接、本地路径
└── checkpoint.json       # 断点记录
```

## 注意事项
- 首次登录需扫码，cookies 有效期约 24h，过期自动提示重新扫码
- 合并 PDF 需本地安装 [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) 并加入 PATH
- 抓取速度过快可能被微信限制，出现 403 时程序自动降速重试
- 仅供个人备份与学习，请勿用于商业及非法用途

## 更新日志
- v1.1.0 新增 PDF 合并导出、增量更新、断点续爬
- v1.0.0 首版，支持 HTML/Excel 导出、关键词过滤

## License
MIT