from flask import Flask, request, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap               # html bootstrap layout
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config
from flask_moment import Moment

bootstrap = Bootstrap()
db = SQLAlchemy()       # data base
migrate = Migrate()     # data base migration
moment = Moment()       # date-time rendering


login_manager = LoginManager()
login_manager.login_view = 'auth.login' # set endpoint for login page

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    moment.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/user')

    return app
