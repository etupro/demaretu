import streamlit as st
from streamlit_utils.cache_ressource import get_vectorial_db, get_drive
from utils.matchmaking_func import reverse_proposal
import logging
from jinja2 import Template
import os
import pandas as pd

# Logger configuration
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(page_title="Matchmaking de post-formation")

# Constants
MATCH_PHASE_KEY = "match_phase"
DATA_STORAGE_KEY = "data_storage"
COL_DB = [
    "nom_formation",  "niveau", "domaine", "spécialisation",
    "mail_responsables", "mails", "universite",
    "cp", "url"
]

# Resource initialization
drive_client = get_drive()

# Initialize databases for posts and formations
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
    other_cols=COL_DB
)

# Retrieve post data
data_post = posts_db.get_data()


# --- Utility Functions ---
def change_phase():
    """
    Switches the application phase from matching to the next step.
    Updates the session state to signal the matching phase is completed.
    """
    st.session_state[MATCH_PHASE_KEY] = False
    logger.debug("Turned off: match_phase")


def format_mail(content: str, data: dict):
    """
    Formats email content using a Jinja2 template.

    Parameters:
    - content (str): Template string for the email.
    - data (dict): Dictionary containing data for populating the template.

    Returns:
    - str: Formatted email content, or an error message if formatting fails.
    """
    try:
        return Template(content).render(data)
    except Exception as e:
        logger.error(f"Error formatting email: {e}")
        st.error("An error occurred while formatting the email.")
        return ""


def initialize_session_state(key: str, default_value):
    """
    Initializes a key in `st.session_state` with a default value, if not already set.

    Parameters:
    - key (str): The key to initialize in the session state.
    - default_value: The default value to assign if the key does not exist.
    """
    if key not in st.session_state:
        st.session_state[key] = default_value
        logger.debug(f"Initialized session state key: {key} with value: {default_value}")


# --- Initialization ---
initialize_session_state(MATCH_PHASE_KEY, True)
initialize_session_state(DATA_STORAGE_KEY, {})


# --- Interface Logic ---
if st.session_state[MATCH_PHASE_KEY] and (
    not st.session_state[DATA_STORAGE_KEY] or
    any(len(post_tasks["proposal"]) == 0 for post_tasks in st.session_state[DATA_STORAGE_KEY].values())
):

    for idx, post in enumerate(data_post.to_dict(orient="records")):
        ## TODO: Récuperer le cp du post
        proposal = formations_db.get_data(
            settings_index={
                "size": 100,
                "_source": COL_DB,
                "query":  {
                    "bool": {
                        "must": [
                            {"prefix": {"cp": {"value": post["number_departement"]}}},
                            {"knn": {
                                    "vector_index": {
                                        "vector": post["vector_index"],
                                        "k": 350
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        )

        if idx not in st.session_state[DATA_STORAGE_KEY]:
            st.session_state[DATA_STORAGE_KEY][idx] = {
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
            "Select the most suitable formations",
            options=proposal["nom_formation"]
        )
        st.session_state[DATA_STORAGE_KEY][idx]["proposal"] = name_formations

        st.dataframe(proposal[proposal["nom_formation"].isin(name_formations)])

        with st.expander("Debug section"):
            st.json(str(st.session_state[DATA_STORAGE_KEY][idx]))

    if st.button("Create or fill the contact email sheet?", use_container_width=True):
        if all(len(post_tasks["proposal"]) > 0 for post_tasks in st.session_state[DATA_STORAGE_KEY].values()):
            change_phase()
        else:
            st.error("All tasks must have an associated formation.")
else:
    all_proposals = reverse_proposal(
        formations_db=formations_db,
        all_posts=st.session_state[DATA_STORAGE_KEY]
    )

    try:
        TEMPLATE_MAIL_PATH = os.environ["PATH_FILE_TEMPLATE"]
        with open(TEMPLATE_MAIL_PATH, mode="r") as f:
            default_template = f.read()
    except FileNotFoundError:
        st.error(f"Email template not found: {TEMPLATE_MAIL_PATH}")
        default_template = ""

    st.markdown("""
# Rédaction des mails

Ajoutez les variables suivantes dans votre contenu de template :

    Bonjour {{ detail.responsable }}

    Blablabla
    {% for task in tasks %}
    - {{task.title}} pour la mission : {{task.tasks}}
    {% endfor %}
    Blablabla
---               
    """)

    template = st.text_area("Email Template", value=default_template)

    all_mail_content = []
    for responsable, dico in all_proposals.items():
        mail = dico["detail"]["mail"]
        st.markdown(f"""
---
## Responsable {responsable}

Voici le contenu du mail :
        """)
        content = st.text_area(
            label=f"Editable content example for {responsable}",
            value=format_mail(content=template, data=dico)
        )
        all_mail_content.append({
            "responsible_name": responsable,
            "mail": mail,
            "content": content,
            "statut": "A envoyer"
        })

    if st.button("Finalize?"):
        df = pd.DataFrame(all_mail_content)

        try:
            gs = drive_client.get_sheet(
                name=os.environ['NAME_SHEET_FORMATION'],
                id_folder=os.environ['ID_FOLDER_DEMAREDU']
            )
            sh1 = gs.sheet1
            file = sh1.get_values() + df.to_numpy().tolist()
            sh1.update(file, 'A1')
            st.success("Data has been successfully updated.")
        except Exception as e:
            logger.error(f"Error writing to Google Sheets: {e}")
            st.error("An error occurred while writing to Google Sheets.")
