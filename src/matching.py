from __future__ import annotations

import pandas as pd

from src.course_mapping import build_course_alias_map_from_wide, build_dim_course


def match_courses_from_wide_mapping(
    df: pd.DataFrame,
    course_mapping_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    alias_map = build_course_alias_map_from_wide(course_mapping_df)
    dim_course = build_dim_course(course_mapping_df)

    matched = df.merge(
        alias_map[["normalized_course_name", "course_id", "alias_source"]],
        on="normalized_course_name",
        how="left",
    )

    matched = matched.merge(
        dim_course[["course_id", "course_name_canonical"]],
        on="course_id",
        how="left",
    )

    unmatched = (
        matched[matched["course_id"].isna()][["course_name", "normalized_course_name"]]
        .drop_duplicates()
        .sort_values(["course_name", "normalized_course_name"])
        .reset_index(drop=True)
    )

    matched_only = matched[matched["course_id"].notna()].copy()

    return matched_only, unmatched, alias_map, dim_course
