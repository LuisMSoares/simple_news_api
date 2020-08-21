import pymongo
from flask_restful import Resource, reqparse, fields, marshal
from flasgger import swag_from
from datetime import datetime
from bson.objectid import ObjectId
from app.resources.types import ObjectIdType
from app import db


posts_field = {
    '_id': fields.String(attribute=lambda x: x['_id']),
    'title': fields.String(),
    'content': fields.String(),
    'created_at': fields.DateTime(dt_format='iso8601'),
    'modified_at': fields.DateTime(dt_format='iso8601'),
    'author': {
        '_id': fields.String(attribute=lambda x: x['author_data'][0]['_id']),
        'name': fields.String(attribute=lambda x: x['author_data'][0]['name'])
    }
}
delete_posts_field = {
    '_id': fields.String(attribute=lambda x: x['_id']),
    'title': fields.String(),
    'content': fields.String(),
    'created_at': fields.DateTime(dt_format='iso8601'),
    'modified_at': fields.DateTime(dt_format='iso8601')
}

post_parser = reqparse.RequestParser()
post_parser.add_argument('author', type=ObjectIdType(), required=True, location=['json'],
                            help='a valid author_id parameter is required')
post_parser.add_argument('title', type=str, required=True, location=['json'],
                            help='title parameter is required')
post_parser.add_argument('content', type=str, required=True, location=['json'],
                            help='content parameter is required')

post_title_query_parser = reqparse.RequestParser()
post_title_query_parser.add_argument('title', type=str, location=['args'],
                            help='search a post by title')

class PostResource(Resource):
    def _post_aggregate(self, match):
        data = list(db.posts.aggregate([
            {'$match': match},
            {'$lookup': {
                'from': 'author',
                'localField': 'author',
                'foreignField': '_id',
                'as': 'author_data'}}
        ]))
        if len(data) == 1:
            return data[0]
        return data

    @swag_from('../docs/posts/get_all.yml', endpoint='posts_post_and_get_all')
    @swag_from('../docs/posts/get_all_by_title.yml', endpoint='posts_by_title')
    @swag_from('../docs/posts/get_one_id.yml', endpoint='posts_get_one_put_delete')
    def get(self, post_id=None):
        title_args = post_title_query_parser.parse_args().get('title')
        if title_args:
            posts_result = self._post_aggregate({'title': title_args})
            posts_result = marshal(posts_result, posts_field)
        
        elif post_id:
            if not ObjectIdType.validate_objectid_type(post_id):
                return {"message": "'{}' is not a valid id".format(post_id)}, 400
            posts_result = self._post_aggregate({'_id': ObjectId(post_id)})
            posts_result = marshal(posts_result, posts_field)
        
        else:
            post_id = [id['_id'] for id in db.posts.find()]
            posts_result = []
            for id in post_id:
                post = self._post_aggregate({'_id': id})
                post = marshal(post, posts_field)
                posts_result.append(post)
        
        if not posts_result:
            return {"message": "posts not found"}, 404

        return posts_result, 200

    @swag_from('../docs/posts/post.yml', endpoint='posts_post_and_get_all')
    def post(self):
        data = post_parser.parse_args()
        author = db.author.find_one({'_id': ObjectId(data['author'])})
        if not author:
            return {"message": "author not found"}, 404

        data['author'] = ObjectId(author['_id'])
        data['created_at'] = datetime.now()
        data['modified_at'] = datetime.now()
        db.posts.insert_one(data)

        data['author_data'] = [author]
        
        return marshal(data, posts_field), 201

    @swag_from('../docs/posts/put.yml', endpoint='posts_get_one_put_delete')
    def put(self, post_id=None):
        if not ObjectIdType.validate_objectid_type(post_id):
            return {"message": "'{}' is not a valid id".format(post_id)}, 400

        data = post_parser.parse_args()
        author = db.author.find_one({'_id': ObjectId(data['author'])})
        if not author:
            return {"message": "author not found"}, 404
        
        data['author'] = ObjectId(author['_id'])
        data['modified_at'] = datetime.now()
        post = db.posts.find_one_and_update(
            {'_id': ObjectId(post_id)},
            {'$set': data},
            return_document=pymongo.ReturnDocument.AFTER
        )
        
        if not post:
            return {"message": "posts not found"}, 404

        post['author_data'] = [author]
        return marshal(post, posts_field), 200

    @swag_from('../docs/posts/delete.yml', endpoint='posts_get_one_put_delete')
    def delete(self, post_id=None):
        if not ObjectIdType.validate_objectid_type(post_id):
            return {"message": "'{}' is not a valid id".format(post_id)}, 400

        data = db.posts.find_one_and_delete({'_id': ObjectId(post_id)})
        if not data:
            return {"message": "posts not found"}, 404
        return marshal(data, delete_posts_field), 200