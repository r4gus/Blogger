from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from . import login_manager
from flask_login import UserMixin, AnonymousUserMixin   # Managing user sessions
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
from markdown import markdown
import bleach

class Permission:
    NONE                = 0
    WRITE_ARTICLES      = 1
    MODIFY_ACCOUNTS     = 2
    SEND_INVITATIONS    = 4
    ADMIN               = WRITE_ARTICLES + MODIFY_ACCOUNTS + SEND_INVITATIONS

@login_manager.user_loader
def load_user(user_id):
    """Used by Flask-Login to retrieve information about the loggedin user"""
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(64))
    short       = db.Column(db.UnicodeText(128))
    body        = db.Column(db.UnicodeText)
    timestamp   = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id   = db.Column(db.Integer, db.ForeignKey('users.id'))
    body_html   = db.Column(db.UnicodeText)
    image_name  = db.Column(db.String(64))  # filename for picture

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        """ converts markdown to html """
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em',
                        'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'h4', 'p']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'),
                                          tags=allowed_tags, strip=True))


class Role(db.Model):
    __tablename__ = 'roles'
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users   = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return '<Role %r>' % self.name

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = Permission.NONE

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = Permission.NONE

    def has_permission(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        """ Initialize every role in roles and at it to the database """
        roles = {
                'Author' : [Permission.WRITE_ARTICLES],
                'Admin'  : [Permission.WRITE_ARTICLES, Permission.MODIFY_ACCOUNTS, Permission.SEND_INVITATIONS],
        }
        default_role = 'Author'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id                  = db.Column(db.Integer, primary_key=True)
    username            = db.Column(db.String(128), unique=True, index=True)
    email               = db.Column(db.String(128), index=True, unique=True)
    password_hash       = db.Column(db.String(128))
    role_id             = db.Column(db.Integer, db.ForeignKey('roles.id'))
    self_description    = db.Column(db.UnicodeText(512))
    confirmed           = db.Column(db.Boolean, default=False)      # set to false until the user has confirmed his email
    member_since        = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen           = db.Column(db.DateTime(), default=datetime.utcnow)
    posts               = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['SWEET_EMAIL']:
                self.role = Role.query.filter_by(name='Admin').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        """ Generate confirmation token to validate an account """
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm' : self.id}).decode('utf-8')
    
    def confirm(self, token):
        """ Validate user account by confirming security token """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_admin(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        """ Update the last_seen field """
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()


class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False

    def is_admin(self):
        return False


login_manager.anonymous_user = AnonymousUser    # Use the custom class as default (anonymous) user

db.event.listen(Post.body, 'set', Post.on_changed_body) # Generate Html from body (markdown) if body changes


