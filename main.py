'''
Stephen Huang
03/05/21 -
Year 13 Flask webapp: Digital Reading Log/Journal
git config --global user.email '17253@burnside.school.nz'
git config --global user.name 'StephenHuang17253'
^ Have my git config pasted here to speed up pushing commits at end of day.
'''

import models
import os
from flask import Flask, render_template, session, redirect, url_for, request, Blueprint, flash
from flask_sqlalchemy import SQLAlchemy
from random import randint, choice
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from forms import LoginForm

project_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


@app.route('/')
def home():
    return render_template('home.html', page_title='Home')


# This page displays a table of all the books read by the user that is
# currently logged in.
@app.route('/journal')
def journal():
    try:
        # Checks the database of users for the currently logged in user
        user = models.Users.query.filter_by(
            userid=session['user']).first_or_404()
    except Exception as e:
        return redirect('404.html')
    return render_template(
        'journal.html',
        user=user,
        userid=user,
        page_title='Journal')


#  All books
@app.route('/books')
def books():
    book = models.Books.query.all()
    return render_template('allbooks.html', book=book, page_title='Books')


# The code that allows users to click on book in the table and be taken to
# a page specifically about that book.
@app.route('/book/<title>')
def book(title):
    book = models.Books.query.filter_by(title=title).first_or_404()
    return render_template('book.html', book=book, page_title=title)


#  Allows for users to go to a page dedicated to a specific author.
@app.route('/author/<name>')
def author(name):
    author = models.Authors.query.filter_by(name=name).first_or_404()
    return render_template(
        'author.html',
        author=author,
        book=book,
        page_title=author.name)


#  Allows for users to go to a page dedicated to a specific genre.
@app.route('/genre/<name>')
def genre(name):
    genre = models.Genres.query.filter_by(name=name).first_or_404()
    return render_template('genre.html', genre=genre, page_title=genre.name)


#  Allows for users to make changes to the database.
@app.route('/update', methods=['GET', 'POST'])
def update():
    try:
        # Checks the database of users for the currently logged in user
        user = models.Users.query.filter_by(
            userid=session['user']).first_or_404()
    except Exception as e:
        return redirect('404.html')
    author_list = models.Authors.query.all()
    genre_list = models.Genres.query.all()
    book = models.Books.query.all()
    return render_template(
        'update.html',
        user=user,
        genre_list=genre_list,
        author_list=author_list,
        userid=user,
        book=book,
        page_title='Update')


# Function that updates a book's title.
@app.route('/updatetitle', methods=['POST'])
def updatetitle():
    try:
        # First we request the new title.
        new_title = request.form.get('newtitle')
        # Then we look for the old title.
        old_title = request.form.get('oldtitle')
        # Finds the first book title that matches the old title.
        book = db.session.query(
            models.Books).filter_by(
            title=old_title).first_or_404()
        book.title = new_title  # Sets the title of the book to the new title.
        db.session.commit()
    except Exception as e:
        print('Could not update title')
        print(e)
        return redirect('404.html')
    return redirect('/update')


# Function that updates a book's synopsis.
@app.route('/updatesynopsis', methods=['POST'])
def updatesynopsis():
    try:
        # Requests the new book synopsis.
        new_synopsis = request.form.get('newsynopsis')
        # Requests the old book synopsis.
        old_synopsis = request.form.get('oldsynopsis')
        # Gets the first book with a synopsis that matches.
        book = db.session.query(
            models.Books).filter_by(
            synopsis=old_synopsis).first_or_404()
        # Sets the synopsis of the book to be equal to the new synopsis from
        # the form.
        book.synopsis = new_synopsis
        db.session.commit()
    except Exception as e:
        print('Could not update book synopsis')
        print(e)
        return redirect('404.html')
    return redirect('/update')


# Function that updates a book's year of release.
@app.route('/updateyear', methods=['POST'])
def updateyear():
    try:
        title = request.form.get('title')
        new_year = request.form.get('newyear')  # Requests the new book year.
        # Find the book we're looking for.
        book = db.session.query(
            models.Books).filter_by(
            title=title).first_or_404()
        # Sets the year of the book to be equal to the new year from the form.
        book.year = new_year
        db.session.commit()
    except Exception as e:
        print('Could not update book year')
        print(e)
        return redirect('404.html')
    return redirect('/update')


# Function that updates a book's genres, allowing for a book to have
# multiple genres or for the correction of typos.
@app.route('/updategenre/<int:book_id>', methods=['POST'])
def updategenre(book_id):
    try:
        genres = request.form.getlist('genre')
        genre_models = []
        for genre_name in genres:
            if genre_name.strip() == '':
                continue
            genre = models.Genres.query.filter_by(name=genre_name).first()
            if genre is None:
                genre = models.Genres(name=genre)
                db.session.add(genre)
            genre_models.append(db.session.merge(genre))
        print(genres)
        book = models.Books.query.get(book_id)
        book = db.session.merge(book)
        book.genres = genre_models
        db.session.commit()
    except Exception as e:
        print('Could not update genre')
        print(e)
        return redirect('404.html')
    return redirect('/update')


# Function that updates the authors of a book, allowing for a book to have
# multiple authors or for the correction of typos.
@app.route('/updateauthor/<int:book_id>', methods=['POST'])
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
        print('Could not update author')
        print(e)
        return redirect('404.html')
    return redirect('/update')


# Allows users to search the database for a book to add to their database.
@app.route('/selectbook', methods=['GET', 'POST'])
def selectbook():
    if request.form:
        try:
            book = request.form.get('book')
            selected_book = db.session.query(
                models.Books).filter_by(
                title=book).first_or_404()
            user = db.session.query(
                models.Users).filter_by(
                userid=session['user']).first_or_404()
            selected_book.users.append(user)
            db.session.add(selected_book)
            db.session.commit()
        except Exception as e:
            print('Could not add book')
            print(e)
            return redirect('404.html')
    return redirect('/journal')


# Allows users to add a new book to the database and their journal.
@app.route('/addbook', methods=['GET', 'POST'])
def addbook():
    if request.form:
        new_book = models.Books()
        new_book.title = request.form.get('title')
        new_book.synopsis = request.form.get('synopsis')
        new_book.year = request.form.get('year')
        genre = models.Genres()
        genre_name = request.form.get('genres')
        genre = db.session.query(
            models.Genres).filter_by(
            name=genre_name).first()
        if genre is None:
            genre = models.Genres(name=genre_name)
        author_name = request.form.get('author')
        author = db.session.query(
            models.Authors).filter_by(
            name=author_name).first()
        if author is None:
            author = models.Authors(name=author_name)
        user = db.session.query(
            models.Users).filter_by(
            userid=session['user']).first()
        db.session.add(new_book)
        db.session.commit()
        new_book.users.append(user)
        new_book.authors.append(author)
        new_book.genres.append(genre)
        db.session.commit()
    return redirect('/update')


# Now deletes a book only from a particular user's journal and not everybody's.
@app.route('/delete', methods=['POST'])
def delete():
    title = request.form.get('title')
    book = db.session.query(models.Books).filter_by(title=title).first()
    user = current_user()
    print(user.books)
    user.books.remove(book)
    db.session.commit()
    return redirect('/update')


# This function gets the current user, letting us now whose journal needs
# to be displayed.
def current_user():
    if session.get('user'):  # if it is able to get a session for user
        return db.session.query(models.Users).get(
            session['user'])  # return the user info
    else:
        return False


@app.context_processor
def add_current_user():
    if session.get('user'):  # if a user is logged in
        # current user is equal to userinfo of user session
        return dict(current_user=models.Users.query.get(session['user']))
    return dict(current_user=None)  # otherwise current user is none


@app.route('/login', methods=['GET', 'POST'])  # /Login page
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        print(login_form.login.data)
        user = models.Users.query.filter(
            models.Users.username == login_form.login.data).first()
        if user and check_password_hash(
            user.password, login_form.password.data):
            session['user'] = user.userid
            return redirect('/')
        else:
            return render_template(
                'login.html',
                error='Username or password is incorrect.',
                login_form=login_form)
    return render_template('login.html', login_form=login_form, page_title='Login')
    """
    if session.get('user'):
        return redirect('/')  # redirects to home page
    if request.method == 'POST':  # request method
        # form fillable to gain username variable:
        User = models.Users.query.filter(
            models.Users.username == request.form.get('username')).first()
        if User and check_password_hash(User.password, request.form.get(
                'password')):  # checks to see if the password is correct
            session['user'] = User.userid
            return redirect('/')  # redirects to home page
        else:
            flash('\nUsername or password was incorrect. Do you have caps lock on?')
            return render_template(
                'login.html',
                error='Username either exceeds limit of 20 characters or does not exist')
    # the html template for this is login.html
    """


@app.route('/logout')  # /logout page
def logout():  # logout function
    try:
        session.pop('user')  # ends user session
    except BaseException:
        # if there is no session to pop this will be printed
        print('you are already logged out!')
        return redirect('/login')
    return redirect('/')


@app.route('/signup', methods=['GET', 'POST'])
def signup():  # create account / register function
    login_form = LoginForm()
    if login_form.validate_on_submit():
        print(login_form.login.data)
        if 5 > len(login_form.login.data) > 12:
            # user is prompted to use a shorter/longer username
            return render_template(
                'signup.html',
                error='username must be between 5 and 12 characters')
        elif models.Users.query.filter(models.Users.username == login_form.login.data).first():
            # user is prompted to use a different username
            return render_template(
                'signup.html',
                error='username already in use')
        elif len(login_form.password.data) < 7:
            # account will not be created and user is prompted to make a
            # password of atleast 7 characters
            return render_template(
                'signup.html',
                error='password must be a minimum of 7 characters')
        else:
            user_info = models.Users(
                username=login_form.login.data, 
                # takes password inputted in form and salts and hashes
                password=generate_password_hash(
                    login_form.password.data, salt_length=10),
            )
            db.session.add(user_info)
            db.session.commit()
            # tells the user they have succesfully logged in.
            flash('\nYou have succesfully registed an Aurora account.')
    return render_template('signup.html', login_form=login_form, page_title='Signup')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', page_title='404')


if __name__ == '__main__':
    app.run(debug=True)
