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

def test_add_to_watchlist(client):
    client.post('/register', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    response = client.post('/add_to_watchlist', data={'movie_id': '1'})
    assert response.status_code == 302
    assert b'Redirecting...' in response.data

def test_remove_from_watchlist(client):
    client.post('/register', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    client.post('/add_to_watchlist', data={'movie_id': '1'})
    response = client.post('/remove_from_watchlist', data={'movie_id': '1'})
    assert response.status_code == 302
    assert b'Redirecting...' in response.data

def test_view_watchlist(client):
    client.post('/register', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    client.post('/add_to_watchlist', data={'movie_id': '1'})
    response = client.get('/watchlist')
    assert response.status_code == 200
    assert b'Your Watchlist' in response.data