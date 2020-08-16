import pymongo
import json
from flask_restful import Resource, reqparse
from bson import json_util
from app import db, get_next_sequence


post_parser = reqparse.RequestParser()
post_parser.add_argument('author_id', type=int, required=True, location=['json'],
                            help='author_id parameter is required')
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
                'localField': 'author_id',
                'foreignField': '_id',
                'as': 'author'}}
        ]))
        if len(data) == 1:
            return data[0]
        return data

    def get(self, post_id=None):
        title_args = post_title_query_parser.parse_args().get('title')
        if title_args:
            posts_result = self._post_aggregate({'title': title_args})
        
        elif post_id:
            posts_result = self._post_aggregate({'_id': post_id})
        
        else:
            post_id = [id['_id'] for id in db.posts.find()]
            posts_result = []
            for id in post_id:
                posts_result.append(self._post_aggregate({'_id': id}))

        return json.loads(json_util.dumps(posts_result)), 200

    def post(self):
        data = post_parser.parse_args()
        author = db.author.find_one({'_id': data['author_id']})
        if not author:
            return {"message": "author id not found"}, 404

        data['_id'] = get_next_sequence(db.post_autoincrement_counter,"post_id")
        data['author_id'] = author['_id']

        db.posts.insert_one(data)
        return json.loads(json_util.dumps(data)), 201

    def put(self, post_id):
        data = post_parser.parse_args()
        author = db.author.find_one({'_id': data['author_id']})
        if not author:
            return {"message": "author id not found"}, 404

        post = db.posts.find_one_and_update(
            {'_id': post_id},
            {'$set': data},
            return_document=pymongo.ReturnDocument.AFTER
        )
        
        if not post:
            return {"message": "post not found"}, 404

        return json.loads(json_util.dumps(post)), 200

    def delete(self, post_id):
        data = db.posts.find_one_and_delete({'_id': post_id})
        if not data:
            return {"message": "post not found"}, 404
        return json.loads(json_util.dumps(data)), 200