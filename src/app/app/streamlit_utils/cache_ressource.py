from utils.db_vector import DBVector
from utils.sender import SenderVectorDB
import streamlit as st
import logging
import os

logger = logging.getLogger(__name__)


@st.cache_resource
def get_vectorial_db(
    env_name_index: str,
    index_col: str,
    other_cols: list
):
    try:
        return SenderVectorDB(
            env_name_index=env_name_index,
            index_col=index_col,
            other_cols=other_cols
        )
    except RuntimeError as e:
        logger.critical(f"Failed to initialize database managers: {e}")
        raise
