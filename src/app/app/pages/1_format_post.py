import streamlit as st
from streamlit_utils.cache_data import get_post_db
from streamlit_utils.cache_ressource import get_vectorial_db
from components.page_1.session_manager import ManagerPage1
from components.page_1.st_component import modify_content_to_split_in_tasks
from components.page_1.text import explanation, describe_task
from hashlib import md5
import logging

# Logger configuration
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(page_title="Formattage des posts")

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
        missing_tasks, description_task = describe_task(post=post, idx=idx)
        st.markdown(description_task)
        if missing_tasks:
            st.error(f"Erreur dans les tâches du post {idx}.")
        if st.button(f"Reprendre le post {idx}"):
            st.session_state.manager.index_to_modify_post(
                    idx=idx
                )
    st.markdown("""---""")

    if st.button("Sauvegarder dans la BD ?", use_container_width=True):
        vectorial_db = get_vectorial_db(
            env_name_index="INDEX_POST",
            index_col="id",
            other_cols=[
                'id', 'content', 'title',
                'updated_at', 'number_departement',
                'tasks'
            ]
        )
        vectorial_db.create_index()
        ids = vectorial_db.get_all_id_data()
        # Prepare data
        docs = st.session_state.posts.copy()
        docs.tasks = docs.tasks.map(eval)
        docs = docs.explode("tasks")
        docs = docs[['id', 'content', 'title', 'updated_at',
                     'number_departement', 'tasks']]
        docs.id = (docs.id.map(str) + docs.tasks)\
            .map(lambda x: md5(x.encode()).hexdigest())
        # Send data
        df = vectorial_db.add_vector(df=docs, col="tasks")
        vectorial_db.send_data(df=docs)
        st.success("Succès pour l'enregistrement !")
