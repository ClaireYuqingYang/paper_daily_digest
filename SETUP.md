# 📚 UTD Paper Daily Digest v2 — 上手指南

每天自动推送一篇 UTD24 Marketing / IS 论文到微信，附中文摘要 + 公众号风格博客文章（发布在 Telegraph，点开即读）。

---

## 功能说明

| 功能 | 说明 |
|------|------|
| 📡 自动抓取 | CrossRef API，覆盖 9 本 UTD24 期刊，无需 API Key |
| 🆕 月刊预警 | 某期刊出新一期时，立刻推送公告 + 本期亮点论文 |
| 🎲 随机漫步 | 每天根据你的研究兴趣推荐 1 篇，避免每次都是同一类 |
| 🌐 Telegraph | 自动发布为公众号风格文章，微信点链接即可阅读 |
| 📱 微信推送 | 企业微信或飞书群机器人，卡片样式，附阅读链接 |

---

## 第一步：配置研究兴趣

编辑 `interests.txt`，填入你的研究方向关键词（已有默认值，随时修改）：

```
消费者行为
人工智能 AI
平台经济
注意力与信息过载
```

---

## 第二步：安装依赖

```bash
pip install -r requirements.txt
```

---

## 第三步：配置密钥

### 本地运行
```bash
export ANTHROPIC_API_KEY="sk-ant-..."   # 用于中文翻译 + 博客生成
export WEBHOOK_URL="https://qyapi.weixin.qq.com/..."  # 微信群机器人
# TELEGRAPH_ACCESS_TOKEN 首次运行自动创建，无需手动配置
```

### GitHub Actions（自动运行）
进入仓库 **Settings → Secrets → Actions**，添加：
- `ANTHROPIC_API_KEY`
- `WEBHOOK_URL`
- `TELEGRAPH_ACCESS_TOKEN`（首次本地运行后，从 `data/.telegraph_token` 文件获取）

---

## 第四步：本地测试

```bash
# 先追溯 30 天建立论文库（首次运行推荐）
python main.py --days 30 --no-send

# 正式跑一次（会发微信推送）
python main.py --days 7

# 只看效果，不发推送
python main.py --days 7 --no-send

# 不用 AI 翻译（节省 API 费用）
python main.py --days 7 --no-send --no-telegraph
```

---

## 第五步：推到 GitHub 自动运行

```bash
git add .
git commit -m "init paper digest v2"
git push
```

之后 GitHub Actions 每天 **北京时间早上 8:00** 自动运行，推送到你的微信群。

---

## Webhook 获取方式

### 企业微信群机器人
群聊 → 右上角 `…` → `添加群机器人` → `自定义` → 复制 Webhook URL

### 飞书群机器人
群设置 → `群机器人` → `添加机器人` → `自定义机器人` → 复制 Webhook URL

---

## 覆盖期刊

**Marketing Management**：JM · JMR · JCR · Marketing Science · JAMS

**Information Science**：MISQ · ISR · JMIS · JIT
