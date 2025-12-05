import pandas as pd

##### Dataset: IMDB non commercial datasets, récupérationn de CSV opensource des films IMDB et des données de ratings #####
####Téléchargement des fichiers compressés TSV depuis IMDB####
title_basics_url= 'https://datasets.imdbws.com/title.basics.tsv.gz'
title_ratings_url= 'https://datasets.imdbws.com/title.ratings.tsv.gz'
title_crew_url='https://datasets.imdbws.com/title.crew.tsv.gz'
crew_names_url='https://datasets.imdbws.com/name.basics.tsv.gz'

####Import des dataframes des datasets IMDB####
df_imdb_title_id= pd.read_csv(title_basics_url, sep='\t', na_values='\\N') #données générales: thème, langues...
df_imdb_ratings = pd.read_csv(title_ratings_url, sep='\t', na_values='\\N') #notation des films
df_imdb_crew=pd.read_csv(title_crew_url, sep='\t', na_values='\\N') #réalisateurs et scénaristes
df_imdb_names=pd.read_csv(crew_names_url, sep='\t', na_values='\\N') #noms des réalisateurs et scénaristes en fonction de leur ID nconst


####Jointure des infos sur les réalisateurs et associations de leurs noms à leurs ID####
df_imdb_names.rename(columns={'nconst':'directors'}, inplace=True) 

df_imdb_directors=pd.DataFrame()
df_imdb_directors=pd.merge(df_imdb_crew, df_imdb_names,on='directors', how='left') #Association nom ID

df_imdb_directors.drop(columns=['writers','knownForTitles'], inplace=True) #Retrait des colonnes non pertinentes
df_imdb_directors.rename(columns={'directors':'directors_id','primaryName':'director_name'}, inplace=True) #distinction ID réalisateur


#### Merge des dataframes titres et ratings pour associer aux films leurs notes IMDB avec titres et ID: plus de 1.6 million de films notés ####
df_imdb_ratings=pd.merge(df_imdb_ratings, df_imdb_title_id, on='tconst', how='left')

####Cleaning du dataframe merged####
df_imdb_ratings.drop(columns=['primaryTitle'], inplace=True)
df_imdb_ratings.sort_values(by='startYear')


####Réduction du champ d'études du dataframe aux longs métrages####
mask_movies=df_imdb_ratings["titleType"]=="movie"
df_movie_ratings=df_imdb_ratings.loc[mask_movies]
df_movie_ratings.drop(columns=['titleType','endYear'], inplace=True)
df_movie_ratings.rename(columns={'startYear':'release_year'}, inplace=True)


####Association des réalisateurs aux films####
df_movie_ratings_complete=df_movie_ratings.copy()
df_movie_ratings_complete=pd.merge(df_movie_ratings_complete, df_imdb_directors, on='tconst',how='left')
df_movie_ratings_complete.reset_index(drop=True, inplace=True)

####Retrait des lignes avec valeurs manquantes, non pertinentes: seuil <10% en valeurs perdues, pas d'anomalie####
mask_nanruntime=df_movie_ratings_complete['runtimeMinutes'].isna()
mask_nandirector=df_movie_ratings_complete['director_name'].isna()
mask_nangenres=df_movie_ratings_complete['genres'].isna()
mask_nanreleaseyear=df_movie_ratings_complete['release_year'].isna()
df_movie_ratings_complete=df_movie_ratings_complete.loc[~(mask_nanruntime | mask_nandirector | mask_nangenres | mask_nanreleaseyear)]


###Retrait de colonnes non pertinentes####
df_movie_ratings_complete.drop(columns=['tconst','directors_id','birthYear','deathYear'], inplace=True)

df_movie_ratings_complete.to_csv('projet_python_films/Data processing/IMDB_movie_ratings.csv', index=False)