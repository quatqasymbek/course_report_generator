import streamlit as st
import pandas as pd

st.set_page_config(page_title="Protected App")

# ---- PIN AUTH ----
def check_pin():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔒 Protected App")

    pin_input = st.text_input("Enter PIN", type="password")

    if st.button("Login"):
        if pin_input == st.secrets["APP_PIN"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Wrong PIN")

    return False


if not check_pin():
    st.stop()

# ---- APP CONTENT ----

st.title("Minimal Streamlit App")

uploaded_file = st.file_uploader("Upload Excel", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("File loaded")
    st.dataframe(df.head())
