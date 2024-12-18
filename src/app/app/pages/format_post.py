import streamlit as st
from streamlit_utils.cache_data import get_post_db

from components.page_1.session_manager import ManagerPage1
from components.page_1.st_component import modify_content_to_split_in_tasks
from components.page_1.text import explanation, describe_task

import logging

# Logger configuration
logger = logging.getLogger(__name__)

# Initialize session states
if "manager" not in st.session_state:
    try:
        st.session_state.manager = ManagerPage1(posts=get_post_db())
        logger.info("Loaded posts from the database.")
    except Exception as e:
        logger.error(f"Error loading posts: {e}")
        st.error(
            "Une erreur est survenue lors du chargement des données. Veuillez réessayer."
        )
        st.stop()


# #### #### #### #### #### #### #### Page #### #### #### #### #### ####
if st.session_state.manager.is_finish_posts():

    with st.expander(
        "Explanation",
        expanded=st.session_state.manager.have_to_expanded()
            ):
        st.markdown(explanation)

    try:
        desc, tasks = modify_content_to_split_in_tasks()
        if st.button(
            label="Next",
            use_container_width=True,
            disabled=(len(tasks) == 0)
        ):
            if st.session_state.manager.save_post(
                content=desc, tasks=tasks
            ):
                st.success("Post sauvegardé !")
            else:
                st.error("Post non sauvegardé")
            st.session_state.manager.next_index()
            st.rerun()

    except Exception as e:
        logger.error(
            f"Error displaying or modifying post: {e}"
        )
        st.error("Attention il faut revoir le post")
else:
    st.markdown("## Récapitulatif de fin !")
    docs = st.session_state.manager.get_post_by_tasks()
    st.dataframe(docs[docs.columns[::-1]])

    # Describe by post
    posts = st.session_state.manager.get_posts()
    for idx in posts.index:
        post = posts.iloc[idx]
        is_missing_tasks, description_task = describe_task(post=post, idx=idx)
        st.markdown(description_task)
        if is_missing_tasks:
            st.error(f"Il n'y pas de tâches présentes pour le post {idx}.")
        if st.button(f"Reprendre le post {idx}"):
            st.session_state.manager.index_to_modify_post(
                    idx=idx
                )
            st.rerun()
    st.markdown("""---""")

    if st.button("Sauvegarder dans la BD ?", use_container_width=True):
        st.session_state.manager.send_to_db(
            cols=['id', 'content', 'title', 'updated_at',
                  'number_departement', 'tasks'])
        st.success("L'enregistrement a été fait avec succès !")
