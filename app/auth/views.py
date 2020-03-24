from flask import Flask, request, render_template, session, redirect, url_for, flash
from . import auth
from .forms import LoginForm, RegistrationForm
from .. import db
from ..models import User
from flask_login import login_user, logout_user, login_required

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, phone_number="", self_description="")
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registered. You can now login.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
