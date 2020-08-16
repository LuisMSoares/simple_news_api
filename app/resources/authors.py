import json
from flask_restful import Resource, reqparse
from bson import json_util
from app import db, get_next_sequence


author_parser = reqparse.RequestParser()
author_parser.add_argument('name', type=str, required=True, location=['json'],
                            help='name parameter is required')

class AuthorResource(Resource):
    def get(self, author_id=None):
        if author_id:
            authors = db.author.find_one({'_id': author_id})
        else:
            authors = db.author.find()

        return json.loads(json_util.dumps(authors)), 200

    def post(self):
        data = author_parser.parse_args()
        data['_id'] = get_next_sequence(db.author_autoincrement_counter,"author_id")
        db.author.insert_one(data)

        return json.loads(json_util.dumps(data)), 201