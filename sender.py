"""
Sender — Server酱 (个人微信推送)
===================================
用 Server酱 把每日推荐和新刊公告推送到个人微信。
消息正文简洁，点链接跳转到 Telegraph 阅读完整文章。

Server酱 API：POST https://sctapi.ftqq.com/{SendKey}.send
文档：https://sct.ftqq.com
"""
from __future__ import annotations

from datetime import date

import requests

from config import SERVERCHAN_KEY

SERVERCHAN_API = "https://sctapi.ftqq.com/{key}.send"


def _send(title: str, content: str) -> bool:
    key = SERVERCHAN_KEY
    if not key or key == "your-sendkey-here":
        print("[WARN] SERVERCHAN_KEY 未配置，跳过推送。")
        print(f"       标题：{title}")
        return False

    try:
        resp = requests.post(
            SERVERCHAN_API.format(key=key),
            data={"title": title, "desp": content},
            timeout=15,
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("data", {}).get("errno", 0) != 0:
            print(f"[ERROR] Server酱返回错误：{result}")
            return False
        print("✅ 微信推送成功！")
        return True
    except Exception as exc:
        print(f"[ERROR] 推送失败：{exc}")
        return False


# ── 每日论文推荐（3篇打包成1条消息）─────────────────────────────────────────────

def send_daily_digest(featured: list[dict], extra: list[dict] = None) -> bool:
    """
    Send the full daily digest in one Server酱 message:
      - featured: 3 papers with Chinese abstract snippet + Telegraph link
      - extra:    5 papers with Chinese title only + DOI link
    """
    today = date.today().strftime("%Y年%m月%d日")
    extra = extra or []
    title = f"📚 今日论文推荐 · {today}"

    # ── Section 1: Featured 3 ──────────────────────────────────────────────────
    featured_blocks = []
    for i, paper in enumerate(featured):
        label   = "🎯 精选" if i < 2 else "🎲 随机"
        journal = paper["journal_short"]
        authors = "、".join(paper.get("authors", [])[:2])
        if len(paper.get("authors", [])) > 2:
            authors += " et al."
        link    = paper.get("telegraph_url") or paper.get("url", "")
        snippet = paper.get("abstract_zh", "").strip()[:150]
        if len(paper.get("abstract_zh", "")) > 150:
            snippet += "…"

        featured_blocks.append(
            f"**[{label}] {paper['title']}**\n"
            f"*{journal} · {authors} · {paper.get('pub_date', '')}*\n\n"
            f"{snippet}\n\n"
            f"[👉 读完整解读]({link})"
        )

    # ── Section 2: Extra 5 (title only) ───────────────────────────────────────
    extra_lines = []
    for paper in extra:
        title_zh = paper.get("title_zh", paper["title"])
        link     = paper.get("url", "")
        journal  = paper["journal_short"]
        extra_lines.append(f"- [{title_zh}]({link}) *{journal}*")

    content = "\n\n---\n\n".join(featured_blocks)
    if extra_lines:
        content += "\n\n---\n\n**📋 你可能感兴趣**\n\n" + "\n".join(extra_lines)

    print(f"推送今日推荐：{len(featured)} 篇精选 + {len(extra)} 篇扩展 …")
    return _send(title, content)


def send_daily_recommendation(paper: dict, telegraph_url: str) -> bool:
    """Legacy single-paper push."""
    paper["telegraph_url"] = telegraph_url
    return send_daily_digest([paper])


# ── 新刊公告 ───────────────────────────────────────────────────────────────────

def send_new_issue_announcement(issue_info: dict) -> bool:
    short   = issue_info["short"]
    journal = issue_info["journal"]
    volume  = issue_info["volume"]
    iss     = issue_info["issue"]
    papers  = issue_info["papers"]

    title = f"🆕 {short} 新刊上线！Vol.{volume} No.{iss}"

    highlights = "\n".join(
        f"- {p['title']}" for p in papers[:3]
    )

    content = f"""**{journal}** 出版了新一期

**Vol. {volume}，Issue {iss}**，共 {len(papers)} 篇

---

**本期可能值得关注：**

{highlights}

---

_今日随机漫步将从本期为你精选一篇深度解读 📖_
"""

    print(f"推送新刊公告：{short} Vol.{volume} No.{iss}")
    return _send(title, content)
