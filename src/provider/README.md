# Provider: Orchestrateur plateforme data engineering

## Contexte:

Cet orchestrateur sert à recapter la donnée brute issues des csv de contact pour l'intégrer à la base de données vectorielles.

## Liste des tâches

### Coté données contact formation:

1. Récupérer les contacts (autre repo)
2. **transform:** Transformer les données (nettoyage, affinage du texte et récupération)
3. **load:** Vectorialiser les donnée et les injecter dans la base de données vetorielle.
