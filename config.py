"""
Configuration for Paper Daily Digest
"""
import os

# ── API Keys ───────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your-anthropic-api-key-here")

# ── Server酱 SendKey ───────────────────────────────────────────────────────────
# 获取地址：https://sct.ftqq.com  登录后复制 SendKey
# 格式：SCT 开头的一串字符
# ⚠️  不要把真实 Key 写死在代码里，用环境变量或 GitHub Secrets
SERVERCHAN_KEY = os.getenv("SERVERCHAN_KEY", "your-sendkey-here")

# ── Telegraph ──────────────────────────────────────────────────────────────────
# Auto-created on first run and saved here. Leave blank initially.
TELEGRAPH_ACCESS_TOKEN = os.getenv("TELEGRAPH_ACCESS_TOKEN", "")
TELEGRAPH_AUTHOR_NAME  = "UTD Paper Digest"
TELEGRAPH_AUTHOR_URL   = "https://github.com/ClaireYuqingYang/paper_daily_digest"

# ── Claude Model ───────────────────────────────────────────────────────────────
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

# ── Fetch Settings ─────────────────────────────────────────────────────────────
LOOKBACK_DAYS          = 1    # days to look back for new papers
MAX_PAPERS_PER_JOURNAL = 5    # cap per journal per run

# ── UTD24 Journals — Marketing + IS + Management ──────────────────────────────
# Source: UT Dallas Top 100 Business School Research Rankings
# https://jindal.utdallas.edu/the-utd-top-100-business-school-research-rankings/
UTD24_JOURNALS = [
    # Marketing (4 journals)
    {"name": "Journal of Marketing",        "issn": "0022-2429", "category": "Marketing", "short": "JM"},
    {"name": "Journal of Marketing Research","issn": "0022-2437", "category": "Marketing", "short": "JMR"},
    {"name": "Journal of Consumer Research", "issn": "0093-5301", "category": "Marketing", "short": "JCR"},
    {"name": "Marketing Science",            "issn": "0732-2399", "category": "Marketing", "short": "Mktg Sci"},
    # Information Systems (2 journals)
    {"name": "MIS Quarterly",               "issn": "0276-7783", "category": "Information Systems", "short": "MISQ"},
    {"name": "Information Systems Research", "issn": "1047-7047", "category": "Information Systems", "short": "ISR"},
    # Management (6 journals)
    {"name": "Academy of Management Journal","issn": "0001-4273", "category": "Management", "short": "AMJ"},
    {"name": "Academy of Management Review", "issn": "0363-7425", "category": "Management", "short": "AMR"},
    {"name": "Administrative Science Quarterly","issn": "0001-8392","category": "Management","short": "ASQ"},
    {"name": "Management Science",           "issn": "0025-1909", "category": "Management", "short": "Mgmt Sci"},
    {"name": "Organization Science",         "issn": "1047-7039", "category": "Management", "short": "Org Sci"},
    {"name": "Strategic Management Journal", "issn": "0143-2095", "category": "Management", "short": "SMJ"},
]
