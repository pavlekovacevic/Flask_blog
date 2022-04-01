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
    # los jwt to izmeni, los if. 
    try:
        user_login_data = CreateLoginInputSchema().load(request.get_json())
    except ValidationError as err:
        return err.messages, 400

    user = User.query.filter_by(email = user_login_data['email']).first()

    if not user:
        return make_response('Could not verify', 401)

    if Bcrypt.check_password_hash(User.password, user_login_data['password']):
        token = jwt.encode({
            'user_id': User.user_id,
            'exp': datetime.utcnow()+timedelta(minutes=45)
        }), app.config['SECRET KEY']

        return make_response(jsonify({'token': token.decode('UTF-8')}), 201)
    return make_response(
        'Could not verify', 403
    )
    
    


    
    
    

    
    # if Bcrypt.check_password_hash(user.password, auth.password):
    #     token = jwt.encode({'user_id': user.user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=45)}, app.config['SECRET_KEY'], "HS256")
    
    #     return jsonify({'token' : token})
    




