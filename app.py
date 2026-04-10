from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from src.charts import (
    plot_course_overview,
    plot_course_score_distribution,
    plot_csat_content_by_region,
    plot_csat_instructors_by_region,
    plot_csat_organization_by_region,
    plot_region_gains,
)
from src.config import APP_TITLE, BUILD_LABEL
from src.pipeline import PipelineResult, run_pipeline
from src.report_builder import build_course_placeholder_context


st.set_page_config(page_title=APP_TITLE, layout="wide")


def _render_top_metrics(result: PipelineResult) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Строк тестов", int(len(result.tests_raw)))
    col2.metric("Строк анкет", int(len(result.surveys_raw)))
    col3.metric("Курсов в справочнике", int(result.dim_course["course_id"].nunique()))
    col4.metric("Курсов в отчетной витрине", int(result.course_summary["course_id"].nunique()) if not result.course_summary.empty else 0)

    col5, col6, col7 = st.columns(3)
    col5.metric("Unmatched tests courses", int(len(result.unmatched_tests_courses)))
    col6.metric("Unmatched surveys courses", int(len(result.unmatched_surveys_courses)))
    col7.metric("Проблемы в course mapping", int(len(result.mapping_issues)))


def _render_data_tabs(result: PipelineResult) -> None:
    tabs = st.tabs(
        [
            "Итог по курсам",
            "Итог по регионам",
            "Анкеты по курсам",
            "Unmatched courses",
            "Mapping issues",
            "Сырые тесты",
            "Сырые анкеты",
        ]
    )

    with tabs[0]:
        st.dataframe(result.course_summary, use_container_width=True)

    with tabs[1]:
        st.dataframe(result.region_summary, use_container_width=True)

    with tabs[2]:
        st.dataframe(result.survey_summary, use_container_width=True)

    with tabs[3]:
        st.subheader("Курсы, которых нет в course_mapping.xlsx")
        left, right = st.columns(2)
        with left:
            st.caption("Tests")
            st.dataframe(result.unmatched_tests_courses, use_container_width=True)
        with right:
            st.caption("Surveys")
            st.dataframe(result.unmatched_surveys_courses, use_container_width=True)

    with tabs[4]:
        st.dataframe(result.mapping_issues, use_container_width=True)

    with tabs[5]:
        st.dataframe(result.tests_matched.head(200), use_container_width=True)

    with tabs[6]:
        st.dataframe(result.surveys_matched.head(200), use_container_width=True)


def _render_course_section(result: PipelineResult) -> None:
    st.subheader("Метрики и placeholders по курсу")

    if result.course_summary.empty:
        st.warning("Нет ни одного сопоставленного курса. Проверьте course_mapping.xlsx.")
        return

    course_options = result.course_summary[["course_id", "course_name_canonical"]].drop_duplicates()
    label_to_id = {
        f'{row["course_name_canonical"]} ({row["course_id"]})': row["course_id"]
        for _, row in course_options.iterrows()
    }

    selected_label = st.selectbox("Выберите курс", list(label_to_id.keys()))
    selected_course_id = label_to_id[selected_label]

    context = build_course_placeholder_context(result=result, course_id=selected_course_id)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Слушателей по курсу", context["course_students_count_kz"])
    k2.metric("Средний входной", context["course_kz_diag_mean"])
    k3.metric("Средний итоговый", context["course_kz_final_mean"])
    k4.metric("Прирост знаний", context["course_kz_gain_mean"])

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Средняя удовлетворенность (10-балльная)", context["all_courses_avg_satisfaction_score_10"])
    s2.metric("Content excellent %", context["course_csat_content_excellent_pct"])
    s3.metric("Organization excellent %", context["course_csat_organization_excellent_pct"])
    s4.metric("Средняя доля excellent по тренерам", context["avg_trainer_mastery_pct"])

    with st.expander("Полный placeholder context", expanded=False):
        st.json(context)

    st.subheader("Таблица регионов")
    region_df = result.region_summary[result.region_summary["course_id"] == selected_course_id].copy()
    st.dataframe(region_df, use_container_width=True)

    st.subheader("Графики")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig = plot_course_overview(result.tests_matched, selected_course_id)
        if fig is not None:
            st.pyplot(fig)
        fig = plot_region_gains(result.region_summary, selected_course_id)
        if fig is not None:
            st.pyplot(fig)
        fig = plot_course_score_distribution(result.tests_matched, selected_course_id)
        if fig is not None:
            st.pyplot(fig)

    with chart_col2:
        fig = plot_csat_content_by_region(result.surveys_matched, selected_course_id)
        if fig is not None:
            st.pyplot(fig)
        fig = plot_csat_organization_by_region(result.surveys_matched, selected_course_id)
        if fig is not None:
            st.pyplot(fig)
        fig = plot_csat_instructors_by_region(result.surveys_matched, selected_course_id)
        if fig is not None:
            st.pyplot(fig)

    with st.expander("Context JSON (copy/paste for debugging)"):
        st.code(json.dumps(context, ensure_ascii=False, indent=2), language="json")


def main() -> None:
    st.title(APP_TITLE)
    st.caption(BUILD_LABEL)
    st.divider()

    st.info("В отчетную витрину и будущие Word-отчеты включаются только те курсы, которые сопоставлены со справочником metadata/course_mapping.xlsx.")

    tests_file = st.file_uploader("📥 Загрузите Excel с тестированием", type=["xlsx", "xls"], key="tests")
    surveys_file = st.file_uploader("📥 Загрузите Excel с анкетированием", type=["xlsx", "xls"], key="surveys")

    if st.button("Запустить обработку", type="primary", use_container_width=True):
        if tests_file is None and surveys_file is None:
            st.warning("Загрузите хотя бы один файл.")
        else:
            with st.spinner("Обработка данных..."):
                result = run_pipeline(tests_file=tests_file, surveys_file=surveys_file)
            st.session_state["pipeline_result"] = result
            st.success("Обработка завершена.")

    result: PipelineResult | None = st.session_state.get("pipeline_result")
    if result is not None:
        _render_top_metrics(result)
        st.divider()
        _render_data_tabs(result)
        st.divider()
        _render_course_section(result)


if __name__ == "__main__":
    main()
