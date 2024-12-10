import requests
import logging
import re
from hashlib import md5

logger = logging.getLogger(__name__)

compiler_degres_level = re.compile(
    "(Master \d)|(Master)|(Licence \d)|(Licence)|(BUT)|(Module \d)|(Module)|(Doctorat)"
)


def get_postal_code(cities: str) -> list:
    """
    Fetch postal codes for one or more cities using the API from https://api-adresse.data.gouv.fr.

    Parameters:
        cities (str): A single city name or a comma-separated list of cities.

    Returns:
        list: A list of postal codes corresponding to the given cities.

    Behavior:
        - Splits the input string into individual city names if it contains commas.
        - Makes an API request for each city to fetch its postal code.
        - Returns a list of postal codes.

    Logs:
        - Logs errors if the API request fails or if parsing the response fails.

    Warning:
        - This function uses `eval`, which can be unsafe if the API response is compromised.
    """
    if isinstance(cities, str) and cities.find(",") != -1:
        cities = cities.split(",")
    else:
        cities = [cities]
    li_post = []
    for c in cities:
        url = "https://api-adresse.data.gouv.fr/search/"
        params = {
            "q": c,
            "type": "municipality"
        }
        response = requests.get(url, params=params)
        try:
            res = eval(response.content)["features"][0]["properties"]["postcode"]
            li_post.append(res)
        except Exception:
            logger.error(response)
    return li_post


def add_cities(self) -> None:
    """
    Add a new column 'cp' to the DataFrame containing postal codes for each city.

    Behavior:
        - Maps cities in the 'ville' column to their postal codes using `get_postal_code`.
        - Adds a default value of "00000" for missing or NaN cities.

    Effects:
        - Modifies the DataFrame by adding a 'cp' column.

    Logs:
        - Logs a debug message when the operation is completed.
    """
    import numpy as np
    dico = {c: self.get_postal_code(c) for c in self.df.ville.dropna().unique().tolist()}
    dico.update({k: ["00000"] for k in [None, np.nan]})
    self.df["cp"] = self.df.ville.map(lambda cities: dico[cities])
    logger.debug("CP Added !")


def change_domaine(self) -> None:
    """
    Extract the domain from the 'nom_formation' column.

    Behavior:
        - Removes degree levels and extracts the domain before the keyword "Parcours".
        - Logs an error if the column 'nom_formation' is missing.

    Effects:
        - Adds or updates the 'domaine' column in the DataFrame.

    Logs:
        - Logs a debug message when the operation is successful.
        - Logs an error message if 'nom_formation' is not in the DataFrame.
    """
    # FIXME: Attention il faut etre sur que ce soit Parcours qui sépare les deux
    if "nom_formation" in self.df.columns:
        self.df["domaine"] = self.df.nom_formation.map(
            lambda x: re.sub(compiler_degres_level, "", x.split("Parcours")[0]))
        logger.debug("Change domaine done !")
    else:
        logger.error("No col 'nom_formation' in df !")


def add_spe(self) -> None:
    """
    Extract specialization information from the 'nom_formation' column.

    Behavior:
        - Extracts the text after "Parcours" or "spécialité" in the 'nom_formation' column.
        - Logs an error if the column 'nom_formation' is missing.

    Effects:
        - Adds or updates the 'spécialisation' column in the DataFrame.

    Logs:
        - Logs a debug message when the operation is successful.
        - Logs an error message if 'nom_formation' is not in the DataFrame.
    """
    # FIXME: Attention il faut etre sur que ce soit Parcours qui sépare les deux
    if "nom_formation" in self.df.columns:
        self.df["spécialisation"] = self.df.nom_formation \
            .map(
                lambda x: x.split("Parcours")[-1] if x.find("Parcours") != -1
                else "" if x.find("spécialité") == -1
                else x.split("spécialité")[-1]
            )
        logger.debug("Spé added")
    else:
        logger.error("No col 'nom_formation' in df !")


def add_level(self) -> None:
    """
    Extract the degree level (e.g., 'Master', 'Licence') from the 'nom_formation' column.

    Behavior:
        - Uses a regular expression to find degree levels in the text.
        - Stores the extracted level in a new column 'niveau'.

    Effects:
        - Adds or updates the 'niveau' column in the DataFrame.

    Logs:
        - Logs a debug message when the operation is completed.
    """
    self.df["niveau"] = self.df.nom_formation.map(
        lambda x: re.findall(compiler_degres_level, x)) \
        .map(lambda x: list(set(x[0]))[-1] if len(x) else x)
    logger.debug("Level Added")


def add_id(self) -> None:
    """
    Generate unique IDs for each row based on 'nom_formation' and 'mail'.

    Behavior:
        - Concatenates 'nom_formation' and 'mail' to create a unique string.
        - Hashes the string using MD5 and stores the result in a new column 'id'.

    Effects:
        - Adds or updates the 'id' column in the DataFrame.

    Logs:
        - Logs a debug message when the operation is completed.
    """
    self.df["id"] = (self.df.nom_formation + self.df.mail) \
        .map(lambda x: md5(str(x).encode()).hexdigest())
    logger.debug("Id Added")


def transform_data(self, actions: list = []) -> None:
    """
    Apply a sequence of transformations to the DataFrame.

    Parameters:
        actions (list): A list of transformation actions to apply. Supported actions:
            - "add_cities": Calls `add_cities` to add postal codes.
            - "add_spe": Calls `add_spe` to add specialization information.
            - "change_domaine": Calls `change_domaine` to extract domain information.
            - "add_level": Calls `add_level` to extract degree levels.
            - "add_id": Calls `add_id` to generate unique IDs.

    Effects:
        - Applies the specified transformations in the given order.

    """
    if "add_cities" in actions:
        self.add_cities()
    if "add_spe" in actions:
        self.add_spe()
    if "change_domaine" in actions:
        self.change_domaine()
    if "add_level" in actions:
        self.add_level()
    if "add_id" in actions:
        self.add_id()
