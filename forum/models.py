from forum import db 
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), unique=True, nullable=False)
    posts = db.relationship('Post', backref='poster')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), unique=True, nullable=False)
    content = db.Column(db.String(200), unique=True, nullable=False)
    poster_id = db.Column(db.Integer, db.ForeignKey(User.id),nullable=False)#db does not recognize realtionship poster_id is null
    pub_date = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), unique=True, nullable=False)
    poster_id = db.Column(db.Integer, db.ForeignKey(User.id))
    post_id = db.Column(db.Integer, db.ForeignKey(Post.id))
    pub_date = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)