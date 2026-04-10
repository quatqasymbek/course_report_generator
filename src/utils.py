from __future__ import annotations

import re
from typing import Any

import pandas as pd


def normalize_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    text = str(value).replace("\xa0", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text


def normalized_key(value: Any) -> str:
    text = normalize_text(value).lower()
    text = text.replace("ё", "е")
    text = text.replace("’", "'").replace("`", "'")
    return text


def normalize_column_name(col: str) -> str:
    text = normalize_text(col).lower()
    text = text.replace("%", " pct ")
    text = re.sub(r"[^\w]+", "_", text, flags=re.UNICODE)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def safe_round(value: Any, ndigits: int = 2) -> float:
    if pd.isna(value):
        return 0.0
    try:
        return round(float(value), ndigits)
    except Exception:
        return 0.0


def safe_int(value: Any) -> int:
    if pd.isna(value):
        return 0
    try:
        return int(value)
    except Exception:
        return 0


def pct(part: float, total: float) -> float:
    if not total:
        return 0.0
    return round((part / total) * 100.0, 2)
