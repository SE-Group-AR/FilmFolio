import logging
import smtplib
from smtplib import SMTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

def create_colored_tags(genres):
    """
    Utility function to create colored tags for different movie genres.
    """
    genre_colors = {
        'Musical': '#FF1493', 'Sci-Fi': '#00CED1', 'Mystery': '#8A2BE2',
        'Thriller': '#FF6347', 'Horror': '#FF4500', 'Documentary': '#228B22',
        'Fantasy': '#FFA500', 'Adventure': '#FFD700', 'Children': '#32CD32',
        'Film-Noir': '#2F4F4F', 'Comedy': '#FFB500', 'Crime': '#8B0000',
        'Drama': '#8B008B', 'Western': '#FF8C00', 'IMAX': '#20B2AA',
        'Action': '#FF0000', 'War': '#B22222', '(no genres listed)': '#A9A9A9',
        'Romance': '#FF69B4', 'Animation': '#4B0082'
    }
    tags = [f'<span style="background-color: {genre_colors.get(genre, "#CCCCCC")}; color: #FFFFFF; '
            f'padding: 5px; border-radius: 5px;">{genre}</span>' for genre in genres]
    return ' '.join(tags)

def beautify_feedback_data(data):
    """
    Beautifies feedback data for categorizing movies by liked, disliked, and yet-to-watch.
    """
    categories = {"Liked": [], "Disliked": [], "Yet to Watch": []}
    for movie, status in data.items():
        categories.get(status, []).append(movie)
    return categories

def create_movie_genres(movie_genre_df):
    """
    Creates a dictionary mapping each movie to its genres.
    """
    return {row['title']: row['genres'].split('|') for _, row in movie_genre_df.iterrows()}

def send_email_to_user(recipient_email, categorized_data, sender_password):
    """
    Sends an HTML email with movie recommendations to the user.
    """
    email_html_content = """
        <html>
        <head></head>
        <body>
            <h1 style="color: #333333;">Movie Recommendations from PopcornPicks</h1>
            <p style="color: #555555;">Dear Movie Enthusiast,</p>
            <p style="color: #555555;">We hope you're having a fantastic day!</p>
            <div style="padding: 10px; border: 1px solid #cccccc; border-radius: 5px; background-color: #f9f9f9;">
            <h2>Your Movie Recommendations:</h2>
            <h3>Movies Liked:</h3>
            <ul style="color: #555555;">{}</ul>
            <h3>Movies Disliked:</h3>
            <ul style="color: #555555;">{}</ul>
            <h3>Movies Yet to Watch:</h3>
            <ul style="color: #555555;">{}</ul>
            </div>
            <p style="color: #555555;">Enjoy your movie time with PopcornPicks!</p>
            <p style="color: #555555;">Best regards,<br>PopcornPicks Team 🍿</p>
        </body>
        </html>
        """
    # Load movie genres
    movie_genre_df = pd.read_csv('../../data/movies.csv')
    movie_to_genres = create_movie_genres(movie_genre_df)

    # HTML content for each category
    liked_movies = '\n'.join(f'<li>{movie} {create_colored_tags(movie_to_genres.get(movie, ["Unknown Genre"]))}</li>'
                             for movie in categorized_data['Liked'])
    disliked_movies = '\n'.join(f'<li>{movie} {create_colored_tags(movie_to_genres.get(movie, ["Unknown Genre"]))}</li>'
                                for movie in categorized_data['Disliked'])
    yet_to_watch_movies = '\n'.join(f'<li>{movie} {create_colored_tags(movie_to_genres.get(movie, ["Unknown Genre"]))}</li>'
                                    for movie in categorized_data['Yet to Watch'])

    # Final HTML message
    html_content = email_html_content.format(liked_movies, disliked_movies, yet_to_watch_movies)
    
    # Email configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'FilmFolio2024@gmail.com'
    subject = 'Your movie recommendation from PopcornPicks'

    # Create the email message
    message = MIMEMultipart('alternative')
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject
    message.attach(MIMEText(html_content, 'html'))

    # Connect and send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        logging.info("Email sent successfully!")
    except SMTPException as e:
        logging.error("Failed to send email: %s", e)
    finally:
        server.quit()
