from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, RadioField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from culinarycompass.models import User

# User registration form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    # Validation to check if the username is already in use
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already in use. Please choose a different username.')

    # Validation to check if the email is already in use
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already in use. Please use a different email.')

# User login form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# Update account form
class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    # Validation to check if the username is already in use
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already in use. Please choose a different username.')

    # Validation to check if the email is already in use
    def validate_email(self, email):
        # If the email is different from the current user's email, query the database for a user with the provided email
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already in use. Please use a different email.')

# Questionnaire form for dietary preferences
class QuestionnaireForm(FlaskForm):
    choices = [('vegan', 'Vegan'), ('vegetarian', 'Vegetarian'), ('neither', 'Neither')]
    vegetarianism = RadioField('Vegetarian/Veganism', choices=choices)
    
    gluten = BooleanField('Gluten-Free')
    healthy = BooleanField('Healthy Foods')
    no_alcohol = BooleanField('No Alcohol')
    submit = SubmitField('Update')

# Request password reset form
class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    # Validation to check if the account with the provided email exists
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Account with email does not exist.')

# Reset password form
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

# Search restaurants form
class SearchRestaurantForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Search')

# Submit restaurant form
class SubmitRestaurantForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    rating = RadioField('Rating', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], coerce=int)
    submit = SubmitField('Add Restaurant')
    
# Report form
class ReportForm(FlaskForm):
    submit = SubmitField('Generate Report')
    
# Recommendation form
class RecommendationForm(FlaskForm):
    radius = IntegerField('Search Radius (km)', default=5, validators=[NumberRange(min=1, max=30)], render_kw={"placeholder": "5"})
    submit = SubmitField('Generate Recommendations')