from __future__ import annotations

import traceback

import streamlit as st

from src.config import APP_TITLE, BUILD_LABEL
from src.pipeline import run_pipeline
from src.report_builder import build_course_placeholder_context


st.set_page_config(page_title=APP_TITLE, layout="wide")


def main() -> None:
    st.title(APP_TITLE)
    st.caption(BUILD_LABEL)
    st.write("Минимальный диагностический режим")

    tests_file = st.file_uploader("Загрузите Тесты.xlsx", type=["xlsx"])
    surveys_file = st.file_uploader("Загрузите Анкеты.xlsx", type=["xlsx"])

    if st.button("Запустить"):
        if tests_file is None and surveys_file is None:
            st.warning("Нужно загрузить хотя бы один файл.")
            st.stop()

        st.write("Файлы загружены:")
        st.write(
            {
                "tests_file": None if tests_file is None else tests_file.name,
                "surveys_file": None if surveys_file is None else surveys_file.name,
            }
        )

        try:
            st.write("Шаг 1: run_pipeline()")
            result = run_pipeline(tests_file=tests_file, surveys_file=surveys_file)
            st.success("run_pipeline() выполнен")

            st.write("Форма данных после pipeline:")
            st.write(
                {
                    "tests_raw_shape": None if result.tests_raw is None else result.tests_raw.shape,
                    "surveys_raw_shape": None if result.surveys_raw is None else result.surveys_raw.shape,
                    "tests_matched_shape": None if result.tests_matched is None else result.tests_matched.shape,
                    "surveys_matched_shape": None if result.surveys_matched is None else result.surveys_matched.shape,
                    "available_courses_shape": None if result.available_courses is None else result.available_courses.shape,
                }
            )

            if result.available_courses is None:
                st.error("result.available_courses = None")
                st.stop()

            st.write("Первые строки available_courses:")
            st.dataframe(result.available_courses.head(20), width="stretch")

            if result.available_courses.empty:
                st.warning("available_courses пустой")
                st.write("Unmatched tests:")
                st.dataframe(result.unmatched_tests_courses.head(50), width="stretch")
                st.write("Unmatched surveys:")
                st.dataframe(result.unmatched_surveys_courses.head(50), width="stretch")
                st.stop()

            if "course_label" not in result.available_courses.columns:
                st.error("В available_courses нет колонки course_label")
                st.write(result.available_courses.columns.tolist())
                st.stop()

            st.write("Шаг 2: выбор курса")
            selected_label = st.selectbox(
                "Выберите курс",
                options=result.available_courses["course_label"].tolist(),
                index=0,
            )

            selected_row = result.available_courses[result.available_courses["course_label"] == selected_label].iloc[0]
            selected_course_id = str(selected_row["course_id"])

            st.write(
                {
                    "selected_label": selected_label,
                    "selected_course_id": selected_course_id,
                }
            )

            st.write("Шаг 3: build_course_placeholder_context()")
            context = build_course_placeholder_context(result, selected_course_id)
            st.success("context собран")

            st.write("Ключи context:")
            st.write(sorted(list(context.keys())))

            st.write("Значения основных плейсхолдеров:")
            st.write(
                {
                    "course_name": context.get("course_name"),
                    "all_courses_students_count_total": context.get("all_courses_students_count_total"),
                    "all_courses_count_total": context.get("all_courses_count_total"),
                    "all_courses_kz_gain_mean": context.get("all_courses_kz_gain_mean"),
                    "all_courses_largest_gain_course": context.get("all_courses_largest_gain_course"),
                    "all_courses_largest_gain_score": context.get("all_courses_largest_gain_score"),
                    "all_courses_smallest_gain_course": context.get("all_courses_smallest_gain_course"),
                    "all_courses_smallest_gain_score": context.get("all_courses_smallest_gain_score"),
                    "all_courses_avg_satisfaction_score_10": context.get("all_courses_avg_satisfaction_score_10"),
                }
            )

            st.write("Полный context:")
            st.write(context)

        except Exception as e:
            st.error(f"Ошибка: {type(e).__name__}: {e}")
            st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
