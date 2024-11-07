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

def test_add_review(client):
    client.post('/register', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    response = client.post('/add_review', data={
        'movie_id': '1',
        'rating': '5',
        'review_text': 'Great movie!'
    })
    assert response.status_code == 302
    assert b'Redirecting...' in response.data

def test_edit_review(client):
    client.post('/register', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    client.post('/add_review', data={
        'movie_id': '1',
        'rating': '5',
        'review_text': 'Great movie!'
    })
    response = client.post('/edit_review', data={
        'review_id': '1',
        'rating': '4',
        'review_text': 'Good movie, but not great.'
    })
    assert response.status_code == 302
    assert b'Redirecting...' in response.data

def test_delete_review(client):
    client.post('/register', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    client.post('/add_review', data={
        'movie_id': '1',
        'rating': '5',
        'review_text': 'Great movie!'
    })
    response = client.post('/delete_review', data={'review_id': '1'})
    assert response.status_code == 302
    assert b'Redirecting...' in response.data