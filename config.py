import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'good luck in the lottery'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SCHOOL_DEV_DATABASE_URL') or \
                              'mysql://root@localhost/school_me_dev?charset=utf8'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql://root@localhost/school_me?charset=utf8'

config = {
          'development': DevelopmentConfig,
          'production':  ProductionConfig,

          'default':     DevelopmentConfig,
         }
