from __future__ import annotations

import pandas as pd

from src.config import REGION_ORDER
from src.utils import pct, safe_int, safe_round


def _empty_global_metrics() -> dict:
    return {
        "all_courses_students_count_total": 0,
        "all_courses_count_total": 0,
        "all_courses_kz_gain_mean": 0.0,
        "all_courses_largest_gain_score": 0.0,
        "all_courses_largest_gain_course": "",
        "all_courses_smallest_gain_score": 0.0,
        "all_courses_smallest_gain_course": "",
        "all_courses_avg_satisfaction_score_10": 0.0,
    }


def calculate_global_test_metrics(tests_df: pd.DataFrame) -> dict:
    if tests_df.empty:
        return _empty_global_metrics()

    result = _empty_global_metrics()
    result["all_courses_students_count_total"] = safe_int(tests_df["iin"].nunique())
    result["all_courses_count_total"] = safe_int(tests_df["course_id"].nunique())
    result["all_courses_kz_gain_mean"] = safe_round(tests_df["knowledge_gain"].mean())

    course_gain = (
        tests_df.groupby(["course_id", "course_name_canonical"], dropna=False)["knowledge_gain"]
        .mean()
        .reset_index()
    )

    if not course_gain.empty:
        max_row = course_gain.loc[course_gain["knowledge_gain"].idxmax()]
        min_row = course_gain.loc[course_gain["knowledge_gain"].idxmin()]

        result["all_courses_largest_gain_score"] = safe_round(max_row["knowledge_gain"])
        result["all_courses_largest_gain_course"] = str(max_row["course_name_canonical"] or "")

        result["all_courses_smallest_gain_score"] = safe_round(min_row["knowledge_gain"])
        result["all_courses_smallest_gain_course"] = str(min_row["course_name_canonical"] or "")

    return result


def calculate_global_survey_metrics(surveys_df: pd.DataFrame) -> dict:
    if surveys_df.empty:
        return {"all_courses_avg_satisfaction_score_10": 0.0}

    score_cols = [c for c in ["content_score", "material_score"] if c in surveys_df.columns]
    if not score_cols:
        return {"all_courses_avg_satisfaction_score_10": 0.0}

    stacked = pd.concat([surveys_df[c] for c in score_cols], ignore_index=True)
    return {"all_courses_avg_satisfaction_score_10": safe_round(stacked.mean())}


def build_course_summary(tests_df: pd.DataFrame, surveys_df: pd.DataFrame) -> pd.DataFrame:
    if tests_df.empty:
        return pd.DataFrame()

    tests_summary = (
        tests_df.groupby(["course_id", "course_name_canonical"], dropna=False)
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

    if surveys_df.empty:
        return tests_summary

    survey_summary = (
        surveys_df.groupby(["course_id", "course_name_canonical"], dropna=False)
        .agg(
            survey_responses=("iin", "nunique"),
            avg_content_score=("content_score", "mean"),
            avg_material_score=("material_score", "mean"),
            avg_trainer_mastery_score=("trainer_mastery_score", "mean"),
            avg_trainer_organization_score=("trainer_organization_score", "mean"),
        )
        .reset_index()
    )

    return tests_summary.merge(
        survey_summary,
        on=["course_id", "course_name_canonical"],
        how="left",
    )


def build_region_summary(tests_df: pd.DataFrame) -> pd.DataFrame:
    if tests_df.empty:
        return pd.DataFrame()

    summary = (
        tests_df.groupby(["course_id", "course_name_canonical", "region_canonical"], dropna=False)
        .agg(
            students_count=("iin", "nunique"),
            diag_mean=("pre_test_score", "mean"),
            final_mean=("post_test_score", "mean"),
            gain_mean=("knowledge_gain", "mean"),
        )
        .reset_index()
    )
    return summary


def build_survey_summary(surveys_df: pd.DataFrame) -> pd.DataFrame:
    if surveys_df.empty:
        return pd.DataFrame()

    summary = (
        surveys_df.groupby(["course_id", "course_name_canonical"], dropna=False)
        .agg(
            survey_responses=("iin", "nunique"),
            avg_content_score=("content_score", "mean"),
            avg_material_score=("material_score", "mean"),
            avg_trainer_mastery_score=("trainer_mastery_score", "mean"),
            avg_trainer_skill_score=("trainer_skill_score", "mean"),
            avg_trainer_organization_score=("trainer_organization_score", "mean"),
            avg_trainer_engagement_score=("trainer_engagement_score", "mean"),
        )
        .reset_index()
    )
    return summary


def calculate_course_test_metrics(tests_df: pd.DataFrame, course_id: str) -> dict:
    df_course = tests_df[tests_df["course_id"].astype(str) == str(course_id)].copy()
    if df_course.empty:
        return {
            "course_name": "",
            "course_students_count_kz": 0,
            "course_kz_diag_mean": 0.0,
            "course_kz_final_mean": 0.0,
            "course_kz_gain_mean": 0.0,
        }

    course_name = str(df_course["course_name_canonical"].dropna().iloc[0])

    return {
        "course_name": course_name,
        "course_students_count_kz": safe_int(df_course["iin"].nunique()),
        "course_kz_diag_mean": safe_round(df_course["pre_test_score"].mean()),
        "course_kz_final_mean": safe_round(df_course["post_test_score"].mean()),
        "course_kz_gain_mean": safe_round(df_course["knowledge_gain"].mean()),
    }


def calculate_region_placeholder_metrics(region_summary: pd.DataFrame, course_id: str) -> dict:
    course_regions = region_summary[region_summary["course_id"].astype(str) == str(course_id)].copy()
    result: dict[str, object] = {}

    for i, region in enumerate(REGION_ORDER, start=1):
        row = course_regions[course_regions["region_canonical"] == region]

        if not row.empty:
            row = row.iloc[0]
            result[f"r{i}_students_count"] = safe_int(row["students_count"])
            result[f"r{i}_diag"] = safe_round(row["diag_mean"])
            result[f"r{i}_final"] = safe_round(row["final_mean"])
            result[f"r{i}_gain"] = safe_round(row["gain_mean"])
        else:
            result[f"r{i}_students_count"] = 0
            result[f"r{i}_diag"] = 0.0
            result[f"r{i}_final"] = 0.0
            result[f"r{i}_gain"] = 0.0

    return result


def calculate_course_survey_metrics(surveys_df: pd.DataFrame, course_id: str) -> dict:
    df_course = surveys_df[surveys_df["course_id"].astype(str) == str(course_id)].copy()
    if df_course.empty:
        return {
            "course_csat_content_excellent_pct": 0.0,
            "course_csat_organization_excellent_pct": 0.0,
            "min_trainer_mastery_pct": 0.0,
            "avg_trainer_mastery_pct": 0.0,
            "course_avg_content_score": 0.0,
            "course_avg_material_score": 0.0,
            "course_avg_trainer_mastery_score": 0.0,
        }

    content_excellent = pct((df_course["content_score"] == 10).sum(), df_course["content_score"].notna().sum())
    organization_excellent = pct(
        (df_course["trainer_organization_score"] == 5).sum(),
        df_course["trainer_organization_score"].notna().sum(),
    )

    region_trainer = (
        df_course.groupby("region_canonical", dropna=False)
        .agg(
            trainer_mastery_excellent_pct=("trainer_mastery_score", lambda s: pct((s == 5).sum(), s.notna().sum()))
        )
        .reset_index()
    )

    avg_trainer_mastery_pct = safe_round(region_trainer["trainer_mastery_excellent_pct"].mean()) if not region_trainer.empty else 0.0
    min_trainer_mastery_pct = safe_round(region_trainer["trainer_mastery_excellent_pct"].min()) if not region_trainer.empty else 0.0

    return {
        "course_csat_content_excellent_pct": content_excellent,
        "course_csat_organization_excellent_pct": organization_excellent,
        "min_trainer_mastery_pct": min_trainer_mastery_pct,
        "avg_trainer_mastery_pct": avg_trainer_mastery_pct,
        "course_avg_content_score": safe_round(df_course["content_score"].mean()),
        "course_avg_material_score": safe_round(df_course["material_score"].mean()),
        "course_avg_trainer_mastery_score": safe_round(df_course["trainer_mastery_score"].mean()),
    }
