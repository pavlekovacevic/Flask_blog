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
       "username":"Testuser",
       "password":"12345",
       "email":"testuser@testuser" 
    })
    
    assert response.status_code == 201

def test_user_signup(client):

    response = client.post("/users/signup", json={
       "username":"Testuser",
       "password":"12345",
       "email":12345
    })
    
    assert response.status_code == 400

def test_user_login(client):
    response = client.post("/users/login", json={
       "username":"Testuser",
       "password":"12345"
    })
    
    assert response.status_code == 201

def test_user_login(client):
    response = client.post("/users/login", json={
       "username":"notexistingsuername",
       "password":"badpassword"
    })
    
    assert response.status_code == 400