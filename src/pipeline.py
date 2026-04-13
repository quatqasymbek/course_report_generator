from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.config import COURSE_MAPPING_PATH
from src.course_mapping import read_course_mapping, validate_course_mapping
from src.deduplicate import deduplicate_surveys, deduplicate_tests
from src.matching import match_courses_from_wide_mapping
from src.metrics import build_course_summary, build_region_summary, build_survey_summary
from src.normalize import normalize_surveys_dataframe, normalize_tests_dataframe
from src.readers import read_surveys_excel, read_tests_excel


@dataclass
class PipelineResult:
    tests_raw: pd.DataFrame
    surveys_raw: pd.DataFrame
    tests_matched: pd.DataFrame
    surveys_matched: pd.DataFrame
    course_summary: pd.DataFrame
    region_summary: pd.DataFrame
    survey_summary: pd.DataFrame
    unmatched_tests_courses: pd.DataFrame
    unmatched_surveys_courses: pd.DataFrame
    mapping_issues: pd.DataFrame
    dim_course: pd.DataFrame
    alias_map: pd.DataFrame
    available_courses: pd.DataFrame


def _enrich_surveys_with_region(surveys_df: pd.DataFrame, tests_df: pd.DataFrame) -> pd.DataFrame:
    if surveys_df.empty:
        return surveys_df.copy()
    if tests_df.empty:
        result = surveys_df.copy()
        if "region_canonical" not in result.columns:
            result["region_canonical"] = ""
        return result

    region_lookup = (
        tests_df[["iin", "course_id", "region_canonical"]]
        .dropna(subset=["iin", "course_id"])
        .drop_duplicates(subset=["iin", "course_id"], keep="first")
    )

    enriched = surveys_df.merge(region_lookup, on=["iin", "course_id"], how="left")
    enriched["region_canonical"] = enriched["region_canonical"].fillna("")
    return enriched


def _build_available_courses(dim_course: pd.DataFrame, tests_matched: pd.DataFrame, surveys_matched: pd.DataFrame) -> pd.DataFrame:
    if dim_course is None or dim_course.empty:
        return pd.DataFrame(columns=["course_id", "course_name_canonical", "course_label"])

    test_ids = set(
        tests_matched["course_id"].dropna().astype(str).str.strip().tolist()
    ) if not tests_matched.empty and "course_id" in tests_matched.columns else set()

    survey_ids = set(
        surveys_matched["course_id"].dropna().astype(str).str.strip().tolist()
    ) if not surveys_matched.empty and "course_id" in surveys_matched.columns else set()

    matched_ids = test_ids | survey_ids
    if not matched_ids:
        return pd.DataFrame(columns=["course_id", "course_name_canonical", "course_label"])

    courses = dim_course.copy()
    courses["course_id"] = courses["course_id"].fillna("").astype(str).str.strip()
    courses = courses[courses["course_id"].isin(matched_ids)].copy()

    if "course_name_canonical" not in courses.columns:
        courses["course_name_canonical"] = ""

    courses["course_label"] = (
        courses["course_name_canonical"].fillna("").astype(str).str.strip()
        + " | "
        + courses["course_id"]
    )

    return (
        courses[["course_id", "course_name_canonical", "course_label"]]
        .drop_duplicates(subset=["course_id"])
        .sort_values(["course_name_canonical", "course_id"])
        .reset_index(drop=True)
    )


def run_pipeline(tests_file=None, surveys_file=None) -> PipelineResult:
    course_mapping_df = read_course_mapping(COURSE_MAPPING_PATH)
    mapping_issues = validate_course_mapping(course_mapping_df)

    tests_raw = read_tests_excel(tests_file) if tests_file is not None else pd.DataFrame()
    surveys_raw = read_surveys_excel(surveys_file) if surveys_file is not None else pd.DataFrame()

    tests_raw = normalize_tests_dataframe(tests_raw) if not tests_raw.empty else tests_raw
    surveys_raw = normalize_surveys_dataframe(surveys_raw) if not surveys_raw.empty else surveys_raw

    if not tests_raw.empty:
        tests_matched, unmatched_tests_courses, alias_map, dim_course = match_courses_from_wide_mapping(
            tests_raw,
            course_mapping_df,
        )
        tests_matched = deduplicate_tests(tests_matched)
    else:
        tests_matched = pd.DataFrame()
        unmatched_tests_courses = pd.DataFrame(columns=["course_name", "normalized_course_name"])
        from src.course_mapping import build_course_alias_map_from_wide, build_dim_course
        alias_map = build_course_alias_map_from_wide(course_mapping_df)
        dim_course = build_dim_course(course_mapping_df)

    if not surveys_raw.empty:
        surveys_matched, unmatched_surveys_courses, _, _ = match_courses_from_wide_mapping(
            surveys_raw,
            course_mapping_df,
        )
        surveys_matched = deduplicate_surveys(surveys_matched)
    else:
        surveys_matched = pd.DataFrame()
        unmatched_surveys_courses = pd.DataFrame(columns=["course_name", "normalized_course_name"])

    surveys_matched = _enrich_surveys_with_region(surveys_matched, tests_matched)

    course_summary = build_course_summary(tests_matched, surveys_matched)
    region_summary = build_region_summary(tests_matched)
    survey_summary = build_survey_summary(surveys_matched)
    available_courses = _build_available_courses(dim_course, tests_matched, surveys_matched)

    return PipelineResult(
        tests_raw=tests_raw,
        surveys_raw=surveys_raw,
        tests_matched=tests_matched,
        surveys_matched=surveys_matched,
        course_summary=course_summary,
        region_summary=region_summary,
        survey_summary=survey_summary,
        unmatched_tests_courses=unmatched_tests_courses,
        unmatched_surveys_courses=unmatched_surveys_courses,
        mapping_issues=mapping_issues,
        dim_course=dim_course,
        alias_map=alias_map,
        available_courses=available_courses,
    )
