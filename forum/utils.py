import jwt
from datetime import datetime, timedelta
from forum.config import ForumConfig

def generate_token(user_id):
    token = jwt.encode({
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(minutes=200)
        }, ForumConfig.SECRET_KEY
        )

    return token