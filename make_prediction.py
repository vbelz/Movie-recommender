from sqlalchemy import create_engine
import pandas as pd
import pickle
from fuzzywuzzy.process import extract
import numpy as np
from prediction_tools import get_movie_id_for_user
from prediction_tools import create_vector_new_user
from prediction_tools import prediction_nmf, prediction_cosim

engine_lite = create_engine('sqlite:///movielens.db')

df_data = pd.read_sql_query("SELECT * FROM movie_ratings;", engine_lite)

# user_movies = ['Gladiator', 'into the wild', 'seven years in thibet', 'toy story 2', 'Troy']
# user_ratings = ['5.0', '5.0', '4.0', '2.5', '4.5']

user_movies = ['Titanic', 'Jumanji', 'Lion', 'toy story 2', 'Terminator']
user_ratings = ['5.0', '4.0', '3.0', '1.5', '3.5']

#List of id movie
list_id_movies = df_data['movieId'].unique()
#List of title
list_title_movies = df_data.groupby('movieId')['title'].first().values
#dictionary id to title
movie_id_to_title_dictionary = dict(zip(list_id_movies,list_title_movies))
#dictionary title to id
movie_title_to_id_dictionary = dict(zip(list_title_movies,list_id_movies))

user_id_movies = get_movie_id_for_user(user_movies, list_title_movies, movie_title_to_id_dictionary)

new_vector = create_vector_new_user(user_id_movies, user_ratings, list_id_movies)

#movies_to_recommend = prediction_nmf(new_vector, 5, list_id_movies, movie_id_to_title_dictionary)

movies_to_recommend = prediction_cosim(new_vector, 5, list_id_movies, user_id_movies, movie_id_to_title_dictionary, df_data)

print(movies_to_recommend)
