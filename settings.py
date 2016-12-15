import os


class Config(object):
    ROOT_PATH = os.path.dirname(__file__)
    LOG_PATH = os.path.join(ROOT_PATH, 'logs/request.log')
    TIME_ZONE = 'Europe/Moscow'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_POOL_RECYCLE = 200
    SQLALCHEMY_DATABASE_URI = "sqlite:///url.db"
