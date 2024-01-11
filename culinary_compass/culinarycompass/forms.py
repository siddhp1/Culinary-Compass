from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from culinarycompass.models import User

# User registration form
class RegistrationForm(FlaskForm):
    # Form for user registration
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    # Custom validation to check if the username is already in use
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already in use. Please choose a different username.')

    # Custom validation to check if the email is already in use
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already in use. Please use a different email.')

# User login form
class LoginForm(FlaskForm):
    # Form for user login
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# Update account form
class UpdateAccountForm(FlaskForm):
    # Form for updating user account information
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    # Custom validation to check if the username is already in use
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already in use. Please choose a different username.')

    # Custom validation to check if the email is already in use
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already in use. Please use a different email.')

# Questionnaire form
class QuestionnaireForm(FlaskForm):
    # Form for collecting user preferences
    choices = [('vegan', 'Vegan'), ('vegetarian', 'Vegetarian'), ('neither', 'Neither')]
    dietary_preference = RadioField('Dietary Preference', choices=choices)
    gluten = BooleanField('Gluten-Free')
    allergies = BooleanField('Allergies')
    alcohol = BooleanField('Alcohol')
    submit = SubmitField('Submit')

# Request password reset form
class RequestResetForm(FlaskForm):
    # Form for requesting a password reset
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    # Custom validation to check if the account with the provided email exists
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Account with email does not exist.')

# Reset password form
class ResetPasswordForm(FlaskForm):
    # Form for resetting the password
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

# Search for restaurants form
class SearchRestaurantForm(FlaskForm):
    # Form for searching restaurants
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Search')

# Submit restaurant form
class SubmitRestaurantForm(FlaskForm):
    # Form for submitting restaurant visits
    date = DateField('Date', validators=[DataRequired()])
    rating = RadioField('Rating', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], coerce=int)
    submit = SubmitField('Add Restaurant')

class FindRestaurantForm(FlaskForm):
    submit = SubmitField('Search')
    