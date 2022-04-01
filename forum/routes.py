import bcrypt
import jwt

from flask import  jsonify, make_response, request, Blueprint
from marshmallow import ValidationError
from flask import request, Blueprint
from datetime import datetime, timedelta
from forum.jwt import token_required
from forum.models import User, Post, Comment
from forum import db
from flask_bcrypt import Bcrypt
from forum.schemas import CreatePostInputSchema, CreateUserInputSchema, CreateLoginInputSchema
from forum.config import ForumConfig as config



#ubaciti autorizaciju, resiti 404 problem, dodati rutu za komentare("/post/<id>/comment"), i todo u signup ruti

users_blueprint = Blueprint('users', __name__, url_prefix='/users')
blog_blueprint = Blueprint('blog', __name__, url_prefix='/blog')

@users_blueprint.route('/signup', methods=['POST'])
def signup():
    try:
        user_signup_data = CreateUserInputSchema().load(request.get_json())
    except ValidationError as err:
        return err.messages, 400
    
    new_user = User(**user_signup_data)
    # TODO: ako se unese dva puta baza puca, pogledaj kako pokriti taj case
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message':'Singed up successfully'}), 201


@users_blueprint.route('/login', methods=['POST'])
def login():
    try:
        user_login_data = CreateLoginInputSchema().load(request.get_json())
    except ValidationError as err:
        return err.messages, 400
    
    user = User.query.filter_by(email = user_login_data['email']).first()
    
    if Bcrypt.check_password_hash(user.password, user_login_data['password']):
        token = jwt.encode({
            'user_id': User.user_id,
            'exp': datetime.utcnow()+timedelta(minutes=45)
        }), config.SECRET_KEY

        return make_response(jsonify({'token': token.decode('UTF-8')}), 201)
    
    return make_response(
        'Could not verify', 403
    )
    
    
@blog_blueprint.route('/post', methods=['POST'])
@token_required
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

@blog_blueprint.route('/post', methods=['GET'])
@token_required
def get_all_posts():
    posts = Post.query.all()
    all_posts = []
    for post in posts:
        all_posts.append(post)
    
    return jsonify({'all posts': all_posts})

@blog_blueprint.route('/post/<id>', methods=['GET'])
@token_required
def get_single_post_by_id(id):
    post = Post.query.filter_by(id=id).first()
    if not post:
        return 'No matching post_id', 404

    return jsonify(post)

@blog_blueprint.route('/post/<id>', methods = ['PUT'])
@token_required
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

@blog_blueprint.route('/post', methods=['DELETE'])
@token_required
def delete_post_by_id(id):
    post = Post.query.filter_by().first()
    db.session.delete(post)
    db.session.commit()

    return jsonify("Deleted"), 200

@blog_blueprint.route('/post/<id>/comment', methods=['POST'])
@token_required
def add_comment_to_post_by_id(id):
    try:
        comm_data = CreatePostInputSchema().load(request.get_json())
    except ValidationError as err:
        return err.messages, 400

    #prvo autorizacija ovo ovako nece ici 