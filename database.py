"""
SQLite Database Layer
======================
Stores all fetched papers, tracks which issues have been announced,
and records daily recommendation history (so we don't repeat).
"""
from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path("data/papers.db")


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist yet."""
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS papers (
            doi         TEXT PRIMARY KEY,
            title       TEXT NOT NULL,
            authors     TEXT,           -- JSON list
            pub_date    TEXT,
            journal     TEXT,
            journal_short TEXT,
            category    TEXT,
            volume      TEXT,
            issue       TEXT,
            abstract    TEXT,
            subjects    TEXT,           -- JSON list
            url         TEXT,
            fetched_at  TEXT DEFAULT (date('now'))
        );

        CREATE TABLE IF NOT EXISTS issue_announcements (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            journal     TEXT,
            volume      TEXT,
            issue       TEXT,
            announced_at TEXT DEFAULT (date('now')),
            UNIQUE(journal, volume, issue)
        );

        CREATE TABLE IF NOT EXISTS recommendations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            doi         TEXT,
            recommended_date TEXT DEFAULT (date('now')),
            telegraph_url TEXT
        );
        """)


def upsert_paper(paper: dict):
    with get_conn() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO papers
              (doi, title, authors, pub_date, journal, journal_short, category,
               volume, issue, abstract, subjects, url)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            paper["doi"],
            paper["title"],
            json.dumps(paper.get("authors", []), ensure_ascii=False),
            paper.get("pub_date"),
            paper.get("journal"),
            paper.get("journal_short"),
            paper.get("category"),
            paper.get("volume"),
            paper.get("issue"),
            paper.get("abstract"),
            json.dumps(paper.get("subjects", []), ensure_ascii=False),
            paper.get("url"),
        ))


def get_recommended_dois() -> set[str]:
    with get_conn() as conn:
        rows = conn.execute("SELECT doi FROM recommendations").fetchall()
    return {r["doi"] for r in rows}


def mark_recommended(doi: str, telegraph_url: str = ""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO recommendations (doi, telegraph_url) VALUES (?, ?)",
            (doi, telegraph_url),
        )


def get_all_unread_papers() -> list[dict]:
    """Return papers that have never been recommended."""
    recommended = get_recommended_dois()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM papers ORDER BY fetched_at DESC"
        ).fetchall()
    result = []
    for r in rows:
        if r["doi"] not in recommended:
            d = dict(r)
            d["authors"]  = json.loads(d["authors"] or "[]")
            d["subjects"] = json.loads(d["subjects"] or "[]")
            result.append(d)
    return result


def is_issue_announced(journal: str, volume: str, issue: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM issue_announcements WHERE journal=? AND volume=? AND issue=?",
            (journal, volume, issue),
        ).fetchone()
    return row is not None


def mark_issue_announced(journal: str, volume: str, issue: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO issue_announcements (journal, volume, issue) VALUES (?,?,?)",
            (journal, volume, issue),
        )


def get_new_issues(papers: list[dict]) -> list[dict]:
    """
    Given a freshly-fetched list of papers, return those that belong to
    a (journal, volume, issue) combination we haven't announced yet.
    Groups them by issue for the announcement message.
    """
    from itertools import groupby

    # Filter papers that have volume+issue info
    with_issue = [p for p in papers if p.get("volume") and p.get("issue")]

    new_issues = []
    # Group by (journal, volume, issue)
    key = lambda p: (p["journal"], p.get("volume",""), p.get("issue",""))
    for (journal, volume, issue), group in groupby(sorted(with_issue, key=key), key=key):
        if not is_issue_announced(journal, volume, issue):
            new_issues.append({
                "journal":  journal,
                "short":    next(p["journal_short"] for p in with_issue
                                 if p["journal"] == journal),
                "volume":   volume,
                "issue":    issue,
                "papers":   list(group),
            })
    return new_issues
