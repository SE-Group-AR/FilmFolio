import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    client = app.test_client()

    with app.app_context():
        db.create_all()

    yield client

    with app.app_context():
        db.drop_all()

def test_get_recommendations(client):
    client.post('/register', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    response = client.get('/recommendations')
    assert response.status_code == 200
    assert b'Recommended Movies' in response.data

def test_get_recommendations_new_user(client):
    client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpassword'
    })
    client.post('/login', data={
        'username': 'newuser',
        'password': 'newpassword'
    })
    response = client.get('/recommendations')
    assert response.status_code == 200
    assert b'Popular Movies' in response.data