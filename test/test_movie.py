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

def test_movie_search(client):
    response = client.get('/search?query=Inception')
    assert response.status_code == 200
    assert b'Inception' in response.data

def test_movie_search_no_results(client):
    response = client.get('/search?query=NonexistentMovie123456')
    assert response.status_code == 200
    assert b'No results found' in response.data

def test_movie_details(client):
    response = client.get('/movie/1')  # Assuming movie with ID 1 exists
    assert response.status_code == 200
    assert b'Movie Details' in response.data