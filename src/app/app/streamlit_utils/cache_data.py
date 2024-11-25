from utils.db_manager import ANNUAIRE_DB, POST_DB
import streamlit as st
from sqlalchemy import text
import pandas as pd

# Doc: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data


@st.cache_data
def get_post_db():
    post_db = next(POST_DB.get_db())
    posts = post_db.execute(text("""
            select p."id", p."content", p.title, p.created_at, p.updated_at, 
            p.author_name, d."name" as departement_name, 
            d."number" as number_departement
            from postgres.public.posts p
            left join postgres.public.departments d on d.id = p.department_id 
            left join postgres.public.user_profiles up on up.id = p.user_profile_id 
            where p.emitor_status = 'COMMENDATAIRE'
        """))
    posts = pd.DataFrame(posts)
    posts["tasks"] = ''
    return posts


@st.cache_data
def get_formation_db():
    annuaire_db = next(ANNUAIRE_DB.get_db())
    formations = annuaire_db.execute(
        text("select * from partenaire.public.formations"))
    return pd.DataFrame(formations)
