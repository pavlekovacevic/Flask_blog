import pytest
from app import create_app

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

# def test_edit_user(client):
#     response = client.post("/user/2/edit", data={
#         "name": "Flask",
#         "theme": "dark",
#         "picture": (resources / "picture.png").open("rb"),
#     })
#     assert response.status_code == 200

