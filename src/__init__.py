from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

from src.config import Config

db = SQLAlchemy()

def create_app(initial_config=Config):
    app = Flask(__name__)
    app.config.from_object(initial_config)
    
    db.init_app(app)
    JWTManager(app)

    from src.auth.auth_routes import auth
    from src.bookmark.bookmark_routes import bookmark

    app.register_blueprint(auth)
    app.register_blueprint(bookmark)

    return app
