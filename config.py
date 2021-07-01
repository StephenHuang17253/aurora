import os

class Config(object):
    project_dir = os.path.dirname(os.path.abspath(__file__))
    SECRET_KEY = "ajkdfhasdklfaklfjdskal;fakl;djskfjakl;fdjsa"
    SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(os.path.join(project_dir, "journal.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False