"""
Copyright (c) 2024 Abhinav Jami, Meet Patel, Anchita Ramani
This code is licensed under MIT license (see LICENSE for details)

@author: FilmFolio
"""

import json
import os
import requests
from flask import render_template, url_for, redirect, request, jsonify, flash
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import emit
from dotenv import load_dotenv
from src import app, db, bcrypt, socket
from src.search import Search
from src.item_based import recommend_for_new_user
from src.models import User, Movie, Review

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def get_user():
    """Helper function to get the current user if authenticated."""
    if current_user.is_authenticated:
        return redirect(url_for('search_page'))
    return None

@app.route("/", methods=["GET"])
@app.route("/home", methods=["GET"])
def landing_page():
    return get_user() or render_template("landing_page.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if (redirect_to := get_user()):
        return redirect_to

    if request.method == "POST":
        username = request.form['username']
        try:
            user = User(
                username=username,
                email=request.form['email'],
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                password=bcrypt.generate_password_hash(request.form['password']),
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('search_page'))
        except Exception as e:
            flash(f"Username {username} already exists!", 'error')
    return render_template('signup.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if (redirect_to := get_user()):
        return redirect_to

    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for('search_page'))
        flash("Invalid Credentials! Try again!", 'error')
    return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("landing_page"))

@app.route("/profile_page", methods=["GET"])
@login_required
def profile_page():
    reviews = [
        {
            "title": movie_object.title,
            "runtime": movie_object.runtime,
            "overview": movie_object.overview,
            "genres": movie_object.genres,
            "imdb_id": movie_object.imdb_id,
            "review_text": review.review_text,
        }
        for review in Review.query.filter_by(user_id=current_user.id).all()
        if (movie_object := Movie.query.filter_by(movieId=review.movieId).first())
    ]
    return render_template("profile.html", user=current_user, reviews=reviews, search=False)

@app.route("/search_page", methods=["GET"])
@login_required
def search_page():
    return render_template("search.html", user=current_user, search=True)

@app.route("/predict", methods=["POST"])
def predict():
    data = recommend_for_new_user([
        {"title": movie, "rating": 5.0} for movie in json.loads(request.data)["movie_list"]
    ])
    return jsonify(data.to_json(orient="records"))

@app.route("/search", methods=["POST"])
def search():
    term = request.form["q"]
    filtered_dict = Search().results_top_ten(term)
    return jsonify(filtered_dict), 200

@app.route("/chat", methods=["GET"])
def chat_page():
    return get_user() or render_template("movie_chat.html", user=current_user)

@socket.on('connections')
def show_connection(data):
    print('received message:', data)

@socket.on('message')
def broadcast_message(data):
    emit('message', {'username': data['username'], 'msg': data['msg']}, broadcast=True)

@app.route("/getPosterURL", methods=["GET"])
def get_poster_url():
    return jsonify({"posterURL": fetch_poster_url(request.args.get("imdbID"))})

def fetch_poster_url(imdb_id):
    url = f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={TMDB_API_KEY}&external_source=imdb_id"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        poster_path = data.get("movie_results", [{}])[0].get("poster_path")
        return f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
    except requests.RequestException:
        return None

@app.route("/postReview", methods=["POST"])
@login_required
def post_review():
    data = json.loads(request.data)
    movie_object = Movie.query.filter_by(movieId=data["movieId"]).first()
    if not movie_object:
        movie = Movie(
            movieId=data["movieId"],
            title=data['title'],
            runtime=data['runtime'],
            overview=data['overview'],
            genres=data['genres'],
            imdb_id=data['imdb_id'],
            poster_path=data['poster_path'],
        )
        db.session.add(movie)
    db.session.add(Review(
        review_text=data['review_text'],
        movieId=data["movieId"],
        user_id=current_user.id
    ))
    db.session.commit()
    return jsonify({"success": "success"})

@app.route("/movies", methods=["GET"])
@login_required
def movie_page():
    movies = [
        {
            "title": movie_object.title,
            "runtime": movie_object.runtime,
            "overview": movie_object.overview,
            "genres": movie_object.genres,
            "imdb_id": movie_object.imdb_id,
            "reviews": [
                {
                    "username": user.username,
                    "name": f"{user.first_name} {user.last_name}",
                    "review_text": review.review_text,
                }
                for review in Review.query.filter_by(movieId=movie_object.movieId).all()
                if (user := User.query.filter_by(id=review.user_id).first())
            ],
        }
        for movie_object in Movie.query.all()
    ]
    return render_template("movie.html", movies=movies, user=current_user)

@app.route('/new_movies', methods=["GET"])
@login_required
def new_movies():
    endpoint = 'https://api.themoviedb.org/3/movie/upcoming'
    try:
        response = requests.get(endpoint, params={
            'api_key': TMDB_API_KEY, 'language': 'en-US', 'page': 1
        }, timeout=10)
        movie_data = response.json().get('results', []) if response.status_code == 200 else []
        return render_template('new_movies.html', movies=movie_data, user=current_user)
    except requests.RequestException as e:
        flash("Error fetching movie data", 'error')
        return render_template('new_movies.html')
