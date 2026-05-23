"""
Translator & Blog Writer — Claude API
=======================================
1. Translates the abstract to Chinese
2. Writes a blog-style article about the paper
"""
from __future__ import annotations

import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL


def _client() -> anthropic.Anthropic | None:
    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "your-anthropic-api-key-here":
        return None
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def translate_abstract(abstract: str, client: anthropic.Anthropic) -> str:
    """Translate an English abstract to Chinese."""
    if not abstract.strip():
        return "（暂无摘要）"
    try:
        msg = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=600,
            system="你是学术翻译助手。请将以下英文论文摘要翻译成流畅、准确的中文学术语言。只输出翻译结果，不要添加任何解释。",
            messages=[{"role": "user", "content": abstract}],
        )
        return msg.content[0].text.strip()
    except Exception as exc:
        print(f"  [WARN] Translation failed: {exc}")
        return "（翻译失败，请查看英文原文）"


def write_blog_post(paper: dict, abstract_zh: str, client: anthropic.Anthropic) -> str:
    """
    Write a blog-style article about the paper.
    Returns a Markdown string.
    """
    prompt = f"""请根据以下论文信息，用中文写一篇适合微信公众号风格的学术博客文章（600-800字）。

文章结构：
1. **这篇论文在研究什么？**（用一个有趣的问题或场景引入）
2. **他们是怎么研究的？**（研究方法，1-2句话）
3. **发现了什么？**（核心结论，重点突出）
4. **为什么值得关注？**（对领域的意义，或对实践的启示）

论文信息：
标题：{paper['title']}
期刊：{paper['journal']} ({paper['journal_short']})
发表日期：{paper.get('pub_date', 'N/A')}
作者：{', '.join(paper.get('authors', [])[:3])}

英文摘要：
{paper.get('abstract', '（无摘要）')}

要求：语言生动、不枯燥，让非专业读者也能理解，适当使用emoji，段落之间有过渡。"""

    try:
        msg = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()
    except Exception as exc:
        print(f"  [WARN] Blog writing failed: {exc}")
        return abstract_zh  # fallback to Chinese abstract


def translate_title(title: str, client: anthropic.Anthropic) -> str:
    """Translate a paper title to Chinese only."""
    try:
        msg = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=100,
            system="将以下学术论文标题翻译成中文，只输出翻译结果，不加任何解释。",
            messages=[{"role": "user", "content": title}],
        )
        return msg.content[0].text.strip()
    except Exception as exc:
        print(f"  [WARN] Title translation failed: {exc}")
        return title


def enrich_title_only(paper: dict) -> dict:
    """Only translate the title — no abstract translation, no blog post. Much cheaper."""
    client = _client()
    if client is None:
        paper["title_zh"] = paper["title"]
    else:
        paper["title_zh"] = translate_title(paper["title"], client)
    return paper


def enrich_paper(paper: dict) -> dict:
    """
    Add 'abstract_zh' and 'blog_content' to the paper dict.
    Falls back gracefully if no API key is configured.
    """
    client = _client()

    if client is None:
        print("  [INFO] No Anthropic API key — using raw abstract only.")
        paper["abstract_zh"] = "（未配置 API Key，请查看英文摘要）"
        paper["blog_content"] = paper.get("abstract", "")
        return paper

    print(f"  Translating abstract …")
    paper["abstract_zh"] = translate_abstract(paper.get("abstract", ""), client)

    print(f"  Writing blog post …")
    paper["blog_content"] = write_blog_post(paper, paper["abstract_zh"], client)

    return paper
