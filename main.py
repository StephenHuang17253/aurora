"""
Stephen Huang
03/05/21 - 
Year 13 Flask webapp: Digital Reading Log/Journal
"""

import os
from flask import Flask, render_template, session, redirect, url_for, request, Blueprint, flash
from flask_sqlalchemy import SQLAlchemy
from random import randint, choice
from werkzeug.security import generate_password_hash, check_password_hash


project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "journal.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.secret_key = ("29fc9d808e2fa590040dc20e43d41c7346324bf9fe184273")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

import models


@app.route('/', methods=["GET", "POST"])
def home():
    return render_template("home.html")


@app.route('/journal', methods=["GET", "POST"])
def journal():
    #book = Books.query.filter_by(title="Dune").first_or_404()
    book = models.Books.query.all()
    return render_template("journal.html", book=book, title=journal)


@app.route('/update', methods=["GET", "POST"])
def update():
    book = models.Books.query.all()
    if request.form:
        new_book = models.Books()
        new_book.title = request.form.get("title")
        new_book.sypnosis = request.form.get("sypnosis")   
        new_book.year = request.form.get("year")
        new_book.genres = request.form.get("genres")
        db.session.add(new_book)
        db.session.commit()
    return render_template("update.html", book=book)


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
            return render_template('login.html', error='Username exceeds limit of 20 characters or does not exist')
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
