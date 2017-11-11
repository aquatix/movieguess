from __future__ import print_function

import random
import sys

from flask import Flask, abort, jsonify

import requests

try:
    import settings
except ImportError:
    print('Copy settings_example.py to settings.py and set the configuration to your own preferences')
    sys.exit(1)


# Create our Flask app
app = Flask(__name__)
app.config.from_object(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def get_credits(movie_id):
    url = 'https://api.themoviedb.org/3/movie/{}/credits?api_key={}'.format(movie_id, settings.TMDB_API)
    result = requests.get(url)
    if result.status_code == 200:
        return result.json()
    else:
        return []


@app.route('/')
def index():
    return jsonify({'message': 'Please see https://github.com/aquatix/movieguess for documentation'})


@app.route('/tmdb/<appkey>/movie/tmdb/<movie_id>')
def tmdb_movie(appkey, movie_id):
    if appkey != settings.APPKEY:
        abort(403)

    url = 'https://api.themoviedb.org/3/movie/{}?api_key={}'.format(movie_id, settings.TMDB_API)
    result = requests.get(url)
    if result.status_code == 200:
        movie = result.json()
        credits = get_credits(movie['id'])
        movie['cast'] = credits['cast']
        movie['crew'] = credits['crew']
        return jsonify(movie)
    else:
        raise InvalidUsage('Movie not found in TMDB', status_code=410)


@app.route('/tmdb/<appkey>/random')
def randommovie(appkey):
    if appkey != settings.APPKEY:
        abort(403)

    page = random.randint(1, 1000)  # Maximum page is 1000
    url = 'https://api.themoviedb.org/3/discover/movie?api_key={}&include_adult=false&vote_average.gte={}&with_runtime.gte={}&page={}'.format(settings.TMDB_API, settings.VOTE_AVERAGE, settings.RUNTIME_MINIMUM, page)
    print(url)
    movielist = requests.get(url)
    if movielist.status_code != 200:
        result = {'message': 'Get an error {} from the TMDB backend'.format(movielist.status_code)}
    else:
        movies = movielist.json()['results']
        result = movies[random.randint(0, len(movies))]
        credits = get_credits(result['id'])
        result['cast'] = credits['cast']
        result['crew'] = credits['crew']
    return jsonify(result)


# Run when called standalone
if __name__ == '__main__':
    # run the application
    app.run(port=9999, debug=True)
