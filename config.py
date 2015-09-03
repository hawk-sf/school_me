import os

basedir = os.path.abspath(os.path.dirname(__file__))

SF_DISTRICT_CDS = u'38684780000000'
MAPBOX_PK       = os.environ.get('MAPBOX_PK') or 'pk.eyJ1IjoiaGF3ay1zZiIsImEiOiJlZWZiODAxYzA1M2NkOGMyNzc4MmU0MWVmYmIxZDNlMiJ9.xNP0mDW8M6tZ58ZOKRRjTw'
DB_PASSWORD     = os.environ.get('SCHOOL_ME_DB_PASS') or ''


class Config:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'good luck in the lottery'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SCHOOL_DEV_DATABASE_URL') or \
                              'mysql://root:%s@localhost/school_me_dev?charset=utf8' % DB_PASSWORD


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql://root:%s@localhost/school_me?charset=utf8' % DB_PASSWORD

config = {
          'development': DevelopmentConfig,
          'production':  ProductionConfig,

          'default':     DevelopmentConfig,
         }
