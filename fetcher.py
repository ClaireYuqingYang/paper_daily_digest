"""
Paper Fetcher — CrossRef API
"""
from __future__ import annotations

import re
import time
from datetime import date, timedelta

import requests

from config import LOOKBACK_DAYS, MAX_PAPERS_PER_JOURNAL, UTD24_JOURNALS

CROSSREF_BASE = "https://api.crossref.org/journals/{issn}/works"
HEADERS = {"User-Agent": "PaperDailyDigest/2.0 (mailto:claire.yq.yang@gmail.com)"}


def _clean_abstract(raw: str) -> str:
    if not raw:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", text).strip()


def _fetch_journal(issn: str, from_date: str, rows: int) -> list[dict]:
    try:
        resp = requests.get(
            CROSSREF_BASE.format(issn=issn),
            headers=HEADERS,
            params={
                "filter": f"from-pub-date:{from_date}",
                "rows": rows,
                "sort": "published",
                "order": "desc",
                "select": "DOI,title,author,published,abstract,subject,container-title,volume,issue",
            },
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json().get("message", {}).get("items", [])
    except Exception as exc:
        print(f"  [WARN] CrossRef failed for ISSN {issn}: {exc}")
        return []


def _parse(raw: dict, meta: dict) -> dict | None:
    titles = raw.get("title", [])
    if not titles:
        return None

    authors_raw = raw.get("author", [])
    authors = [f"{a.get('family','')}, {a.get('given','')}".strip(", ")
               for a in authors_raw[:5]]
    if len(authors_raw) > 5:
        authors.append("et al.")

    parts = (raw.get("published") or raw.get("published-print") or {}).get("date-parts", [[]])[0]
    pub_date = "-".join(str(p) for p in parts if p is not None)

    doi = raw.get("DOI", "")
    return {
        "title":        titles[0].strip(),
        "authors":      authors,
        "pub_date":     pub_date,
        "doi":          doi,
        "url":          f"https://doi.org/{doi}" if doi else "",
        "abstract":     _clean_abstract(raw.get("abstract", "")),
        "subjects":     raw.get("subject", []),
        "volume":       raw.get("volume", ""),
        "issue":        raw.get("issue", ""),
        "journal":      meta["name"],
        "journal_short": meta["short"],
        "category":     meta["category"],
    }


def fetch_recent_papers(lookback_days: int = LOOKBACK_DAYS) -> list[dict]:
    from_date = (date.today() - timedelta(days=lookback_days)).isoformat()
    print(f"Fetching papers since {from_date} …")
    all_papers = []
    for journal in UTD24_JOURNALS:
        print(f"  → {journal['short']} …", end=" ", flush=True)
        items = _fetch_journal(journal["issn"], from_date, MAX_PAPERS_PER_JOURNAL)
        papers = [p for item in items if (p := _parse(item, journal))]
        print(f"{len(papers)} paper(s)")
        all_papers.extend(papers)
        time.sleep(0.5)
    print(f"Total fetched: {len(all_papers)}\n")
    return all_papers
