import requests


def get_postal_code(city: str):
    if len(city.split(",")) > 1:
        cities = city.split(",")
    else:
        cities = city
    li_post = []
    for c in cities:
        url = "https://api-adresse.data.gouv.fr/search/"
        params = {
            "q": city,
            "type": "municipality"
        }
        response = requests.get(url, params=params)
        res = eval(response.content)["features"][0]["properties"]["postcode"][:2]
        li_post.append(res)
    return li_post


def reverse_proposal(self):
    formations = self.formations_db.get_data()
    all_posts = self.get_data()
    formations = formations[[
            "nom_formation", "niveau", "domaine", "spécialisation",
            "mail_responsables", "mails", "universite",
            "cp", "niveau", "url"
        ]]
    all_formations = {}
    for _, post in all_posts.items():
        for formation in post["proposal"]:
            serie_formation = formations[
                    formations.nom_formation == formation
                    ].to_dict(orient="records")[0]
            responsable = serie_formation["mail_responsables"]
            mail = serie_formation["mails"]
            
            dico = {
                        "title": post["title"],
                        "number_departement": post["number_departement"],
                        "tasks": post["tasks"]
                    }
            
            if responsable in all_formations and all([post["tasks"] != t["tasks"] for t in all_formations[responsable]["tasks"]]):
                all_formations[responsable]["tasks"].append(dico)
                if formation not in all_formations[responsable]["detail"]["formations"]:
                    all_formations[responsable]["detail"]["formations"]\
                        [formation] = serie_formation
            else:
                all_formations[responsable] = {
                    "detail": {
                        "responsable": responsable,
                        "mail": mail,
                        "formations": {
                            formation: serie_formation
                        }
                    },
                    "tasks": [dico]
                }
    return all_formations
