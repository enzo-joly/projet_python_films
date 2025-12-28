### Script qui parcoure la base de donées IMDB pour ajouter les informations importantes de TMDB grâce à l'API. Renvoie un fichier parquet, le script tourne pendant 2 heures environ.

import requests
import threading
from requests.adapters import HTTPAdapter
import pandas as pd
import pyarrow
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_session():
    """
    Renvoie la session unique dédiée au thread qui appelle cette fonction.
    """
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
        
        # --- 3. L'ADAPTER (Tuning) ---
        # On configure le moteur pour être robuste
        adapter = HTTPAdapter(
            pool_connections=10,  # Nombre de site web
            pool_maxsize=10,      # Taille max du pool = max worker
            max_retries=3         # Réessaie 3 fois si échec de connexion pure
        )
        
        # On installe ce moteur pour toutes les requêtes
        thread_local.session.mount('https://', adapter)
        thread_local.session.mount('http://', adapter)

    return thread_local.session

def get_json(url, params=None, max_retries=3, delay=2):
    """A function to make get requests and return a json file, with a retry function"""

    params = params or {}
    params['api_key'] = API_KEY

    session = get_session()

    for attempt in range(max_retries):
        try:
            response = session.get(url, params=params, timeout=10)
            
            # Si on dépasse le quota (429), on attend et on réessaie
            if response.status_code == 429:
                print(f"Rate limit atteint. Pause de {delay}s...")
                time.sleep(delay)
                continue # On passe à l'itération suivante de la boucle for (nouvel essai)
            
            response.raise_for_status() # Lève une exception pour les codes 4xx/5xx
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur API : {e}")
            if attempt+1 < max_retries :
                time.sleep(delay) # Attente avant le prochain essai
            else:
                return None # Abandon après max_retries

    return None

def get_tmdb_id(imdb_id):
    """A funtion to get TMBD id from IMDb id"""

    json_file = get_json(f"{BASE_URL}/find/{imdb_id}", {"external_source" : "imdb_id"})

    if json_file == None : # Return None if API Error
        return None
    
    results = json_file.get('movie_results', [])
    if len(results) == 0:
        return 0
    else:
        return results[0]['id']

def get_movie_details(movie_id):
    """A function to get detailed movie info by movie ID"""

    details = get_json(f"{BASE_URL}/movie/{movie_id}", {"append_to_response": "credits"})

    if details != None : 

        return {
            "tmdb_id" : movie_id,
            "imdb_id" : details.get("imdb_id"),
            "original_language" : details.get("original_language"),
            "popularity" : details.get("popularity"),
            "overview" : details.get("overview"), 
            "budget" : details.get("budget"),
            "country": details.get("origin_country"),
            "production_companies" : [c["name"] for c in details.get("production_companies", [])] if details.get("production_companies") else [],
            "revenue" : details.get("revenue"),
            "vote_average" : details.get("vote_average"),
            "vote_count" : details.get("vote_count"),
            "cast": [{"name": c["name"], "gender": c["gender"], "pop": c["popularity"]} for c in details.get("credits", {}).get("cast",[])[:10]] if details.get("credits", {}).get("cast") else {} # main 10 actors
        }
    else : # If API Error
        return None

def fetch_full_movie_data(imdb_id):
    """Fonction maître"""
    
    tmdb_id = get_tmdb_id(imdb_id)

    if tmdb_id is None:
        return {"status": "api_error", "imdb_id": imdb_id, "data": None}
    elif tmdb_id == 0:
        return {"status": "not_found", "imdb_id": imdb_id, "data": None}
    else:
        details = get_movie_details(tmdb_id)
        if details:
            return {"status": "success", "imdb_id": imdb_id, "data": details}
        else:
            return {"status": "api_error_details", "imdb_id": imdb_id, "data": None}

def save_batch(data_list, folder, prefix, batch_idx):
    """Fonction utilitaire pour sauvegarder une liste si elle n'est pas vide."""
    if data_list:
        df = pd.DataFrame(data_list)

        # --- BLOC DE SÉCURISATION ---
        # On identifie les colonnes qui contiennent des listes ou des objets complexes et on les convertit en chaîne de caractères JSON.
        complex_cols = ["cast", "production_companies"]
        
        for col in complex_cols:
            if col in df.columns:
                df[col] = df[col].astype(str)
        # ----------------------------

        filename = os.path.join(folder, f"{prefix}_{batch_idx:04d}.parquet")
        df.to_parquet(filename, engine='pyarrow')
        print(f"   -> Sauvegardé {filename} ({len(df)} lignes)")

def process_in_batches(full_id_list, batch_size=1000, max_workers=10):
    """
    Traite la liste de films par paquet
    """
    total_processed = 0
    total_films = len(full_id_list)

    # On découpe la liste géante en petits morceaux (chunks)
    # Ex: liste[0:1000], puis liste[1000:2000]...
    chunks = [full_id_list[i:i + batch_size] for i in range(0, total_films, batch_size)]

    print(f"Début du traitement : {total_films} films répartis en {len(chunks)} paquets.")

    for chunk_index, chunk in enumerate(chunks):
        print(f"--- Traitement du paquet {chunk_index + 1}/{len(chunks)} ---")
        
        # 3 Buffers temporaires pour ce paquet
        batch_success = []
        batch_notfound = []
        batch_errors = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            
            # Ici, on ne crée que 'batch_size' (ex: 1000) futures. C'est safe pour la RAM.
            future_to_imdb = {executor.submit(fetch_full_movie_data, mid): mid for mid in chunk}
            
            for future in as_completed(future_to_imdb):
                imdb_id = future_to_imdb[future]
                try:
                    # C'est ici qu'on récupère le résultat.
                    # Si fetch_full_movie_data a crashé (bug imprévu), ça saute au 'except'.
                    result = future.result() 

                    # TRI DES RÉSULTATS
                    if result["status"] == "success":
                        batch_success.append(result["data"])
                    
                    elif result["status"] == "not_found":
                        batch_notfound.append({"imdb_id": result["imdb_id"]})
                    
                    else: # api_error
                        batch_errors.append({"imdb_id": result["imdb_id"], "reason": result.get("reason")})

                except Exception as e:
                    print(f"CRITICAL WORKER CRASH sur {imdb_id}: {e}")
                    batch_errors.append({"imdb_id": imdb_id, "reason": f"system_crash: {str(e)}"})

        # À la fin du paquet, on sauvegarde immédiatement
        save_batch(batch_success, OUTPUT_DIR_SUCCESS, "data", chunk_index)
        save_batch(batch_notfound, OUTPUT_DIR_NOTFOUND, "notfound", chunk_index)
        save_batch(batch_errors, OUTPUT_DIR_ERRORS, "errors", chunk_index)
        
        # Nettoyage explicite
        del batch_success, batch_notfound, batch_errors


# --- EXECUTION ---
if __name__ == "__main__":


    OUTPUT_DIR_SUCCESS = "projet_python_films/Data processing/tmdb_results/success"
    OUTPUT_DIR_NOTFOUND = "projet_python_films/Data processing/tmdb_results/not_found"
    OUTPUT_DIR_ERRORS = "projet_python_films/Data processing/tmdb_results/errors"

    # Création des 3 dossiers
    os.makedirs(OUTPUT_DIR_SUCCESS, exist_ok=True)
    os.makedirs(OUTPUT_DIR_NOTFOUND, exist_ok=True)
    os.makedirs(OUTPUT_DIR_ERRORS, exist_ok=True)

    API_KEY = "1d48b5e24b27cd111582c21dcff9b8f5"
    BASE_URL = "https://api.themoviedb.org/3"

    thread_local = threading.local()

    chemin_parquet = 'projet_python_films/Data processing/IMDB_movie_ratings.parquet'

    try:
        print("Chargement ultra-rapide du Parquet...")
        df_source = pd.read_parquet(chemin_parquet, engine='pyarrow')
        # Extraction de la liste des IDs
        imdb_id_list = df_source['tconst'].unique().tolist()
        print(f"Prêt ! {len(imdb_id_list)} films chargés.")

    except FileNotFoundError:
        print("Fichier introuvable. Lance le script de préparation d'abord.")

    # Supposons que c'est la liste à parcourir
    #imdb_id_list = ["tt0133093", "tt0137523", "tt0068646", "tt_ID_FOIREUX"] * 3000  
    # On lance par paquets
    process_in_batches(imdb_id_list, batch_size=2000, max_workers=10)

print('Scraping terminé')