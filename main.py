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

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


import models


@app.route('/')
def home():
    return render_template("home.html", page_title="Home")


#This page displays a table of all the books read by the user that is currently logged in.
@app.route('/journal')
def journal():
    user = models.Users.query.filter_by(userid=session['user']).first_or_404() #Checks the database of users for the currently logged in user
    return render_template("journal.html", user=user, userid=user, page_title="Journal")


@app.route('/books')
def books():
    book = models.Books.query.all() #All books
    return render_template("allbooks.html", book=book, page_title="Books")


#The code that allows users to click on book in the table and be taken to a page specifically about that book.
@app.route('/book/<title>')
def book(title):
    book = models.Books.query.filter_by(title=title).first_or_404() 
    return render_template('book.html', book=book, page_title=title)


#Allows for users to go to a page dedicated to a specific author.
@app.route('/author/<name>')
def author(name):
    author = models.Authors.query.filter_by(name=name).first_or_404()
    return render_template('author.html', author=author, book=book, page_title=author)


#Allows for users to go to a page dedicated to a specific genre.
@app.route('/genre/<name>')
def genre(name):
    genre = models.Genres.query.filter_by(name=name).first_or_404()
    return render_template('genre.html', genre=genre, page_title=genre)


#Allows for users to make changes to the database.
@app.route('/update', methods=["GET", "POST"])
def update():
    user = models.Users.query.filter_by(userid=session['user']).first_or_404()
    author_list = models.Authors.query.all()
    genre_list = models.Genres.query.all()
    book = models.Books.query.all()
    return render_template("update.html", user=user, genre_list=genre_list, author_list=author_list, userid=user, book=book, page_title="Update")


#Function that updates a book title.
@app.route('/updatetitle', methods=["POST"])
def updatetitle():
    try:
        newtitle = request.form.get("newtitle") #First we request the new title.
        oldtitle = request.form.get("oldtitle") #Then we look for the old title.
        book = db.session.query(models.Books).filter_by(title=oldtitle).first_or_404() #Finds the first book title that matches the old title.
        book.title = newtitle #Sets the title of the book to the new title.
        db.session.commit()
    except Exception as e:
        print("Could not update title")
        print(e)
    return redirect("/journal")


#Function that updates the authors of a book, allowing for a book to have multiple authors.
@app.route('/updateauthor/<int:book_id>', methods=["POST"])
def updateauthor(book_id):
    try:
        authors = request.form.getlist('author')
        author_models = []
        for author_name in authors:
            if author_name.strip() == '':
                continue
            author = models.Authors.query.filter_by(name=author_name).first()
            if author is None:
                author = models.Authors(name=author)
                db.session.add(author)
            author_models.append(db.session.merge(author))
        print(authors)
        book = models.Books.query.get(book_id)
        book = db.session.merge(book)
        book.authors = author_models
        db.session.commit()
    except Exception as e:
        print("Could not update author")
        print(e)
    return redirect("/journal")


#WIP code to upload book cover images. Might just scrap this idea though.
@app.route('/upload', methods=["GET", "POST"])
def upload():
    return redirect("/")


#Allows users to search the database for a book to add to their database.
@app.route('/selectbook', methods=["GET", "POST"])
def selectbook():
    if request.form:
        try:
            book = request.form.get("book")
            selected_book = db.session.query(models.Books).filter_by(title=book).first_or_404()
            user = db.session.query(models.Users).filter_by(userid=session['user']).first_or_404()
            selected_book.users.append(user)
            db.session.add(selected_book)
            db.session.commit()
        except Exception as e:
            print("Could not add book")
            print(e)  
    return redirect("/journal   ")


#Allows users to add a new book to the database and their journal.
@app.route('/addbook', methods=["GET", "POST"])
def addbook():
    if request.form:
        new_book = models.Books()
        new_book.title = request.form.get("title")
        new_book.synopsis = request.form.get("synopsis")   
        new_book.year = request.form.get("year")
        genre = models.Genres()
        genre_name = request.form.get('genres')
        genre = db.session.query(models.Genres).filter_by(name=genre_name).first()
        if genre is None:
            genre = models.Genres(name=genre_name)
        author_name = request.form.get('author')
        author = db.session.query(models.Authors).filter_by(name=author_name).first()
        if author is None:
            author = models.Authors(name=author_name)
        user = db.session.query(models.Users).filter_by(userid=session['user']).first_or_404()
        db.session.add(new_book)             
        db.session.commit()
        new_book.users.append(user)
        new_book.authors.append(author)        
        new_book.genres.append(genre)  
        db.session.commit()          
    return redirect("/")
   

#Now deletes a book only from a particular user's journal and not everybody's.
@app.route("/delete", methods=["POST"])
def delete():    
    title = request.form.get("title")
    book = db.session.query(models.Books).filter_by(title=title).first()
    user = current_user()
    print(user.books)
    user.books.remove(book)
    db.session.commit()
    return redirect("/journal")

#This function gets the current user, letting us now whose journal needs to be displayed.
def current_user(): 
    if session.get("user"): # if it is able to get a session for user
        return db.session.query(models.Users).get(session["user"]) # return the user info
    else:
        return False


@app.context_processor
def add_current_user():
    if session.get('user'): # if a user is logged in
        return dict(current_user=models.Users.query.get(session['user'])) # current user is equal to userinfo of user session
    return dict(current_user=None) # otherwise current user is none


@app.route('/login', methods=["GET", "POST"]) # /Login page
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
    return render_template("login.html", page_title="Login") # the html template for this is login.html


@app.route('/logout') # /logout page
def logout(): # logout function
    try:
        session.pop("user") # ends user session
    except:
        print('you are already logged out!') # if there is no session to pop this will be printed
        return redirect("/login")
    return redirect("/")


@app.route('/signup', methods=["GET","POST"])
def signup(): # create account / register function
    if request.method == "POST":
        if len(request.form.get('username')) > 20: # if the inputted username is greater than 20 characters it will not be accepted
            flash("Username exceeds limit of 20 characters") #Informs user that their username exceeds 20 characters            
            return render_template('signup.html', error='Username exceeds limit of 20 characters') # prompts the user to create a shorter username
        elif models.Users.query.filter(models.Users.username == request.form.get("username")).first():
            flash("Name already in use") #Informs user that their name is already in use
            return render_template('signup.html', error='Username already in use') # prompts the user to create a unique username
        else:
            user_info = models.Users (  
                username = request.form.get('username'), # requests username from the user as a form
                password = generate_password_hash(request.form.get('password'), salt_length=10), # requests password from the user as a form then salts and hashes it with a salt length of 10
            )
            db.session.add(user_info) # adds the data to the database
            db.session.commit() # commits the add
            flash("You have succesfully registed an Aurora account.") # tells the user they have succesfully logged in.
    return render_template('signup.html', page_title="Signup")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", page_title="404")


if __name__ == "__main__":
    app.run(debug=True)
