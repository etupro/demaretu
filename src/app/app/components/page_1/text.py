from pandas import Series
import logging
from typing import Union
# Logger configuration
logger = logging.getLogger(__name__)

explanation = """
# Formattage des posts
## Description
Pour permettre à l'algorithme de retrouver automatiquement les tâches, il faut séparer les tâches par des listes à puces de cette manière :
- Activité entreprise 1
- Activité entreprise 2

Ces besoins :
* Mission 1
* Mission 2

**Exemple acceptable** :

Une entreprise fait :
- De la mise en rayon
- Trie les articles
Elle souhaite engager des étudiants pour :
* Communication
* Création d'un site web

**Attention** : Utilisez '-' pour les puces dans la description et '*' pour les tâches.
"""

description_general_company = """
--- \n
### **Nom de l'organisation :** \n {title} \n
#### Description du post :  \n  {content} \n
#### Les missions :
"""


def describe_task(post: Series, idx: int) -> Union[bool, str]:
    missing_tasks = False
    try:
        description_post = description_general_company.format(
            title=post.title,
            content=post.content
        )
        tasks = eval(post.tasks)
        if len(tasks):
            for task in tasks:
                description_post += f"- {task}"
            logger.debug("Tasks here")
        else:
            missing_tasks = True
            logger.debug("No tasks here")
    except Exception as e:
        missing_tasks = True
        description_post = ""
        logger.error(
            f"Erreur lors de l'évaluation des tâches pour le post {idx} : {e}")
    finally:
        return missing_tasks, description_post
