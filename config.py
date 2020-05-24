import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY                          = os.environ.get('SECRET_KEY') or 'hard to guess string'
    WEB_ADMIN                           = os.environ.get('WEB_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS      = False
    SWEET_EMAIL                         = os.environ.get('SWEET_EMAIL') or 'admin@example.com'
    SWEET_PW                            = os.environ.get('SWEET_PW')
    POSTS_PER_PAGE                      = os.environ.get('POSTS_PER_PAGE') or 9
    UPLOAD_FOLDER                       = os.path.join(basedir, 'app/static/images')
    USER_PICTURES                       = os.path.join(basedir, 'app/static/profile_pictures')
    ALLOWED_EXTENSIONS                  = {'png', 'jpg', 'jpeg'}
    SSL_REDIRECT                        = False

    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI     = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'database/data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI     = os.environ.get('TEST_DATABASE_URL') or 'sqlite://'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI     = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'database/data.sqlite')


class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        # handle reverse proxy server headers
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

    SSL_REDIRECT = True if os.environ.get('DYNO') else False

config = {
        'development' : DevelopmentConfig,
        'testing' : TestingConfig,
        'production' : ProductionConfig,
        'default' : DevelopmentConfig,
        'heroku' : HerokuConfig,
}


