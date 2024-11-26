import streamlit as st
from streamlit_utils.cache_data import get_post_db
from streamlit_utils.cache_ressource import get_vectorial_db
import logging
import os
from hashlib import md5

# Configuration du logger
logger = logging.getLogger(__name__)

# Configuration de la page
st.set_page_config(page_title="Formattage des posts")

# Initialisation des états de session
if "index_post" not in st.session_state:
    st.session_state.index_post = 0
    logger.debug("Initialisation de index_post à 0")

if "only_one_modify" not in st.session_state:
    st.session_state.only_one_modify = False
    logger.debug("Initialisation de only_one_modify à False")

if "posts" not in st.session_state:
    try:
        st.session_state.posts = get_post_db()
        logger.info("Chargement des posts depuis la base de données.")
    except Exception as e:
        logger.error(f"Erreur lors du chargement des posts : {e}")
        st.error(
            "Une erreur est survenue lors du chargement des données. Veuillez réessayer.")
        st.stop()

# Fonctions utilitaires


def next_index():
    """
    Passe à l'index suivant. Si only_one_modify est activé, passe à la fin de la liste.
    """
    if st.session_state.only_one_modify:
        st.session_state.index_post = len(st.session_state.posts)
        logger.info("Mode 'only_one_modify' activé : index réglé à la fin.")
    else:
        st.session_state.index_post += 1
        logger.debug(f"Index avancé à {st.session_state.index_post}.")


def save_post(content: str, tasks: list):
    """
    Sauvegarde les modifications d'un post.

    Args:
        content (str): Description du post.
        tasks (list): Liste des tâches associées.
    """
    try:
        st.session_state.posts.loc[st.session_state.index_post,
                                   "content"] = content
        st.session_state.posts.loc[st.session_state.index_post, "tasks"] = str(
            tasks)
        st.success("Les modifications ont été sauvegardées.")
        logger.info(
            f"Post {st.session_state.index_post} sauvegardé avec succès.")
    except Exception as e:
        logger.error(
            f"Erreur lors de la sauvegarde du post {st.session_state.index_post} : {e}")
        st.error("Erreur lors de la sauvegarde. Veuillez réessayer.")


def modify_post(idx):
    """
    Passe en mode modification d'un post spécifique.

    Args:
        idx (int): Index du post à modifier.
    """
    st.session_state.index_post = idx
    st.session_state.only_one_modify = True
    logger.info(f"Modification du post à l'index {idx} activée.")

# #### #### #### #### #### #### #### Page #### #### #### #### #### ####


if len(st.session_state.posts) > st.session_state.index_post:
    have_to_expanded = (not st.session_state.only_one_modify) and (
        st.session_state.index_post == 0)

    with st.expander("Explication", expanded=have_to_expanded):
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
        ```
        Une entreprise fait :
        - De la mise en rayon
        - Trie les articles
        Elle souhaite engager des étudiants pour :
        * Communication
        * Création d'un site web
        ```
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
            raise ValueError(
                f"Type inattendu pour post.tasks : {type(post.tasks)}")

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
            f"Erreur lors de l'affichage ou de la modification du post : {e}")
        st.error("Une erreur est survenue. Veuillez vérifier le format du post.")
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
    if st.button("Sauvez dans la bd ?", use_container_width=True):
        vectorial_db = get_vectorial_db()
        query = {
            "_source": "id",
            'query': {
                'match_all': {}
            }
        }
        response = vectorial_db.search(
            body=query,
            index='post-decomposed'
        )
        all_ids = [h['_source']["id"] for h in response["hits"]["hits"]]

        docs = st.session_state.posts.copy()
        docs.tasks = docs.tasks.map(eval)
        docs = docs.explode("tasks")
        docs = docs[['id', 'content', 'title', 'updated_at',
                     'number_departement', 'tasks']].to_dict(orient="records")
        # TODO récupère les id du sheet
        for d in docs:
            try:
                id_name = str(d["id"]) + d["tasks"]
                d["id"] = md5(id_name.encode()).hexdigest()
                if not d["id"] in all_ids:
                    vectorial_db.index(
                        index=os.environ["INDEX_POST"],
                        body=d
                    )
                else:
                    logger.info("Id existe déjà: " + str(d["id"]))
            except Exception:
                st.error(
                    "Attention la taches suivantes ne s'est pas intégrer:" + str(d))
        st.success("Succed to upload in db !")
