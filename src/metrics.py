from dataclasses import dataclass
import pandas as pd

from src.readers import read_tests_excel, read_surveys_excel
from src.metrics import (
    prepare_tests_metrics,
    prepare_region_metrics,
    prepare_survey_metrics,
    combine_course_summary,
)


@dataclass
class PipelineResult:
    tests_raw: pd.DataFrame
    surveys_raw: pd.DataFrame
    course_summary: pd.DataFrame
    region_summary: pd.DataFrame
    survey_summary: pd.DataFrame


def run_pipeline(tests_file, surveys_file) -> PipelineResult:
    tests_df = read_tests_excel(tests_file) if tests_file is not None else pd.DataFrame()
    surveys_df = read_surveys_excel(surveys_file) if surveys_file is not None else pd.DataFrame()

    tests_summary = prepare_tests_metrics(tests_df) if not tests_df.empty else pd.DataFrame()
    region_summary = prepare_region_metrics(tests_df) if not tests_df.empty else pd.DataFrame()
    survey_summary = prepare_survey_metrics(surveys_df) if not surveys_df.empty else pd.DataFrame()

    course_summary = combine_course_summary(tests_summary, survey_summary) if not tests_summary.empty else pd.DataFrame()

    return PipelineResult(
        tests_raw=tests_df,
        surveys_raw=surveys_df,
        course_summary=course_summary,
        region_summary=region_summary,
        survey_summary=survey_summary,
    )
