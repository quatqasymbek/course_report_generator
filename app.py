import streamlit as st
import pandas as pd

st.set_page_config(page_title="Course Report Generator", layout="wide")

st.title("Course Report Generator")
st.caption("Build: v0.1.0")

tests_file = st.file_uploader("Upload tests Excel", type=["xlsx", "xls"], key="tests")
survey_file = st.file_uploader("Upload surveys Excel", type=["xlsx", "xls"], key="surveys")

col1, col2 = st.columns(2)

with col1:
    if tests_file is not None:
        try:
            tests_df = pd.read_excel(tests_file, engine="openpyxl")
            st.subheader("Tests preview")
            st.write(f"Rows: {len(tests_df)}, Columns: {len(tests_df.columns)}")
            st.dataframe(tests_df.head(20), use_container_width=True)
        except Exception as e:
            st.error(f"Failed to read tests file: {e}")

with col2:
    if survey_file is not None:
        try:
            survey_df = pd.read_excel(survey_file, engine="openpyxl")
            st.subheader("Surveys preview")
            st.write(f"Rows: {len(survey_df)}, Columns: {len(survey_df.columns)}")
            st.dataframe(survey_df.head(20), use_container_width=True)
        except Exception as e:
            st.error(f"Failed to read surveys file: {e}")
