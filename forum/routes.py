import bcrypt
import jwt
from flask import  jsonify, make_response, request, Blueprint
from marshmallow import ValidationError
from flask import request, Blueprint
from datetime import datetime, timedelta
from forum.models import User, Post, Comment
from forum import db
from forum.schemas import CreateCommentInputSchema, CreatePostInputSchema, CreateUserInputSchema, CreateLoginInputSchema
from forum.config import ForumConfig as config
from forum.jwt import token_required
users_blueprint = Blueprint('users', __name__, url_prefix='/users')
blog_blueprint = Blueprint('blog', __name__, url_prefix='/blog')

@users_blueprint.route('/signup', methods=['POST'])
def signup():
    try:
        user_signup_data = CreateUserInputSchema().load(request.get_json())
    except ValidationError as err:
        return err.messages, 400

    new_user = User(**user_signup_data)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message':'Singed up successfully'}), 201
    
    
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
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(minutes=45)
        }, config.SECRET_KEY)

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

    # token_required vraca ulogovani user, sad samo proveriti kako da pristupas toj promenljivoj
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

@blog_blueprint.route('/post/<post_id>/comment/<comment_id>', methods=['GET'])
@token_required
def add_comment_to_post_by_id(post_id, comment_id):
    """"patch comment by seraching its id and post id"""

@blog_blueprint.route('/comment', methods=['GET'])
def get_all_comments():
    try:
        comment_data = CreateCommentInputSchema().load(request.get_json)
    except ValidationError as err:
        return err.messages, 400

    new_comment = Comment(content=comment_data['content'])

    db.session.add(new_comment)
    db.session.commit()

    comm_id = getattr(new_comment, 'id')
    return jsonify({'id':comm_id})



