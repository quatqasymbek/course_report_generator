from __future__ import annotations

import pandas as pd


def validate_required_columns(df: pd.DataFrame, required_columns: list[str], dataset_name: str) -> pd.DataFrame:
    issues: list[dict[str, object]] = []

    for col in required_columns:
        if col not in df.columns:
            issues.append(
                {
                    "dataset": dataset_name,
                    "issue_type": "missing_required_column",
                    "column_name": col,
                    "details": f"Отсутствует обязательная колонка: {col}",
                }
            )

    return pd.DataFrame(issues)


def validate_missing_values(df: pd.DataFrame, required_columns: list[str], dataset_name: str) -> pd.DataFrame:
    issues: list[dict[str, object]] = []

    for col in required_columns:
        if col in df.columns:
            count = int(df[col].isna().sum() + (df[col].astype(str).str.strip() == "").sum())
            if count > 0:
                issues.append(
                    {
                        "dataset": dataset_name,
                        "issue_type": "missing_required_values",
                        "column_name": col,
                        "details": f"Пустые значения в {col}: {count}",
                    }
                )

    return pd.DataFrame(issues)
