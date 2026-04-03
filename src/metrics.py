import pandas as pd


SURVEY_SCORE_MAP = {
    "отлично": 5,
    "высокий": 5,
    "хорошо": 4,
    "удовлетворительно": 3,
    "плохо": 2,
}


def prepare_tests_metrics(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    for col in ["pre_test_score", "post_test_score", "knowledge_gain", "final_course_score", "project_score", "attendance"]:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce")

    summary = (
        result.groupby("course_name", dropna=False)
        .agg(
            participants=("iin", "nunique"),
            avg_pre_test=("pre_test_score", "mean"),
            avg_post_test=("post_test_score", "mean"),
            avg_knowledge_gain=("knowledge_gain", "mean"),
            avg_final_course_score=("final_course_score", "mean"),
            avg_project_score=("project_score", "mean"),
            avg_attendance=("attendance", "mean"),
        )
        .reset_index()
    )
    return summary


def prepare_region_metrics(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    for col in ["pre_test_score", "post_test_score", "knowledge_gain"]:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce")

    summary = (
        result.groupby(["course_name", "region"], dropna=False)
        .agg(
            participants=("iin", "nunique"),
            avg_pre_test=("pre_test_score", "mean"),
            avg_post_test=("post_test_score", "mean"),
            avg_knowledge_gain=("knowledge_gain", "mean"),
        )
        .reset_index()
    )
    return summary


def prepare_survey_metrics(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    for col in ["content_score", "material_score"]:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce")

    summary = (
        result.groupby("course_name", dropna=False)
        .agg(
            survey_responses=("iin", "nunique"),
            avg_content_score=("content_score", "mean"),
            avg_material_score=("material_score", "mean"),
        )
        .reset_index()
    )
    return summary


def combine_course_summary(
    tests_summary: pd.DataFrame,
    survey_summary: pd.DataFrame,
) -> pd.DataFrame:
    return tests_summary.merge(survey_summary, on="course_name", how="left")
