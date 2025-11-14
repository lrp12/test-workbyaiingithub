# 小红书图文批量导出器

一键爬取小红书笔记图文，自动去重、过滤并打包下载。

## 功能
- 关键词/话题搜索
- 自动翻页抓取笔记详情（标题、描述、图片、视频）
- 智能去重（按 note_id）
- 多维度过滤（点赞、收藏、发布时间）
- 多线程高速下载
- 导出 CSV + 原始文件（图片/视频）

## 快速开始

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置 Cookie（必须）
将浏览器 Cookie 粘到 `cookie.txt` 一行即可。

3. 运行示例
```bash
# 搜索关键词“露营” 下载前 200 条笔记
python main.py --keyword 露营 --limit 200

# 指定话题页 URL
python main.py --topic https://www.xiaohongshu.com/page/5c3b4c4b000000000501e5c3 --limit 100

# 只导出 CSV，不下载文件
python main.py --keyword 露营 --limit 100 --no-download
```

## 参数说明
| 参数 | 说明 | 默认值 |
|------|------|--------|
| --keyword | 搜索关键词 | 无 |
| --topic | 话题页完整 URL | 无 |
| --limit | 抓取笔记数量 | 50 |
| --min-like | 最小点赞数 | 0 |
| --min-collect | 最小收藏数 | 0 |
| --days | 最近 N 天内发布 | 365 |
| --output | 输出目录 | output |
| --no-download | 仅导出 CSV | False |
| --workers | 下载线程数 | 8 |

## 输出结构
```
output/
├── 2025-06-25_14-30-00/          # 本次运行时间戳
│   ├── notes.csv                 # 笔记元数据
│   ├── images/                   # 图片原图
│   └── videos/                   # 视频文件
└── ...
```

## 注意事项
- 请遵守小红书 ToS，勿用于商业用途；
- 高频请求可能触发风控，建议降低线程数并增加间隔；
- 仅供学习研究，违者自负责任。

## 更新日志
- v1.1.0 新增话题页支持、多线程下载、CSV 导出
- v1.0.0 初版发布

## License
MIT