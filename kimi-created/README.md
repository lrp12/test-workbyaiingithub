# 微信公众号文章爬虫

## 功能
- 按关键词搜索微信公众号文章
- 支持时间范围过滤（最近 1/7/30 天）
- 自动去重、导出 CSV/Excel
- 可配置并发与请求间隔，降低封号风险

## 快速开始
1. 安装依赖  
   ```bash
   pip install -r requirements.txt
   ```

2. 配置 Cookie（必填）  
   将微信搜狗 Cookie 写入 `config.json`：
   ```json
   {"cookie": "your_sogou_cookie_here"}
   ```

3. 运行示例  
   ```bash
   python main.py --keyword "人工智能" --days 7 --limit 100 --output result.xlsx
   ```

## 参数说明
| 参数       | 说明                          | 默认值 |
|------------|-------------------------------|--------|
| --keyword  | 搜索关键词（必填）            | 无     |
| --days     | 时间范围：1/7/30              | 7      |
| --limit    | 最大抓取篇数                  | 100    |
| --output   | 输出文件路径，支持 csv/xlsx   | result.csv |
| --workers  | 并发协程数                    | 8      |
| --delay    | 请求间隔（秒）                | 1.0    |

## 输出字段
- title：文章标题
- url：原文链接
- pub_time：发布时间
- author：公众号名称
- digest：摘要
- cover：封面图 URL

## 注意事项
- 请勿设置过高并发，建议 ≤10
- 定期更换 Cookie，避免失效
- 遵循网站 robots 协议与法律法规

## 更新日志
- v1.1.0：增加 Excel 导出、去重逻辑、进度条
- v1.0.0：初始版本，支持关键词搜索与 CSV 导出