from __future__ import annotations

import pandas as pd

from src.utils import normalize_column_name


TESTS_COLUMN_MAP = {
    "иин": "iin",
    "название_курса": "course_name",
    "область_город": "region_raw",
    "район_город": "district_raw",
    "дата_начала_обучения": "start_date",
    "дата_завершения_обучения": "end_date",
    "диагностическое_тестирование": "pre_test_score",
    "итоговое_тестирование": "post_test_score",
    "прирост_знаний": "knowledge_gain",
    "итоговая_оценка_за_курс_значение": "final_course_score",
    "итоговая_оценка_за_курс": "final_course_score",
    "защита_проекта": "project_score",
    "посещаемость": "attendance",
    "уникальный_код_группы": "group_code",
    "код_группы": "group_code",
    "номер_группы": "group_number",
    "язык_обучения": "study_language",
    "фамилия": "last_name",
    "имя": "first_name",
    "отчество": "middle_name",
    "филиал": "branch",
}


SURVEY_COLUMN_MAP = {
    "дата_сдачи": "submit_date",
    "дата_заполнения": "submit_date",
    "иин": "iin",
    "название_курса": "course_name",
    "филиал": "branch",
    "дата_начала_обучения": "start_date",
    "дата_завершения_обучения": "end_date",
    "категория_курса": "course_category",
    "код_группы": "group_code",
    "уникальный_код_группы": "group_code",
    "1_1_насколько_вы_удовлетворены_содержанием_курса": "content_score",
    "1_2_насколько_вы_удовлетворены_качеством_учебных_материалов_ресурсов": "material_score",
    "4_какие_у_вас_есть_предложения_по_улучшению_данного_курса": "improvement_comment",
}


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result.columns = [normalize_column_name(c) for c in result.columns]
    return result


def map_test_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    rename_map = {k: v for k, v in TESTS_COLUMN_MAP.items() if k in result.columns}
    return result.rename(columns=rename_map)


def map_survey_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    rename_map = {k: v for k, v in SURVEY_COLUMN_MAP.items() if k in result.columns}
    return result.rename(columns=rename_map)
