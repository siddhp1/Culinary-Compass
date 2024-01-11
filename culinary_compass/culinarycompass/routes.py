import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, session
from sqlalchemy import or_
from culinarycompass import app, db, bcrypt, mail
from culinarycompass.forms import (RegistrationForm,
                                   LoginForm,
                                   UpdateAccountForm,
                                   RequestResetForm,
                                   ResetPasswordForm,
                                   SearchRestaurantForm,
                                   SubmitRestaurantForm,
                                   QuestionnaireForm,
                                   FindRestaurantForm)
from culinarycompass.models import User, Restaurant, RestaurantVisit, RestaurantFeature
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
    
# Home page
@app.route("/")
@app.route("/home")
def home():
    # Render the home template
    return(render_template('home.html', title='Home'))

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
    return(redirect(url_for('login')))

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
    
    profile_form = QuestionnaireForm()
    if profile_form.validate_on_submit():
        current_user.dietary_preference = profile_form.dietary_preference.data
        current_user.gluten = profile_form.gluten.data
        current_user.allergies = profile_form.allergies.data
        current_user.alcohol = profile_form.alcohol.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return(redirect(url_for('account')))
    elif request.method == 'GET':
        profile_form.dietary_preference.data = current_user.dietary_preference
        profile_form.gluten.data = current_user.gluten
        profile_form.allergies.data = current_user.allergies
        profile_form.alcohol.data = current_user.alcohol
        
    return(render_template('account.html', title='Account', image_file=image_file, form=form, profile_form=profile_form))

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

# Add restaurant page
import requests

@app.route("/add", methods=['GET', 'POST'])
@login_required
def add():
    # Initialize forms
    search_form = SearchRestaurantForm()
    submit_form = SubmitRestaurantForm()

    # If input to the search form is valid
    if search_form.validate_on_submit():
        restaurant_full_name = search_form.name.data
        restaurant_coords = request.form['place_latlng']
        
        # Set 'rest_id' as a session variable used for the restaurant id
        session['rest_id'] = restaurant_full_name
        
        # If a restaurant is found
        found = False
        
        # Check if restaurant searched is found in the database
        restaurant_exists = Restaurant.query.filter_by(id=restaurant_full_name).first()
        
        # If restaurant is not found in database, fetch from Foursquare Places API
        if not restaurant_exists:
            # Get name of restaurant from google autocomplete
            parts = restaurant_full_name.split(', ', 1)
            restaurant_name = parts[0]
            
            # API request URL
            url = f"https://api.foursquare.com/v3/places/match?name={restaurant_name}&ll={restaurant_coords}&fields=categories%2Cmenu%2Cwebsite%2Cprice%2Ctastes%2Cfeatures%2Clocation%2Cdescription"
            
            # API settings and key
            # MAKE AN APP/ENVIRONMENT VARIABLE
            headers = {
                "accept": "application/json",
                "Authorization": "fsq3891kysJBh536fngR4yL2X7D8lqkaNSF8vzQTtQNZqs0="
            }
            
            # Make the API request
            response = requests.get(url, headers=headers)

            # Parse the JSON data
            parsed_data = response.json()
            
            print(f"{response.text}this")

            # Check if a match is found
            if 'place' in parsed_data and 'location' in parsed_data['place']:                
                # Match found, extract information to add to database
                 
                categories = [f"{category['short_name']}:{category['id']}" for category in parsed_data['place']['categories']]
                categories_str = ",".join(categories)

                if 'menu' in parsed_data['place']:
                    menu = parsed_data['place']['menu']
                else:
                    menu = None

                if 'website' in parsed_data['place']:
                    website = parsed_data['place']['website']
                else:
                    website = None
                    
                if 'tastes' in parsed_data['place']:
                    tastes = parsed_data['place']['tastes']
                    tastes_str = ",".join(tastes)
                else:
                    tastes_str = None

                price = parsed_data['place']['price']
                address = parsed_data['place']['location']['formatted_address']
                description = parsed_data['place']['description']

                # Add the information to the database
                restaurant = Restaurant(
                    id=restaurant_full_name,
                    name=restaurant_name, 
                    address=address, 
                    category=categories_str, 
                    website=website, 
                    menu=menu, 
                    price=price, 
                    description=description, 
                    tastes=tastes_str
                )
                
                features_data = parsed_data['place']['features']

                # Create a list of feature names based on the RestaurantFeature model columns
                feature_columns = [column.name for column in RestaurantFeature.__table__.columns]
                
                # Initialize the dictionary to store feature values
                feature_values = {}

                # Sections to ignore
                ignore_sections = ['payment', 'services', 'amenities']

                # Flatten nested structures in features_data
                def flatten_features(data, prefix=""):
                    flat_data = {}
                    for key, value in data.items():
                        if key in ignore_sections:
                            continue  # Skip sections to be ignored
                        if isinstance(value, dict):
                            flat_data.update(flatten_features(value, f"{prefix}{key}_"))
                        else:
                            flat_data[key] = value  # Use only the last part of the prefix as the feature name
                    return flat_data

                flattened_features = flatten_features(features_data)

                # Iterate through features and check if the corresponding column exists
                for feature_name, feature_data in flattened_features.items():
                    if feature_name in feature_columns:
                        # If the feature column exists, set its value in the feature_values dictionary
                        feature_values[feature_name] = feature_data

                # Add features to the database
                restaurant_features = RestaurantFeature(restaurant_id=restaurant.id, **feature_values)
                
                # Add features to the database
                db.session.add(restaurant)
                db.session.add(restaurant_features)
                db.session.commit()

                # Set found to true
                found = True
            else:
                # Restaurant not found in Foursquare database
                flash('Restaurant information could not be found!', 'danger')
                found = False
        else:
            # If restaurant is found in the culinary compass database
            found = True
        
        # Flash status messages to screen
        if found:
            flash('Restaurant found!', 'success')
            # Re-render page with submit form
            return render_template('add_restaurant.html', search_form=search_form, submit_form=submit_form, submit_form_visible=True)
        else:
            flash('Restaurant not found.', 'danger')
            # Refresh page for user to start again
            return(redirect(url_for('add')))

    # If input to submit form is valid
    if submit_form.validate_on_submit():
        date = submit_form.date.data
        rating = submit_form.rating.data
        
        # Add the information to the database
        restaurant_visit = RestaurantVisit(user_id = current_user.id, restaurant_id = session['rest_id'], date_visited = date, rating=rating)
        db.session.add(restaurant_visit)
        db.session.commit()
        
        # Flash status message
        flash('Added restaurant to my restaurants', 'success')
        
        # Redirect user to my restaurants page
        return(redirect(url_for('my')))

    return render_template('add_restaurant.html', title='Add Restaurant', search_form=search_form, key='AIzaSyC9tZs8iF_dWZKbJtwFF3uBrle944RYtHc', api=True)

# My restaurants page
@app.route("/my")
@login_required
def my():
    # Get the current page
    page = request.args.get('page', default=1, type=int)
    # Get search query from the user
    search_query = request.args.get('q', '').strip()
    
    # Build the database query to filter by user and search query
    base_query = RestaurantVisit.query.filter_by(user_id=current_user.id)
    if search_query:
        search_filter = or_(
            # Currently searching for keywords in name and address
            # WILL EXPAND TO KEYWORDS LIKE GLUTEN FREE AND CUSINES
            RestaurantVisit.restaurant.has(Restaurant.name.ilike(f"%{search_query}%")),
            RestaurantVisit.restaurant.has(Restaurant.address.ilike(f"%{search_query}%"))
        )
        restaurant_visits = base_query.filter(search_filter).order_by(RestaurantVisit.date_visited.desc()).paginate(page=page, per_page=3)
        
    else:
        restaurant_visits = base_query.order_by(RestaurantVisit.date_visited.desc()).paginate(page=page, per_page=3)

    return(render_template('my_restaurants.html', title='My Restaurants', restaurant_visits=restaurant_visits, search_query=search_query))

# Find restaurants page
@app.route("/find")
@login_required
def find():
    submit_form = FindRestaurantForm()
    
    if submit_form.validate_on_submit():
        coordinates = request.form.get('coordinates')
        # Do something with the coordinates (e.g., store in a database)
        print(f'Received coordinates: {coordinates}')

    return(render_template('find_restaurants.html', title='Find Restaurants', form = submit_form, key='AIzaSyC9tZs8iF_dWZKbJtwFF3uBrle944RYtHc', api=True))