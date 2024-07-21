import os
import secrets
import requests
from PIL import Image
from flask import jsonify, render_template, url_for, flash, redirect, request, session
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from sqlalchemy import or_

# Import modules, forms, models
from culinarycompass import app, db, bcrypt, mail, google, foursquare
from culinarycompass.forms import (RegistrationForm,
                                   LoginForm,
                                   UpdateAccountForm,
                                   RequestResetForm,
                                   ResetPasswordForm,
                                   SearchRestaurantForm,
                                   SubmitRestaurantForm,
                                   QuestionnaireForm,
                                   ReportForm,
                                   RecommendationForm)
from culinarycompass.models import User, Restaurant, RestaurantVisit, RestaurantFeature

# Custom classes
from .generate_report import ReportGenerator
from .generate_recommendation import RecommendationGenerator

# Home page
@app.route("/")
@app.route("/home")
def home():
    return(render_template('home.html', title='Home'))

# Register page
@app.route("/register", methods=['GET', 'POST'])
def register():
    
    # If the user is already logged in, redirect to the home page
    if current_user.is_authenticated:
        return(redirect(url_for('home')))
    
    # Registration form
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created. You are now able to log in!.', 'success')
        return(redirect(url_for('login')))
    return(render_template('register.html', title='Register', form=form))

# Login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    
    # If the user is already logged in, redirect to the home page
    if current_user.is_authenticated:
        return(redirect(url_for('home')))
    
    # Login form
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # Get the next page from the request (if the user was prompted to login from a login-required page)
            next_page = request.args.get('next')
            # Redirect to the next page if it exists, otherwise redirect to the home page
            return(redirect(next_page) if next_page else redirect(url_for('home')))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return(render_template('login.html', title='Login', form=form))

# Logout page
@app.route("/logout")
def logout():
    logout_user()
    return(redirect(url_for('login')))

# Account page

# Function to save the profile picture
def save_picture(form_picture):
    # Generate a random hex for the image name
    random_hex = secrets.token_hex(8)
    # Get the file extension
    _, f_ext = os.path.splitext(form_picture.filename)
    
    # Create the image name and path
    picture_name = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_name)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size) # Resize the image
    i.save(picture_path)
    
    return(picture_name)

# Function to send the report email
def send_report_email(pdf_path):
    msg = Message('Your Culinary Mapped',
                  sender='siddhdevelopment@gmail.com',
                  recipients=[current_user.email])
    msg.body = f'''Here is your Culinary Mapped:'''
    
    filename = os.path.basename(pdf_path)
    with app.open_resource(pdf_path) as attachment:
        msg.attach(filename, 'application/pdf', attachment.read())
    mail.send(msg)

# Function to delete the report
def delete_report(pdf_path):
    try:
        os.remove(pdf_path)
    except OSError as e:
        print(f"Error deleting file: {pdf_path} - {e}")

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():

    # Update account form
    update_account_form = UpdateAccountForm()
    if update_account_form.validate_on_submit():
        current_user.username = update_account_form.username.data
        current_user.email = update_account_form.email.data

        if update_account_form.picture.data:
            picture_file = save_picture(update_account_form.picture.data)
            current_user.image_file = picture_file

        db.session.commit()
        flash('Your account has been updated!', 'success')
        return(redirect(url_for('account')))
    elif request.method == 'GET':
        update_account_form.username.data = current_user.username
        update_account_form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    
    # Questionnaire form
    questionnaire_form = QuestionnaireForm()
    if questionnaire_form.validate_on_submit():
        current_user.vegetarianism = questionnaire_form.vegetarianism.data
        current_user.gluten = questionnaire_form.gluten.data
        current_user.healthy = questionnaire_form.healthy.data
        current_user.no_alcohol = questionnaire_form.no_alcohol.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return(redirect(url_for('account')))
    elif request.method == 'GET':
        questionnaire_form.vegetarianism.data = current_user.vegetarianism
        questionnaire_form.gluten.data = current_user.gluten
        questionnaire_form.healthy.data = current_user.healthy
        questionnaire_form.no_alcohol.data = current_user.no_alcohol
    
    # Report form
    report_form = ReportForm()
    if report_form.validate_on_submit():
        pdf_name = current_user.username
        pdf_path = os.path.join(app.root_path, 'static/reports', pdf_name + ".pdf")
        ReportGenerator.create_pdf(pdf_path, current_user.username)
        send_report_email(pdf_path)
        delete_report(pdf_path)
        flash('A report has been sent to your email', 'success')
        return(redirect(url_for('account')))
    return(render_template('account.html',
                           title='Account',
                           image_file=image_file,
                           update_account_form=update_account_form,
                           questionnaire_form=questionnaire_form,
                           report_form=report_form))

# Reset password pages

# Function to send the reset password email
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

    # If the user is already logged in, redirect to the home page
    if current_user.is_authenticated:
        return(redirect(url_for('home')))
    
    # Request reset
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return(redirect(url_for('login')))
    return(render_template('reset_request.html', title='Reset Password', form=form))

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):

    # If the user is already logged in, redirect to the home page
    if current_user.is_authenticated:
        return(redirect(url_for('home')))
    
    # Check if the token is valid
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired token.', 'warning')
        return(redirect(url_for('reset_request')))

    # Reset Password form (if token is valid)
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated. You are now able to log in.', 'success')
        return(redirect(url_for('login')))
    return(render_template('reset_token.html', title='Reset Password', form=form))

# Add restaurant page
@app.route("/add", methods=['GET', 'POST'])
@login_required
def add():
    # Search and submit forms
    search_form = SearchRestaurantForm()
    submit_form = SubmitRestaurantForm()

    if search_form.validate_on_submit():
        restaurant_full_name = search_form.name.data
        restaurant_coords = request.form['place_latlng']
        
        # Variable to store if restaurant is found in FourSquare database
        found = False
        
        # Get name of restaurant from google autocomplete
        parts = restaurant_full_name.split(', ', 1)
        restaurant_name = parts[0] # Get the name of the restaurant
        
        # FourSquare API request
        url = f"https://api.foursquare.com/v3/places/match?name={restaurant_name}&ll={restaurant_coords}&fields=fsq_id%2Ccategories%2Cmenu%2Cwebsite%2Cprice%2Ctastes%2Cfeatures%2Clocation%2Cdescription"
        headers = {
            "accept": "application/json",
            "Authorization": foursquare
        }
        response = requests.get(url, headers=headers)
        parsed_data = response.json()

        # If a match is found
        if 'place' in parsed_data and 'location' in parsed_data['place']:  
            
            # Extract and store restaurant id in session
            fsq_id = parsed_data['place']['fsq_id']
            session['fsq_id'] = fsq_id  
            
            # Extract the category information and store as a string
            categories = [f"{category['short_name']}:{category['id']}" for category in parsed_data['place']['categories']]
            categories_str = ",".join(categories) 
            
            # Extract the tastes information and store as a string
            tastes = parsed_data['place'].get('tastes')
            tastes_str = ",".join(tastes) if tastes else None
            
            # Extract other information
            menu = parsed_data['place'].get('menu')
            website = parsed_data['place'].get('website')
            description = parsed_data['place'].get('description')
            price = parsed_data['place'].get('price')
            address = parsed_data['place']['location']['formatted_address']

            # Check if restaurant features information is available
            if 'features' in parsed_data['place']:
                features_data = parsed_data['place']['features']
            else:
                features_data = None

            # Create a list of feature names based on the RestaurantFeature model columns
            feature_columns = [column.name for column in RestaurantFeature.__table__.columns]
            feature_values = {}
            ignore_sections = ['payment', 'services', 'amenities']

            # Function to flatten nested JSON structures
            def flatten_features(data, prefix=""):
                if data is None:
                    return {}

                flat_data = {}
                for key, value in data.items():
                    if key in ignore_sections:
                        continue
                    if isinstance(value, dict):
                        flat_data.update(flatten_features(value, f"{prefix}{key}_"))
                    else:
                        flat_data[key] = value
                return flat_data
            flattened_features = flatten_features(features_data)

            # Add feature values to dictionary
            for feature_name, feature_data in flattened_features.items():
                if feature_name in feature_columns:
                    feature_values[feature_name] = feature_data

            # Query the local database for the restaurant
            restaurant_exists = Restaurant.query.filter_by(id=fsq_id).first()
            
            # Add restaurant information to local database if not already there
            if not restaurant_exists:
                restaurant = Restaurant(
                    id=fsq_id,
                    full_name=restaurant_full_name,
                    name=restaurant_name, 
                    address=address, 
                    category=categories_str, 
                    website=website, 
                    menu=menu, 
                    price=price, 
                    description=description, 
                    tastes=tastes_str
                )
                if feature_values:
                    restaurant_features = RestaurantFeature(restaurant_id=restaurant.id, **feature_values)
                    db.session.add(restaurant_features)
                db.session.add(restaurant)
                db.session.commit()
            found = True
        # If a match is not found in the FourSquare database
        else:
            found = False
        
        if found:
            flash('Restaurant found!', 'success')
            # Re-render page with submit form
            return render_template('add_restaurant.html', search_form=search_form, submit_form=submit_form, submit_form_visible=True)
        else:
            flash('Restaurant not found.', 'danger')
            # Refresh page for user to start again
            return(redirect(url_for('add')))

    if submit_form.validate_on_submit():
        date = submit_form.date.data
        rating = submit_form.rating.data
        restaurant_visit = RestaurantVisit(user_id = current_user.id, restaurant_id = session['fsq_id'], date_visited = date, rating=rating)
        db.session.add(restaurant_visit)
        db.session.commit()
        flash('Added restaurant to my restaurants', 'success')
        return(redirect(url_for('my')))
    return render_template('add_restaurant.html', title='Add Restaurant', search_form=search_form, key=google, api=True)

# My restaurants page
@app.route("/my")
@login_required
def my():
    page = request.args.get('page', default=1, type=int)
    search_query = request.args.get('q', '').strip()
    
    # Database query to filter by user and search query
    base_query = RestaurantVisit.query.filter_by(user_id=current_user.id)
    if search_query:
        search_filter = or_(
            RestaurantVisit.restaurant.has(Restaurant.name.ilike(f"%{search_query}%")),
            RestaurantVisit.restaurant.has(Restaurant.address.ilike(f"%{search_query}%"))
        )
        restaurant_visits = base_query.filter(search_filter).order_by(RestaurantVisit.date_visited.desc()).paginate(page=page, per_page=10)
    else:
        restaurant_visits = base_query.order_by(RestaurantVisit.date_visited.desc()).paginate(page=page, per_page=10)
    return(render_template('my_restaurants.html', title='My Restaurants', restaurant_visits=restaurant_visits, search_query=search_query))

# Find restaurants page
@app.route("/update_coordinates", methods=['POST'])
def update_coordinates():
    lat = request.form.get('lat')
    lng = request.form.get('lng')
    coords = f"{lat},{lng}"
    session['coordinates'] = coords
    return jsonify({'status': 'success'})

@app.route("/find", methods=['GET', 'POST'])
@login_required
def find():
    has_visited = RestaurantVisit.query.filter_by(user_id=current_user.id).first() is not None
    if not has_visited:
        flash('Please add restaurants to your history before generating recommendations.', 'danger')
        return(redirect(url_for('my')))
    
    # Recommendation form
    form = RecommendationForm()
    coords = session.get('coordinates', None)
    if form.validate_on_submit():
        radius = form.radius.data
        recommended_ids = RecommendationGenerator.generate_recommendation(current_user.id, coords, radius)
        recommendations = [Restaurant.query.get(id) for id in recommended_ids]
        return(render_template('find_restaurants.html', title='Find Restaurants', key=google, form=form, api=True, recommendations=recommendations))
    # Render the find restaurants template without recommendations if the form has not been submitted
    return(render_template('find_restaurants.html', title='Find Restaurants', key=google, form=form, api=True))