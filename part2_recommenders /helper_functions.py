# Toutes les fonctions un peu longues pour le fichier user_preferences.ipynb se triuvent ici 

import pandas as pd
import numpy as np
import re
import os
import zipfile
import urllib.request


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ZIP_PATH = os.path.join(BASE_DIR, "ml-1m.zip")
EXTRACT_ROOT = os.path.join(BASE_DIR, "ml-1m")
DATA_FOLDER = os.path.join(EXTRACT_ROOT, "ml-1m") # Le sous-dossier créé par l'extraction

# Funtion to download the data from MovieLens  
def download_movielens():

    DATA_URL = "https://files.grouplens.org/datasets/movielens/ml-1m.zip"
    
    if not os.path.exists(ZIP_PATH):
        print(f"Téléchargement vers {ZIP_PATH}...")
        urllib.request.urlretrieve(DATA_URL, ZIP_PATH)
        print("Téléchargement terminé.")

    if not os.path.exists(EXTRACT_ROOT):
        print(f"Extraction dans {EXTRACT_ROOT}...")
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_ROOT)
        print("Extraction terminée.")


# Function to create a merged df (including user info, movie info and ratings)
def create_df(): 
    users_file = os.path.join(DATA_FOLDER, "users.dat")
    movies_file = os.path.join(DATA_FOLDER, "movies.dat")
    ratings_file = os.path.join(DATA_FOLDER, "ratings.dat")

    df_user_info = pd.read_csv(users_file,
        sep="::", engine="python",  
        names=["UserID", "Gender", "Age", "Occupation", "Zip-code"]) 
    
    df_films = pd.read_csv(movies_file,
        sep="::", engine="python",
        names=["MovieID", "Title", "Genres"], 
        encoding="ISO-8859-1") 
    
    df_ratings = pd.read_csv(ratings_file,
        sep="::", engine="python",
        names=["UserID", "MovieID", "Rating", "Timestamp"],
        encoding="ISO-8859-1")

    # Harmonize MovieID before merging
    df_ratings["MovieID"] = df_ratings["MovieID"].astype(int)
    df_user_info["UserID"] = df_user_info["UserID"].astype(int)
    df_films["MovieID"] = df_films["MovieID"].astype(int)

    # Merge df_user_info, df_films and df_ratings into 1 df_users 
    df_users = (df_ratings.merge(df_user_info, on="UserID").merge(df_films, on="MovieID"))

    # Drop 'Timestamp' column
    df = df_users.drop(columns=["Timestamp"])
    # Convert 'Genres' string to list
    df["Genres"] = df["Genres"].apply(lambda x: x.split("|") if isinstance(x, str) else [])
    # Transform 'Gender' to binary values 
    df["Gender"] = df["Gender"].apply(lambda x: 1 if x == "F" else 0)
    # Split year and title 
    df['Year'] = df['Title'].str.extract(r'\((\d{4})\)', expand=False).astype(float)
    # Remove the year suffix from the Title (e.g., "Toy Story (1995)" -> "Toy Story")
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df['Title'] = df['Title'].str.replace(r'\s*\(\d{4}\)', '', regex=True).str.strip()
    return df
    return df_users


# Function to find full movie name and movie id using an approximate name 
def search_films(titre_approx, df):
    """
    Trouve l'ID et le nom exact d'un film à partir d'un titre approximatif
    en utilisant directement le DataFrame principal.
    """
    # On récupère la liste unique des films (MovieID et Title)
    df_unique_movies = df[['MovieID', 'Title']].drop_duplicates()
    
    # Filtrage insensible à la casse
    resultats = df_unique_movies[df_unique_movies['Title'].str.contains(titre_approx, case=False, na=False)]
    
    if resultats.empty:
        print(f"Aucun film trouvé pour : '{titre_approx}'")
        return None
    
    print(f"Correspondances pour '{titre_approx}':")
    for _, row in resultats.iterrows():
        print(f"  - ID: {row['MovieID']} | Titre: {row['Title']}")
    
    # Retourne les infos du dernier résultat trouvé (ou vous pouvez adapter pour retourner une liste)
    last_movie = resultats.iloc[-1]
    return last_movie['MovieID'], last_movie['Title']
