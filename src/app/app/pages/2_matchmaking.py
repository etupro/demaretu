import streamlit as st
from streamlit_utils.cache_ressource import get_vectorial_db, get_drive
from utils.matchmaking_func import reverse_proposal
import logging
from jinja2 import Template
import os
import pandas as pd

# Configuration du logger
logger = logging.getLogger(__name__)

# Get ressource
drive_client = get_drive()

posts_db = get_vectorial_db(
    env_name_index="INDEX_POST",
    index_col="id",
    other_cols=[
        'id', 'content', 'title',
        'updated_at', 'number_departement', 'tasks'
    ]
)

formations_db = get_vectorial_db(
    index_col="id",
    env_name_index="INDEX_FORMATION",
    other_cols=[
        "nom_formation", "domaine_formation",
        "niveau_formation", "presentation_formation", "contenu_formation",
        "url_fiche_formation", "mail_responsables", "universite",
        "ville", "url"
    ]
)

data_post = posts_db.get_data()


def change_phase():
    st.session_state.match_phase = False
    logger.debug("Turn off: match_phase")


def format_mail(content, data):
    template_str = Template(content)
    return template_str.render(data)


# Initialisation des états de session
if "match_phase" not in st.session_state:
    st.session_state.match_phase = True
    logger.debug("Initiate var: match_phase")


# Initialisation des états de session
if "data_storage" not in st.session_state:
    st.session_state.data_storage = {}
    logger.debug("Initiate var: data_storage")

# page
if st.session_state.match_phase and\
    ((len(st.session_state.data_storage.values()) == 0)\
    or any([
            len(post_tasks["proposal"]) == 0
            for post_tasks in st.session_state.data_storage.values()
        ])
    ):
    for idx, post in enumerate(data_post.to_dict(orient="records")):

        proposal = formations_db.get_data(
            settings_index={
                "size": 100,
                "_source": [
                    "nom_formation", "domaine_formation", "niveau_formation",
                    "mail_responsables", "ville"
                ],
                "query": {
                    "knn": {
                        "vector_index": {
                            "vector": post["vector_index"],
                            "k": 350
                        }
                    }
                }
            }
        )

        if idx not in st.session_state.data_storage.keys():
            st.session_state.data_storage[idx] = {
                "title": post["title"],
                "number_departement": post["number_departement"],
                "tasks": post["tasks"],
                "proposal": [],
                "df": proposal
            }
        title = post["title"]
        number_departement = post["number_departement"]
        tasks = post["tasks"]
        st.markdown(f"""--- 
## {title} - {number_departement}
{tasks}
        """)
        name_formations = st.multiselect(
            "Choissez les formations les plus adaptées",
            options=proposal.nom_formation
        )
        st.session_state.data_storage[idx]["proposal"] = name_formations
        # TODO: différiencier en fonction des villes
        # proposal["CP"] = proposal["ville"].map(get_postal_code)
        st.dataframe(proposal[proposal.nom_formation.isin(name_formations)])

        with st.expander("Debug section"):
            st.json(str(st.session_state.data_storage[idx]))

    if st.button(
        "Crée ou remplir le sheet de contact mail ?",
        use_container_width=True
    ):
        if all([
            len(post_tasks["proposal"]) > 0
            for post_tasks in st.session_state.data_storage.values()
        ]):
            change_phase()
        else:
            st.error("Attention toutes les tâches n'ont pas de formation associcées")
else:
    all_proposals = reverse_proposal(
        formations_db=formations_db,
        all_posts=st.session_state.data_storage
    )
    with open("/home/romain/Documents/association/demaretu/data/template_mails/4-12-2024-init.txt", mode="r") as f:
        doc = f.read()
    st.markdown("""
# Redaction des mails

Ajouter les variables suivantes à votre dispositions dans le contenu du templates de la manière suivantes:

    Bonjour {{ detail.responsable }}

    Blablabla
    {% for task in tasks %}
    - {{task.title}} pour la missions: {{task.tasks}}
    {% endfor %}
    blablabla

En accord avec les noms de variables ci dessous (comme tasks, ville, etc...) 
                
---               
""")
    st.json(list(all_proposals.values())[0])

    template = st.text_area("Templates mail", value=doc)

    all_mail_content = []
    for responsable, dico in all_proposals.items():
        st.markdown(f"""
---
                    
## Responsable {responsable}

Voici le contenu du mail:
""")
        content = st.text_area(
            label=f"Exemple de contenu modifiable pour {responsable}",
            value=format_mail(
                content=template,
                data=dico
            )
        )
        all_mail_content.append({
            "nom_responsable": responsable,
            "content": content
        })

    if st.button("Finito ?"):
        df = pd.DataFrame(all_mail_content)
        gs = drive_client.get_sheet(
                name=os.environ['NAME_SHEET_FORMATION'],
                id_folder=os.environ['ID_FOLDER_DEMAREDU']
        )
        sh1 = gs.sheet1
        file = sh1.get_values() + df.to_numpy().tolist()
        sh1.update(file, 'A2')
