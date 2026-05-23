"""
Interest-based Random Walk Recommender
========================================
Reads interests.txt, scores unread papers by keyword relevance,
then adds a small random weight so you occasionally discover
something outside your usual wheelhouse.
"""
from __future__ import annotations

import math
import os
import random
from pathlib import Path

INTERESTS_FILE = Path("interests.txt")


def _load_interests() -> list[str]:
    if not INTERESTS_FILE.exists():
        return []
    lines = INTERESTS_FILE.read_text(encoding="utf-8").splitlines()
    return [l.strip().lower() for l in lines
            if l.strip() and not l.strip().startswith("#")]


def _score(paper: dict, interests: list[str]) -> float:
    """
    Simple keyword overlap score.
    Checks title + abstract + subjects against your interest keywords.
    """
    haystack = " ".join([
        paper.get("title", ""),
        paper.get("abstract", ""),
        " ".join(paper.get("subjects", [])),
    ]).lower()

    score = 0.0
    for kw in interests:
        # partial match: "AI" matches "artificial intelligence" etc.
        if kw in haystack:
            score += 1.0
        # bonus for title match
        if kw in paper.get("title", "").lower():
            score += 0.5

    return score


def pick_papers(papers: list[dict], n_related: int = 2, n_random: int = 1) -> list[dict]:
    """
    Pick (n_related + n_random) papers per day:
      - n_related: highest interest-score papers (deterministic top picks)
      - n_random:  one truly random paper from the rest (discovery / random walk)

    Returns a list with related papers first, then the random one.
    """
    if not papers:
        return []

    interests = _load_interests()

    if not interests:
        # No interests configured — all random
        k = min(n_related + n_random, len(papers))
        return random.sample(papers, k)

    # Score and sort
    scored = sorted(papers, key=lambda p: _score(p, interests), reverse=True)

    # Top n_related
    related = scored[:n_related]
    picked_dois = {p["doi"] for p in related}

    # Random 1 from the rest
    remaining = [p for p in scored if p["doi"] not in picked_dois]
    random_pick = random.sample(remaining, min(n_random, len(remaining))) if remaining else []

    return related + random_pick


def pick_paper(papers: list[dict]) -> dict | None:
    """Legacy single-paper picker — kept for backward compatibility."""
    result = pick_papers(papers, n_related=1, n_random=0)
    return result[0] if result else None


def top_papers_for_issue(papers: list[dict], n: int = 3) -> list[dict]:
    """
    For a new issue announcement, return the n most interesting papers
    based on interest score (deterministic, no randomness).
    """
    interests = _load_interests()
    if not interests:
        return papers[:n]
    scored = sorted(papers, key=lambda p: _score(p, interests), reverse=True)
    return scored[:n]
