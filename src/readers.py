import pandas as pd

from src.standardize import (
    standardize_columns,
    map_test_columns,
    map_survey_columns,
)


def read_tests_excel(uploaded_file) -> pd.DataFrame:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    df = standardize_columns(df)
    df = map_test_columns(df)
    return df


def read_surveys_excel(uploaded_file) -> pd.DataFrame:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    df = standardize_columns(df)
    df = map_survey_columns(df)
    return df
