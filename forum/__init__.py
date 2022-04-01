from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from forum.config import ForumConfig

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(ForumConfig)
    
    db.init_app(app)
    migrate.init_app(app, db)

    return app