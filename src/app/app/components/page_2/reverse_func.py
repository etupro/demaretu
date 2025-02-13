import requests
import logging

logger = logging.getLogger(__name__)


def get_postal_code(city: str):
    """
    Retrieves the postal code(s) for the given city or list of cities.

    Args:
        city (str): The name of the city (or a comma-separated list of cities).

    Returns:
        list: A list of postal codes (first two digits) for the provided city/cities.

    Raises:
        Exception: If the API request fails or no postal code is found.
    """
    try:
        cities = city.split(",") if "," in city else [city]
        postal_codes = []

        for c in cities:
            url = "https://api-adresse.data.gouv.fr/search/"
            params = {
                "q": c.strip(),
                "type": "municipality"
            }
            logger.debug(f"Requesting postal code for city: {c.strip()}")
            response = requests.get(url, params=params)

            if response.status_code != 200:
                logger.error(f"Failed to fetch postal code for city '{c}': HTTP {response.status_code}")
                raise Exception(f"HTTP Error: {response.status_code}")

            res = response.json()
            if "features" not in res or not res["features"]:
                logger.warning(f"No postal code found for city '{c}'")
                raise Exception(f"No postal code found for city '{c}'")

            postal_code = res["features"][0]["properties"]["postcode"][:2]
            postal_codes.append(postal_code)
            logger.info(f"Postal code for city '{c}': {postal_code}")

        return postal_codes

    except Exception as e:
        logger.exception(f"Error while fetching postal codes: {e}")
        raise


def reverse_proposal(self, formations_db):
    """
    Reverses the proposal by matching posts to their respective formations.

    Args:
        self: The object instance containing session data and utility methods.
        formations_db: The database containing formation data.

    Returns:
        dict: A dictionary where keys are responsible persons, and values are their tasks and formation details.

    Raises:
        Exception: If formations data or session data is invalid.
    """
    try:
        logger.debug("Fetching formation data from the database.")
        formations = formations_db.get_data()
        all_posts = self.get_data()

        if formations.empty or not all_posts:
            logger.error("Formation or session data is empty.")
            raise Exception("Formation or session data is missing or empty.")

        formations = formations[self.col_formation_db]
        all_formations = {}

        for _, post in all_posts.items():
            for formation in post["proposal"]:
                try:
                    logger.debug(f"Matching formation '{formation}' for post '{post['title']}'")
                    serie_formation = formations[
                        formations.nom_formation == formation
                    ].to_dict(orient="records")[0]

                    responsable = serie_formation["mail_responsables"]
                    mail = serie_formation["mails"]
                    task_data = {
                        "title": post["title"],
                        "number_departement": post["number_departement"],
                        "tasks": post["tasks"]
                    }

                    if responsable in all_formations:
                        if all(
                            post["tasks"] != t["tasks"]
                            for t in all_formations[responsable]["tasks"]
                            ):
                            all_formations[responsable]["tasks"].append(task_data)
                        if formation not in all_formations[responsable]["detail"]["formations"]:
                            all_formations[responsable]["detail"]["formations"][formation] = serie_formation
                    else:
                        all_formations[responsable] = {
                            "detail": {
                                "responsable": responsable,
                                "mail": mail,
                                "formations": {formation: serie_formation}
                            },
                            "tasks": [task_data]
                        }
                    logger.info(f"Added formation '{formation}' to responsable '{responsable}'")

                except Exception as formation_error:
                    logger.warning(f"Error processing formation '{formation}': {formation_error}")

        return all_formations

    except Exception as e:
        logger.exception(f"Error during reverse proposal process: {e}")
        raise
