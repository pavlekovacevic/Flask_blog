from functools import wraps
import jwt
from flask import request, jsonify
from forum.models import User
from forum.config import ForumConfig as config

def token_required(f):
   @wraps(f)
   def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
            
        try:
            headers = request.headers
            token_header = headers['Authorization']
            if token_header.startswith('Bearer '):
                get_token = request.headers.get("Authorization")
                token = get_token[len('Bearer '):]
                decoded_token = jwt.decode(jwt=token, key=config.SECRET_KEY)
                current_user = User.query.filter_by(id=decoded_token['user_id']).first()
        except Exception as e:
            print(e)
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        
        return  f(current_user, *args, **kwargs)
  
   return decorated