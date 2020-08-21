import os
import pymongo
from flask import Flask
from flask_restful import Api
from flasgger import Swagger


app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'News Api',
    'version': '1.0.0',
    'specs_route': '/docs/'
}
swag = Swagger(app)
api = Api(app)
api.prefix = '/api'

client = pymongo.MongoClient(os.environ["DB_PORT_27017_TCP_ADDR"], 27017)
db = client.news


from app.resources.authors import AuthorResource
from app.resources.posts import PostResource

api.add_resource(AuthorResource, '/authors/<author_id>', endpoint='author_get_one_id')
api.add_resource(AuthorResource, '/authors', endpoint='author_post_and_get_all')

api.add_resource(PostResource, '/posts/<post_id>', endpoint='posts_get_one_put_delete')
api.add_resource(PostResource, '/posts', endpoint='posts_post_and_get_all')
api.add_resource(PostResource, '/posts/', endpoint='posts_by_title')