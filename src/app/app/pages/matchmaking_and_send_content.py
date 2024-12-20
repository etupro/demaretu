import streamlit as st
from components.page_2.session_manager import SessionManager
from components.page_2.text import present_post_in_markdown, \
    presentation_content_mail, explination_wrtting_template, \
    format_mail

from streamlit_utils.cache_ressource import get_vectorial_db, get_drive
import logging

# Logger configuration
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(page_title="2 - Matchmaking de post-formation")

if "manager" not in st.session_state:
    posts_db = get_vectorial_db(
        index_col="id",
        env_name_index="INDEX_POST",
        other_cols=SessionManager.col_post_db
    )
    st.session_state.manager = SessionManager(
        data_post=posts_db.get_data()
    )
    formations_db = get_vectorial_db(
            index_col="id",
            env_name_index="INDEX_FORMATION",
            other_cols=SessionManager.col_formation_db
    )
    drive_client = get_drive()
    logger.info("Initialized session manager")


# --- Interface Logic ---
if st.session_state.manager.is_matching_step():
    for idx, post in enumerate(
        st.session_state.manager.get_post_in_dictionnary()
    ):
        if st.session_state.manager.exist_idx_in_storage(idx):
            proposal = st.session_state.manager\
                .get_recommandation_formation_from_in_vectorial_db(
                    post, formations_db
                )
            st.session_state.manager.add_post_to_storage(post, idx, proposal)
        else:
            proposal = st.session_state.manager.get_df_recommanded_of_post(idx)

        st.markdown(present_post_in_markdown(post=post))

        name_formations = st.multiselect(
            "Selectionne les formations les plus adaptées à la mission du post ci-dessus",
            options=proposal["nom_formation"]
        )
        st.session_state.manager.add_selected_formations_to_post(
            idx=idx,
            name_formations=name_formations
        )

        st.dataframe(proposal[proposal["nom_formation"].isin(name_formations)])

        with st.expander("Debuggage"):
            st.json(st.session_state.manager.get_post_data(idx=idx))

    if st.button(
            "Remplir les mails d'envoie ?",
            use_container_width=True,
            disabled=(not st.session_state.manager.all_post_have_formations())
            ):
        st.session_state.manager.change_phase()
        st.rerun()

else:
    all_proposals = st.session_state.manager.reverse_proposal(
        formations_db=formations_db
    )

    default_template, is_missing_template = st.session_state.manager.\
        get_templates_mail()

    if is_missing_template:
        st.warning("The template is missing, sorry you have to write your own mail template...")

    st.markdown(explination_wrtting_template)
    template = st.text_area("Email Template", value=default_template)

    all_mail_content = []

    for responsable, dico in all_proposals.items():
        st.markdown(presentation_content_mail(responsable=responsable))
        content = st.text_area(
            label=f"Contenu éditable pour la personne: {responsable}",
            value=format_mail(content=template, data=dico)
        )
        st.session_state.manager.add_mail_content(
            content=content,
            dico=dico,
            responsable=responsable
        )

    if st.button("Revenir à l'étape précédente ?"):
        st.session_state.manager.change_phase()
        st.rerun()

    if st.button("Envoyer sur le google sheet ?"):
        is_send = st.session_state.manager.sent_to_google_sheet(drive_client)
        if is_send:
            st.success("Les données ont bien été enregistrés.")
        else:
            st.error("Un problème est apparu consulter la liste des logs pour en savoir plus.")
