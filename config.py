import os

class Config(object):
    project_dir = os.path.dirname(os.path.abspath(__file__))
    database_file = "sqlite:///{}".format(os.path.join(project_dir, "journal.db"))
    SECRET_KEY = ("ajkdfhasdklfaklfjdskal;fakl;djskfjakl;fdjsa")
    SQLALCHEMY_DATABASE_URI = database_file
    SQLALCHEMY_TRACK_MODIFICATIONS = False