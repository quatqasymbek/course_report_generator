import re
import pandas as pd


def normalize_column_name(col: str) -> str:
    col = str(col).strip().lower()
    col = col.replace("\n", " ")
    col = col.replace("/", "_")
    col = col.replace("\\", "_")
    col = col.replace("-", "_")
    col = col.replace("(", "")
    col = col.replace(")", "")
    col = col.replace("?", "")
    col = col.replace("%", "pct")
    col = re.sub(r"\s+", "_", col)
    col = re.sub(r"_+", "_", col)
    return col.strip("_")


TESTS_COLUMN_MAP = {
    "иин": "iin",
    "название_курса": "course_name",
    "область_город": "region",
    "район_город": "district",
    "дата_начала_обучения": "start_date",
    "дата_завершения_обучения": "end_date",
    "диагностическое_тестирование": "pre_test_score",
    "итоговое_тестирование": "post_test_score",
    "прирост_знаний": "knowledge_gain",
    "итоговая_оценка_за_курс_значение": "final_course_score",
    "защита_проекта": "project_score",
    "посещаемость": "attendance",
    "уникальный_код_группы": "group_code",
    "номер_группы": "group_number",
    "язык_обучения": "study_language",
}


SURVEY_COLUMN_MAP = {
    "дата_сдачи": "submit_date",
    "иин": "iin",
    "название_курса": "course_name",
    "филиал": "branch",
    "дата_начала_обучения": "start_date",
    "дата_завершения_обучения": "end_date",
    "категория_курса": "course_category",
    "код_группы": "group_code",
    "1.1_насколько_вы_удовлетворены_содержанием_курса": "content_score",
    "1.2_насколько_вы_удовлетворены_качеством_учебных_материалов_ресурсов": "material_score",
    "4._какие_у_вас_есть_предложения_по_улучшению_данного_курса": "improvement_comment",
}


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [normalize_column_name(c) for c in df.columns]
    return df


def map_test_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rename_map = {k: v for k, v in TESTS_COLUMN_MAP.items() if k in df.columns}
    return df.rename(columns=rename_map)


def map_survey_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rename_map = {k: v for k, v in SURVEY_COLUMN_MAP.items() if k in df.columns}
    return df.rename(columns=rename_map)
