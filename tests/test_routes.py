import pytest
from forum import create_app
import psycopg2
from psycopg2.errors import DuplicateDatabase
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask_migrate import upgrade
import bcrypt
from forum.models import User
from forum import db
from forum.utils import generate_token
from forum.config import ForumConfig

SQLALCHEMY_DATABASE_BASE_URI = "postgresql://postgres:password@localhost:5432"

@pytest.fixture(scope="session", autouse=True)
def app():
    con = psycopg2.connect(SQLALCHEMY_DATABASE_BASE_URI)
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    app = create_app()
    app.config.update({
        "SECRET_KEY":ForumConfig.SECRET_KEY,
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"{SQLALCHEMY_DATABASE_BASE_URI}/test_forum"
    })
    
    ctx = app.app_context()
    ctx.push()
    
    cursor = con.cursor()
    try:
        cursor.execute('''CREATE DATABASE test_forum''')
    except DuplicateDatabase:
        cursor.execute('''DROP DATABASE test_forum''')
        cursor.execute('''CREATE DATABASE test_forum''')

    print('Test database created')
    # Migrate database.
    upgrade()

    yield app

    # First kill all database sessions for test_forum database.
    cursor.execute(
        '''
        SELECT 
            pg_terminate_backend(pid) 
        FROM 
            pg_stat_activity 
        WHERE 
            -- don't kill my own connection!
            pid <> pg_backend_pid()
            -- don't kill the connections to other databases
            AND datname = 'test_forum'
            ;
        '''
    )
    # Drop database.
    cursor.execute('''DROP DATABASE test_forum''')
    print('database murdered')

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def user_client(client):
    user = User(username='Testuser1', email='test@test1', password='testuser1')
    user.password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    db.session.add(user)
    db.session.commit()
    token = generate_token(user_id=user.id)
    
    client.headers = {"Authorization": f"Bearer {token}"}
    
    return client
    
def test_user_signup(user_client):
    response = user_client.post("/users/signup", json={
       "username":"Testuser12",
       "password":"testuser12",
       "email":"test@test12" 
    })

    assert response.status_code == 201
    assert response.json == ({'message':'Signed up successfully!'})

def test_user_signup_incorecct_format(user_client):
    response = user_client.post("/users/signup", json={
       "username":1,
       "password":"testuser",
       "email":"test@test" 
    })

    assert response.status_code == 400

def test_user_signup_already_in_db(user_client):
    response = user_client.post("/users/signup", json={
       "username":"Testuser1",
       "password":"testuser1",
       "email":"test@test1" 
    })

    assert response.status_code == 400
    assert response.json == ({'message':"User already exists"})

def test_user_login(user_client):
    response = user_client.post("/users/login", json={
       "username":"Testuser1",
       "password":"testuser1",
       "email":"test@test1" 
    })
    
    assert response.status_code == 200

def test_add_new_post(user_client):
    response = user_client.post("/blog/post", json={
        "title":"FirstTitle",
        "content":"Hello world!"
    })

    assert response.status_code == 201

def test_add_new_post_incorrect_data(user_client):
    response = user_client.post("/blog/post", json={
        "title":"FirstTitle",
        "content":2
    })

    assert response.status_code == 400

def test_add_new_post_user_forbidden(user_client):
    user_client.headers = {"Authorization": "Bearer invalid token"}
    response = user_client.post('/blog/post', json={
        "title":"Wrong user",
        "content":"123"
    })
    
    assert response.status_code == 403

def test_get_all_posts(user_client):
    response = user_client.get("/blog/post")

    assert response.status_code == 200
    
def test_get_all_posts_user_forbidden(user_client):
    user_client.headers = {"Authorization": "Bearer invalid token"}

    response = user_client.get('/blog/post')
    
    assert response.status_code == 403

def test_get_post_by_id(user_client):
    response = user_client.get("/blog/post/1")
    
    assert response.status_code == 200

def test_update_post_valid_user(user_client):
    response = user_client.post("/blog/post/<id>", json={
        "title":"updated title",
        "content":"its me again"
    })
    
    assert response.status_code == 201

def test_update_post_user_forbidden(user_client):
    user_client.headers = {"Authorization": "Bearer invalid token"}

    response = user_client.post('/blog/post/1', json={
        "title":"new_title",
        "content":"random content"
    })

    assert response.status_code == 403
    assert response.json == {"message": "U are not allowed to update this post!"}

def test_update_post_invalid_data(user_client):
    response = user_client.post("/blog/post/1", json={
        "title":"GOT",
        "content":2
    })

    assert response.status_code == 400

def test_delete_post_by_id(user_client):
    response = user_client.delete("/blog/post/1")

    assert response.status_code == 200
    assert response.json == ("Post deleted")

def test_add_comment_to_post_by_id(user_client):
    response = user_client.post('/blog/post/1/comment', json={
        "content":"Hello"
    })
    
    assert response.status_code == 201

def test_add_comment_to_post_by_id_invalid_data(user_client):
    response = user_client.post('/blog/post/1/comment', json={
        "title":"First title",
        "content":2
    })
    
    assert response.status_code == 403
    assert response.json == ...

def test_add_comment_by_id_forbidden_user(user_client):
    user_client.headers = {"Authorization": "Bearer invalid token"}

    response = user_client.post('/blog/post/1/comment', json={
         "content":"Comment"
     })
    
    assert response.status_code == 403
    assert response.json == {"message":"U are not allowed to delete this post!"}, 403
    
def test_add_comment_by_id_invalid_post_id(user_client):
    response = user_client.post('/blog/post/103/comment', json={
        "content":"Hello"
    })
    
    assert response.status_code == 403
    assert response.json == {"message":"Post does not exist"}

def get_all_comments(user_client):
    response = user_client.get('/post/<post_id>/comment')

    assert response.status_code == 200

def get_all_comments_invalid_post_id(user_client):
    response = user_client.get('/blog/post/98/comment')

    assert response.status_code == 403
    
def get_all_comments_user_forbidden(user_client):
    user_client.headers = {"Authorization": "Bearer invalid token"}

    response = user_client.get('/blog/post/<post_id>/comment')
    
    assert response.status_code == 403