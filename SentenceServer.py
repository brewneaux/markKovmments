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


print 'Loading chain...'
chain = open(os.path.expanduser('~/markov_db')).read()
txt = markovify.Text.from_chain(chain)
print 'Chain loaded'

api.add_resource(GetSentence, '/get_sentence', resource_class_kwargs=dict(mark=txt))

if __name__ == '__main__':
    app.run(debug=False)