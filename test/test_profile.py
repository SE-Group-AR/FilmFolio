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

def test_update_profile(client):
    client.post('/register', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    response = client.post('/update_profile', data={
        'email': 'newemail@example.com',
        'bio': 'I love movies!'
    })
    assert response.status_code == 302
    assert b'Redirecting...' in response.data

def test_change_password(client):
    client.post('/register', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    response = client.post('/change_password', data={
        'current_password': 'testpassword',
        'new_password': 'newpassword',
        'confirm_password': 'newpassword'
    })
    assert response.status_code == 302
    assert b'Redirecting...' in response.data

def test_delete_account(client):
    client.post('/register', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    response = client.post('/delete_account', data={'confirm_delete': 'true'})
    assert response.status_code == 302
    assert b'Redirecting...' in response.data