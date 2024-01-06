from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from culinarycompass.models import User

# User registration form
class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):        
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already in use. Please choose a different username.')
    
    def validate_email(self, email):        
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already in use. Please use a different email.')

# User login form
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# Update account form
class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')
    
    def validate_username(self, username):
        if username.data != current_user.username:         
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already in use. Please choose a different username.')
    
    def validate_email(self, email):       
        if email.data != current_user.email: 
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already in use. Please use a different email.')

# Questionnaire form


# Request password reset form
class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):        
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Account with email does not exist.')

# Reset password form
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

# Search for restaurants form
class SearchRestaurantForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    location = TextAreaField('Location', validators=[DataRequired()])
    submit = SubmitField('Search')

# Submit restaurant form
class SubmitRestaurantForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    rating = IntegerField('Rating', validators=[DataRequired()])
    submit = SubmitField('Add Restaurant')

    # This will be dictated by the maps API
    # What information is required to find and validate that the restaurant exists
    
# Classes for adding the rating field