from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, BooleanField, SelectField
from flask_login import current_user
from wtforms.validators import DataRequired, Length, Regexp, ValidationError, Email
from ..models import User, Role

class EditProfileForm(FlaskForm):
    username            = StringField('Username', validators=[Length(1, 128),
                          Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    self_description    = TextAreaField('About me', validators=[Length(0, 512)])
    submit              = SubmitField('Submit')

    def validate_username(self, field):
        if field.data != current_user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class EditProfileAdminForm(FlaskForm):
    email       = StringField('Email', validators=[DataRequired(), Length(1, 128), Email()])
    username    = StringField('Username', validators=[Length(1, 128),
                  Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    confirmed   = BooleanField('Confirmed')
    role        = SelectField('Role', coerce=int)
    self_description = TextAreaField('About me', validators=[Length(0, 512)])
    submit              = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user    # the user to update

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
