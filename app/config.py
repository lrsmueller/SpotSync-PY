import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'project.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = './app/.flask_session/'
    SCOPE = "user-library-read playlist-read-private playlist-modify-private playlist-modify-public"
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(64)