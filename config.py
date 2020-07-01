import os

class Config:
    DEBUG = True
    SECRET_KEY= "secret_key"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False