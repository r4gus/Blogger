from flask import Flask, request, render_template, session, redirect, url_for, flash, current_app
from . import main
from .. import db
from ..models import User, Permission, Post
from ..decorators import admin_required, permission_required
from flask_login import login_required

@main.route('/')
def index():
    page = request.args.get('page', 1, type=int) # get the requested page or the first one
    search_str = request.args.get('search')

    if search_str is not None:
        entries = Post.query.filter(Post.title.contains(search_str))
        entries = entries.order_by(Post.timestamp.desc())
    else:
        entries = Post.query.order_by(Post.timestamp.desc())

    pagination = entries.paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], 
                                  error_out=False) 
    posts = pagination.items
    print(search_str)
    return render_template('index.html', posts=posts, pagination=pagination, search_str=search_str)


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)
