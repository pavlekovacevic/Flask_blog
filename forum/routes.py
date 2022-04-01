import bcrypt
from flask import  jsonify, make_response, request
from marshmallow import Schema,fields,ValidationError
from flask import Flask, request
from datetime import datetime, timedelta
from forum.models import User, Post, Comment
import jwt
from app import app
from forum import db
from flask_bcrypt import Bcrypt
from forum.schemas import CreateCommentInputSchema, CreatePostInputSchema, CreateUserInputSchema, CreateLoginInputSchema
from flask_serialize import FlaskSerialize


@app.route('/signup', methods=['POST'])
def signup():
    #TODO pokri scenario kad nije ispunjena sema done
    try:
        user_signup_data = CreateUserInputSchema().load(request.get_json())
    except ValidationError as err:
        return err.messages, 400
    #TODO logika za hash pass prebaci u semu, da pass bude omdha hashed u semi 
    user_signup_data['password'] = Bcrypt.hashpw(user_signup_data['password'].encode('UTF-8'), bcrypt.gensalt())
    
    new_user = User(**user_signup_data)
    # TODO: ako se unese dva puta baza puca, pogledaj kako pokriti taj case
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message':'Singed up successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    try:
        user_login_data = CreateLoginInputSchema().load(request.get_json())
    except ValidationError as err:
        return err.messages, 400
    
    user = User.query.filter_by(email = user_login_data['email']).first()
    
    if Bcrypt.check_password_hash(User.password, user_login_data['password']):
        token = jwt.encode({
            'user_id': User.user_id,
            'exp': datetime.utcnow()+timedelta(minutes=45)
        }), app.config['SECRET KEY']

        return make_response(jsonify({'token': token.decode('UTF-8')}), 201)
    
    return make_response(
        'Could not verify', 403
    )
    
    
@app.route('/post', methods=['POST'])
def create_post():
    try:
        post_data = CreatePostInputSchema().load(request.get_json())
    except ValidationError as err:
        return err.messages, 400

    new_post = Post(title=post_data['title'], content = post_data['content'])

    db.session.add(new_post)
    db.session.commit()

    post_id = getattr(new_post, 'id')
    return jsonify({'id':post_id}), 201

@app.route('/post', methods=['GET'])
def get_all_posts():
    posts = Post.query.all()
    all_posts = []
    for post in posts:
        all_posts.append(post)
    
    return jsonify({'all posts': all_posts})

@app.route('/post/<id>')
def get_single_post_by_id(id):
    post = Post.query.filter_by(id=id).first()
    if not post:
        return 'No matching post_id', 404

    return jsonify(post)
"""Import authorization for every rout"""
@app.route('/post/<id>', methods = ['PUT'])
def update_post(id):
    try:
        post_data = CreatePostInputSchema().load(request.get_json())
    except ValidationError as err:
        return err.messages, 400
    
    post = Post.query.filter_by(id=id).first()

    post.title = post_data['title']
    post.content = post_data['content']
    
    updated_post = post

    db.session.commit()
    return jsonify(updated_post)

@app.route('/post', methods=['DELETE'])
def delete_post_by_id(id):
    post = Post.query.filter_by().first()
    db.session.delete(post)
    db.session.commit()

    return jsonify("Deleted"), 200