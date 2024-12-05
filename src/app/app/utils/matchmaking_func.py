import requests


def get_postal_code(city:str):
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


def reverse_proposal(formations_db, all_posts):
    formations = formations_db.get_data()
    formations = formations[[
            "nom_formation", "domaine_formation", "niveau_formation",
            "mail_responsables", "ville"
        ]]
    all_formations = {}
    for idx, post in all_posts.items():
        for formation in post["proposal"]:
            serie_formation = formations[
                    formations.nom_formation == formation
                    ].to_dict(orient="records")[0]
            mail = serie_formation["mail_responsables"]
            
            dico = {
                        "title": post["title"],
                        "number_departement": post["number_departement"],
                        "tasks": post["tasks"]
                    }
            
            if mail in all_formations and all([post["tasks"] != t["tasks"] for t in all_formations[mail]["tasks"]]):
                all_formations[mail]["tasks"].append(dico)
                if formation not in all_formations[mail]["detail"]["formations"]:
                    all_formations[mail]["detail"]["formations"]\
                        [formation] = serie_formation
            else:
                all_formations[mail] = {
                    "detail": {
                        "responsable": mail,
                        "formations": {
                            formation: serie_formation
                        }
                    },
                    "tasks": [dico]
                }
    return all_formations
