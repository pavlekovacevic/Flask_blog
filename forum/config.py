import os

class ForumConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "postgresql://postgres:password@localhost:5432")
    
    SECRET_KEY = os.environ.get("SECRET-KEY", "very-very-very-secret")