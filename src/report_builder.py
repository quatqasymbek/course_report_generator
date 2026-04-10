from __future__ import annotations

from src.metrics import (
    calculate_course_survey_metrics,
    calculate_course_test_metrics,
    calculate_global_survey_metrics,
    calculate_global_test_metrics,
    calculate_region_placeholder_metrics,
)


def build_course_placeholder_context(result, course_id: str) -> dict:
    global_test_metrics = calculate_global_test_metrics(result.tests_matched)
    global_survey_metrics = calculate_global_survey_metrics(result.surveys_matched)
    course_test_metrics = calculate_course_test_metrics(result.tests_matched, course_id)
    course_survey_metrics = calculate_course_survey_metrics(result.surveys_matched, course_id)
    region_metrics = calculate_region_placeholder_metrics(result.region_summary, course_id)

    context = {
        **global_test_metrics,
        **global_survey_metrics,
        **course_test_metrics,
        **course_survey_metrics,
        **region_metrics,
        "figure_1_course_overview": "",
        "figure_2_region_gains": "",
        "figure_3_course_score_distribution": "",
        "figure_4_csat_content_by_region": "",
        "figure_5_csat_organization_by_region": "",
        "figure_6_csat_instructors_by_region": "",
    }

    return context
