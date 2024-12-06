import requests
import logging
import re
from hashlib import md5
logger = logging.getLogger(__name__)


compiler_degres_level = re.compile("(Master \d)|(Master)|(Licence \d)|(Licence)|(BUT)|(Module \d)|(Module)|(Doctorat)")

def get_postal_code(cities:str):
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
        except:
            logger.error(response)
    return li_post

def add_cities(self):
    import numpy as np
    dico = {c: self.get_postal_code(c) for c in self.df.ville.dropna().unique().tolist()}
    dico.update({np.nan: ["00000"]})
    self.df["cp"] = self.df.ville.map(lambda cities: dico[cities])
    logger.debug("CP Added !")

def change_domaine(self):
    # FIXME: Verifier que le split avec Parcours est fonctionnel
    if "nom_formation" in self.df.columns:
        self.df["domaine"] = self.df.nom_formation.map(
        lambda x: re.sub(compiler_degres_level, "", x.split("Parcours")[0]))
        logger.debug("Change domaine done !")
    else:
        logger.error("No col 'nom_formation' in  df !")

def add_spe(self):
    if "nom_formation" in self.df.columns:
        self.df["spécialisation"] = self.df.nom_formation\
        .map(lambda x: 
            x.split("Parcours")[-1] if x.find("Parcours") != -1 else 
            "" if x.find("spécialité") == -1 else x.split("spécialité")[-1]
        )
        logger.debug("Spé added")
    else:
        logger.error("No col 'nom_formation' in  df !")

def add_level(self):
    self.df["niveau"] = self.df.nom_formation.map(
    lambda x: re.findall(compiler_degres_level, x))\
    .map(lambda x: list(set(x[0]))[-1] if len(x) else x)

def add_id(self):
    self.df["id"] = (self.df.nom_formation + self.df.mail).map(md5)
    logger.debug("Id Added")

def transform_data(self, actions:list = []):
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