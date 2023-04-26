import os
from datetime import timedelta
from dotenv import load_dotenv

class Config:
    load_dotenv()

    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=3)