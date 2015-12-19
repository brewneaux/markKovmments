#!/usr/bin/env python

import os
import markovify
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class GetSentence(Resource):
    def __init__(self, mark):
        self.txt = mark

    def get(self):
        return self.txt.make_sentence()

class SeeRepoList(Resource):
    def get(self):
        return open(os.path.expanduser('~/repo_list')).read()


chain = open(os.path.expanduser('~/markov_db')).read()
txt = markovify.Text.from_chain(chain)

api.add_resource(GetSentence, '/get_sentence', resource_class_kwargs=dict(mark=txt))
api.add_resource(SeeRepoList, '/get_repo_list')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10080)
