from flask import Flask, request, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap               # html bootstrap layout
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from login import LoginForm                         # login form
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'   # used by flask wtf for encryption
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database/data.sqlite')    # path to sqlite db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)

db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html', name=session.get('name'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash('Invalid username or password')
            return redirect(url_for('login'))
        else:
            if user.check_password(form.password.data):
                flash('Successfully loged in!')
                session['name'] = form.username.data
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password')
                return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500





class Role(db.Model):
    __tablename__ = 'roles'
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(64), unique=True)
    users   = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id                  = db.Column(db.Integer, primary_key=True)
    username            = db.Column(db.String(128), unique=True, index=True)
    email               = db.Column(db.String(128), index=True, unique=True)
    phone_number        = db.Column(db.String(16), index=True)
    password_hash       = db.Column(db.String(128))
    role_id             = db.Column(db.Integer, db.ForeignKey('roles.id'))
    self_description    = db.Column(db.UnicodeText(512))

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)





