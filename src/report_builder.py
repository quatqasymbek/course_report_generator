from __future__ import annotations

from src.metrics import (
    calculate_course_name_placeholder,
    calculate_course_survey_metrics,
    calculate_course_test_metrics,
    calculate_global_text_placeholders,
    calculate_region_placeholder_metrics,
)


def build_course_placeholder_context(result, course_id: str) -> dict:
    global_text_metrics = calculate_global_text_placeholders(
        result.tests_matched,
        result.surveys_matched,
    )
    course_name_metric = calculate_course_name_placeholder(result.dim_course, course_id)
    course_test_metrics = calculate_course_test_metrics(result.tests_matched, course_id)
    course_survey_metrics = calculate_course_survey_metrics(result.surveys_matched, course_id)
    region_metrics = calculate_region_placeholder_metrics(result.region_summary, course_id)

    context = {
        **global_text_metrics,
        **course_name_metric,
        **course_test_metrics,
        **course_survey_metrics,
        **region_metrics,
        "figure_1_course_overview": "[заглушка]",
        "figure_2_region_gains": "[заглушка]",
        "figure_3_course_score_distribution": "[заглушка]",
        "figure_4_csat_content_by_region": "[заглушка]",
        "figure_5_csat_organization_by_region": "[заглушка]",
        "figure_6_csat_instructors_by_region": "[заглушка]",
    }

    return context
