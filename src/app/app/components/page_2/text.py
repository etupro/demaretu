from jinja2 import Template
import logging

logger = logging.getLogger(__name__)

explination_wrtting_template = """
# Rédaction des mails

Ajoutez les variables suivantes dans votre contenu de template :

    Bonjour {{ detail.responsable }}

    Blablabla
    {% for task in tasks %}
    - {{task.title}} pour la mission : {{task.tasks}}
    {% endfor %}
    Blablabla
---               
"""


def present_post_in_markdown(post):
    title = post["title"]
    number_departement = post["number_departement"]
    tasks = post["tasks"]
    return f"""--- 
## {title} - {number_departement}
{tasks}
"""


def presentation_content_mail(responsable):
    return f"""
---
## Responsable {responsable}

Voici le contenu du mail :
"""


def format_mail(content: str, data: dict):
    """
    Formats email content using a Jinja2 template.

    Parameters:
    - content (str): Template string for the email.
    - data (dict): Dictionary containing data for populating the template.

    Returns:
    - str: Formatted email content, or an error message if formatting fails.
    """
    try:
        return Template(content).render(data)
    except Exception as e:
        logger.error(f"Error formatting email: {e}")
        return ""