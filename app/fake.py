# Used in devellopment to fake data for test purposes
from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Post

def users(count=100):
    fake = Faker()
    i = 0
    while i < count:
        u = User(username=fake.user_name(),
                 email=fake.email(),
                 confirmed=True,
                 self_description=fake.text(),
                 member_since=fake.past_date())
        u.set_password('password')
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()

def posts(count=100):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(title=fake.sentence(),
                 short=fake.sentence(),
                 body=fake.text(),
                 timestamp=fake.past_date(),
                 author=u)
        db.session.add(p)
    db.session.commit()

