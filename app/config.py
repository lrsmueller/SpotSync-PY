import os

config = {}

basedir = os.path.abspath(os.path.dirname(__file__))
config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(basedir, 'project.db')
config['SECRET_KEY'] = os.urandom(64)
config['SESSION_TYPE'] = 'filesystem'
config['SESSION_FILE_DIR'] = './.flask_session/'


basedir = os.path.abspath(os.path.dirname(__file__))
config = {
    "SQLALCHEMY_DATABASE_URI": 'sqlite:///' + os.path.join(basedir, 'project.db'),
    'SECRET_KEY': os.urandom(64),
    'SESSION_TYPE':'filesystem',
    'SESSION_FILE_DIR': './.flask_session/'
}