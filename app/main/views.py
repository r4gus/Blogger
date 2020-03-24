from flask import Flask, request, render_template, session, redirect, url_for, flash
from . import main
from .. import db
from ..models import User, Permission
from ..decorators import admin_required, permission_required
from flask_login import login_required

@main.route('/')
def index():
    return render_template('index.html', name=session.get('name'))

@main.route('/post')
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    return "Be creative"
