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


def _build_debug_info(result) -> dict:
    return {
        "tests_raw_shape": list(result.tests_raw.shape),
        "surveys_raw_shape": list(result.surveys_raw.shape),
        "tests_matched_shape": list(result.tests_matched.shape),
        "surveys_matched_shape": list(result.surveys_matched.shape),
        "course_summary_shape": list(result.course_summary.shape),
        "region_summary_shape": list(result.region_summary.shape),
        "survey_summary_shape": list(result.survey_summary.shape),
        "dim_course_shape": list(result.dim_course.shape),
        "alias_map_shape": list(result.alias_map.shape),
        "tests_raw_columns": result.tests_raw.columns.tolist(),
        "surveys_raw_columns": result.surveys_raw.columns.tolist(),
        "tests_matched_columns": result.tests_matched.columns.tolist(),
        "surveys_matched_columns": result.surveys_matched.columns.tolist(),
        "unmatched_tests_count": 0 if result.unmatched_tests_courses is None else len(result.unmatched_tests_courses),
        "unmatched_surveys_count": 0 if result.unmatched_surveys_courses is None else len(result.unmatched_surveys_courses),
        "mapping_issues_count": 0 if result.mapping_issues is None else len(result.mapping_issues),
    }


def _show_fig(fig, empty_message: str = "Недостаточно данных для построения графика") -> None:
    if fig is None:
        st.info(empty_message)
        return
    st.pyplot(fig, clear_figure=True)


def main() -> None:
    st.title(APP_TITLE)
    st.caption(BUILD_LABEL)
    st.markdown(
        """
        Приложение считает витрину и placeholder-метрики для отчетов по курсам ПК.

        Важные правила:
        - в отчетную витрину попадают только курсы, сматченные через `course_mapping.xlsx`
        - `UstazPro` считается alias того же курса
        - fuzzy matching не используется
        - unmatched courses показываются отдельно и исключаются из отчетных метрик
        """
    )

    with st.sidebar:
        st.header("Загрузка файлов")
        tests_file = st.file_uploader("Загрузите tests.xlsx", type=["xlsx"])
        surveys_file = st.file_uploader("Загрузите surveys.xlsx", type=["xlsx"])

        run_clicked = st.button("Запустить обработку", type="primary", use_container_width=True)

    if not run_clicked:
        st.info("Загрузите Excel-файлы и нажмите «Запустить обработку».")
        return

    with st.spinner("Обрабатываю данные..."):
        result = run_pipeline(tests_file=tests_file, surveys_file=surveys_file)

    st.success("Обработка завершена")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "Сводка",
            "Курсы и метрики",
            "Графики",
            "Unmatched",
            "Mapping / Debug",
            "Placeholder context",
        ]
    )

    with tab1:
        st.header("Сводка по загрузке")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("tests_raw", len(result.tests_raw))
        c2.metric("surveys_raw", len(result.surveys_raw))
        c3.metric("tests_matched", len(result.tests_matched))
        c4.metric("surveys_matched", len(result.surveys_matched))

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Курсов в витрине", result.course_summary["course_id"].nunique() if not result.course_summary.empty else 0)
        c6.metric("Unmatched tests", len(result.unmatched_tests_courses))
        c7.metric("Unmatched surveys", len(result.unmatched_surveys_courses))
        c8.metric("Проблемы mapping", len(result.mapping_issues))

        _show_dataframe("Сводка по курсам", result.course_summary)
        _show_dataframe("Сводка по survey", result.survey_summary)

    course_options_df = result.dim_course.copy() if result.dim_course is not None else pd.DataFrame()
    if not course_options_df.empty:
        course_options_df = course_options_df[["course_id", "course_name_canonical"]].drop_duplicates()
        course_options_df["course_label"] = (
            course_options_df["course_name_canonical"].fillna("").astype(str)
            + " | "
            + course_options_df["course_id"].fillna("").astype(str)
        )
        course_labels = course_options_df["course_label"].tolist()
        selected_label = course_labels[0] if course_labels else None
    else:
        selected_label = None
        course_options_df = pd.DataFrame(columns=["course_id", "course_name_canonical", "course_label"])

    with tab2:
        st.header("Курсы и метрики")

        if course_options_df.empty:
            st.warning("Нет сматченных курсов для отображения")
        else:
            selected_label = st.selectbox(
                "Выберите курс",
                options=course_options_df["course_label"].tolist(),
                index=0,
            )

            selected_course_row = course_options_df[course_options_df["course_label"] == selected_label].iloc[0]
            selected_course_id = str(selected_course_row["course_id"])
            selected_course_name = str(selected_course_row["course_name_canonical"])

            st.subheader(f"Курс: {selected_course_name}")

            course_summary_row = result.course_summary[
                result.course_summary["course_id"].astype(str) == selected_course_id
            ].copy()

            course_region_summary = result.region_summary[
                result.region_summary["course_id"].astype(str) == selected_course_id
            ].copy()

            context = build_course_placeholder_context(result, selected_course_id)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Слушателей", context.get("course_students_count_kz", 0))
            m2.metric("Среднее входное", context.get("course_kz_diag_mean", 0.0))
            m3.metric("Среднее итоговое", context.get("course_kz_final_mean", 0.0))
            m4.metric("Прирост знаний", context.get("course_kz_gain_mean", 0.0))

            m5, m6, m7, m8 = st.columns(4)
            m5.metric("Content excellent %", context.get("course_csat_content_excellent_pct", 0.0))
            m6.metric("Organization excellent %", context.get("course_csat_organization_excellent_pct", 0.0))
            m7.metric("Min trainer mastery %", context.get("min_trainer_mastery_pct", 0.0))
            m8.metric("Avg trainer mastery %", context.get("avg_trainer_mastery_pct", 0.0))

            _show_dataframe("Сводка по выбранному курсу", course_summary_row)
            _show_dataframe("Региональная таблица по выбранному курсу", course_region_summary)

    with tab3:
        st.header("Графики")

        if course_options_df.empty:
            st.warning("Нет сматченных курсов для построения графиков")
        else:
            selected_label_charts = st.selectbox(
                "Выберите курс для графиков",
                options=course_options_df["course_label"].tolist(),
                index=0,
                key="charts_course_select",
            )

            selected_course_row = course_options_df[course_options_df["course_label"] == selected_label_charts].iloc[0]
            selected_course_id = str(selected_course_row["course_id"])
            selected_course_name = str(selected_course_row["course_name_canonical"])

            st.subheader(f"Графики по курсу: {selected_course_name}")

            fig1 = plot_course_overview(result.tests_matched, selected_course_id)
            st.markdown("**Figure 1. Общий overview по курсу**")
            _show_fig(fig1)

            fig2 = plot_region_gains(result.region_summary, selected_course_id)
            st.markdown("**Figure 2. Прирост знаний по регионам**")
            _show_fig(fig2)

            fig3 = plot_course_score_distribution(result.tests_matched, selected_course_id)
            st.markdown("**Figure 3. Распределение входных и итоговых баллов**")
            _show_fig(fig3)

            fig4 = plot_csat_content_by_region(result.surveys_matched, selected_course_id)
            st.markdown("**Figure 4. Content satisfaction by region**")
            _show_fig(fig4)

            fig5 = plot_csat_organization_by_region(result.surveys_matched, selected_course_id)
            st.markdown("**Figure 5. Organization satisfaction by region**")
            _show_fig(fig5)

            fig6 = plot_csat_instructors_by_region(result.surveys_matched, selected_course_id)
            st.markdown("**Figure 6. Instructor ratings by region**")
            _show_fig(fig6)

    with tab4:
        st.header("Unmatched courses")
        st.markdown("Эти курсы не попали в отчетную витрину, потому что не были сматчены через course_mapping.xlsx.")

        col1, col2 = st.columns(2)
        with col1:
            _show_dataframe("Unmatched из tests.xlsx", result.unmatched_tests_courses)
        with col2:
            _show_dataframe("Unmatched из surveys.xlsx", result.unmatched_surveys_courses)

    with tab5:
        st.header("Mapping / Debug")

        _show_dataframe("Проблемы course mapping", result.mapping_issues)
        _show_dataframe("Dim course", result.dim_course)
        _show_dataframe("Alias map", result.alias_map)

        debug_info = _build_debug_info(result)

        st.subheader("Debug JSON")
        st.json(_json_ready(debug_info))

    with tab6:
        st.header("Placeholder context")

        if course_options_df.empty:
            st.warning("Нет курсов для сборки placeholder context")
        else:
            selected_label_ctx = st.selectbox(
                "Выберите курс для placeholder context",
                options=course_options_df["course_label"].tolist(),
                index=0,
                key="context_course_select",
            )

            selected_course_row = course_options_df[course_options_df["course_label"] == selected_label_ctx].iloc[0]
            selected_course_id = str(selected_course_row["course_id"])

            context = build_course_placeholder_context(result, selected_course_id)

            st.subheader("Context как JSON")
            st.json(_json_ready(context))

            st.subheader("Context как таблица")
            context_df = pd.DataFrame(
                [{"placeholder": k, "value": _json_ready(v)} for k, v in context.items()]
            ).sort_values("placeholder")
            st.dataframe(context_df, use_container_width=True)

            st.download_button(
                label="Скачать context.json",
                data=json.dumps(_json_ready(context), ensure_ascii=False, indent=2),
                file_name=f"context_{selected_course_id}.json",
                mime="application/json",
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
