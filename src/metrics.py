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

    if not course_gain.empty and course_gain["knowledge_gain"].notna().any():
        course_gain_non_null = course_gain.dropna(subset=["knowledge_gain"]).copy()

        if not course_gain_non_null.empty:
            max_row = course_gain_non_null.loc[course_gain_non_null["knowledge_gain"].idxmax()]
            min_row = course_gain_non_null.loc[course_gain_non_null["knowledge_gain"].idxmin()]

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

    stacked = pd.concat([surveys_df[c] for c in score_cols], ignore_index=True).dropna()
    if stacked.empty:
        return {"all_courses_avg_satisfaction_score_10": 0.0}

    return {"all_courses_avg_satisfaction_score_10": safe_round(stacked.mean())}


def build_course_summary(tests_df: pd.DataFrame, surveys_df: pd.DataFrame) -> pd.DataFrame:
    if tests_df.empty:
        return pd.DataFrame(
            columns=[
                "course_id",
                "course_name_canonical",
                "participants",
                "avg_pre_test",
                "avg_post_test",
                "avg_knowledge_gain",
                "avg_final_course_score",
                "avg_project_score",
                "avg_attendance",
                "survey_responses",
                "avg_content_score",
                "avg_material_score",
                "avg_trainer_mastery_score",
                "avg_trainer_skill_score",
                "avg_trainer_organization_score",
                "avg_trainer_engagement_score",
            ]
        )

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

    for col in [
        "avg_pre_test",
        "avg_post_test",
        "avg_knowledge_gain",
        "avg_final_course_score",
        "avg_project_score",
        "avg_attendance",
    ]:
        if col in tests_summary.columns:
            tests_summary[col] = tests_summary[col].map(safe_round)

    if surveys_df.empty:
        return tests_summary

    survey_summary = (
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

    for col in [
        "avg_content_score",
        "avg_material_score",
        "avg_trainer_mastery_score",
        "avg_trainer_skill_score",
        "avg_trainer_organization_score",
        "avg_trainer_engagement_score",
    ]:
        if col in survey_summary.columns:
            survey_summary[col] = survey_summary[col].map(safe_round)

    return tests_summary.merge(
        survey_summary,
        on=["course_id", "course_name_canonical"],
        how="left",
    )


def build_region_summary(tests_df: pd.DataFrame) -> pd.DataFrame:
    if tests_df.empty:
        return pd.DataFrame(
            columns=[
                "course_id",
                "course_name_canonical",
                "region_canonical",
                "students_count",
                "diag_mean",
                "final_mean",
                "gain_mean",
            ]
        )

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

    for col in ["diag_mean", "final_mean", "gain_mean"]:
        summary[col] = summary[col].map(safe_round)

    return summary


def build_survey_summary(surveys_df: pd.DataFrame) -> pd.DataFrame:
    if surveys_df.empty:
        return pd.DataFrame(
            columns=[
                "course_id",
                "course_name_canonical",
                "survey_responses",
                "avg_content_score",
                "avg_material_score",
                "avg_trainer_mastery_score",
                "avg_trainer_skill_score",
                "avg_trainer_organization_score",
                "avg_trainer_engagement_score",
            ]
        )

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

    for col in [
        "avg_content_score",
        "avg_material_score",
        "avg_trainer_mastery_score",
        "avg_trainer_skill_score",
        "avg_trainer_organization_score",
        "avg_trainer_engagement_score",
    ]:
        summary[col] = summary[col].map(safe_round)

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
    result: dict[str, object] = {}

    if region_summary.empty:
        for i in range(1, len(REGION_ORDER) + 1):
            result[f"r{i}_students_count"] = 0
            result[f"r{i}_diag"] = 0.0
            result[f"r{i}_final"] = 0.0
            result[f"r{i}_gain"] = 0.0
        return result

    course_regions = region_summary[region_summary["course_id"].astype(str) == str(course_id)].copy()

    for i, region in enumerate(REGION_ORDER, start=1):
        row = course_regions[course_regions["region_canonical"] == region]

        if not row.empty:
            row0 = row.iloc[0]
            result[f"r{i}_students_count"] = safe_int(row0["students_count"])
            result[f"r{i}_diag"] = safe_round(row0["diag_mean"])
            result[f"r{i}_final"] = safe_round(row0["final_mean"])
            result[f"r{i}_gain"] = safe_round(row0["gain_mean"])
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

    content_den = df_course["content_score"].notna().sum() if "content_score" in df_course.columns else 0
    content_num = (df_course["content_score"] == 10).sum() if "content_score" in df_course.columns else 0
    content_excellent = pct(content_num, content_den)

    org_den = (
        df_course["trainer_organization_score"].notna().sum()
        if "trainer_organization_score" in df_course.columns else 0
    )
    org_num = (
        (df_course["trainer_organization_score"] == 5).sum()
        if "trainer_organization_score" in df_course.columns else 0
    )
    organization_excellent = pct(org_num, org_den)

    if "trainer_mastery_score" in df_course.columns:
        region_trainer = (
            df_course.groupby("region_canonical", dropna=False)
            .agg(
                trainer_mastery_excellent_pct=(
                    "trainer_mastery_score",
                    lambda s: pct((s == 5).sum(), s.notna().sum()),
                )
            )
            .reset_index()
        )
    else:
        region_trainer = pd.DataFrame(columns=["region_canonical", "trainer_mastery_excellent_pct"])

    avg_trainer_mastery_pct = (
        safe_round(region_trainer["trainer_mastery_excellent_pct"].mean())
        if not region_trainer.empty else 0.0
    )
    min_trainer_mastery_pct = (
        safe_round(region_trainer["trainer_mastery_excellent_pct"].min())
        if not region_trainer.empty else 0.0
    )

    return {
        "course_csat_content_excellent_pct": content_excellent,
        "course_csat_organization_excellent_pct": organization_excellent,
        "min_trainer_mastery_pct": min_trainer_mastery_pct,
        "avg_trainer_mastery_pct": avg_trainer_mastery_pct,
        "course_avg_content_score": safe_round(df_course["content_score"].mean()) if "content_score" in df_course.columns else 0.0,
        "course_avg_material_score": safe_round(df_course["material_score"].mean()) if "material_score" in df_course.columns else 0.0,
        "course_avg_trainer_mastery_score": safe_round(df_course["trainer_mastery_score"].mean()) if "trainer_mastery_score" in df_course.columns else 0.0,
    }
