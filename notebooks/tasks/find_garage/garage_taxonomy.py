"""Shared garage-work detection patterns.

Single source of truth for the garage mention flag and the work-type
categories, so results are comparable across permit datasets
(hbkd-qubn vs the (N) pair). Mirrors the first-pass patterns developed
in find_garage.ipynb.
"""

import re

import pandas as pd

# garage + misspellings/abbreviations seen in LADBS free text
GARAGE_PAT = re.compile(
    r"\b(?:garage|gargage|garge|garrage|grage|garag|gar\.?|carport|car\s?port)\b",
    re.IGNORECASE,
)

G = r"(?:garage|gargage|garge|garrage|grage|garag|carport|car\s?port)"

# (category, pattern) checked in priority order
CATEGORY_PATTERNS = [
    ("conversion", rf"(?:convert|conversion|chang\w+)[^.]*{G}|{G}[^.]*(?:convert|conversion|to\s+(?:an?\s+)?(?:adu|dwelling|living|habitable|rec\w*\s?room|office|bedroom|studio))|{G}\s+conversion"),
    ("demolition", rf"(?:demo\w*|remove|removal|raze)[^.]*{G}|{G}[^.]*(?:demo\w*|to\s+be\s+(?:demolish|remove)\w*)"),
    ("new",        rf"(?:new|proposed|construct\w*|build|erect)[^.]*(?:detached\s+)?{G}|{G}[^.]*\bnew\b"),
    ("addition",   rf"(?:addition|add\w*|expand|enlarg\w*|extend\w*)[^.]*{G}|{G}[^.]*(?:addition|expansion)"),
    ("alteration", rf"(?:remodel|repair|re-?roof|reroof|alter\w*|replac\w*|retrofit|rebuild|foundation|stucco|drywall|door)[^.]*{G}|{G}[^.]*(?:remodel|repair|re-?roof|reroof|alter\w*|replac\w*|only)"),
]

_COMPILED = [(cat, re.compile(pat, re.IGNORECASE)) for cat, pat in CATEGORY_PATTERNS]

CATEGORIES = [cat for cat, _ in CATEGORY_PATTERNS] + ["incidental"]


def categorize(text: str) -> str:
    for cat, pat in _COMPILED:
        if pat.search(text):
            return cat
    return "incidental"


def flag_and_categorize(df: pd.DataFrame, desc_col: str) -> pd.DataFrame:
    """Return the subset of df mentioning a garage, with a garage_category column."""
    desc = df[desc_col].fillna("")
    garage = df[desc.str.contains(GARAGE_PAT)].copy()
    garage["garage_category"] = garage[desc_col].fillna("").map(categorize)
    garage["garage_category"] = pd.Categorical(garage["garage_category"], categories=CATEGORIES)
    return garage
