from flask_restful import Resource, reqparse, fields, marshal
from flasgger import swag_from
from datetime import datetime
from bson.objectid import ObjectId
from app.resources.types import ObjectIdType
from app import db


author_field = {
    'name': fields.String,
    '_id': fields.String(attribute=lambda x: x['_id']),
    'created_at': fields.DateTime(dt_format='iso8601')
}

author_parser = reqparse.RequestParser()
author_parser.add_argument('name', type=str, required=True, location=['json'],
                            help='name parameter is required')

class AuthorResource(Resource):
    @swag_from('../docs/author/get_all.yml', endpoint='author_post_and_get_all')
    @swag_from('../docs/author/get_one_id.yml', endpoint='author_get_one_id')
    def get(self, author_id=None):
        if author_id:
            if not ObjectIdType.validate_objectid_type(author_id):
                return {"message": "'{}' is not a valid id".format(author_id)}, 400
                
            authors = db.author.find_one({'_id': ObjectId(author_id)})
        else:
            authors = db.author.find()

        if not authors:
            return {"message": "authors not found"}, 404

        if author_id:
            return marshal(authors, author_field), 200
        authors = [marshal(author, author_field) for author in authors]
        return authors, 200

    @swag_from('../docs/author/post.yml', endpoint='author_post_and_get_all')
    def post(self):
        data = author_parser.parse_args()
        data['created_at'] = datetime.now()
        db.author.insert_one(data)
        return marshal(data, author_field), 201