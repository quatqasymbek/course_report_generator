import streamlit as st
import pandas as pd

st.set_page_config(page_title="Minimal Streamlit App", layout="centered")

st.title("Minimal Streamlit App")
st.write("Это минимальное приложение для деплоя через GitHub на Streamlit Cloud.")

uploaded_file = st.file_uploader("Загрузите Excel-файл", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("Файл успешно прочитан.")
        st.write("Размер данных:", df.shape)
        st.dataframe(df.head(20), use_container_width=True)
    except Exception as e:
        st.error(f"Ошибка чтения файла: {e}")
else:
    st.info("Пока файл не загружен.")
