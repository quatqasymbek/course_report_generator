from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.standardize import map_survey_columns, map_test_columns, standardize_columns


def read_excel_upload(uploaded_file) -> pd.DataFrame:
    return pd.read_excel(uploaded_file, engine="openpyxl")


def read_tests_excel(uploaded_file) -> pd.DataFrame:
    df = read_excel_upload(uploaded_file)
    df = standardize_columns(df)
    df = map_test_columns(df)
    return df


def read_surveys_excel(uploaded_file) -> pd.DataFrame:
    df = read_excel_upload(uploaded_file)
    df = standardize_columns(df)
    df = map_survey_columns(df)
    return df


def read_excel_path(path: Path) -> pd.DataFrame:
    return pd.read_excel(path, engine="openpyxl")
