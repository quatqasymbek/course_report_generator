from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import APP_TITLE, BUILD_LABEL
from src.pipeline import run_pipeline
from src.report_builder import build_course_placeholder_context


st.set_page_config(page_title=APP_TITLE, layout="wide")


def _show_dataframe(title: str, df: pd.DataFrame, use_container_width: bool = True) -> None:
    st.subheader(title)
    if df is None or df.empty:
        st.info("Нет данных")
        return
    st.dataframe(df, use_container_width=use_container_width)


def _json_ready(value):
    if isinstance(value, dict):
        return {k: _json_ready(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_ready(v) for v in value]
    if isinstance(value, tuple):
        return [_json_ready(v) for v in value]
    if pd.isna(value):
        return None
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            return str(value)
    return value


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


def main() -> None:
    st.title(APP_TITLE)
    st.caption(BUILD_LABEL)
    st.markdown(
        """
        На этом этапе приложение показывает значения плейсхолдеров прямо в Streamlit.

        Сейчас реализовано:
        - выбор курса из сматченных курсов
        - расчёт общих текстовых плейсхолдеров
        - показ значений в UI
        - плейсхолдеры для картинок пока выводятся как заглушки
        """
    )

    with st.sidebar:
        st.header("Загрузка файлов")
        tests_file = st.file_uploader("Загрузите Тесты.xlsx", type=["xlsx"])
        surveys_file = st.file_uploader("Загрузите Анкеты.xlsx", type=["xlsx"])
        run_clicked = st.button("Запустить обработку", type="primary", use_container_width=True)

    if not run_clicked:
        st.info("Загрузите Excel-файлы и нажмите «Запустить обработку».")
        return

    with st.spinner("Обрабатываю данные..."):
        result = run_pipeline(tests_file=tests_file, surveys_file=surveys_file)

    st.success("Обработка завершена")

    tab1, tab2, tab3 = st.tabs(
        [
            "Preview плейсхолдеров",
            "Служебные таблицы",
            "Unmatched / Mapping",
        ]
    )

    with tab1:
        st.header("Preview плейсхолдеров")

        if result.available_courses is None or result.available_courses.empty:
            st.warning("Нет сматченных курсов для выбора.")
        else:
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
            st.json(_json_ready(context))

    with tab2:
        st.header("Служебные таблицы")
        _show_dataframe("Доступные курсы", result.available_courses)
        _show_dataframe("Course summary", result.course_summary)
        _show_dataframe("Survey summary", result.survey_summary)

    with tab3:
        st.header("Unmatched / Mapping")
        _show_dataframe("Unmatched из Тесты.xlsx", result.unmatched_tests_courses)
        _show_dataframe("Unmatched из Анкеты.xlsx", result.unmatched_surveys_courses)
        _show_dataframe("Проблемы mapping", result.mapping_issues)


if __name__ == "__main__":
    main()
