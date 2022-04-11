import bcrypt
from marshmallow import fields, Schema, post_load
from marshmallow.validate import Length



class CreatePostInputSchema(Schema):
    title = fields.Str(required=True, validate=Length(max=20))
    content = fields.Str(required=True, validate=Length(max=200))


class CreateUserInputSchema(Schema):
    username = fields.Str(required=True, validate=Length(max=20), unique=True)
    password = fields.Str(required=True) 
    email = fields.Str(required=True, validate=Length(max=20), unique=True)

    @post_load
    def hash_password(self, in_data, **kwargs):
        # Hash the `data` parameter and return the new hashed value.
        in_data["password"] = bcrypt.hashpw(in_data["password"].encode(), bcrypt.gensalt())
        return in_data

class CreateCommentInputSchema(Schema):
    content = fields.Str(required=True, validate=Length(max=200))

class CreateLoginInputSchema(Schema):
    username = fields.Str(required=True, validate=Length(max=20))
    password = fields.Str(required=True, validate=Length(max=20))