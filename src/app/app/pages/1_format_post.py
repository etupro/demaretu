import streamlit as st
from streamlit_utils.cache_data import get_post_db
from streamlit_utils.cache_ressource import get_vectorial_db
import logging
from hashlib import md5

# Logger configuration
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(page_title="Formattage des posts")

# Initialize session states
if "index_post" not in st.session_state:
    st.session_state.index_post = 0
    logger.debug("Initialized index_post to 0")

if "only_one_modify" not in st.session_state:
    st.session_state.only_one_modify = False
    logger.debug("Initialized only_one_modify to False")

if "posts" not in st.session_state:
    try:
        st.session_state.posts = get_post_db()
        logger.info("Loaded posts from the database.")
    except Exception as e:
        logger.error(f"Error loading posts: {e}")
        st.error(
            "Une erreur est survenue lors du chargement des données. Veuillez réessayer."
        )
        st.stop()

# Utility functions


def next_index():
    """
    Move to the next index. If only_one_modify is enabled, skip to the end of the list.
    """
    if st.session_state.only_one_modify:
        st.session_state.index_post = len(st.session_state.posts)
        logger.info("Mode 'only_one_modify' enabled: index set to the end.")
    else:
        st.session_state.index_post += 1
        logger.debug(f"Advanced index to {st.session_state.index_post}.")


def save_post(content: str, tasks: list):
    """
    Save the modifications of a post.

    Args:
        content (str): Post description.
        tasks (list): List of associated tasks.
    """
    try:
        st.session_state.posts.loc[st.session_state.index_post, "content"] = content
        st.session_state.posts.loc[st.session_state.index_post, "tasks"] = str(tasks)
        st.success("Changes have been saved.")
        logger.info(f"Post {st.session_state.index_post} successfully saved.")
    except Exception as e:
        logger.error(f"Error saving post {st.session_state.index_post}: {e}")
        st.error("Erreur lors de la sauvegarde. Veuillez réessayer.")


def modify_post(idx):
    """
    Enter edit mode for a specific post.

    Args:
        idx (int): Index of the post to modify.
    """
    st.session_state.index_post = idx
    st.session_state.only_one_modify = True
    logger.info(f"Edit mode activated for post at index {idx}.")

# #### #### #### #### #### #### #### Page #### #### #### #### #### ####

if len(st.session_state.posts) > st.session_state.index_post:
    have_to_expanded = (not st.session_state.only_one_modify) and (
        st.session_state.index_post == 0)

    with st.expander("Explanation", expanded=have_to_expanded):
        st.markdown("""
        # Formattage des posts
        ## Description
        Pour permettre à l'algorithme de retrouver automatiquement les tâches, il faut séparer les tâches par des listes à puces de cette manière :
        - Activité entreprise 1
        - Activité entreprise 2
        
        Ces besoins :
        * Mission 1
        * Mission 2
        
        **Exemple acceptable** :
        
Une entreprise fait :
        - De la mise en rayon
        - Trie les articles
        Elle souhaite engager des étudiants pour :
        * Communication
        * Création d'un site web

        **Attention** : Utilisez '-' pour les puces dans la description et '*' pour les tâches.
        """)

    post = st.session_state.posts.iloc[st.session_state.index_post]

    try:
        st.markdown(
            f"### {st.session_state.index_post}/ **Nom de l'organisation:** {post.title}")

        if isinstance(post.tasks, str) and len(post.tasks) == 0:
            tasks_content = post.tasks
        elif isinstance(eval(post.tasks), list):
            tasks_content = "*" + "*".join(eval(post.tasks))
        else:
            raise ValueError(f"Unexpected type for post.tasks: {type(post.tasks)}")

        content = st.text_area(
            label="Description",
            value=post.content + tasks_content
        )
        list_content = content.split("*")
        desc = list_content[0]
        tasks = list_content[1:]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### Description du post :\n{desc}")
        with col2:
            for idx, t in enumerate(tasks):
                task = t.strip().replace("-", "").replace("*", "")
                st.markdown(f"- **Mission {idx + 1}** : {task}")

        if st.button(label="Suivant", use_container_width=True):
            save_post(content=desc, tasks=tasks)
            next_index()

    except Exception as e:
        logger.error(
            f"Error displaying or modifying post: {e}"
        )
        st.error("Attention il faut revoir le post")
else:
    st.markdown("## Récapitulatif de fin !")
    docs = st.session_state.posts.copy()
    docs.tasks = docs.tasks.map(eval)
    docs = docs.explode("tasks")
    st.dataframe(docs[docs.columns[::-1]])

    for idx in st.session_state.posts.index:
        post = st.session_state.posts.iloc[idx]
        st.markdown(f"""
--- \n
### **Nom de l'organisation :** \n {post.title} \n
#### Description du post :  \n  {post.content} \n
#### Les missions :
        """)
        try:
            tasks = eval(post.tasks)
            if len(tasks):
                for task in tasks:
                    st.markdown(f"- {task}")
            else:
                st.error("Il n'y a pas de tâche ici !")
        except Exception as e:
            logger.error(
                f"Erreur lors de l'évaluation des tâches pour le post {idx} : {e}")
            st.error(f"Erreur dans les tâches du post {idx}.")

        if st.button(f"Reprendre le post {idx}"):
            modify_post(idx)
    st.markdown("""---""")
    if st.button("Sauvegarder dans la BD?", use_container_width=True):
        vectorial_db = get_vectorial_db(
            env_name_index="INDEX_POST",
            index_col="id",
            other_cols=['id', 'content', 'title', 'updated_at', 'number_departement', 'tasks']
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
