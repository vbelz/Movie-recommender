from fuzzywuzzy.process import extract
import numpy as np
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import sklearn.utils
from sqlalchemy import create_engine
from sklearn.decomposition import NMF


class Recommender:

    def __init__(self, nb_movies, movie_list, ratings_list):
        """ Getting the number of movies to recommend, the movie
        list and associated rating from the user """
        self.nb_movies = nb_movies
        self.movie_list = movie_list
        self.ratings_list = ratings_list

    def __repr__(self):
        return f"""The User will have {self.nb_movies} movies recommended,
        his movie list is {self.movie_list} with rating {self.ratings_list}"""

    def read_db_get_predictions(self):
        """ Here is where we take the user input (movie_list, ratings_list)
        and use them as inputs to the model for prediction. """

        engine_lite = create_engine('sqlite:///data/movielens.db')

        df_data = pd.read_sql_query("SELECT * FROM movie_ratings;", engine_lite)

        #List of id movie
        list_id_movies = df_data['movieId'].unique()
        #List of title
        list_title_movies = df_data.groupby('movieId')['title'].first().values
        #dictionary id to title
        movie_id_to_title_dictionary = dict(zip(list_id_movies, list_title_movies))
        #dictionary title to id
        movie_title_to_id_dictionary = dict(zip(list_title_movies, list_id_movies))

        user_id_movies = self.get_movie_id_for_user(self.movie_list, list_title_movies, movie_title_to_id_dictionary)

        new_vector = self.create_vector_new_user(user_id_movies, self.ratings_list, list_id_movies)

        #movies_to_recommend = self.prediction_nmf(new_vector, self.nb_movies, list_id_movies, movie_id_to_title_dictionary, df_data)

        movies_to_recommend = self.prediction_cosim(new_vector, self.nb_movies, list_id_movies, user_id_movies, movie_id_to_title_dictionary, df_data)

        return movies_to_recommend

    def get_movie_id_for_user(self, user_movie, list_title_movies, title_to_id_dictionary):
        """ This function takes as input the movies typed by the user.
        for each movie, get the closest movie in the movies list (typing mistakes are
        taken into account) and return the list of movies id number"""
        user_id_movie = []

        for m in user_movie:

            id_m = title_to_id_dictionary[extract(m, list_title_movies)[0][0]]
            user_id_movie.append(id_m)

        return user_id_movie

    def create_vector_new_user(self, user_id_movies, user_ratings, list_id_movies):
        """This function takes the id of the user movies and the id of all movies
        and create the rating vector for prediction"""
        empty_list = [np.nan] * len(list_id_movies)
        ratings_dict = dict(zip(list_id_movies, empty_list))

        for u_movie_id, u_rating in zip(user_id_movies,user_ratings):

            ratings_dict[u_movie_id] = float(u_rating)

        new_vector = list(ratings_dict.values())

        return new_vector

    def prediction_cosim(self, new_vector, N, list_id_movies, user_id_movies, movie_id_to_title_dictionary, df_data):
        """ This function takes the movie vector from user rating
        and predict the top N movie id to recommend based on cosine similarities
        (it picks N movies among the top ranked movies of the three closest other users) """

        new_vector = pd.DataFrame(new_vector, index=list_id_movies).T

        matrix = pd.pivot_table(df_data, 'rating', 'userId', 'movieId')


        print(new_vector)

        # Centered to have magnitude taken into account for cosine similarity
        matrix.fillna(3.0, inplace=True)
        matrix = (matrix - 3.0)/2.0
        #List of users from the database
        list_id_users = matrix.index

        vector_filled_for_cosine = new_vector.fillna(3.0)
        vector_filled_for_cosine = (vector_filled_for_cosine - 3.0)/2.0
        #Label for new user to select it easily
        vector_filled_for_cosine.index = ['new_user']

        #concatenate the new user
        matrix_w_new_user = pd.concat([matrix,vector_filled_for_cosine])
        cos_matrix_user = cosine_similarity(matrix_w_new_user)
        cos_matrix_user = pd.DataFrame(cos_matrix_user, index=matrix_w_new_user.index, columns=matrix_w_new_user.index)

        #Get cosine similarity of new users with other users
        cosim_new_user = cos_matrix_user['new_user'].iloc[:-1]
        #Take the 3 closest users
        most_similar = cosim_new_user.nlargest(3).index.values

        #Get N*3*2 possibilities of movies to recommend with associated scores

        movie_id_to_rec = []
        score_of_rec = []

        for id_user in most_similar:
            movie_id_to_rec.extend(matrix.loc[id_user].nlargest(N*2).index)
            score_of_rec.extend(matrix.loc[id_user].nlargest(N*2).values)

        df_recommend = {'id_movie': movie_id_to_rec, 'score': score_of_rec}
        df_recommend = pd.DataFrame(df_recommend)

        #Shuffle to select among unordered top movies (in term of movie id)
        df_recommend = sklearn.utils.shuffle(df_recommend)
        #Order then from top scored movies
        df_recommend = df_recommend.sort_values(by='score',ascending=False)
        #list of movies id to recommend
        list_id_to_recommend = df_recommend['id_movie'].unique()

        #Transform back the movie ids to Title for recommendation
        movie_to_recommend = []

        for id_nb in list_id_to_recommend:
            #Returning N movies not rated by the user
            if (id_nb not in user_id_movies) and (len(movie_to_recommend) < N) :

                movie_to_recommend.append(movie_id_to_title_dictionary[id_nb])

        return movie_to_recommend

    def prediction_nmf(self, new_vector, N, list_id_movies, movie_id_to_title_dictionary, df_data):
        """ This function takes the movie vector from user rating
        and predict the top N movie id to recommend based on NMF model
        previously trained on the full database"""
        data_folder = './data/'
        if not os.path.exists(data_folder+'nmf_model_rating.bin'):
                nmf = self.train_nmf_model(df_data)

        else:

            binary = open(data_folder+'nmf_model_rating.bin', 'rb').read()
            nmf = pickle.loads(binary)

        new_vector = pd.DataFrame(new_vector, index=list_id_movies).T

        print(new_vector)

        new_user_vector_filled = new_vector.fillna(2.5)
        hidden_profile = nmf.transform(new_user_vector_filled)
        ypred = nmf.inverse_transform(hidden_profile)

        vector_pred = pd.DataFrame(ypred.reshape(-1), index=list_id_movies).T


        #Exclude the rated movies for recommendation
        mask = np.isnan(new_vector)

        non_rated_movies = vector_pred[mask]

        top_id_movies = non_rated_movies.T.sort_values(by=[0], ascending=False).index[:N]

        #Transform back the movie ids to Title for recommendation
        movie_to_recommend = []

        for id_nb in top_id_movies:

            movie_to_recommend.append(movie_id_to_title_dictionary[id_nb])

        return movie_to_recommend

        def train_nmf(self, df_data):
            """ train nmf model and save to disk """
            #Get pivot tabme userId, movieId and ratings
            df_pivot = pd.pivot_table(df_merge, 'rating', 'userId', 'movieId')

            #Fill Nan with median per movie:
            df_pivot.fillna(df_pivot.median(), inplace=True)

            model = NMF(n_components=25, max_iter=500)
            model.fit(df_pivot)

            binary = pickle.dumps(m)
            open(data_folder+'nmf_model_rating.bin', 'wb').write(binary)

        return
