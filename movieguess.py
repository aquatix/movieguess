from __future__ import print_function

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


@app.route('/')
def index():
    return jsonify({'message': 'Please see https://github.com/aquatix/movieguess for documentation'})


@app.route('/tmdb/<appkey>/random')
def randommovie(appkey):
    print(appkey)
    print(settings.APPKEY)
    if appkey != settings.APPKEY:
        abort(403)

    page = 4  # certified random
    url = 'https://api.themoviedb.org/3/discover/movie?api_key={}&include_adult=false&vote_average.gte={}&with_runtime.gte={}&page={}'.format(settings.TMDB_API, settings.VOTE_AVERAGE, settings.RUNTIME_MINIMUM, page)
    print(url)
    movielist = requests.get(url)
    if movielist.status_code != 200:
        result = {'message': 'Get an error {} from the TMDB backend'.format(movielist.status_code)}
    else:
        print(movielist.json())
        movies = movielist.json()['results']
        result = movies[4]  # Still random
        #result = {'message': 'not implemented yet'}
    return jsonify(result)


# Run when called standalone
if __name__ == '__main__':
    # run the application
    app.run(port=9999, debug=True)