# Analyse de données et recommandation cinématographique

## Introduction

Ce projet vise à mettre en application les différentes étapes d'un projet de science des données, de la collecte à la modélisation, en prenant pour sujet d'étude le domaine cinématographique.

L'objectif principal est de construire une chaîne de traitement complète permettant d'agréger des données, de les analyser statistiquement et de proposer des mécanismes de recommandation.

## Problématique

Comment exploiter et croiser des bases de données cinématographiques distinctes (API, fichiers plats) pour en extraire de l'information pertinente et modéliser les préférences des utilisateurs ?

## Déroulé du projet

Notre approche s'articule autour de trois axes méthodologiques :

1.  **Collecte et structuration des données :** Constitution d'un jeu de données unifié en croisant les informations techniques et les métadonnées issues de l'API **TMDB** (The Movie Database) et de la base de données **IMDb**. Cela correspond au **dossier `Step1`**, qui comprend trois scripts pythons. Tout d'abord, `fetch_ratings_IMDB.py` récupère et nettoie les données de la base IDMb. Ensuite `get_data_TMDB_script.py` s'occupe d'itérer sur la première base de données IMDB pour compléter les informations à partir de l'API TMDB. Enfin `join_data_TMDB_IMDB_final.py` joint les deux tables et crée un fichier parquet prêt à l'emploi avec toutes les données nettoyées. Le fichier est ensuite hébergé sur Huggingface et peut facilement être récupéré grâce à la commande pd.read_parquet("https://huggingface.co/datasets/enzojoly/projet_films/resolve/main/data_IMDB_TMDB_join.parquet")

2.  **Analyse exploratoire (EDA) et modélisation :** Étude statistique et visualisation des données récoltées pour identifier les tendances du marché cinématographique et les corrélations entre les variables (budget, genres, casting). Ensuite, 2 types de modélisation pour générer les recommandations. 
    * Le fichier `1_analysis_IMDB_rating.ipynb` **(notebook 1)** se divise en deux étapes. Tout d'abord, en se servant du parquet TMDB, des statistiques descriptives sommaires sont d’abord exploitées pour effectuer une analyse du data frame. Dans un second temps, on met en place un algorithme relativement simple reposant sur la méthode des K-Meaans (clustering des données) puis des K-Neighbors (rapprochement des films selon des facteurs donnés: genre, notation etc.). L’algorithme prend dans cette partie un seul film en input, et en recommande cinq autres.
    * Le fichier `2_overview_nlp_analysis` **(notebook 2)** : Dans l’approche précédente, nous avons exploité l’ensemble des features de la base de données, à l’exception des overviews (résumés des films). Ce second notebook se concentre spécifiquement sur l’analyse NLP des descriptions textuelles des films. Dans un premier temps, nous réalisons une analyse exploratoire et des visualisations à l’aide de wordclouds afin de mieux comprendre le contenu des résumés. Ensuite, nous construisons un système de recommandation basé sur la similarité entre les descriptions des films, en cherchant à identifier les contenus les plus proches sur le plan sémantique. Afin d’améliorer la pertinence des recommandations et d’éviter des suggestions incohérentes, nous avons également choisi d’intégrer des informations supplémentaires telles que le genre et le réalisateur, tout en pondérant les résultats par la popularité des films.

3.  **Approfondissement et recommandation (MovieLens) :** Il s'agit du dernier dossier `Step3_movielens_exploration` et notamment du notebook `3_user_preferences.ipynb` **(notebook 3)**. C'est une extension du projet via l'intégration du jeu de données **MovieLens**. Cette partie se concentre sur l'analyse des notes attribuées par les spectateurs pour mettre en place une approche de filtrage basée sur les préférences utilisateurs et non seulement sur les caractéristiques des films. Dans ce notebook, nous implémentons des algorithmes de recommandation plus avancés, tels que des méthodes de **filtrage collaboratif** et des **modèles basés sur des réseaux de neurones**, dans le but de prédire les notes des utilisateurs et de proposer des recommandations personnalisées.
