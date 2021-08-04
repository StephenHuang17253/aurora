from main import db


BooksAuthors = db.Table("BooksAuthors", db.Model.metadata,
                db.Column("bookid", db.Integer, db.ForeignKey("Books.bookid")),
                db.Column("authorid", db.Integer, db.ForeignKey("Authors.authorid")))


BooksUsers = db.Table("BooksUsers", db.Model.metadata,
                db.Column("bookid", db.Integer, db.ForeignKey("Books.bookid")),
                db.Column("userid", db.Integer, db.ForeignKey("Users.userid")))


BooksGenres = db.Table("BooksGenres", db.Model.metadata,
                db.Column("bookid", db.Integer, db.ForeignKey("Books.bookid")),
                db.Column("genreid", db.Integer, db.ForeignKey("Genres.genreid")))


class Books (db.Model):
    __tablename__ = "Books"
    bookid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80)) 
    synopsis = db.Column(db.String(80)) 
    year = db.Column(db.String(80)) 
    
    authors = db.relationship("Authors", secondary=BooksAuthors, back_populates="books" )
    users = db.relationship("Users", secondary=BooksUsers, back_populates="books")  
    genres = db.relationship("Genres", secondary=BooksGenres, back_populates="books")


class Authors (db.Model):
    __tablename__ = "Authors"
    authorid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80)) 

    books = db.relationship("Books", secondary=BooksAuthors, back_populates="authors")


class Users (db.Model):
    __tablename__ = "Users"
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))       
    password = db.Column(db.String(80)) 

    books = db.relationship("Books", secondary=BooksUsers, back_populates="users")


class Genres (db.Model):
    __tablename__ = "Genres"
    genreid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))       
    description = db.Column(db.String(80)) 

    books = db.relationship("Books", secondary=BooksGenres, back_populates="genres")