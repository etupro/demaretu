from utils.db_vector import DBVector
import streamlit as st
import logging
import os

logger = logging.getLogger(__name__)


@st.cache_resource
def get_vectorial_db():
    try:
        option_db = eval(os.environ["OPTION_DB_VECTOR"])
        option_host = eval(os.environ["HOST_DB_VECTOR"])
        if isinstance(option_db, dict) and isinstance(option_host, list):
            return DBVector(
                option_db=option_db,
                option_host=option_host
            ).get_db()
        else:
            raise ValueError(
                f"the type of option_db is {type(option_db)} and the type of option_host is {type(option_host)}")
    except RuntimeError as e:
        logger.critical(f"Failed to initialize database managers: {e}")
        raise
