import logging
from pandas import DataFrame, Series
from streamlit_utils.cache_ressource import get_vectorial_db
from hashlib import md5

logger = logging.getLogger(__name__)


class ManagerPage1:
    """
    A class to manage posts and their related tasks.

    The ManagerPage1 class provides methods for navigating posts, saving modifications, 
    and managing posts based on tasks. It also supports sending structured data to a 
    vectorial database for further indexing and analysis.

    Attributes:
        index_post (int): The current index of the post being managed.
        only_one_modify (bool): A flag indicating if the user is modifying a single post.

    Methods:
        set_post_dataset() -> None:
            Set post dataframe

        is_finish_posts() -> bool:
            Checks if there are more posts left to process.

        have_to_expanded() -> bool:
            Determines if the post management should expand, depending on conditions.

        next_index() -> None:
            Moves to the next post in the list.

        index_to_modify_post(idx: int) -> None:
            Sets the current index to the specified value and activates single-modify mode.

        get_index() -> int:
            Returns the current index of the post.

        save_post(content: str, tasks: list) -> bool:
            Updates the content and tasks of the current post.

        get_post() -> Series:
            Retrieves the current post as a pandas Series.

        get_posts() -> DataFrame:
            Returns a copy of the DataFrame containing all posts.

        get_post_by_tasks() -> DataFrame:
            Explodes tasks associated with posts into separate rows.

        get_tasks_for_modification(post: Series) -> str:
            Generates a string representation of tasks for a given post.

        send_to_db(cols: list) -> None:
            Sends the post data to a vectorial database for indexing.
    """

    def __init__(self) -> None:
        """
        Initializes the ManagerPage1 instance.

        Args:
            posts (DataFrame): A DataFrame containing the posts to manage. Must have at 
                               least "id", "content", and "tasks" columns.

        Raises:
            AttributeError: If the provided DataFrame is empty or None.
        """
        self.index_post = 0
        logger.debug("Initialized index_post to 0")
        self.only_one_modify = False
        logger.debug("Initialized only_one_modify to False")

    def set_post_dataset(self, posts: DataFrame, ids_already_done: list = None
                         ):
        """
        Set the dataframe post.

        Args:
            posts (DataFrame): A DataFrame containing posts with columns such as "id",
                           "content", and "tasks".
            id_already_done (list): A list of post id that already formatted. 

        Raises:
            AttributeError: If the provided DataFrame is empty or None.
        """
        if "raw_id" in posts.columns:
            basic_size = posts.shape[0]
            posts["raw_id"] = posts["raw_id"].astype(int)
            posts = posts[~posts["raw_id"].isin(ids_already_done)]
        
        if posts is not None and posts.shape[0] != 0:
            self.posts = posts
            len_post = posts.shape[0]
            logger.info(f"Loaded {len_post} posts from the database.")
        elif basic_size != 0:
            self.posts = []
            len_post = 0
            logger.info("All post are already posted !")
        else:
            logger.error("No post found")
            raise AttributeError("No post found")

    def is_finish_posts(self) -> bool:
        """
        Checks whether there are more posts to process.

        Returns:
            bool: True if there are remaining posts; otherwise, False.
        """
        logger.debug(f"is_finish_posts => index post {self.index_post} and len(self.posts): {len(self.posts)}")
        return len(self.posts) > self.index_post

    def not_post_to_format(self) -> bool:
        """
        Checks whether there are more posts to process.

        Returns:
            bool: True if there are remaining posts; otherwise, False.
        """
        logger.debug(f"is_finish_posts => index post {self.index_post} and len(self.posts): {len(self.posts)}")
        return len(self.posts) == 0

    def have_to_expanded(self) -> bool:
        """
        Determines if post expansion is required.

        Returns:
            bool: True if the current index is 0 and not in single-modify mode.
        """
        logger.debug(f"is_finish_posts => index_post {self.index_post} and only_one_modify: {self.only_one_modify}")
        return (not self.only_one_modify) and (self.index_post == 0)

    def next_index(self) -> None:
        """
        Advances to the next post. If single-modify mode is active, jumps to the end.
        """
        if self.only_one_modify:
            self.index_post = len(self.posts)
            logger.info("Mode 'only_one_modify' enabled: index set to the end.")
        else:
            self.index_post += 1
            logger.debug(f"Advanced index to {self.index_post}.")

    def index_to_modify_post(self, idx: int) -> None:
        """
        Sets the index to a specified value and enables single-modify mode.

        Args:
            idx (int): The index of the post to modify.
        """
        self.index_post = idx
        self.only_one_modify = True
        logger.info(f"Edit mode activated for post at index {idx}.")

    def get_index(self) -> int:
        """
        Returns the current index of the post.

        Returns:
            int: The current post index.
        """
        return self.index_post

    def save_post(self, content: str, tasks: list) -> bool:
        """
        Updates the content and tasks of the current post.

        Args:
            content (str): The new content for the post.
            tasks (list): A list of tasks associated with the post.

        Returns:
            bool: True if the post was successfully updated; otherwise, False.
        """
        is_saved = False
        try:
            if content[:20] == self.posts.loc[self.index_post, "content"][:20]:
                self.posts.loc[self.index_post, "content"] = content
                self.posts.loc[self.index_post, "tasks"] = str(tasks)
                logger.info(f"Post {self.index_post} successfully saved.")
                is_saved = True
            else:
                raise ValueError("Wrong location of post to save")
        except Exception as e:
            logger.error(f"Error saving post {self.index_post}: {e}")
        finally:
            return is_saved

    def get_post(self) -> Series:
        """
        Retrieves the current post.

        Returns:
            Series: The current post as a pandas Series.
        """
        return self.posts.iloc[self.index_post]

    def get_posts(self) -> DataFrame:
        """
        Returns all posts.

        Returns:
            DataFrame: A copy of the DataFrame containing all posts.
        """
        return self.posts.copy()

    def get_post_by_tasks(self) -> DataFrame:
        """
        Explodes tasks associated with posts into individual rows.

        Returns:
            DataFrame: A DataFrame where each row corresponds to a single task.
        """
        docs = self.posts.copy()
        docs.tasks = docs.tasks.map(eval)
        docs = docs.explode("tasks")
        return docs

    @staticmethod
    def get_tasks_for_modification(post: Series) -> str:
        """
        Generates a string representation of tasks for a given post.

        Args:
            post (Series): A post represented as a pandas Series.

        Returns:
            str: A string representation of tasks.

        Raises:
            ValueError: If the tasks format is invalid.
        """
        if isinstance(post.tasks, str) and len(post.tasks) == 0:
            return post.tasks
        elif isinstance(eval(post.tasks), list):
            return "*" + "*".join(eval(post.tasks))
        else:
            logger.error("Unexpected type for post.tasks")
            raise ValueError(f"Unexpected type for post.tasks: {type(post.tasks)}")

    def get_to_raw_id(self) -> None:
        """
        Sends post data to a vectorial database for indexing.

        Args:
            cols (list): A list of columns to include when sending data to the database.
        """
        vectorial_db = get_vectorial_db(
            env_name_index="INDEX_POST",
            index_col="id",
            other_cols=["raw_id"]
        )
        if vectorial_db.index_exists():
            df = vectorial_db.get_data()
            return df["raw_id"].astype(int).to_list()
        else:
            return []

    def send_to_db(self, cols: list) -> None:
        """
        Sends post data to a vectorial database for indexing.

        Args:
            cols (list): A list of columns to include when sending data to the database.
        """
        vectorial_db = get_vectorial_db(
            env_name_index="INDEX_POST",
            index_col="id",
            other_cols=["id"] + cols
        )
        vectorial_db.create_index()
        docs = self.get_post_by_tasks()
        docs = docs[cols]
        docs["id"] = (docs.raw_id.map(str) + docs.tasks)\
            .map(lambda x: md5(x.encode()).hexdigest())
        df = vectorial_db.add_vector(df=docs, col="tasks")
        vectorial_db.send_data(df=df)
