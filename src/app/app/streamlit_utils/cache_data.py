from utils.db_manager import POST_DB
import streamlit as st
from sqlalchemy import text
import pandas as pd
import logging

logger = logging.getLogger(__name__)


@st.cache_data
def get_post_db(list_id: list = ""):
    post_db = next(POST_DB.get_db())
    if list_id != "":
        list_id = 'AND p."id" NOT IN ('+",".join(list_id)+")"
    posts = post_db.execute(text(f"""
            select p."id" as raw_id, p."content", p.title, p.created_at, p.updated_at, 
            p.author_name, d."name" as departement_name,
            d."code" as number_departement
            from postgres.public.posts p
            left join postgres.public.departments d on d.code = p.department_code 
            left join postgres.public.user_profiles up on up.id = p.user_profile_id 
            where p.emitor_status = 'COMMENDATAIRE'
            {list_id}
        """))
    posts = pd.DataFrame(posts)
    posts["tasks"] = ''
    posts["status"] = 'FORMATTED'
    return posts