from __future__ import annotations

import traceback
from typing import Any

import pandas as pd
import streamlit as st

from src.config import APP_TITLE, BUILD_LABEL
from src.pipeline import run_pipeline
from src.report_builder import build_course_placeholder_context


st.set_page_config(page_title=APP_TITLE, layout="wide")


def _show_dataframe(title: str, df: pd.DataFrame, use_container_width: bool = True) -> None:
    st.subheader(title)
    if df is None:
        st.info("DataFrame = None")
        return
    if df.empty:
        st.info("Нет данных")
        return
    st.dataframe(df, use_container_width=use_container_width)


def _safe_shape(df: pd.DataFrame | None) -> list[int] | None:
    if df is None:
        return None
    try:
        return list(df.shape)
    except Exception:
        return None


def _safe_columns(df: pd.DataFrame | None) -> list[str]:
    if df is None:
        return []
    try:
        return df.columns.tolist()
    except Exception:
        return []


def _json_ready(value: Any):
    if isinstance(value, dict):
        return {k: _json_ready(v) for k, v in value.items()}

    if isinstance(value, list):
        return [_json_ready(v) for v in value]

    if isinstance(value, tuple):
        return [_json_ready(v) for v in value]

    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            return str(value)

    return str(value)


def _placeholder_table(context: dict) -> pd.DataFrame:
    ordered = [
        "course_name",
        "all_courses_students_count_total",
        "all_courses_count_total",
        "all_courses_kz_gain_mean",
        "all_courses_largest_gain_course",
        "all_courses_largest_gain_score",
        "all_courses_smallest_gain_course",
        "all_courses_smallest_gain_score",
        "all_courses_avg_satisfaction_score_10",
        "figure_1_course_overview",
        "figure_2_region_gains",
        "figure_3_course_score_distribution",
        "figure_4_csat_content_by_region",
        "figure_5_csat_organization_by_region",
        "figure_6_csat_instructors_by_region",
    ]

    rows = [{"placeholder": key, "value": _json_ready(context.get(key))} for key in ordered]
    return pd.DataFrame(rows)


def _show_uploaded_file_info(tests_file, surveys_file) -> None:
    st.subheader("Информация о загруженных файлах")

    info_rows = [
        {
            "file_role": "Тесты.xlsx",
            "name": getattr(tests_file, "name", None),
            "type": getattr(tests_file, "type", None),
            "size_bytes": getattr(tests_file, "size", None),
            "is_uploaded": tests_file is not None,
        },
        {
            "file_role": "Анкеты.xlsx",
            "name": getattr(surveys_file, "name", None),
            "type": getattr(surveys_file, "type", None),
            "size_bytes": getattr(surveys_file, "size", None),
            "is_uploaded": surveys_file is not None,
        },
    ]
    st.dataframe(pd.DataFrame(info_rows), use_container_width=True)


def _build_debug_info(result) -> dict:
    return {
        "tests_raw_shape": _safe_shape(getattr(result, "tests_raw", None)),
        "surveys_raw_shape": _safe_shape(getattr(result, "surveys_raw", None)),
        "tests_matched_shape": _safe_shape(getattr(result, "tests_matched", None)),
        "surveys_matched_shape": _safe_shape(getattr(result, "surveys_matched", None)),
        "course_summary_shape": _safe_shape(getattr(result, "course_summary", None)),
        "region_summary_shape": _safe_shape(getattr(result, "region_summary", None)),
        "survey_summary_shape": _safe_shape(getattr(result, "survey_summary", None)),
        "dim_course_shape": _safe_shape(getattr(result, "dim_course", None)),
        "alias_map_shape": _safe_shape(getattr(result, "alias_map", None)),
        "available_courses_shape": _safe_shape(getattr(result, "available_courses", None)),
        "tests_raw_columns": _safe_columns(getattr(result, "tests_raw", None)),
        "surveys_raw_columns": _safe_columns(getattr(result, "surveys_raw", None)),
        "tests_matched_columns": _safe_columns(getattr(result, "tests_matched", None)),
        "surveys_matched_columns": _safe_columns(getattr(result, "surveys_matched", None)),
        "available_courses_columns": _safe_columns(getattr(result, "available_courses", None)),
        "unmatched_tests_count": 0 if getattr(result, "unmatched_tests_courses", None) is None else len(result.unmatched_tests_courses),
        "unmatched_surveys_count": 0 if getattr(result, "unmatched_surveys_courses", None) is None else len(result.unmatched_surveys_courses),
        "mapping_issues_count": 0 if getattr(result, "mapping_issues", None) is None else len(result.mapping_issues),
    }


def _check_required_result_fields(result) -> list[str]:
    missing = []

    required_attrs = [
        "tests_raw",
        "surveys_raw",
        "tests_matched",
        "surveys_matched",
        "course_summary",
        "region_summary",
        "survey_summary",
        "dim_course",
        "alias_map",
        "available_courses",
        "unmatched_tests_courses",
        "unmatched_surveys_courses",
        "mapping_issues",
    ]

    for attr in required_attrs:
        if not hasattr(result, attr):
            missing.append(attr)

    return missing


def _check_required_available_courses_columns(df: pd.DataFrame) -> list[str]:
    required_columns = ["course_id", "course_name_canonical", "course_label"]
    return [c for c in required_columns if c not in df.columns]


def main() -> None:
    st.title(APP_TITLE)
    st.caption(BUILD_LABEL)
    st.markdown(
        """
        На этом этапе приложение показывает значения плейсхолдеров прямо в Streamlit.

        Что сейчас включено:
        - выбор курса из сматченных курсов
        - расчёт общих текстовых плейсхолдеров
        - вывод значений в UI
        - расширенная диагностика ошибок и traceback прямо на странице
        """
    )

    with st.sidebar:
        st.header("Загрузка файлов")
        tests_file = st.file_uploader("Загрузите Тесты.xlsx", type=["xlsx"])
        surveys_file = st.file_uploader("Загрузите Анкеты.xlsx", type=["xlsx"])
        run_clicked = st.button("Запустить обработку", type="primary", use_container_width=True)

        st.divider()
        show_debug = st.checkbox("Показывать debug-информацию", value=True)

    if not run_clicked:
        st.info("Загрузите Excel-файлы и нажмите «Запустить обработку».")
        if show_debug:
            _show_uploaded_file_info(tests_file, surveys_file)
        return

    if tests_file is None and surveys_file is None:
        st.warning("Нужно загрузить хотя бы один файл.")
        st.stop()

    if show_debug:
        _show_uploaded_file_info(tests_file, surveys_file)

    try:
        with st.spinner("Обрабатываю данные..."):
            result = run_pipeline(tests_file=tests_file, surveys_file=surveys_file)

        st.success("Обработка завершена")
    except Exception as e:
        st.error(f"Ошибка во время run_pipeline: {type(e).__name__}: {e}")
        st.code(traceback.format_exc())
        st.stop()

    missing_result_fields = _check_required_result_fields(result)
    if missing_result_fields:
        st.error("PipelineResult не содержит обязательные поля.")
        st.write({"missing_fields": missing_result_fields})
        st.stop()

    if result.available_courses is None:
        st.error("result.available_courses = None")
        if show_debug:
            st.json(_json_ready(_build_debug_info(result)))
        st.stop()

    if not result.available_courses.empty:
        missing_cols = _check_required_available_courses_columns(result.available_courses)
        if missing_cols:
            st.error("В available_courses отсутствуют обязательные колонки.")
            st.write({"missing_columns": missing_cols})
            _show_dataframe("available_courses", result.available_courses)
            st.stop()

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Preview плейсхолдеров",
            "Служебные таблицы",
            "Unmatched / Mapping",
            "Debug",
        ]
    )

    with tab1:
        st.header("Preview плейсхолдеров")

        if result.available_courses.empty:
            st.warning("Нет сматченных курсов для выбора.")
            if show_debug:
                st.info("Проверь unmatched-курсы и mapping.")
        else:
            try:
                selected_label = st.selectbox(
                    "Выберите курс",
                    options=result.available_courses["course_label"].tolist(),
                    index=0,
                )

                selected_row = result.available_courses[result.available_courses["course_label"] == selected_label].iloc[0]
                selected_course_id = str(selected_row["course_id"])

                context = build_course_placeholder_context(result, selected_course_id)

                c1, c2, c3 = st.columns(3)
                c1.metric("Все слушатели", context.get("all_courses_students_count_total", 0))
                c2.metric("Все найденные курсы", context.get("all_courses_count_total", 0))
                c3.metric("Средний satisfaction / 10", context.get("all_courses_avg_satisfaction_score_10", 0.0))

                c4, c5, c6 = st.columns(3)
                c4.metric("Средний прирост знаний", context.get("all_courses_kz_gain_mean", 0.0))
                c5.metric("Макс. средний прирост", context.get("all_courses_largest_gain_score", 0.0))
                c6.metric("Мин. средний прирост", context.get("all_courses_smallest_gain_score", 0.0))

                st.subheader("Значения общих текстовых плейсхолдеров")
                st.dataframe(_placeholder_table(context), use_container_width=True)

                st.subheader("Context как JSON")
                try:
                    st.json(_json_ready(context))
                except Exception as e:
                    st.error(f"Ошибка при отображении context JSON: {type(e).__name__}: {e}")
                    st.code(traceback.format_exc())
                    st.write("Сырой context:")
                    st.write(context)

            except Exception as e:
                st.error(f"Ошибка в Preview плейсхолдеров: {type(e).__name__}: {e}")
                st.code(traceback.format_exc())

    with tab2:
        st.header("Служебные таблицы")

        try:
            _show_dataframe("Доступные курсы", result.available_courses)
            _show_dataframe("Course summary", result.course_summary)
            _show_dataframe("Survey summary", result.survey_summary)
            _show_dataframe("Tests matched", result.tests_matched)
            _show_dataframe("Surveys matched", result.surveys_matched)
        except Exception as e:
            st.error(f"Ошибка при показе служебных таблиц: {type(e).__name__}: {e}")
            st.code(traceback.format_exc())

    with tab3:
        st.header("Unmatched / Mapping")

        try:
            _show_dataframe("Unmatched из Тесты.xlsx", result.unmatched_tests_courses)
            _show_dataframe("Unmatched из Анкеты.xlsx", result.unmatched_surveys_courses)
            _show_dataframe("Проблемы mapping", result.mapping_issues)
            _show_dataframe("Dim course", result.dim_course)
        except Exception as e:
            st.error(f"Ошибка при показе unmatched/mapping: {type(e).__name__}: {e}")
            st.code(traceback.format_exc())

    with tab4:
        st.header("Debug")

        debug_info = _build_debug_info(result)
        st.subheader("Debug JSON")
        st.json(_json_ready(debug_info))

        if show_debug:
            st.subheader("Первые строки raw-данных")
            _show_dataframe("Tests raw", result.tests_raw.head(20) if result.tests_raw is not None else pd.DataFrame())
            _show_dataframe("Surveys raw", result.surveys_raw.head(20) if result.surveys_raw is not None else pd.DataFrame())

            st.subheader("Первые строки matched-данных")
            _show_dataframe("Tests matched head", result.tests_matched.head(20) if result.tests_matched is not None else pd.DataFrame())
            _show_dataframe("Surveys matched head", result.surveys_matched.head(20) if result.surveys_matched is not None else pd.DataFrame())


if __name__ == "__main__":
    main()
