from __future__ import annotations

import pandas as pd


def deduplicate_tests(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    subset = [c for c in ["iin", "course_id", "group_code", "start_date", "end_date"] if c in df.columns]
    if not subset:
        return df.copy()

    ordered = df.sort_values([c for c in ["end_date", "start_date"] if c in df.columns])
    return ordered.drop_duplicates(subset=subset, keep="last").copy()


def deduplicate_surveys(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    subset = [c for c in ["iin", "course_id", "group_code", "submit_date"] if c in df.columns]
    if not subset:
        return df.copy()

    ordered = df.sort_values([c for c in ["submit_date"] if c in df.columns])
    return ordered.drop_duplicates(subset=subset, keep="last").copy()
