from opensearchpy import OpenSearch
import logging
import os
from sentence_transformers import SentenceTransformer
import pandas as pd
import traceback
from copy import deepcopy

logger = logging.getLogger(__name__)

class SenderVectorDB:
    """
    A class to manage vector-based search indices in OpenSearch.
    It uses sentence embeddings generated by a pre-trained SentenceTransformer model.
    
    Attributes:
        vector_col (str): Name of the column to store vector embeddings.
        index_col (str): Name of the primary key column.
        other_cols (list): List of other metadata columns to include.
        model (SentenceTransformer): Pre-trained SentenceTransformer model for embeddings.
        vector_dim (int): Dimensionality of the vector embeddings.
        index_name_db (str): Name of the OpenSearch index to interact with.
    """
    
    vector_col = "vector_index"
    index_col = "id"
    other_cols = [
        "nom_formation", "domaine_formation",
        "niveau_formation", "presentation_formation", "contenu_formation",
        "url_fiche_formation", "mail_responsables", "universite",
        "ville", "url"
    ]
    model = SentenceTransformer("dangvantuan/sentence-camembert-base")
    vector_dim = 768
    index_name_db = "index"

    def __init__(self, vector_col: str = None, index_col: str = None,
                 other_cols: list = None, model: SentenceTransformer = None,
                 env_name_index: str = None):
        """
        Initialize the SenderVectorDB instance with optional overrides for configuration.

        Args:
            vector_col (str, optional): Custom column name for vector storage.
            index_col (str, optional): Custom primary key column for indexing.
            other_cols (list, optional): List of additional metadata columns.
            model (SentenceTransformer, optional): Custom SentenceTransformer model for embeddings.
            env_name_index (str, optional): Environment variable name for the index name.

        Raises:
            RuntimeError: If database initialization fails.
        """
        if vector_col is not None:
            self.vector_col = vector_col

        if index_col is not None:
            self.index_col = index_col

        if other_cols is not None:
            self.other_cols = other_cols

        if model is not None:
            self.model = model

        if env_name_index in os.environ:
            self.index_name_db = os.environ[env_name_index]

        try:
            option_db = eval(os.environ["OPTION_DB_VECTOR"])
            option_host = eval(os.environ["HOST_DB_VECTOR"])
            if isinstance(option_db, dict) and isinstance(option_host, list):
                self.db = OpenSearch(
                    hosts=option_host,
                    **option_db
                )
            else:
                logger.error(option_db)
                logger.error(option_host)
                raise ValueError(
                    f"The type of option_db is {type(option_db)} and the type of option_host is {type(option_host)}")
        except RuntimeError as e:
            logger.critical(f"Failed to initialize database managers: {e}")
            raise

    def add_vector(self, df, col) -> pd.DataFrame:
        """
        Generate sentence embeddings for a specified column and add them to the DataFrame.

        Args:
            df (pd.DataFrame): Input pandas DataFrame.
            col (str): Column name containing text to encode into vectors.

        Returns:
            pd.DataFrame: Updated DataFrame with vector embeddings.

        Raises:
            Exception: If vector generation fails.
        """
        logger.debug("--- add_vector ---")
        try:
            df[self.vector_col] = df[col].map(
                lambda x: self.model.encode(x.lower()).reshape(-1))
            self.vector_dim = max(df[self.vector_col].iloc[0].shape)
            return df
        except Exception:
            logger.error(traceback.format_exc())
            raise 

    def get_all_id_data(self) -> list:
        """
        Retrieve all document IDs from the OpenSearch index.

        Returns:
            list: List of document IDs.

        Raises:
            Exception: If data retrieval fails.
        """
        query = {
            "_source": "id",
            'query': {
                'match_all': {}
            }
        }
        response = self.db.search(
            body=query,
            index=self.index_name_db
        )
        try:
            return [h["_id"] for h in response["hits"]["hits"]]
        except Exception:
            logger.error(response)
            logger.error("query: "+str(query))
            logger.error("index_name_db: "+self.index_name_db)

    def get_data(self, cols: list = None, settings_index: dict = None):
        """
        Retrieve data from the OpenSearch index based on the specified columns or query.

        Args:
            cols (list, optional): List of columns to retrieve.
            settings_index (dict, optional): Custom query to use.

        Returns:
            pd.DataFrame: Data retrieved from the index.
        """
        logger.debug("--- get_data ---")
        if isinstance(cols, list) and all([
                c in ([self.vector_col, self.index_col] + self.other_cols)
                for c in cols
            ]):
            docs = self.db.search(
                body={
                    "size": 1000,
                    "_source": cols,
                    "query": {"match_all": {}}
                },
                index=self.index_name_db
            )
        elif isinstance(settings_index, dict):
            docs = self.db.search(
                body=settings_index,
                index=self.index_name_db
            )
        else:
            logger.warning("All cols are getting, here !")
            docs = self.db.search(
                body={
                    "size": 1000,
                    "query": {"match_all": {}}
                },
                index=self.index_name_db
            )
        data = docs["hits"]["hits"]
        logger.info(f"Get {len(data)} datas")
        return pd.DataFrame([d["_source"] for d in data])

    def create_index(self):
        """
        Create an OpenSearch index with the necessary mappings for vector-based search.
        If the index already exists, it does nothing.

        Raises:
            Exception: If index creation fails.
        """
        if not self.db.indices.exists(index=self.index_name_db):
            try:
                logger.info(f"Creating index {self.index_name_db}")
                properties = {
                    self.vector_col: {
                        'type': 'knn_vector',
                        'dimension': self.vector_dim,
                        "space_type": "cosinesimil",
                        "method": {
                            "name": "hnsw",
                            "engine": "lucene",
                            "parameters": {
                                "ef_construction": 100,
                                "m": 16
                            }
                        }
                    }
                }
                properties.update(
                    {
                        c: {"type": "text"}
                        for c in self.other_cols
                    }
                )
                body = {
                        "settings": {
                            "index": {
                                "knn": True
                            }
                        },
                        "mappings": {
                            "properties": properties
                        }
                } 
                self.db.indices.create(
                    index=self.index_name_db,
                    body=body
                )
            except Exception:
                logger.error(body)
                logger.error(traceback.format_exc())
                self.db.indices.delete(index=self.index_name_db)
                raise
        else:
            logger.info("Index already exists")

    def send_data(self, df: pd.DataFrame):
        """
        Send data to the OpenSearch index after creating it, if necessary.

        Args:
            df (pd.DataFrame): Input pandas DataFrame with vector and metadata columns.
        """
        logger.debug("--- send_data ---")
        self.create_index()
        ids_in_db = self.get_all_id_data()
        all_cols = deepcopy(self.other_cols)
        all_cols.append(self.vector_col)
        documents = df[all_cols].to_dict(orient="records")
        ids = df[self.index_col].to_list()
        for id_doc, doc in zip(ids, documents):
            if id_doc not in ids_in_db:
                try:
                    self.db.index(
                        index=self.index_name_db,
                        id=id_doc,
                        body=doc
                    )
                except Exception:
                    logger.error(f"This doc not working:{id_doc} with values: {doc}")
