import streamlit as st


def modify_content_to_split_in_tasks():
    post = st.session_state.manager.get_post()
    st.markdown(
        f"### {st.session_state.manager.index_post}/ **Nom de l'organisation:** {post.title}")

    tasks_content = st.session_state.manager.get_tasks_for_modification(
        post=post
        )

    content = st.text_area(
        label="Description",
        value=post.content + tasks_content
    )
    list_content = content.split("*")
    desc = list_content[0]
    tasks = list_content[1:]

    col_right, col_left = st.columns(2)
    with col_right:
        st.markdown(f"### Description du post :\n{desc}")
    with col_left:
        for idx, t in enumerate(tasks):
            task = t.strip().replace("-", "").replace("*", "")
            st.markdown(f"- **Mission {idx + 1}** : {task}")
    return desc, tasks
