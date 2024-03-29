from flask import Flask, request, render_template, session, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from . import user
from ..decorators import admin_required, permission_required
from ..models import User, Role, Permission, Post
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, EditPostForm, EditPasswordForm
from .. import db
from werkzeug.utils import secure_filename
import os
from cloudinary.uploader import upload, destroy
from cloudinary.utils import cloudinary_url

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@user.route('/<username>')
def user_info(username):
    """ User info page """
    page = request.args.get('page', 1, type=int) # get the requested page or the first one
    u = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author_id=u.id)
    posts = posts.order_by(Post.timestamp.desc())
    pagination = posts.paginate(page, per_page=int(current_app.config['POSTS_PER_PAGE']), error_out=False)
    posts = pagination.items
    return render_template('user/user.html', user=u, posts=posts, pagination=pagination)

@user.route('/administrate-users')
@login_required
@admin_required
def admin():
    user = User.query.filter_by(id=current_user.id).first_or_404()
    users = User.query.all()
    return render_template('user/admin.html', admin=user, users=users)

@user.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():

        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    """
                    if os.path.isfile(os.path.join(current_app.config['USER_PICTURES'], filename)) == False:
                        if current_user.image_name and current_user.image_name != 'user_placeholder.jpg':
                            if os.path.isfile(os.path.join(current_app.config['USER_PICTURES'], current_user.image_name)):
                                os.remove(os.path.join(current_app.config['USER_PICTURES'], current_user.image_name))
                        file.save(os.path.join(current_app.config['USER_PICTURES'], filename))
                        current_user.image_name = filename
                    else:
                        flash('Filename does already exist')
                        return render_template(url_for('user.edit_profile'), form=form)
                    """
                    
                    if current_user.image_id:
                        destroy(public_id=current_user.image_id) # delete old image
                    upload_result = upload(file, folder="images", unique_filename=True) # upload new image

                    if upload_result:
                        secure_url = upload_result['secure_url'] # url that points to the image
                        public_id = upload_result['public_id'] # image id
                        current_user.image_url = secure_url
                        current_user.image_id = public_id
                    else:
                        flash("Couldn't upload the given file.")
                        return render_template(url_for('user.edit_profile'), form=form)
                else:
                    flash('Invalid filename.')
                    return render_template(url_for('user.edit_profile'), form=form)

        current_user.username = form.username.data
        current_user.self_description = form.self_description.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('user.user_info', username=current_user.username))
    form.username.data = current_user.username
    form.self_description.data = current_user.self_description
    return render_template('user/edit_profile.html', form=form)

@user.route('/new_password/<int:id>', methods=['GET', 'POST'])
@login_required
def new_password(id):
    user = User.query.get_or_404(id)
    form = EditPasswordForm()
    if form.validate_on_submit():
        if current_user == user or current_user.is_admin():
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Password succesfully changed.')
            return redirect(url_for('.user_info', username=user.username))
        else:
            flash("You're not allowed to perform this operation.")
            return redirect(url_for('.user_info', username=user.username))
    return render_template('user/edit_password.html', form=form, user=user)


@user.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.role = Role.query.get(form.role.data)
        user.self_description = form.self_description.data
        user.confirmed = form.confirmed.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated')
        return redirect(url_for('.user_info', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.self_description.data = user.self_description
    return render_template('user/edit_profile_admin.html', form=form, user=user)


@user.route('/delete_user/<int:id>', methods=['GET'])
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)

    if current_user.id != id and not current_user.is_admin():
        flash("You can only delete your own account")
        return redirect(url_for('user.user_info', username=current_user.username))
    else:
        """
        if user.image_name and user.image_name != 'user_placeholder.jpg':
            if os.path.isfile(os.path.join(current_app.config['USER_PICTURES'], user.image_name)):
                os.remove(os.path.join(current_app.config['USER_PICTURES'], user.image_name))
        """
        if user.image_id:
            destroy(public_id=user.image_id) # delete old image

        db.session.delete(user)
        db.session.commit()
        flash("Account successfully deleted")
        return redirect(url_for('main.index'))


@user.route('/new_post', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(title = form.title.data,
                    short = form.short.data,
                    body = form.body.data,
                    author = current_user._get_current_object())

        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':                         # has a file been selected ?
                if file and allowed_file(file.filename):        # is file allowed for upload ?
                    filename = secure_filename(file.filename)
                    """
                    if os.path.isfile(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)) == False: # does file name already exist?
                        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                        post.image_name = filename
                    else:
                        flash('Filename does already exist.')
                        return render_template('user/new_post.html', form=form)
                    """
                    upload_result = upload(file, folder="images", unique_filename=True) # upload new image

                    if upload_result:
                        secure_url = upload_result['secure_url'] # url that points to the image
                        public_id = upload_result['public_id'] # image id
                        post.image_url = secure_url
                        post.image_id = public_id
                    else:
                        flash("Couldn't upload the given file.")
                        return render_template('user/new_post.html', form=form)
                else:
                    flash('Invalid filename.')
                    return render_template('user/new_post.html', form=form)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('user/new_post.html', form=form)


@user.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    form = EditPostForm()

    if post.author_id != current_user.id and not current_user.is_admin():
        flash("You can only edit your own posts.")
        return redirect(url_for('main.index'))

    if form.validate_on_submit():
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    """
                    if os.path.isfile(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)) == False:
                        if post.image_name and post.image_name != 'placeholder.jpg':
                            if os.path.isfile(os.path.join(current_app.config['UPLOAD_FOLDER'], post.image_name)):
                                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], post.image_name))
                            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                            post.image_name = filename
                    else:
                        flash('Invalid filename.')
                        return render_template(url_for('user.edit_post'), form=form)
                    """
                    if post.image_id:
                        destroy(public_id=post.image_id) # delete old image
                    upload_result = upload(file, folder="images", unique_filename=True) # upload new image

                    if upload_result:
                        secure_url = upload_result['secure_url'] # url that points to the image
                        public_id = upload_result['public_id'] # image id
                        post.image_url = secure_url
                        post.image_id = public_id
                    else:
                        flash("Couldn't upload the given file.")
                        return render_template(url_for('user.edit_post'), form=form)
                else:
                    flash('Invalid filename.')
                    return render_template(url_for('user.edit_post'), form=form)
        post.title = form.title.data
        post.short = form.short.data
        post.body  = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('main.post', id=post.id))

    form.title.data = post.title
    form.short.data = post.short
    form.body.data = post.body
    return render_template('user/edit_post.html', form=form)


@user.route('/delete_post/<int:id>', methods=['GET'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def delete_post(id):
    post = Post.query.get_or_404(id)

    if post.author_id != current_user.id and not current_user.is_admin():
        flash("You can only delete your own posts.")
        return redirect(url_for('main.post', id=post.id))
    else:
        """
        if post.image_name and post.image_name != 'placeholder.jpg':
            if os.path.isfile(os.path.join(current_app.config['UPLOAD_FOLDER'], post.image_name)):
                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], post.image_name))
        """

        if post.image_id:
            destroy(public_id=post.image_id) # delete old image
        db.session.delete(post)
        db.session.commit()
        flash("Post successfully deleted.")
        return redirect(url_for('main.index'))





