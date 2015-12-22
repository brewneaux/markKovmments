#!/usr/bin/env python

import os
import markovify
from flask import Flask
from flask_restful import Resource, Api
import ConfigParser
import argparse

MARKOV_DB_LOCATION = '~/markov_db'
REPO_LIST_LOCATION = '~/repo_list'
DEBUG = False
CHAIN = None
TXT = None
DEFAULT_MAX_OVERLAP_RATIO = 0.7
DEFAULT_MAX_OVERLAP_TOTAL = 15
DEFAULT_TRIES = 10

app = Flask(__name__)
api = Api(app)

class customText(markovify.Text):
    def make_sentence(self, init_state=None, **kwargs):
        """
        Attempts `tries` (default: 10) times to generate a valid sentence,
        based on the model and `test_sentence_output`. Passes `max_overlap_ratio`
        and `max_overlap_total` to `test_sentence_output`.
        If successful, returns the sentence as a string. If not, returns None.
        If `init_state` (a tuple of `self.chain.state_size` words) is not specified,
        this method chooses a sentence-start at random, in accordance with
        the model.
        """
        tries = kwargs.get('tries', 10)
        mor = kwargs.get('max_overlap_ratio', DEFAULT_MAX_OVERLAP_RATIO)
        mot = kwargs.get('max_overlap_total', DEFAULT_MAX_OVERLAP_TOTAL)

        for _ in range(tries):
            words = [w.replace('.', '') for w in self.chain.walk(init_state)]
            if self.test_sentence_output(words, mor, mot) and len(words) < 10 and len(words) > 2:
                return self.word_join(words)
            else: continue
        return None


class GetSentence(Resource):
    def __init__(self, mark):
        self.txt = mark

    def get(self):
        return self.txt.make_sentence()

class SeeRepoList(Resource):
    def __init__(self, repo_list_location):
        self.repo_list_location = repo_list_location;

    def get(self):
        return open(os.path.expanduser(self.repo_list_location)).read()



def main():
    global MARKOV_DB_LOCATION
    global REPO_LIST_LOCATION
    global CHAIN
    global TXT
    global DEBUG 

    parser = argparse.ArgumentParser(description='Serve up some sentences like they are hot sandwhiches.')

    parser.add_argument('--config',
        help='Config file location')

    args = parser.parse_args()
    config_path = 'config.ini'
    if args.config:
        config_path = args.config
        print "Config path: {}".format(config_path)

    if os.path.isfile(config_path):
        Config = ConfigParser.ConfigParser()
        Config.read(config_path)
        if Config.get('main', 'markov_db_location'):
            MARKOV_DB_LOCATION = Config.get('main', 'markov_db_location')
        if Config.get('main', 'repo_list_location'):
            REPO_LIST_LOCATION = Config.get('main', 'repo_list_location')

    CHAIN = open(os.path.expanduser(MARKOV_DB_LOCATION)).read()
    TXT = customText.from_chain(CHAIN)

    api.add_resource(GetSentence, '/get_sentence', resource_class_kwargs=dict(mark=TXT))
    api.add_resource(SeeRepoList, '/get_repo_list', resource_class_kwargs=dict(repo_list_location=REPO_LIST_LOCATION))

    # app.run(host='0.0.0.0', port=10080)
    app.run(debug=True)

if __name__ == '__main__':
    main()

