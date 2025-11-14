# 小红书图文批量导出器

一键爬取小红书关键词搜索结果，自动下载图文并整理成 Markdown + 本地图片，方便离线阅读或二次创作。

## 功能亮点
- 关键词搜索：支持多关键词批量爬取
- 图文下载：自动下载笔记正文与高清图片
- 去重过滤：按标题/作者/关键词黑名单去重
- 多格式导出：Markdown + 本地图片、CSV、JSON
- 增量更新：断点续爬，避免重复下载
- 代理池 & 随机 UA：降低封禁风险
- 开箱即用：pip 安装依赖即可跑

## 快速开始

1. 克隆/下载代码
```bash
git clone https://github.com/yourname/xhs-exporter.git
cd xhs-exporter
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置 `config.yaml`（首次运行自动生成模板）
```yaml
search_keywords:
  - 露营攻略
  - 北京咖啡店
max_pages: 20                # 每个关键词爬多少页
save_dir: ./output           # 下载根目录
fetch_images: true           # 是否下载图片
use_proxy: false             # 是否启用代理池
```

4. 启动
```bash
python main.py
```

5. 结果查看
```
output/
├── 露营攻略/
│   ├── 2025-06-20_露营装备清单.md
│   └── images/
├── 北京咖啡店/
│   └── ...
└── meta.csv                  # 所有笔记元信息
```

## 高级用法

### 过滤规则
在 `filter.yaml` 中自定义黑名单：
```yaml
title_blacklist:
  - "抽奖"
  - "广告"
author_blacklist:
  - "营销号"
min_likes: 100               # 只保留点赞 ≥100 的笔记
```

### 导出为 CSV/JSON
```bash
python exporter.py --format csv --output results.csv
```

### 增量更新
```bash
python main.py --incremental  # 只下载本地不存在的新笔记
```

### 代理池
支持 `http/https/socks5` 代理，格式：
```yaml
proxies:
  - http://127.0.0.1:7890
  - socks5://user:pass@ip:port
```

## 目录结构
```
kimi-created/
├── main.py          # 入口，调度爬取+导出
├── spider.py        # 爬取逻辑、去重、代理池
├── filter.py        # 黑名单/点赞过滤
├── exporter.py      # Markdown/CSV/JSON 导出
├── requirements.txt # 依赖列表
└── README.md        # 本文档
```

## 常见问题

**Q：爬取过快被封？**  
A：调低 `max_pages`，启用代理池，或加大 `delay` 参数。

**Q：图片下载失败？**  
A：检查网络、磁盘空间，或手动删除 `output/*/images/` 后重试。

**Q：如何只导出文字？**  
A：设置 `fetch_images: false`，或运行 `exporter.py --no-images`。

## 更新日志
- v1.1.0 新增增量更新、CSV 导出
- v1.0.0 初版发布

## 免责声明
仅供学习研究，请勿用于商业及非法用途。数据所有权归小红书及原作者所有。

## Star 一下
如果帮到你，欢迎点个 ⭐ 鼓励持续更新！