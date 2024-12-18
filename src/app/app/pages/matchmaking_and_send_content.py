import streamlit as st
from components.page_2.session_manager import SessionManager
from components.page_2.text import present_post_in_markdown, \
    presentation_content_mail, explination_wrtting_template, \
    format_mail
import logging

# Logger configuration
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(page_title="2 - Matchmaking de post-formation")

if "manager" not in st.session_state:
    # Initialize databases for posts and formations
    st.session_state.manager = SessionManager()
    logger.info("Initialized session manager")


# --- Interface Logic ---
if st.session_state.manager.have_to_switch_step():
    for idx, post in enumerate(
        st.session_state.manager.get_post_in_dictionnary()
    ):
        proposal = st.session_state.manager\
            .get_recommandation_formation_from_in_vectorial_db(post)

        if st.session_state.manager.exist_idx_in_storage(idx):
            st.session_state.manager.add_post_to_storage(post, idx, proposal)

        st.markdown(present_post_in_markdown(post=post))

        name_formations = st.multiselect(
            "Select the most suitable formations",
            options=proposal["nom_formation"]
        )
        st.session_state.manager.add_selected_formation_to_post(
            idx=idx,
            name_formations=name_formations
        )

        st.dataframe(proposal[proposal["nom_formation"].isin(name_formations)])

        with st.expander("Debug section"):
            st.json(str(st.session_state.manager.get_post_data(idx=idx)))

    if st.button("Create or fill the contact email sheet?", use_container_width=True):
        if st.session_state.manager.all_post_have_formations():
            st.session_state.manager.change_phase()
        else:
            st.error("All tasks must have an associated formation.")
else:
    all_proposals = st.session_state.manager.reverse_proposal()

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
            label=f"Editable content example for {responsable}",
            value=format_mail(content=template, data=dico)
        )
        st.session_state.manager.add_mail_content(
            content=content,
            dico=dico,
            responsable=responsable
        )

    if st.button("Finalize?"):
        is_send = st.session_state.manager.sent_to_google_sheet()
        if is_send:
            st.success("Data has been successfully updated.")
        else:
            st.error("An error occurred while writing to Google Sheets.")
