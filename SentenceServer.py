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

app = Flask(__name__)
api = Api(app)

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
    TXT = markovify.Text.from_chain(CHAIN)

    api.add_resource(GetSentence, '/get_sentence', resource_class_kwargs=dict(mark=TXT))
    api.add_resource(SeeRepoList, '/get_repo_list', resource_class_kwargs=dict(repo_list_location=REPO_LIST_LOCATION))

    # app.run(host='0.0.0.0', port=10080)
    app.run(debug=True)

if __name__ == '__main__':
    main()

