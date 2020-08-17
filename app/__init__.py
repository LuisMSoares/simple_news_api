import os
import pymongo
from flask import Flask
from flask_restful import Api


app = Flask(__name__)
api = Api(app)
api.prefix = '/api'

client = pymongo.MongoClient(os.environ["DB_PORT_27017_TCP_ADDR"], 27017)
db = client.news


from app.resources.authors import AuthorResource
from app.resources.posts import PostResource

api.add_resource(AuthorResource, '/authors', '/authors/', '/authors/<author_id>')
api.add_resource(PostResource, '/posts', '/posts/', '/posts/<post_id>')