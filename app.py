import streamlit as st

from src.pipeline import run_pipeline

st.set_page_config(page_title="Генератор отчетов", layout="wide")

st.title("📊 Генератор отчетов по курсам ПК")
st.caption("Версия: v0.3")

st.divider()

tests_file = st.file_uploader("📥 Загрузите Excel с тестированием", type=["xlsx"], key="tests")
surveys_file = st.file_uploader("📥 Загрузите Excel с анкетированием", type=["xlsx"], key="surveys")

if st.button("Запустить обработку", use_container_width=True):
    if tests_file is None and surveys_file is None:
        st.warning("Загрузите хотя бы один файл.")
    else:
        with st.spinner("Выполняется обработка данных..."):
            result = run_pipeline(tests_file, surveys_file)

        st.success("Обработка завершена.")

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["Итог по курсам", "Итог по регионам", "Анкеты", "Сырые тесты", "Сырые анкеты"]
        )

        with tab1:
            st.subheader("Итоговые показатели по курсам")
            st.dataframe(result.course_summary, use_container_width=True)

        with tab2:
            st.subheader("Итоги по регионам")
            st.dataframe(result.region_summary, use_container_width=True)

        with tab3:
            st.subheader("Сводка по анкетам")
            st.dataframe(result.survey_summary, use_container_width=True)

        with tab4:
            st.subheader("Сырые данные тестов")
            st.dataframe(result.tests_raw.head(100), use_container_width=True)

        with tab5:
            st.subheader("Сырые данные анкет")
            st.dataframe(result.surveys_raw.head(100), use_container_width=True)
