import logging
from pandas import DataFrame, Series

logger = logging.getLogger(__name__)


class ManagerPage1:
    def __init__(self, posts: DataFrame):
        self.index_post = 0
        logger.debug("Initialized index_post to 0")
        self.only_one_modify = False
        logger.debug("Initialized only_one_modify to False")
        if posts is not None and posts.shape[0] != 0:
            self.posts = posts
            len_post = posts.shape[0]
            logger.info(f"Loaded {len_post} posts from the database.")
            logger.debug("Loaded posts from the database.")
        else:
            logger.error("No post found")

    def is_finish_posts(self) -> bool:
        logger.debug(f"is_finish_posts => index post {self.index_post} and len(self.posts): {len(self.posts)}")
        return len(self.posts) > self.index_post

    def have_to_expanded(self) -> bool:
        return (not self.only_one_modify) and (self.index_post == 0)

    # Management des index:
    def next_index(self):
        """
        Move to the next index. If only_one_modify is enabled, skip to the end of the list.
        """
        if self.only_one_modify:
            self.index_post = len(self.posts)
            logger.info("Mode 'only_one_modify' enabled: index set to the end.")
        else:
            self.index_post += 1
            logger.debug(f"Advanced index to {self.index_post}.")

    def index_to_modify_post(self, idx: int):
        """
        Enter edit mode for a specific post.

        Args:
            idx (int): Index of the post to modify.
        """
        self.index_post = idx
        self.only_one_modify = True
        logger.info(f"Edit mode activated for post at index {idx}.")

    def get_index(self):
        return self.index_post

    # Management des posts:
    def save_post(self, content: str, tasks: list) -> bool:
        """
        Save the modifications of a post.

        Args:
            content (str): Post description.
            tasks (list): List of associated tasks.
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
        return self.posts.iloc[self.index_post]

    def get_posts(self) -> DataFrame:
        return self.posts.copy()

    def get_post_by_tasks(self):
        docs = self.posts.copy()
        docs.tasks = docs.tasks.map(eval)
        docs = docs.explode("tasks")
        return docs

    @staticmethod
    def get_tasks_for_modification(post: Series) -> str:
        if isinstance(post.tasks, str) and len(post.tasks) == 0:
            return post.tasks
        elif isinstance(eval(post.tasks), list):
            return "*" + "*".join(eval(post.tasks))
        else:
            raise ValueError(f"Unexpected type for post.tasks: {type(post.tasks)}")
