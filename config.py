import os

class Config(object):
    project_dir = os.path.dirname(os.path.abspath(__file__))
    database_file = "sqlite:///{}".format(os.path.join(project_dir, "journal.db"))
    SECRET_KEY = ("29fc9d808e2fa590040dc20e43d41c7346324bf9fe184273")
    SQLALCHEMY_DATABASE_URI = database_file
    SQLALCHEMY_TRACK_MODIFICATIONS = False