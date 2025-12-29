### Script qui récupère les données TMDB et IMDB pour fusionner les datraframe et sortir un seul df utilisable

import pandas as pd
import pyarrow

df_TMDB = pd.read_parquet("tmdb_results/success", engine="pyarrow")
df_IMDB = pd.read_parquet("IMDB_movie_ratings.parquet", engine="pyarrow")

df_alldata = pd.merge(
    df_IMDB,
    df_TMDB,
    how='left',
    left_on='tconst',
    right_on='imdb_id'
)

pd.set_option('display.max_columns', None)
df_alldata.drop(columns='imdb_id', inplace=True)
df_alldata.rename(columns={
    'vote_average': 'vote_average_TMDB',
    'vote_count': 'vote_count_TMDB',
    'popularity': 'popularity_TMDB',
    'numVotes': 'numVotes_IMDB',
    'averageRating': 'averageRating_IMDB'
    },
    inplace=True)

df_alldata.to_parquet('data_IMDB_TMDB_join.parquet',engine='pyarrow')