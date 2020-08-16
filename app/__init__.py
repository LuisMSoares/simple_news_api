import os
import pymongo
from flask import Flask
from flask_restful import Api


app = Flask(__name__)
api = Api(app)
api.prefix = '/api'

client = pymongo.MongoClient(os.environ["DB_PORT_27017_TCP_ADDR"], 27017)
db = client.news


try:
    db.post_autoincrement_counter.insert_one({'_id': "post_id", 'seq': 0})
    db.author_autoincrement_counter.insert_one({'_id': "author_id", 'seq': 0})
except pymongo.errors.DuplicateKeyError:
    pass
def get_next_sequence(collection, name):
    return collection.find_one_and_update(
        filter = {'_id': name},
        update = {'$inc': {'seq': 1}},
        return_document=pymongo.ReturnDocument.AFTER
    ).get('seq')


from app.resources.authors import AuthorResource
from app.resources.posts import PostResource

api.add_resource(AuthorResource, '/authors', '/authors/', '/authors/<int:author_id>')
api.add_resource(PostResource, '/posts', '/posts/', '/posts/<int:post_id>')