from flask import Blueprint, jsonify, request
from jsonschema import validate, ValidationError
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from email_validator import validate_email

from src import db
from src.auth.auth_validation import register_schema, login_schema
from src.auth.auth_model import User
from src.constants import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_201_CREATED

auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth.route('/register', methods=['POST'])
def register():
    """
        an Endpoint to Register a new user to the API Database.
    """

    data = request.get_json()

    try:
        validate_email(data['email'])
    except Exception as error:
        return jsonify({'error': str(error)}), HTTP_400_BAD_REQUEST

    try:
        validate(data, register_schema)
    except ValidationError as errors:
        return jsonify({'error': str(errors.message)}), HTTP_400_BAD_REQUEST
    
    username_taken = User.query.filter_by(username=data['username']).first()
    email_taken = User.query.filter_by(email=data['email']).first()
    if username_taken:
        return jsonify({'error': 'Username is already taken'}), HTTP_400_BAD_REQUEST
    if email_taken:
        return jsonify({'error': 'Email is already taken'}), HTTP_400_BAD_REQUEST
    
    user = User(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully', 'user': user.to_dict()}), HTTP_201_CREATED

@auth.route('/login', methods=['POST'])
def login():

    """
        an Endpoint to Login an existing user from the API Database.
    """

    data = request.get_json()
    try:
        validate(data, login_schema)
    except ValidationError as errors:
        return jsonify({'error': str(errors.message)}), HTTP_400_BAD_REQUEST
    
    user = User.query.filter_by(email=data['email']).first()
    if user:
        correct_password = check_password_hash(user.password, data['password'])
        if correct_password:
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            return jsonify({'user': user.to_dict(), 'access_token': access_token, 'refresh_token': refresh_token}), 201
    else:
        return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED
    
@auth.route('/me')
@jwt_required()
def me():

    """
        an Endpoint to Returns the data of current logged in user.
    """

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    return jsonify({'user': user.to_dict()}), HTTP_200_OK

@auth.route('/refresh')
@jwt_required(refresh=True)
def get_refresh_token():

    """
        an Endpoint to get a new access token from refresh token.
    """

    user_id = get_jwt_identity()
    access = create_access_token(identity=user_id)

    return jsonify({
        'access_token': access
    }), HTTP_200_OK
