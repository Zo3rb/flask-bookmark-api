from flask import Blueprint, jsonify, request
from jsonschema import validate, ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from urllib.parse import urlparse

from src import db
from src.bookmark.bookmark_validation import create_bookmark_schema
from src.bookmark.bookmark_model import Bookmark
from src.constants import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND

bookmark = Blueprint('bookmark', __name__, url_prefix='/api/v1/bookmarks')

@bookmark.route('/', methods=['GET', 'POST'])
@jwt_required()
def handle_bookmarks():

    """
        Protected Route
        an Endpoint to handle Adding a new Bookmark to the Database - POST
        or Getting all the bookmarks the current logged in user saved.
    """

    if request.method == 'POST':
        data = request.get_json()
        parsed_url = urlparse(data['url'])

        if not all([parsed_url.scheme, parsed_url.netloc]):
            return jsonify({'error': 'Invalid URL Format, Please provide a valid URL'}), HTTP_400_BAD_REQUEST

        try:
            validate(data, create_bookmark_schema)
        except ValidationError as errors:
            return jsonify({'error': str(errors.message)}), HTTP_400_BAD_REQUEST
        
        user_id = get_jwt_identity()
        new_bookmark = Bookmark(body=data['body'], url=data['url'], user_id=user_id)
        db.session.add(new_bookmark)
        db.session.commit()
        
        return jsonify({'data': new_bookmark.to_dict()}), HTTP_201_CREATED
    elif request.method == 'GET':
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        bookmarks = Bookmark.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page)
        data = []
        for bookmark in bookmarks.items:
            data.append({
                'id': bookmark.id,
                'body': bookmark.body,
                'url': bookmark.url,
                'short_url': bookmark.short_url,
                'visits': bookmark.visits,
                'user_id': bookmark.user_id,
                'created_at': bookmark.created_at,
                'updated_at': bookmark.updated_at
            })
        meta = {
            "page": bookmarks.page,
            'pages': bookmarks.pages,
            'total_count': bookmarks.total,
            'prev_page': bookmarks.prev_num,
            'next_page': bookmarks.next_num,
            'has_next': bookmarks.has_next,
            'has_prev': bookmarks.has_prev,

        }

        return jsonify({'data': data, 'meta': meta}), HTTP_200_OK
        

@bookmark.get('/<string:short_url>')
def handle_short(short_url):

    """
        an Endpoint to retrieve info of a Shorted link added to the database.
        Args:
            short_url (str): the short link to search for.
    """

    bookmark = Bookmark.query.filter_by(short_url=short_url).first()
    if not bookmark:
        return jsonify({'error': 'Item not found'}), HTTP_404_NOT_FOUND
    bookmark.visits += 1
    db.session.commit()

    return jsonify({'data': bookmark.to_dict()})

@bookmark.put('/<string:short_url>')
@jwt_required()
def handle_edit(short_url):

    """
        an Endpoint to update an existing record (shorted link).
        Args:
            short_url (str): the short link to search for.
    """

    data = request.get_json()
    parsed_url = urlparse(data['url'])

    if not all([parsed_url.scheme, parsed_url.netloc]):
        return jsonify({'error': 'Invalid URL Format, Please provide a valid URL'}), HTTP_400_BAD_REQUEST
    
    try:
            validate(data, create_bookmark_schema)
    except ValidationError as errors:
        return jsonify({'error': str(errors.message)}), HTTP_400_BAD_REQUEST
    
    user_id = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(short_url=short_url, user_id=user_id).first()

    if not bookmark:
        return jsonify({'error': 'Item not found'}), HTTP_404_NOT_FOUND
    
    bookmark.url = data['url']
    bookmark.body = data['body']
    db.session.commit()

    return jsonify({'data': bookmark.to_dict()}), HTTP_200_OK
    

@bookmark.delete('/<string:short_url>')
@jwt_required()
def handle_delete(short_url):

    """
        an Endpoint to delete an existing record (shorted link).
        Args:
            short_url (str): the short link to search for and delete.
    """

    user_id = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(short_url=short_url).first()

    if not bookmark:
        return jsonify({'error': 'Item not found'}), HTTP_404_NOT_FOUND
    elif bookmark.user_id != user_id:
        return jsonify({'error': 'Authorization error'}), HTTP_401_UNAUTHORIZED
    
    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({'message': 'Bookmark deleted successfully'})
