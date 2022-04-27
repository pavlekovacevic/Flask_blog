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

users_blueprint = Blueprint('users', __name__, url_prefix='/users')
blog_blueprint = Blueprint('blog', __name__, url_prefix='/blog') 

@users_blueprint.route('/signup', methods=['POST'])
def signup():
    try:
        user_signup_data = CreateUserInputSchema().load(request.get_json())
    except ValidationError as err:
        return err.messages, 400
    #Popravljena cela ruta sada ruta validatuje da li user zapravo postoji u db, ako postoji message i error ako ne create
    user=User.query.filter_by(username=user_signup_data['username']).first()
    
    if not user:
        new_user = User(**user_signup_data)
        db.session.add(new_user)
        db.session.commit()
        import pdb;pdb.set_trace()
        return jsonify({'message':'Signed up successfully!'}), 201    
    
    return ({'message':"User already exists"}), 404
    
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
            'exp': datetime.utcnow() + timedelta(minutes=200)
        }, config.SECRET_KEY
        )
        
        return jsonify({'token': token.decode()}), 201
    
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

    # token_required vraca ulogovanog usera, sad samo proveriti kako se pristupa toj promenljivoj
    new_post = Post(title=post_data['title'], content = post_data['content'], poster_id=user.id)
    
    db.session.add(new_post)
    db.session.commit()

    post_id = getattr(new_post, 'id')
    return jsonify({'id':post_id}), 201

@blog_blueprint.route('/post', methods=['GET'])
@token_required
def get_all_posts(user):
    posts = Post.query.all()
    schemas = CreatePostOutputSchema(many=True)
    result = schemas.dump(posts)
   
    return jsonify(result)

@blog_blueprint.route('/post/<id>', methods=['GET'])
@token_required
def get_single_post_by_id(user, id):
    post = Post.query.filter_by(id=id).first()
    schemas = CreatePostOutputSchema()
    result = schemas.dump(post)
   
    return jsonify(result)


@blog_blueprint.route('/post/<id>', methods = ['PUT'])
@token_required
def update_post(user, id):
    try:
        post_data = CreatePostInputSchema().load(request.get_json())
    except ValidationError as err:
        return err.messages, 400
    
    post = Post.query.filter_by(id=id).first()

    post.title = post_data['title']
    post.content = post_data['content']
    
    schema = CreatePostOutputSchema()
    updated_post = schema.dump(post)

    db.session.commit()
    return jsonify(updated_post)

@blog_blueprint.route('/post/<id>', methods=['DELETE'])
@token_required
def delete_post_by_id(user, id):
    post = Post.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()

    return jsonify("Deleted"), 200

@blog_blueprint.route('/post/<post_id>/comment', methods=['POST'])
@token_required
def add_comment_to_post_by_id(user, post_id):
    try:
        comment_data = CreateCommentInputSchema().load(request.get_json())
    except ValidationError as err:
        return err.messages, 400
    
    post = Post.query.filter_by(id=post_id).first()
    # return 404 if post doesnt exist

    new_comment = Comment(content = comment_data['content'], poster_id=user.id, post_id=post.id)
    
    db.session.add(new_comment)
    db.session.commit()
    
    
    schema = CreateCommentOutputSchema()
    result = schema.dump(new_comment)

    return jsonify(result), 201

@blog_blueprint.route('/post/<post_id>/comment', methods=['GET'])
@token_required
def get_all_comments(user, post_id):
    comments = Comment.query.filter_by(post_id=post_id).all()

    schema = CreateCommentOutputSchema(many=True)
    result = schema.dump(comments)

    return jsonify(result)