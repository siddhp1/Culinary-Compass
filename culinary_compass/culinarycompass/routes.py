from flask import render_template, url_for, flash, redirect, request
from culinarycompass import app, db, bcrypt
from culinarycompass.forms import RegistrationForm, LoginForm
from culinarycompass.models import User, Restaurant
from flask_login import login_user, current_user, logout_user, login_required
    
# Home page
@app.route("/")
@app.route("/home")
def home():
    return(render_template('home.html', title='Home'))

# My restaurants page
@app.route("/my")
@login_required
def my():
    return(render_template('my_restaurants.html', title='My Restaurants'))

# Find restaurants page
@app.route("/find")
@login_required
def find():
    return(render_template('find_restaurants.html', title='Find Restaurants'))

# Register page
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return(redirect(url_for('home')))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created. You are now able to log in.', 'success')
        return(redirect(url_for('login')))
    return(render_template('register.html', title='Register', form=form))

# Login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return(redirect(url_for('home')))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return(redirect(next_page) if next_page else redirect(url_for('home')))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return(render_template('login.html', title='Login', form=form))

# Logout page
@app.route("/logout")
def logout():
    logout_user()
    return(redirect(url_for('home')))

# Account page
@app.route("/account")
@login_required
def account():
    return(render_template('account.html', title='Account'))