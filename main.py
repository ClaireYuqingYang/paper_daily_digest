"""
Paper Daily Digest — Main Orchestrator
========================================

Daily flow:
  1. Fetch new papers from UTD24 journals → save to SQLite DB
  2. Detect new journal issues → send announcement
  3. Random-walk pick one paper based on your research interests
  4. Translate abstract to Chinese + write blog article (Claude API)
  5. Publish to Telegraph → get public URL
  6. Push to WeChat / Feishu webhook

Usage:
  python main.py                   # normal daily run
  python main.py --days 30         # catch up on past 30 days
  python main.py --no-send         # dry run (no webhook push)
  python main.py --no-telegraph    # skip Telegraph, send text-only
"""
from __future__ import annotations

import argparse
import sys

import config
from database import (
    get_all_unread_papers,
    get_new_issues,
    init_db,
    mark_issue_announced,
    mark_recommended,
    upsert_paper,
)
from fetcher import fetch_recent_papers
from recommender import pick_paper, pick_papers, top_papers_for_issue
from sender import send_daily_digest, send_new_issue_announcement
from telegraph_publisher import publish_paper
from translator import enrich_paper


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days",          type=int,  default=None)
    parser.add_argument("--no-send",       action="store_true")
    parser.add_argument("--no-telegraph",  action="store_true")
    args = parser.parse_args()

    if args.days:
        config.LOOKBACK_DAYS = args.days

    # ── Init DB ────────────────────────────────────────────────────────────────
    init_db()

    # ── 1. Fetch new papers ────────────────────────────────────────────────────
    new_papers = fetch_recent_papers()
    for p in new_papers:
        upsert_paper(p)

    # ── 2. Detect & announce new issues ───────────────────────────────────────
    new_issues = get_new_issues(new_papers)
    for issue_info in new_issues:
        # Highlight top papers by interest score
        issue_info["papers"] = top_papers_for_issue(issue_info["papers"], n=3)
        if not args.no_send:
            send_new_issue_announcement(issue_info)
        mark_issue_announced(
            issue_info["journal"], issue_info["volume"], issue_info["issue"]
        )

    # ── 3. Pick today's papers (2 interest-related + 1 random) ────────────────
    unread = get_all_unread_papers()
    if not unread:
        print("No unread papers in database. Try running with --days 30 to build up the library.")
        sys.exit(0)

    todays_papers = pick_papers(unread, n_related=2, n_random=1)
    print(f"\n📌 Today's picks ({len(todays_papers)} papers):")
    for i, p in enumerate(todays_papers):
        label = "🎯 interest" if i < 2 else "🎲 random"
        print(f"   [{label}] {p['title'][:65]}…  ({p['journal_short']})")
    print()

    # ── 4. Translate + write blog for each paper ───────────────────────────────
    enriched = []
    for paper in todays_papers:
        print(f"Enriching: {paper['title'][:60]}…")
        enriched.append(enrich_paper(paper))

    # ── 5. Publish each to Telegraph ──────────────────────────────────────────
    for paper in enriched:
        telegraph_url = ""
        if not args.no_telegraph:
            telegraph_url = publish_paper(paper)
        paper["telegraph_url"] = telegraph_url

    # ── 6. Push one bundled webhook message ────────────────────────────────────
    if not args.no_send:
        send_daily_digest(enriched)

    # ── 7. Mark all as recommended ────────────────────────────────────────────
    for paper in enriched:
        mark_recommended(paper["doi"], paper.get("telegraph_url", ""))

    print("\nDone! 🎉")


if __name__ == "__main__":
    main()
