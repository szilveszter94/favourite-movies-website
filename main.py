from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired
import requests


# API parameters
YOUR_API = "YOUR_API_HERE"
headers = {
    "api_key": YOUR_API,
    "query": "Inception"
}
website = "https://api.themoviedb.org/3/search/movie"

# insert bootstrap and sqalchemy into Flask
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies-collection.db"
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
db = SQLAlchemy(app)

# Create a Flask Edit Form
class EditForm(FlaskForm):
    rating_label = StringField('A te értékelésed, pl. 7.5', [InputRequired()])
    review_label = StringField('Rövid vélemény a filmről:', [InputRequired()])
    submit = SubmitField(label='Kész')

# Create a Flask Add Form
class AddForm(FlaskForm):
    movie_title = StringField('Film címe', [InputRequired()])
    submit = SubmitField(label='Kész')

# Setting up the sql database
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(350), nullable=False)
    rating = db.Column(db.String(10), nullable=False)
    ranking = db.Column(db.String(10), nullable=False)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

# Create the sql database
db.create_all()
movies = Movie.query.all()

# db.session.add(new_movie)
db.session.commit()

# Create the home page, rendering the index.html template
@app.route("/")
def home():
    movies = db.session.query(Movie).order_by(Movie.rating.desc()).all()
    for i in movies:
        i.ranking = movies.index(i) + 1
    db.session.commit()
    return render_template("index.html", new_movie=movies)

# Create the edit page
@app.route('/edit/<string:id>', methods=["POST", "GET"])
def edit(id):
    form = EditForm()
    if form.validate_on_submit():
        book_to_update = Movie.query.filter_by(id=id).first()
        book_to_update.rating = form.rating_label.data
        book_to_update.review = form.review_label.data
        db.session.commit()
        return redirect(url_for('home'))
    this_movie = Movie.query.filter_by(id=id).first()
    return render_template("edit.html", form=form, movie=this_movie)

# Create the Add page
@app.route('/add', methods=["POST", "GET"])
def add():
    form = AddForm()
    if request.method == "POST":
        title = form.movie_title.data
        headers_api = {
            "api_key": YOUR_API,
            "query": title
        }
        response = requests.get(url="https://api.themoviedb.org/3/search/movie?", params=headers_api)
        result = response.json()
        movies_api = (result["results"])
        return render_template("add.html", post=True, result=movies_api)
    return render_template("add.html", form=form)

# query and insert movie data into the database
@app.route('/add_movie/<string:id>', methods=["POST", "GET"])
def add_movie(id):
    headers_api = {
        "api_key": YOUR_API,
        "language": "hu"
    }
    response = requests.get(url=f"https://api.themoviedb.org/3/movie/{id}?", params=headers_api)
    result = response.json()
    title = (result["original_title"])
    description = (result["overview"])
    year = (result["release_date"]).split("-")[0]
    img_url = (result["poster_path"])
    first_path = "https://www.themoviedb.org/t/p/w600_and_h900_bestv2"
    new_movie = Movie(
        title=title,
        year=year,
        description=description,
        rating=11,
        ranking=11,
        review="Good movie.",
        img_url=f"{first_path}{img_url}"
    )
    db.session.add(new_movie)
    db.session.commit()
    this_movie = Movie.query.filter_by(title=title).first()
    id_1 = this_movie.id
    return redirect(url_for('edit', id=id_1))

# Delete page
@app.route('/delete/<string:id>')
def delete(id):
    book_id = id
    book_to_delete = Movie.query.get(book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

# Starting the website
if __name__ == '__main__':
    app.run(debug=True)
