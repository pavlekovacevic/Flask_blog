from functools import wraps
import jwt
from flask import request, abort, jsonify
from flask import app
from forum import db
from forum.models import User
from forum.config import ForumConfig as config

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        
        token = request.headers.get("Authorization")
        
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
            
        
        try:
            # decoding the payload to fetch the stored details
            pure_token=token[7:]
            token_payload = jwt.decode(jwt=pure_token, key=config.SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.filter_by(id = token_payload['user_id']).first()
        
        except Exception as e:
            import pdb;pdb.set_trace()
            print(e)
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated