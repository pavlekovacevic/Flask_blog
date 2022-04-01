from marshmallow import fields, Schema
from marshmallow.validate import Length
from flask_bcrypt import Bcrypt
from forum.routes import signup 

class CreatePostInputSchema(Schema):
    title = fields.Str(required=True, validate=Length(max=20))
    content = fields.Str(required=True, validate=Length(max=200))
    

class CreateUserInputSchema(Schema):
    username = fields.Str(required=True, validate=Length(max=20))
    password = fields.password(load_default=Bcrypt.hashpw) #???
    email = fields.Str(required=True, validate=Length(max=20))


class CreateCommentInputSchema(Schema):
    content = fields.Str(required=True, validate=Length(max=200))

class CreateLoginInputSchema(Schema):
    username = fields.Str(required=True, validate=Length(max=20))
    password = fields.Str(required=True, validate=Length(max=20))