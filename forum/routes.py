import json
import bcrypt
import jwt
from flask import  jsonify, make_response, request, Blueprint
from marshmallow import ValidationError
from flask import request, Blueprint
from datetime import datetime, timedelta
from forum.models import User, Post, Comment
from forum import db
from forum.schemas import CreateCommentInputSchema, CreatePostInputSchema, CreateUserInputSchema, CreateLoginInputSchema, CreatePostOutputSchema, CreateCommentOutputSchema
from forum.config import ForumConfig as config
from forum.jwt import token_required
from sqlalchemy import desc
from forum.utils import generate_token

users_blueprint = Blueprint('users', __name__, url_prefix='/users')
blog_blueprint = Blueprint('blog', __name__, url_prefix='/blog') 

@users_blueprint.route('/signup', methods=['POST'])
def signup():
    try:
        user_signup_data = CreateUserInputSchema().load(request.get_json())
    except ValidationError as err:
        return err.messages, 400
        
    user=User.query.filter_by(username=user_signup_data['username']).first()
    
    if not user:
        new_user = User(**user_signup_data)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message':'Signed up successfully!'}), 201    
    
    return ({'message':"User already exists"}), 400
    
@users_blueprint.route('/login', methods=['POST'])
def login():
    try:
        user_login_data = CreateLoginInputSchema().load(request.get_json())
    except ValidationError as err:
        return err.messages, 400

    user = User.query.filter_by(username=user_login_data['username']).first()
    if not user:
        return 'User not found', 404
    
    if bcrypt.checkpw(user_login_data['password'].encode(), user.password.encode()):
        token = generate_token(user_id=user.id)
        
        return jsonify({'token': token.decode()}), 200
    
    return make_response(
        'Could not verify', 403
    )

@blog_blueprint.route('/post', methods=['POST'])
@token_required
def create_post(user):
    try:
        post_data = CreatePostInputSchema().load(request.get_json())
    except ValidationError as err:
        return err.messages, 400

    new_post = Post(poster_id=user.id, **post_data)
    
    db.session.add(new_post)
    db.session.commit()

    return jsonify({'id': new_post.id}), 201

@blog_blueprint.route('/post', methods=['GET'])
@token_required
def get_all_posts(user):
    posts = Post.query.all()
    results = CreatePostOutputSchema(many=True).dump(posts)
   
    return jsonify(results)

@blog_blueprint.route('/post/<id>', methods=['GET'])
@token_required
def get_single_post_by_id(user, id):
    post = Post.query.filter_by(id=id).first()
    results = CreatePostOutputSchema().dump(post)
   
    return jsonify(results)

@blog_blueprint.route('/post/<id>', methods=['PUT'])
@token_required
def update_post(user, id):
    try:
        post_data = CreatePostInputSchema().load(request.get_json())
    except ValidationError as err:
        return err.messages, 400
    
    post = Post.query.filter_by(id=id, poster_id=user.id).first()
    if not post:
        return {"message": "U are not allowed to update this post!"}, 403
   
    post.title = post_data['title']
    post.content = post_data['content']
    db.session.commit()
    updated_post = CreatePostOutputSchema().dump(post)
    
    return jsonify(updated_post)

@blog_blueprint.route('/post/<id>', methods=['DELETE'])
@token_required
def delete_post_by_id(user, id):
    post = Post.query.filter_by(id=id, poster_id=user.id).first()
    if not post:
        return {"message":"U are not allowed to delete this post!"}, 403
    
    db.session.delete(post)
    db.session.commit()

    return jsonify("Post deleted"), 200

@blog_blueprint.route('/post/<post_id>/comment', methods=['POST'])
@token_required
def add_comment_to_post_by_id(user, post_id):
    try:
        comment_data = CreateCommentInputSchema().load(request.get_json())
    except ValidationError as err:
        return err.messages, 400
    
    post = Post.query.filter_by(id=post_id).first()
   
    if not post:
        return {"message":"Post does not exist"}, 403

    new_comment = Comment(content=comment_data['content'], poster_id=user.id, post_id=post.id)
    db.session.add(new_comment)
    db.session.commit()
    result = CreateCommentOutputSchema().dump(new_comment)

    return jsonify(result), 201

@blog_blueprint.route('/post/<post_id>/comment', methods=['GET'])
@token_required
def get_all_comments(user, post_id):
    comments = Comment.query.order_by(desc(Post.pub_date),post_id=post_id).all()
    schema = CreateCommentOutputSchema(many=True)
    result = schema.dump(comments)

    return jsonify(result)