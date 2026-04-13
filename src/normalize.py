from __future__ import annotations

from typing import Any

import pandas as pd

from src.utils import normalize_text, normalized_key


SURVEY_10_SCORE_MAP = {
    "отлично": 10.0,
    "очень хорошо": 9.0,
    "хорошо": 8.0,
    "удовлетворительно": 6.0,
    "средне": 6.0,
    "плохо": 3.0,
    "очень плохо": 1.0,
}

TRAINER_TEXT_SCORE_MAP = {
    "отлично": 5.0,
    "высокий": 5.0,
    "проявляли высокую активность": 5.0,
    "хорошо": 4.0,
    "хороший": 4.0,
    "в целом помог": 4.0,
    "удовлетворительно": 3.0,
    "средний": 3.0,
    "на подходящем уровне сложности": 3.0,
    "проявляли умеренную активность": 3.0,
    "плохо": 2.0,
    "низкий": 2.0,
    "слишком сложно": 2.0,
    "проявляли низкую активность": 2.0,
}


def canonicalize_region(value: Any) -> str:
    text = normalized_key(value)
    if not text:
        return ""

    text = text.replace(".", " ")
    text = " ".join(text.split())

    exact_checks = [
        ("г.Алматы", ["г алматы", "город алматы"]),
        ("г.Астана", ["г астана", "город астана"]),
        ("г.Шымкент", ["г шымкент", "город шымкент"]),
        ("Акмолинская", ["акмолин"]),
        ("Актюбинская", ["актюбин", "актоб"]),
        ("Алматинская", ["алматинская область", "алматин обл", "алматин"]),
        ("Атырауская", ["атырау"]),
        ("Восточно-Казахстанская", ["восточно казахстан", "вко"]),
        ("Жамбылская", ["жамбыл"]),
        ("Западно-Казахстанская", ["западно казахстан", "зко"]),
        ("Карагандинская", ["караганд"]),
        ("Костанайская", ["костанай"]),
        ("Кызылординская", ["кызылорд"]),
        ("Мангистауская", ["мангиста"]),
        ("Абай", ["область абай", "абай"]),
        ("Жетісу", ["жетісу", "жетису"]),
        ("Ұлытау", ["ұлытау", "улытау"]),
        ("Павлодарская", ["павлодар"]),
        ("Северо-Казахстанская", ["северо казахстан", "ско"]),
        ("Туркестанская", ["туркест"]),
    ]

    for canonical, patterns in exact_checks:
        if any(pattern in text for pattern in patterns):
            return canonical

    if text == "алматы":
        return "г.Алматы"
    if text == "астана":
        return "г.Астана"
    if text == "шымкент":
        return "г.Шымкент"

    return normalize_text(value)


def _text_score_to_numeric_10(value: Any) -> float | pd.NA:
    if pd.isna(value):
        return pd.NA

    if isinstance(value, (int, float)) and not pd.isna(value):
        return float(value)

    text = normalized_key(value)
    if not text:
        return pd.NA

    if text in SURVEY_10_SCORE_MAP:
        return SURVEY_10_SCORE_MAP[text]

    for k, v in SURVEY_10_SCORE_MAP.items():
        if k in text:
            return v

    return pd.NA


def _text_score_to_numeric_5(value: Any) -> float | pd.NA:
    if pd.isna(value):
        return pd.NA

    if isinstance(value, (int, float)) and not pd.isna(value):
        return float(value)

    text = normalized_key(value)
    if not text:
        return pd.NA

    if text in TRAINER_TEXT_SCORE_MAP:
        return TRAINER_TEXT_SCORE_MAP[text]

    for k, v in TRAINER_TEXT_SCORE_MAP.items():
        if k in text:
            return v

    return pd.NA


def _mean_from_prefixes(df: pd.DataFrame, prefixes: list[str], output_col: str) -> pd.DataFrame:
    matching_cols = [c for c in df.columns if any(c.startswith(prefix) for prefix in prefixes)]

    if not matching_cols:
        df[output_col] = pd.NA
        return df

    temp = df[matching_cols].copy()
    for col in matching_cols:
        temp[col] = temp[col].map(_text_score_to_numeric_5)

    df[output_col] = temp.mean(axis=1, skipna=True)
    return df


def normalize_tests_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    text_cols = [
        "iin",
        "course_name",
        "region_raw",
        "district_raw",
        "group_code",
        "group_number",
        "study_language",
        "branch",
        "last_name",
        "first_name",
        "middle_name",
    ]
    for col in text_cols:
        if col in result.columns:
            result[col] = result[col].map(normalize_text)

    if "course_name" in result.columns:
        result["normalized_course_name"] = result["course_name"].map(normalized_key)
    else:
        result["normalized_course_name"] = ""

    if "region_raw" in result.columns:
        result["region_canonical"] = result["region_raw"].map(canonicalize_region)
    else:
        result["region_canonical"] = ""

    numeric_cols = [
        "pre_test_score",
        "post_test_score",
        "knowledge_gain",
        "final_course_score",
        "project_score",
        "attendance",
    ]
    for col in numeric_cols:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce")

    for col in ["start_date", "end_date"]:
        if col in result.columns:
            result[col] = pd.to_datetime(result[col], errors="coerce", dayfirst=True)

    return result


def normalize_surveys_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    text_cols = [
        "iin",
        "course_name",
        "branch",
        "group_code",
        "improvement_comment",
        "course_category",
    ]
    for col in text_cols:
        if col in result.columns:
            result[col] = result[col].map(normalize_text)

    if "course_name" in result.columns:
        result["normalized_course_name"] = result["course_name"].map(normalized_key)
    else:
        result["normalized_course_name"] = ""

    for col in ["content_score", "material_score"]:
        if col in result.columns:
            result[col] = result[col].map(_text_score_to_numeric_10)

    result = _mean_from_prefixes(result, prefixes=["3_1_"], output_col="trainer_mastery_score")
    result = _mean_from_prefixes(result, prefixes=["3_2_"], output_col="trainer_skill_score")
    result = _mean_from_prefixes(result, prefixes=["3_3_"], output_col="trainer_organization_score")
    result = _mean_from_prefixes(result, prefixes=["3_4_"], output_col="trainer_engagement_score")

    for col in ["submit_date", "start_date", "end_date"]:
        if col in result.columns:
            result[col] = pd.to_datetime(result[col], errors="coerce", dayfirst=True)

    return result
