# Movie-recommender
---
>
>
## Introduction

<img src="img/demo_movie_compressed.gif" alt="Demo website movie recommender" title="Movie recommender"/>

This project aims at building a movie recommender with a Flask web interface. You can visit the website at
this [link](http://vincentbelz.pythonanywhere.com).

The dataset of movies and ratings I will be using is the movielens dataset available at:

[https://www.ssa.gov/oact/babynames/limits.html](https://grouplens.org/datasets/movielens/)

## Prepare the database

I provide a sqlite database at `data/movielens.db` in order to run the program (this section can be skipped to test the recommender).

To update it regularly including new movies (or create your own database),

download `movies.csv` and `ratings.csv` from [https://www.ssa.gov/oact/babynames/limits.html](https://grouplens.org/datasets/movielens/) and place them in the folder `data`.

Then run `python prepare_database.py` (make sure you delete the old database before).

It will extract the year from movies title, clean the title with regex and merge them into a database containing
`['userId','movieId','rating','title','genres','year','timestamp']`. Then it will be saved as a sqlite database
in the folder `data`.

In the code there is the option to save it as a postgres database  as well (turn `Save_to_postgres` to True).
By default it will only be saved as a sqlite database (because it is the option i used to deploy on pythonanywhere
with the free plan).

Below, a word cloud created based on the appearance of movies genres in the database:

<img src="img/Word_cloud_movie_genre.png" alt="Word cloud movie genre" title="Movie genre word cloud"  />

## Flask web server

The python file that will house the instructions for launching a web server is
available at `application.py`



<img src="img/form_page.png" alt="website form" title="website form" />

## Movie recommendation

The *Recommender* class available at `recommender_tools.py` can predict movies recommendations
based on Non-negative matrix factorization (NMF) or cosine similarity.

<img src="img/result_page.png" alt="result page" title="Results page" />

## How to use?

```
Clone this repository
Make sure you have installed the packages in requirements.txt (pip install -r requirements.txt)
```

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

- **[MIT license](http://opensource.org/licenses/mit-license.php)**
