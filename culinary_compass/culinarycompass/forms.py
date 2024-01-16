# Import flask_wtf for web forms
from flask_wtf import FlaskForm
# Import FileField and FileAllowed for uploading profile pictures
from flask_wtf.file import FileField, FileAllowed
# Import flask_login for user sessions
from flask_login import current_user
# Import fields for web forms
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, RadioField
# Import validators for web forms
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
# Import User model from models.py
from culinarycompass.models import User

# User registration form
class RegistrationForm(FlaskForm):
    # Username string field with validation for required data and length
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    # Email string field with validation for required data and email format
    email = StringField('Email', validators=[DataRequired(), Email()])
    # Password field with validation for required data
    password = PasswordField('Password', validators=[DataRequired()])
    # Confirm password field with validation for required data and equality to password field
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    # Submit field for submitting the form
    submit = SubmitField('Sign Up')

    # Custom validation to check if the username is already in use
    def validate_username(self, username):
        # Query the database for a user with the provided username
        user = User.query.filter_by(username=username.data).first()
        # If a user with the provided username exists, raise a validation error
        if user:
            raise ValidationError('Username already in use. Please choose a different username.')

    # Custom validation to check if the email is already in use
    def validate_email(self, email):
        # Query the database for a user with the provided email
        user = User.query.filter_by(email=email.data).first()
        # If a user with the provided email exists, raise a validation error
        if user:
            raise ValidationError('Email already in use. Please use a different email.')

# User login form
class LoginForm(FlaskForm):
    # Email string field with validation for required data and email format
    email = StringField('Email', validators=[DataRequired(), Email()])
    # Password field with validation for required data
    password = PasswordField('Password', validators=[DataRequired()])
    # Remember me field for keeping the user logged in
    remember = BooleanField('Remember Me')
    # Submit field for submitting the form
    submit = SubmitField('Login')

# Update account form
class UpdateAccountForm(FlaskForm):
    # Username string field with validation for required data and length
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    # Email string field with validation for required data and email format
    email = StringField('Email', validators=[DataRequired(), Email()])
    # Profile picture field with validation for allowed file types
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    # Submit field for submitting the form
    submit = SubmitField('Update')

    # Custom validation to check if the username is already in use
    def validate_username(self, username):
        # If the username is different from the current user's username, query the database for a user with the provided username
        if username.data != current_user.username:
            # Query the database for a user with the provided username
            user = User.query.filter_by(username=username.data).first()
            # If a user with the provided username exists, raise a validation error
            if user:
                raise ValidationError('Username already in use. Please choose a different username.')

    # Custom validation to check if the email is already in use
    def validate_email(self, email):
        # If the email is different from the current user's email, query the database for a user with the provided email
        if email.data != current_user.email:
            # Query the database for a user with the provided email
            user = User.query.filter_by(email=email.data).first()
            # If a user with the provided email exists, raise a validation error
            if user:
                raise ValidationError('Email already in use. Please use a different email.')

# questionnaire form for dietary preferences
class QuestionnaireForm(FlaskForm):
    # Options for vegetarianism
    choices = [('vegan', 'Vegan'), ('vegetarian', 'Vegetarian'), ('neither', 'Neither')]
    # Radio field for dietary preferences
    vegetarianism = RadioField('Vegetarian/Veganism', choices=choices)
    # Boolean field for gluten-free
    gluten = BooleanField('Gluten-Free')
    # Boolean field for healthy foods
    healthy = BooleanField('Healthy Foods')
    # Boolean field for alcohol
    no_alcohol = BooleanField('No Alcohol')
    # Submit field for submitting the form
    submit = SubmitField('Update')

# Request password reset form
class RequestResetForm(FlaskForm):
    # Email string field with validation for required data and email format
    email = StringField('Email', validators=[DataRequired(), Email()])
    # Submit field for submitting the form
    submit = SubmitField('Request Password Reset')

    # Custom validation to check if the account with the provided email exists
    def validate_email(self, email):
        # Query the database for a user with the provided email
        user = User.query.filter_by(email=email.data).first()
        # If a user with the provided email does not exist, raise a validation error
        if user is None:
            raise ValidationError('Account with email does not exist.')

# Reset password form
class ResetPasswordForm(FlaskForm):
    # Password field with validation for required data
    password = PasswordField('Password', validators=[DataRequired()])
    # Confirm password field with validation for required data and equality to password field
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    # Submit field for submitting the form
    submit = SubmitField('Reset Password')

# Search restaurants form (for users to input restaurants to "my restaurants")
class SearchRestaurantForm(FlaskForm):
    # Name field for restaurant name with validation for required data
    name = StringField('Name', validators=[DataRequired()])
    # Submit field for submitting the form
    submit = SubmitField('Search')

# Submit restaurant form (for users to rate and add restaurants to "my restaurants")
class SubmitRestaurantForm(FlaskForm):
    # Date field for date visited with validation for required data
    date = DateField('Date', validators=[DataRequired()])
    # Rating field for rating with validation for required data
    rating = RadioField('Rating', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], coerce=int)
    # Submit field for submitting the form
    submit = SubmitField('Add Restaurant')
    
# Report form (for generating a Culinary Mapped report)
class ReportForm(FlaskForm):
    # Submit field for submitting the form
    submit = SubmitField('Generate Report')
    
# Recommendation form (for generating a list of recommended restaurants)
class RecommendationForm(FlaskForm):
    # Submit field for submitting the form
    submit = SubmitField('Generate Recommendations')