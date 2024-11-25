from utils.db_vector import DB_VECTORIAL
import streamlit as st


@st.cache_resource
def get_vectorial_db():
    db_vectorial = DB_VECTORIAL.get_db()
    return db_vectorial
