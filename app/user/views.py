from flask import Flask, request, render_template, session, redirect, url_for, flash
from flask_login import login_required, current_user
from . import user
from ..decorators import admin_required, permission_required
from ..models import User, Role
from .forms import EditProfileForm, EditProfileAdminForm
from .. import db

@user.route('/<username>')
@login_required
def user_info(username):
    """ User info page """
    u = User.query.filter_by(username=username).first_or_404()
    return render_template('user/user.html', user=u)

@user.route('/admin')
@login_required
@admin_required
def admin():
    return "You're admin"

@user.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.self_description = form.self_description.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('user.user_info', username=current_user.username))
    form.username.data = current_user.username
    form.self_description.data = current_user.self_description
    return render_template('user/edit_profile.html', form=form)

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
    return render_template('user/edit_profile.html', form=form, user=user)


