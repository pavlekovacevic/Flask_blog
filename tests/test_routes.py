import pytest
from forum import create_app
from forum.jwt import token_required

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def test_user_signup(client):
    response = client.post("/users/signup", json={
       "username":"Usr9175639536",
       "password":"9017590273566",
       "email":"gmail@12774343\9.com" 
    })
    
    assert response.data == (b'{"message":"Signed up successfully!"}\n') # whereas json. dumps() simply returns a string of JSON data???
    assert response.status_code == 201

def test_user_already_in_db(client):
    response = client.post("/users/signup", json={
        "username":"Testusesssr123",
        "password":"1234512ss3",
        "email":"testuses@testuser"
    })

    assert response.data == (b'{"message":"User already exists"}\n')
    assert response.status_code == 404

def test_user_signup_wrong_data(client):
    response = client.post("/users/signup", json={
       "username":"Testuser12",
       "password":"1234512",
       "email":12345
    })
    
    assert response.data == (b'{"email":["Not a valid string."]}\n')
    assert response.status_code == 400

def test_user_login(client):
    response = client.post("/users/login", json={
       "username":"Testuser",
       "password":"12345"
    })
    
    assert response.status_code == 201

def test_user_login_not_exist(client):
    response = client.post("/users/login", json={
       "username":"notexistingsuername",
       "password":"badpassword"
    })
    
    assert response.data == (b'User not found')
    assert response.status_code == 404

def test_user_login_wrong_data(client):
    response = client.post("/users/login", json={
        "username":"Randomusername",
        "password":9222
    })
    
    assert response.data == (b'{"password":["Not a valid string."]}\n')
    assert response.status_code == 400

def test_add_new_post(client, app):
    test_client = app.test_client()
    access_token = token_required('testuser')
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }
    response = test_client.post('/post', headers=headers, json={
        "title":"QWERTY",
        "content":"something123"})
    
    assert response.status_code == 201

    