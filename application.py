from flask import Flask, render_template, request
from recommender import movie_recommender

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
    movie_list = movie_recommender(5, movies, ratings)
    print(movie_list)

    return render_template('results.html', movies=movie_list)
