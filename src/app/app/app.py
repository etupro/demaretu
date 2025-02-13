import conf_env
import streamlit as st

# st.title("Pipline de démarchage: DemarEtu")

# st.markdown("""
# ## Workflow de démarchage:

# - Etape 1: Ségmenter les posts en tâches,
# - Etape 2: 
#     - Superviser le matchmaking entre formations et posts,
#     - Générer ou introduire un template de mail pour le démarchage.
# """)

pages = st.navigation([
    st.Page(
        "./pages/format_post.py", title="1 - Formattage des posts"
        ),
    st.Page(
        "./pages/matchmaking_and_send_content.py", title="2 - Matchmaking de post-formation"
        )
    ]
)
pages.run()
