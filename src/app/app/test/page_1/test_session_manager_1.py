import conf_test_lvl_2
import pytest
import pandas as pd
from pandas import DataFrame, Series
from components.page_1.session_manager import ManagerPage1


@pytest.fixture
def sample_posts():
    """Fixture qui retourne un DataFrame de posts d'exemple."""
    return pd.DataFrame({
        "id": [1, 2, 3],
        "content": ["Post numéro 1", "Post numéro 2", "Post numéro 3"],
        "tasks": ['["task1", "task2"]', '["task3"]', '[]']
    })


@pytest.fixture
def manager_page(sample_posts):
    """Fixture qui retourne une instance de ManagerPage1 initialisée avec des posts."""
    return ManagerPage1(posts=sample_posts)


def test_initialization_with_posts(sample_posts):
    """Test de l'initialisation avec un DataFrame valide."""
    manager = ManagerPage1(posts=sample_posts)
    assert manager.index_post == 0
    assert manager.only_one_modify is False
    assert len(manager.posts) == 3


def test_initialization_with_empty_posts():
    """Test de l'initialisation avec un DataFrame vide."""
    empty_posts = pd.DataFrame(columns=["id", "content", "tasks"])
    with pytest.raises(AttributeError):  # Vérifie si logger.error est déclenché
        ManagerPage1(posts=empty_posts)


def test_is_finish_posts(manager_page):
    """Test de la méthode is_finish_posts."""
    assert manager_page.is_finish_posts() is True
    manager_page.index_post = 3
    assert manager_page.is_finish_posts() is False


def test_have_to_expanded(manager_page):
    """Test de la méthode have_to_expanded."""
    assert manager_page.have_to_expanded() is True
    manager_page.index_post = 1
    assert manager_page.have_to_expanded() is False


def test_next_index(manager_page):
    """Test de la méthode next_index."""
    manager_page.next_index()
    assert manager_page.index_post == 1
    manager_page.only_one_modify = True
    manager_page.next_index()
    assert manager_page.index_post == 3  # Atteint la fin des posts


def test_index_to_modify_post(manager_page):
    """Test de la méthode index_to_modify_post."""
    manager_page.index_to_modify_post(2)
    assert manager_page.index_post == 2
    assert manager_page.only_one_modify is True


def test_get_post(manager_page):
    """Test de la méthode get_post."""
    post = manager_page.get_post()
    assert isinstance(post, Series)
    assert post.content == "Post numéro 1"


def test_save_post(manager_page):
    """Test de la méthode save_post."""
    new_content = "Post numéro 1"
    tasks = ["new_task1", "new_task2"]
    assert manager_page.save_post(new_content, tasks) is True
    updated_post = manager_page.get_post()
    assert updated_post.content == new_content
    assert updated_post.tasks == str(tasks)


def test_save_post_wrong_location(manager_page):
    """Test de la méthode save_post avec un mauvais contenu."""
    wrong_content = "Contenu incorrect"
    tasks = ["task1"]
    assert manager_page.save_post(wrong_content, tasks) is False


def test_get_post_by_tasks(manager_page):
    """Test de la méthode get_post_by_tasks."""
    exploded_posts = manager_page.get_post_by_tasks()
    assert len(exploded_posts) == 4  # tasks = ["task1", "task2", "task3", None]
    assert "tasks" in exploded_posts.columns


def test_get_tasks_for_modification(manager_page):
    """Test de la méthode get_tasks_for_modification."""
    post = manager_page.get_post()
    tasks_str = manager_page.get_tasks_for_modification(post)
    assert tasks_str == "*task1*task2"


def test_get_tasks_for_modification_with_empty_tasks(manager_page):
    """Test de la méthode get_tasks_for_modification avec des tasks vides."""
    manager_page.index_post = 2
    post = manager_page.get_post()
    tasks_str = manager_page.get_tasks_for_modification(post)
    assert tasks_str == "*"
