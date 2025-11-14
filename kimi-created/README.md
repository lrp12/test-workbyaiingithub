# 微信公众号文章导出工具

一键抓取并导出指定公众号的全部图文为 PDF/HTML，支持按关键词过滤、增量更新、并发加速、失败重试、自动去重。

## 功能
- 扫码登录，自动维护 Cookie
- 并发抓取，速度≈10 篇/秒
- 断点续爬，增量更新
- 关键词过滤（标题/正文/作者）
- 导出为 PDF、HTML、Markdown
- 自动去重、失败重试、进度可视化

## 快速开始
```bash
# 1. 克隆
git clone https://github.com/yourname/wechat-spider.git
cd wechat-spider

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python main.py
```

## 配置
首次运行会在当前目录生成 `config.json`：
```json
{
  "biz": "__biz=xxx",      // 公众号唯一 ID
  "key": "",               // 可选：关键词过滤
  "out_dir": "output",     // 输出目录
  "format": "pdf",         // pdf | html | md
  "max_workers": 16,       // 并发数
  "retry": 3               // 失败重试次数
}
```

## 使用示例
```bash
# 抓取并导出全部文章为 PDF
python main.py

# 仅导出标题含“AI”的文章为 HTML
python main.py --key AI --format html

# 增量更新（只抓新文章）
python main.py --incremental
```

## 输出
- 文章：`output/公众号名/年-月/文章标题.pdf`
- 元数据：`output/公众号名/index.json`（含标题、作者、发布时间、原文链接）

## 注意事项
- 首次使用需微信扫码登录，Cookie 有效期≈24 h，过期自动提示刷新
- 建议抓取间隔≥1 s，避免触发风控
- 仅用于个人备份与学习，请遵守微信公众平台版权规范

## 更新日志
v1.1.0  2025-06-01  新增关键词过滤、增量更新、Markdown 导出
v1.0.0  2025-05-10  首版，支持 PDF/HTML 导出、并发抓取、失败重试

## License
MIT