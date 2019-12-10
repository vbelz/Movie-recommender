import os
import re
import pandas as pd
from sqlalchemy import create_engine


data_folder = './data/'

#movie and rating csv from https://grouplens.org/datasets/movielens/
df_movies = pd.read_csv(data_folder+'movies.csv')
df_ratings = pd.read_csv(data_folder+'ratings.csv')

#Choose if you want to save as sqlite or postgres
Save_to_postgres = False
Save_to_sqlite = True

df_merge = pd.merge(df_ratings, df_movies, how='outer', left_on='movieId', right_on='movieId')

def get_year(x):
    '''Extract year from title'''
    y = re.findall("\(([0-9]{4})\)", x)
    try:
        y = y[0]
    except:
        y = 0
    return y

#Extract year from title and add in a separate column
df_merge['year'] = df_merge['title'].apply(get_year)
#romve year from title
df_merge['title'] = df_merge['title'].str.replace("\(([0-9]{4})\)","")
#Select columns to keep
cols = ['userId','movieId','rating','title','genres','year','timestamp']
df_merge = df_merge[cols]

#Sort increasing order
df_merge.sort_values(by=['movieId'], inplace=True)
#Remove movies without any rating at all
df_merge.dropna(subset=['userId'], how='any',inplace=True)


#Save to postgres
if Save_to_postgres:

    HOST = 'localhost'
    PORT = '5432'
    DBNAME = 'movielens'
    connection_string_short = f'postgres://{HOST}:{PORT}/{DBNAME}'
    db = create_engine(connection_string_short)
    df_merge.to_sql('movies_ratings', db)

#Save to a sqlite file
if Save_to_sqlite:

    engine_lite = create_engine('sqlite:///data/movielens.db')
    df_merge.to_sql('movie_ratings', engine_lite)

#Remove csv files from disk
os.remove(data_folder+'movies.csv')
os.remove(data_folder+'ratings.csv')
