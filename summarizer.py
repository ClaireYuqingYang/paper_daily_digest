"""
AI Summarizer — Claude API
============================
Generates a concise bilingual (Chinese + English) digest for each paper.
Falls back to the raw abstract when the API is unavailable or no API key is set.
"""

from __future__ import annotations

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_PAPERS_TO_SUMMARISE

_SYSTEM_PROMPT = """You are an academic paper digest assistant.
Given a paper title and its English abstract, produce a structured bilingual summary in the following exact format:

**【中文简介】**
（2–3 句话：研究问题是什么、用了什么方法、主要发现是什么）

**【English Summary】**
(2–3 sentences: research question, method, key finding)

**【Keywords】**
（3–5 个最重要的关键词，中英文均可，逗号分隔）

Be concise and factual. Do not add opinions or extra headings."""

_FALLBACK_NOTE = "（摘要由原文 Abstract 提供，AI 摘要暂不可用）"


def _summarise_one(client: anthropic.Anthropic, paper: dict) -> str:
    """Call Claude to generate a bilingual summary for a single paper."""
    user_msg = f"Title: {paper['title']}\n\nAbstract:\n{paper['abstract'] or '(No abstract available)'}"
    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=512,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        return message.content[0].text.strip()
    except Exception as exc:
        print(f"  [WARN] AI summary failed for "{paper['title'][:60]}…": {exc}")
        return _make_fallback_summary(paper)


def _make_fallback_summary(paper: dict) -> str:
    """Return a plain-text fallback when the API is unavailable."""
    abstract = paper.get("abstract", "")
    if abstract:
        snippet = abstract[:300] + ("…" if len(abstract) > 300 else "")
        return f"{_FALLBACK_NOTE}\n\n{snippet}"
    return _FALLBACK_NOTE


def add_summaries(papers: list[dict]) -> list[dict]:
    """
    Attach an 'ai_summary' field to each paper dict.
    Only the first MAX_PAPERS_TO_SUMMARISE papers get real AI summaries;
    the rest get the fallback to control API cost.
    """
    if not papers:
        return papers

    # Initialise client only if we actually have a key
    use_ai = ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "your-anthropic-api-key-here"
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if use_ai else None

    print(f"Generating AI summaries for up to {MAX_PAPERS_TO_SUMMARISE} paper(s) …")

    for i, paper in enumerate(papers):
        if use_ai and i < MAX_PAPERS_TO_SUMMARISE:
            print(f"  [{i+1}/{min(len(papers), MAX_PAPERS_TO_SUMMARISE)}] {paper['title'][:70]}…")
            paper["ai_summary"] = _summarise_one(client, paper)
        else:
            paper["ai_summary"] = _make_fallback_summary(paper)

    print("Summaries done.\n")
    return papers
