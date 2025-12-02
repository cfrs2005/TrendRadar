# TrendRadar

**原项目链接：[sansan0/TrendRadar](https://github.com/sansan0/TrendRadar)**

全网热点聚合推送工具，告别无效刷屏，只看真正关心的新闻资讯。

## 快速开始

### 1. Fork 本项目

点击本页面右上角的"Fork"按钮

### 2. 设置 GitHub Secrets

在你 Fork 后的仓库中，进入 `Settings` > `Secrets and variables` > `Actions` > `New repository secret`

### 3. 配置推送平台（可选其中一个）

#### Bark 推送（iOS 专属）

**GitHub Secret 配置：**
- **Name（名称）**：`BARK_URL`
- **Secret（值）**：你的 Bark 推送 URL

**获取方法：**
1. 下载 Bark App：[App Store](https://apps.apple.com/cn/app/bark-给你的手机发推送/id1403753865)
2. 打开 Bark App，复制首页显示的推送 URL
3. 将 URL 配置到 GitHub Secrets 中的 `BARK_URL`

#### 其他推送平台

- **企业微信**：配置 `WEWORK_WEBHOOK_URL`
- **飞书**：配置 `FEISHU_WEBHOOK_URL`
- **Telegram**：配置 `TELEGRAM_BOT_TOKEN` 和 `TELEGRAM_CHAT_ID`
- **钉钉**：配置 `DINGTALK_WEBHOOK_URL`

### 4. 测试推送

1. 进入你项目的 Actions 页面
2. 找到 "Hot News Crawler" 并点击 "Run workflow"
3. 等待约 1 分钟，消息会推送到你配置的平台

### 5. 配置关键词（可选）

编辑 `config/frequency_words.txt` 文件，添加你关心的关键词：

```
人工智能
AI
ChatGPT
```

## 功能特点

- **全网热点聚合**：支持知乎、抖音、微博、百度热搜等 11+ 个主流平台
- **智能推送策略**：支持三种推送模式（当日汇总、当前榜单、增量监控）
- **精准内容筛选**：支持普通词、必须词、过滤词等高级语法
- **多渠道推送**：支持企业微信、飞书、Telegram、Bark、钉钉、邮件等
- **零技术门槛**：GitHub 一键 Fork 即可使用

## 部署方式

### GitHub Actions（推荐）

适合大多数用户，无需服务器，自动运行

### Docker 部署

```bash
docker run -d --name trend-radar \
  -v ./config:/app/config:ro \
  -e BARK_URL="你的Bark URL" \
  -e CRON_SCHEDULE="*/30 * * * *" \
  wantcat/trendradar:latest
```

## 更多功能

详细功能说明和配置教程请参考：[原项目文档](https://github.com/sansan0/TrendRadar)

## 许可证

GPL-3.0 License