import streamlit as st
import pandas as pd

st.set_page_config(page_title="Course Report Generator", layout="wide")

def check_pin() -> bool:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔒 Course Report Generator")
    st.caption("Build: v0.1.0")

    pin = st.text_input("Enter PIN", type="password")

    if st.button("Login"):
        if pin == st.secrets["APP_PIN"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Wrong PIN")

    return False

if not check_pin():
    st.stop()

st.title("Course Report Generator")

tests_file = st.file_uploader("Upload tests Excel", type=["xlsx", "xls"], key="tests")
survey_file = st.file_uploader("Upload surveys Excel", type=["xlsx", "xls"], key="surveys")

if tests_file is not None:
    tests_df = pd.read_excel(tests_file, engine="openpyxl")
    st.subheader("Tests preview")
    st.dataframe(tests_df.head(20), use_container_width=True)

if survey_file is not None:
    survey_df = pd.read_excel(survey_file, engine="openpyxl")
    st.subheader("Surveys preview")
    st.dataframe(survey_df.head(20), use_container_width=True)
