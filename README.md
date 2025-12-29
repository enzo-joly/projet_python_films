# Analyse de données et recommandation cinématographique

## 📄 Introduction

Ce projet vise à mettre en application les différentes étapes d'un projet de science des données, de la collecte à la modélisation, en prenant pour sujet d'étude le domaine cinématographique.

L'objectif principal est de construire une chaîne de traitement complète permettant d'agréger des données hétérogènes, de les analyser statistiquement et de proposer des mécanismes de recommandation.

## ❓ Problématique

Comment exploiter et croiser des bases de données cinématographiques distinctes (API, fichiers plats) pour en extraire de l'information pertinente et modéliser les préférences des utilisateurs ?

Notre approche s'articule autour de trois axes méthodologiques :

1.  **Collecte et structuration des données :** Constitution d'un jeu de données unifié en croisant les informations techniques et les métadonnées issues de l'API **TMDB** (The Movie Database) et de la base de données **IMDb**. Cela correspond au dossier "Step1", qui comprend trois scripts pythons. Tout d'abord, fetch_ratings_IMDB récupère et nettoie les données de la base IDMb. Ensuite get_data_TMDB_script s'occupe d'itérer sur la première base de données IMDB pour compléter les informations à partir de l'API TMDB. Enfin join_data_TMDB_IMDB_final joint les deux tables et crée un fichier parquet prêt à l'emploi avec toutes les données nettoyées. Le fichier est ensuite hébergé sur Huggingface et peut facilement être récupéré grâce à la commande pd.read_parquet("https://huggingface.co/datasets/enzojoly/projet_films/resolve/main/data_IMDB_TMDB_join.parquet")

2.  **Analyse exploratoire (EDA) :** Étude statistique et visualisation des données récoltées pour identifier les tendances du marché cinématographique et les corrélations entre les variables (budget, genres, casting).

3.  **Approfondissement et recommandation (MovieLens) :** Extension du projet via l'intégration du jeu de données **MovieLens**. Cette partie se concentre sur l'analyse des notes attribuées par les spectateurs pour mettre en place une approche de filtrage basée sur les préférences utilisateurs.