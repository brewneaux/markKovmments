#!/usr/bin/env python

import os
from pymarkovchain import MarkovChain
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class GetSentence(Resource):
    def __init__(self, chain):
        print 'Loading chain...'
        self.mc = chain
        print 'Chain loaded, running.'

    def get(self):
        print self.mc.generateString()
        return self.mc.generateString()

mc = MarkovChain(os.path.expanduser("~/markov_db"))
api.add_resource(GetSentence, '/', resource_class_kwargs=dict(chain=mc))

if __name__ == '__main__':
    print mc.generateString()
    app.run(debug=True)