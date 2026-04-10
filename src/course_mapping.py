from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.readers import read_excel_path
from src.utils import normalize_text, normalized_key


REQUIRED_COLUMNS = [
    "course_id",
    "course_name_canonical",
    "course_name_rus",
    "course_name_kaz",
    "course_name_ustazpro",
]


def read_course_mapping(path: Path) -> pd.DataFrame:
    df = read_excel_path(path)

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    if "is_active" not in df.columns:
        df["is_active"] = 1
    if "comment" not in df.columns:
        df["comment"] = pd.NA

    df = df.copy()
    for col in REQUIRED_COLUMNS:
        df[col] = df[col].map(normalize_text)

    df["is_active"] = df["is_active"].fillna(1)
    df = df[df["is_active"].astype(int) == 1].copy()

    df["course_name_canonical"] = df["course_name_canonical"].where(
        df["course_name_canonical"].astype(str).str.strip() != "",
        df["course_name_rus"],
    )
    df["course_name_canonical"] = df["course_name_canonical"].where(
        df["course_name_canonical"].astype(str).str.strip() != "",
        df["course_name_kaz"],
    )
    df["course_name_canonical"] = df["course_name_canonical"].where(
        df["course_name_canonical"].astype(str).str.strip() != "",
        df["course_name_ustazpro"],
    )

    return df


def build_dim_course(course_mapping_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "course_id",
        "course_name_canonical",
        "course_name_rus",
        "course_name_kaz",
        "course_name_ustazpro",
        "is_active",
        "comment",
    ]
    return course_mapping_df[cols].drop_duplicates(subset=["course_id"]).copy()


def build_course_alias_map_from_wide(course_mapping_df: pd.DataFrame) -> pd.DataFrame:
    alias_rows: list[dict[str, object]] = []

    alias_columns = [
        ("course_name_canonical", "canonical"),
        ("course_name_rus", "rus"),
        ("course_name_kaz", "kaz"),
        ("course_name_ustazpro", "ustazpro"),
    ]

    for _, row in course_mapping_df.iterrows():
        course_id = row["course_id"]
        for col_name, alias_source in alias_columns:
            raw_name = normalize_text(row.get(col_name, ""))
            if not raw_name:
                continue

            alias_rows.append(
                {
                    "raw_course_name": raw_name,
                    "normalized_course_name": normalized_key(raw_name),
                    "course_id": course_id,
                    "alias_source": alias_source,
                    "is_active": 1,
                }
            )

    alias_df = pd.DataFrame(alias_rows).drop_duplicates(
        subset=["normalized_course_name", "course_id"]
    )
    return alias_df


def validate_course_mapping(course_mapping_df: pd.DataFrame) -> pd.DataFrame:
    issues: list[dict[str, object]] = []

    missing_course_id = course_mapping_df["course_id"].astype(str).str.strip().eq("").sum()
    if missing_course_id:
        issues.append(
            {
                "issue_type": "missing_course_id",
                "row_count": int(missing_course_id),
                "details": "Есть строки с пустым course_id",
            }
        )

    no_names_mask = (
        course_mapping_df["course_name_canonical"].astype(str).str.strip().eq("")
        & course_mapping_df["course_name_rus"].astype(str).str.strip().eq("")
        & course_mapping_df["course_name_kaz"].astype(str).str.strip().eq("")
        & course_mapping_df["course_name_ustazpro"].astype(str).str.strip().eq("")
    )
    if int(no_names_mask.sum()) > 0:
        issues.append(
            {
                "issue_type": "no_course_names",
                "row_count": int(no_names_mask.sum()),
                "details": "Есть строки без единого варианта названия курса",
            }
        )

    duplicated_course_ids = course_mapping_df["course_id"].duplicated().sum()
    if int(duplicated_course_ids) > 0:
        issues.append(
            {
                "issue_type": "duplicate_course_id_rows",
                "row_count": int(duplicated_course_ids),
                "details": "Есть дубли course_id в wide mapping table",
            }
        )

    alias_df = build_course_alias_map_from_wide(course_mapping_df)
    alias_dup = alias_df.groupby("normalized_course_name")["course_id"].nunique().reset_index()
    alias_conflicts = alias_dup[alias_dup["course_id"] > 1]
    if not alias_conflicts.empty:
        issues.append(
            {
                "issue_type": "alias_conflict",
                "row_count": int(len(alias_conflicts)),
                "details": "Одно и то же normalized_course_name маппится на несколько course_id",
            }
        )

    return pd.DataFrame(issues)
