"""
Stephen Huang
03/05/21 - 
Year 13 Flask webapp: Digital Reading Log/Journal
git config --global user.email "17253@burnside.school.nz"
git config --global user.name "StephenHuang17253"
^ Have my git config pasted here to speed up pushing commits at end of day.
"""

import os
from flask import Flask, render_template, session, redirect, url_for, request, Blueprint, flash
from flask_sqlalchemy import SQLAlchemy
from random import randint, choice
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config


project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "journal.db"))

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

import models


@app.route('/') #Home
def home():
    return render_template("home.html")


@app.route('/allbooks') #This page simply displays all books, it will be replaced eventually by one that is user-specific.
def allbooks():
    book = models.Books.query.all()
    return render_template("allbooks.html", book=book)


@app.route('/journal') #This journal only displays books that are related to the logged in user.
def journal():
    user = models.Users.query.filter_by(userid=session['user']).first_or_404()
    return render_template("journal.html", user=user, userid=user)


@app.route('/book/<title>') #Each book has an individual page with its information. Here you can find the sypnosis of a book which you can't find on the journal tables.
def book(title):
    book = models.Books.query.filter_by(title=title).first_or_404()
    return render_template('book.html', book=book)


@app.route('/author/<name>') #Each author has their own page that displays all the books they've written.
def author(name):
    author = models.Authors.query.filter_by(name=name).first_or_404()
    book = models.Books.query.all()
    return render_template('author.html', author=author, book=book)

@app.route('/genre/<name>') #Each genre has its own page that displays all the books belonging to that genre.
def genre(name):
    genre = models.Genres.query.filter_by(name=name).first_or_404()
    return render_template('genre.html', genre=genre)


@app.route('/update', methods=["GET", "POST"]) #This page allows users to update the database.
def update():
    book = models.Books.query.all()
    return render_template("update.html", book=book)


@app.route('/updatetitle', methods=["POST"]) #Function to allow users to rename a book.
def updatetitle():
    try:
        new_title = request.form.get("new_title") #First we request the new title.
        old_title = request.form.get("old_title") #Then we look for the old title.
        book = models.Books.query.filter_by(title=old_title).first() #Finds the first title that matches the old title.
        book.title = new_title #Replace that book's old title with the new title.
        db.session.commit() #Commit to the DB.
    except Exception as e:
        print("Couldn't update book title")
        print(e)
    return redirect("/journal")


@app.route('/addbook', methods=["GET", "POST"])
def addbook():
    if request.form:
        new_book = models.Books()
        author = models.Authors()
        genre = models.Genres()
        new_book.title = request.form.get("title")
        new_book.sypnosis = request.form.get("sypnosis")   
        new_book.year = request.form.get("year")
        author.name = request.form.get('author')        
        genre.name = request.form.get('genre')        
        new_book.authors.append(author)        
        new_book.genres.append(genre)
        db.session.add(new_book)
        db.session.commit()
    return redirect("/")


def current_user(): # current user function
    if session.get("user"): # if it is able to get a session for user
        return models.Users.query.get(session["user"]) # return the user info
    else:
        return False


@app.context_processor
def add_current_user():
    if session.get('user'): # if a user is logged in
        return dict(current_user=models.Users.query.get(session['user'])) # current user is equal to userinfo of user session
    return dict(current_user=None) # otherwise current user is none


@app.route('/login', methods=["GET", "POST"])
def login():
    if session.get("user"): # 
        return redirect('/') # redirects to home page
    if request.method == "POST": # request method 
        User = models.Users.query.filter(models.Users.username==request.form.get("username")).first() # form fillable to gain username variable:
        if User and check_password_hash(User.password, request.form.get("password")): # checks to see if the password is correct
            session['user']=User.userid
            return redirect('/') # redirects to home page

        else:
            return render_template('login.html', error='Username either exceeds limit of 20 characters or does not exist')
    return render_template("login.html") # the html template for this is login.html


@app.route('/logout') # /logout page
def logout(): # logout function
    try:
        session.pop("user") # ends user session
    except:
        print('you are already logged out!') # if there is no session to pop this will be printed
        return redirect("/login")
    return redirect("/")


@app.route('/signup', methods=["GET","POST"])
def signup(): # create user function
    if request.method == "POST":
        if len(request.form.get('username')) > 20: # if the inputted username is greater than 20 characters it will not be accepted
            return render_template('signup.html', error='Username exceeds limit of 20 characters') # prompts the user to create a shorter username
        elif models.Users.query.filter(models.Users.username == request.form.get("username")).first():
            return render_template('signup.html', error='Username already in use') # prompts the user to create a unique username
        else:
            user_info = models.Users (  
                username = request.form.get('username'), # requests username from the user as a form
                password = generate_password_hash(request.form.get('password'), salt_length=10), # requests password from the user as a form then salts and hashes it with a salt length of 10
            )
            db.session.add(user_info) # adds the data to the database
            db.session.commit() # commits the add
            flash("You have succesfully registed an Aurora account.") # tells the user they have succesfully logged in.
    return render_template('signup.html')


if __name__ == "__main__":
    app.run(debug=True)
