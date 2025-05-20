import pytest
from back import create_app, db
from flask_jwt_extended import create_access_token
from back.models import User

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret"
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user_and_token(client):
    client.post('/api/signup', json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass"
    })
    res = client.post('/api/login', json={
        "login_name": "test@example.com",
        "password": "testpass"
    })
    data = res.get_json()
    token = data["access_token"]

    return "testuser", token

