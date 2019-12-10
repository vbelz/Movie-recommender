from sqlalchemy import create_engine
import pandas as pd
import pickle
import pytest
from fuzzywuzzy.process import extract
import numpy as np
from recommender_tools import Recommender

# user_movies = ['Gladiator', 'into the wild', 'seven years in thibet', 'toy story 2', 'Troy']
# user_ratings = ['5.0', '5.0', '4.0', '2.5', '4.5']

user_movies = ['Titanic', 'Jumanji', 'Lion', 'toy story 2', 'Terminator']
user_ratings = ['5.0', '4.0', '3.0', '1.5', '3.5']


recommender = Recommender(5, user_movies, user_ratings)

def test_input_recommender():
    """ test that values are correctly passed to the class"""
    assert recommender.nb_movies == 5
    assert recommender.movie_list == user_movies
    assert recommender.ratings_list == user_ratings


result = recommender.read_db_get_predictions()

def test_output_recommender():
    """ test that output is returned as expected """
    assert type(result) == list
    assert len(result) == 5
    assert type(result[0]) == str

print(result)
