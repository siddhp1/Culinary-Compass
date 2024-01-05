import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from culinarycompass import app, db, bcrypt, mail
from culinarycompass.forms import (RegistrationForm,
                                   LoginForm,
                                   UpdateAccountForm,
                                   RequestResetForm,
                                   ResetPasswordForm)
from culinarycompass.models import User, Restaurant
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
    
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
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return(render_template('login.html', title='Login', form=form))

# Logout page
@app.route("/logout")
def logout():
    logout_user()
    return(redirect(url_for('home')))

# Account page
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    # Resize image
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return(picture_fn)

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return(redirect(url_for('account')))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return(render_template('account.html', title='Account', image_file=image_file, form=form))

# Reset password pages
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='siddhdevelopment@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, ignore this email.'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return(redirect(url_for('home')))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return(redirect(url_for('login')))
    return(render_template('reset_request.html', title='Reset Password', form=form))

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return(redirect(url_for('home')))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired token.', 'warning')
        return(redirect(url_for('reset_request')))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated. You are now able to log in.', 'success')
        return(redirect(url_for('login')))
    return(render_template('reset_token.html', title='Reset Password', form=form))