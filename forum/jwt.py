from functools import wraps
import jwt
from flask import request, abort, jsonify
from flask import app
from forum import db
from forum.models import User
from forum.config import ForumConfig as config

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        
        token = request.headers.get("Authorization")
        
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
            
        
        try:
            # decoding the payload to fetch the stored details
            import pdb;pdb.set_trace()
            token_payload = jwt.decode(jwt=token, key=config.SECRET_KEY)
            current_user = User.query.filter_by(id = token_payload['user_id']).first()
        
        except Exception as e:
            print(e)
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return  func(current_user, *args, **kwargs)
  
    return decorated