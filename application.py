from flask import Flask, render_template, request
from recommender_tools import Recommender

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recommender')
def recommender():
    return render_template('recommender.html')


@app.route('/results')
def results():
    user_input = request.args #some kind of dictionary-like object
    user_input = dict(user_input).values()

    movies = list(user_input)[::2] #list of strings
    ratings = list(user_input)[1::2] #list of strings
    print(movies)
    print(ratings)
    new_recommendation = Recommender(5, movies, ratings)
    movie_list = new_recommendation.read_db_get_predictions()
    print(movie_list)

    return render_template('results.html', movies=movie_list)
