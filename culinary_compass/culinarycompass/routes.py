# Import secrets for random hex generation (for storing profile images)
import secrets
# Import os for file deletion
import os
# Import requests for API requests
import requests
# Import PIL for image resizing
from PIL import Image
# Import jsonify, render_template, url_for, flash, redirect, request, and session from Flask for routing
from flask import jsonify, render_template, url_for, flash, redirect, request, session
# Import login_required, login_user, current_user, logout_user from flask_login for user authentication
from flask_login import login_user, current_user, logout_user, login_required
# Import Message from flask_mail for sending emails
from flask_mail import Message
# Import or_ from SQLAlchemy for filtering queries
from sqlalchemy import or_
# Import the app, db, bcrypt, and mail from the __init__.py file
from culinarycompass import app, db, bcrypt, mail, google, foursquare
# Import the forms from the forms.py file
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
# Import the models from the models.py file
from culinarycompass.models import User, Restaurant, RestaurantVisit, RestaurantFeature
# Import the ReportGenerator class from the generate_report.py file
from .generate_report import ReportGenerator
# Import the RecommendationGenerator class from the generate_recommendation.py file
from .generate_recommendation import RecommendationGenerator

# Home page
@app.route("/") # Root URL directs to the home page
@app.route("/home") # Home URL directs to the home page
def home():
    # Render the home template
    return(render_template('home.html', title='Home'))

# Register page
# Register URL directs to the register page
@app.route("/register", methods=['GET', 'POST']) # GET and POST requests allowed for form submission
def register():
    # If the user is already logged in, redirect to the home page
    if current_user.is_authenticated:
        # Redirect to the home page
        return(redirect(url_for('home')))
    # Initialize the registration form
    form = RegistrationForm()
    # If the form is valid
    if form.validate_on_submit():
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # Create a new user object in the database
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        # Add the user to the database
        db.session.add(user)
        # Commit the changes to the database
        db.session.commit()
        # Flash a success message
        flash('Your account has been created. You are now able to log in!.', 'success')
        # Redirect to the login page
        return(redirect(url_for('login')))
    # Render the registration template
    return(render_template('register.html', title='Register', form=form))

# Login page
# Login URL directs to the login page
@app.route("/login", methods=['GET', 'POST']) # GET and POST requests allowed for form submission
def login():
    # If the user is already logged in, redirect to the home page
    if current_user.is_authenticated:
        # Redirect to the home page
        return(redirect(url_for('home')))
    # Initialize the login form
    form = LoginForm()
    # If the form is valid
    if form.validate_on_submit():
        # Query the database for the user
        user = User.query.filter_by(email=form.email.data).first()
        # If the user exists and the password is correct
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Log the user in
            login_user(user, remember=form.remember.data)
            # Get the next page from the request (if the user was prompted to login from a loginrequired page)
            next_page = request.args.get('next')
            # Redirect to the next page if it exists, otherwise redirect to the home page
            return(redirect(next_page) if next_page else redirect(url_for('home')))
        # If the user does not exist or the password is incorrect
        else:
            # Flash an error message
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    # Render the login template
    return(render_template('login.html', title='Login', form=form))

# Logout page
@app.route("/logout") # Logout URL directs to the logout page
def logout():
    # Log the user out
    logout_user()
    # Redirect to the login page
    return(redirect(url_for('login')))

# Account page
# Function to save the profile picture
def save_picture(form_picture):
    # Generate a random hex for the image name
    random_hex = secrets.token_hex(8)
    # Get the file extension
    _, f_ext = os.path.splitext(form_picture.filename)
    # Create the image name
    picture_fn = random_hex + f_ext
    # Create the image path
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    # Image output size
    output_size = (125, 125)
    # Open the image
    i = Image.open(form_picture)
    # Resize the image
    i.thumbnail(output_size)
    # Save the image
    i.save(picture_path)
    
    # Return the image name
    return(picture_fn)

# Function to send the report email
def send_report_email(pdf_path):
    # Create the message with the sender, recipient, and subject
    msg = Message('Your Culinary Mapped',
                  sender='siddhdevelopment@gmail.com',
                  recipients=[current_user.email])
    # Set the body of the message
    msg.body = f'''Here is your Culinary Mapped:'''
    
    # Extract the pdf file name from the attachment path
    filename = os.path.basename(pdf_path)
    # Open the pdf file as an attachment
    with app.open_resource(pdf_path) as attachment:
        # Add the attachment to the message
        msg.attach(filename, 'application/pdf', attachment.read())

    # Send the email
    mail.send(msg)

# Function to delete the report
def delete_report(pdf_path):
    # If the file exists
    try:
        # Delete the file
        os.remove(pdf_path)
    # If the file does not exist
    except OSError as e:
        # Print an error message
        print(f"Error deleting file: {pdf_path} - {e}")

# Account URL directs to the account page
@app.route("/account", methods=['GET', 'POST']) # GET and POST requests allowed for form submission
@login_required # Login required to access the account page
def account():
    # Initialize the update account form
    update_account_form = UpdateAccountForm()
    # If the form is valid
    if update_account_form.validate_on_submit():
        # Update the user's username
        current_user.username = update_account_form.username.data
        # Update the user's email
        current_user.email = update_account_form.email.data
        # If the user uploaded a profile picture
        if update_account_form.picture.data:
            # Save the profile picture
            picture_file = save_picture(update_account_form.picture.data)
            # Update the user's profile picture
            current_user.image_file = picture_file
        # Commit the changes to the database
        db.session.commit()
        # Flash a success message
        flash('Your account has been updated!', 'success')
        # Refresh the account page
        return(redirect(url_for('account')))
    # If the request method is GET (when loading the page)
    elif request.method == 'GET':
        # Set the username field to the current user's username
        update_account_form.username.data = current_user.username
        # Set the email field to the current user's email
        update_account_form.email.data = current_user.email
    # Get the profile picture file name
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    
    # Initialize the questionnaire form
    questionnaire_form = QuestionnaireForm()
    # If the form is valid
    if questionnaire_form.validate_on_submit():
        # Update the user's dietary preference
        current_user.vegetarianism = questionnaire_form.vegetarianism.data
        # Update the user's gluten preference
        current_user.gluten = questionnaire_form.gluten.data
        # Update the user's allergies
        current_user.healthy = questionnaire_form.healthy.data
        # Update the user's alcohol preference
        current_user.no_alcohol = questionnaire_form.no_alcohol.data
        # Commit the changes to the database
        db.session.commit()
        # Flash a success message
        flash('Your account has been updated!', 'success')
        # Refresh the account page
        return(redirect(url_for('account')))
    # If the request method is GET (when loading the page)
    elif request.method == 'GET':
        # Set the dietary preference field to the current user's dietary preference
        questionnaire_form.vegetarianism.data = current_user.vegetarianism
        # Set the gluten field to the current user's gluten preference
        questionnaire_form.gluten.data = current_user.gluten
        # Set the allergies field to the current user's allergies
        questionnaire_form.healthy.data = current_user.healthy
        # Set the alcohol field to the current user's alcohol preference
        questionnaire_form.no_alcohol.data = current_user.no_alcohol
    
    # Initialize the report form
    report_form = ReportForm()
    # If the form is valid
    if report_form.validate_on_submit():
        # Set the pdf name to the current user's username
        pdf_name = current_user.username
        # Set the pdf path to the static/reports folder
        pdf_path = os.path.join(app.root_path, 'static/reports', pdf_name + ".pdf")
        # Create the pdf report
        ReportGenerator.create_pdf(pdf_path, current_user.username)
        # Send the report email
        send_report_email(pdf_path)
        # Delete the report
        delete_report(pdf_path)
        # Flash a success message
        flash('A report has been sent to your email', 'success')
        # Refresh the account page
        return(redirect(url_for('account')))
    # Render the account template
    return(render_template('account.html',
                           title='Account',
                           image_file=image_file,
                           update_account_form=update_account_form,
                           questionnaire_form=questionnaire_form,
                           report_form=report_form))

# Reset password pages
# Function to send the reset password email
def send_reset_email(user):
    # Generate a token for the user
    token = user.get_reset_token()
    # Create the message with the sender, recipient, and subject
    msg = Message('Password Reset Request',
                  sender='siddhdevelopment@gmail.com',
                  recipients=[user.email])
    # Set the body of the message with a tokened URL to reset the password
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, ignore this email.'''
    # Send the email
    mail.send(msg)

# Reset password URL directs to the reset password page
@app.route("/reset_password", methods=['GET', 'POST']) # GET and POST requests allowed for form submission
def reset_request():
    # If the user is already logged in, redirect to the home page
    if current_user.is_authenticated:
        # Redirect to the home page
        return(redirect(url_for('home')))
    # Initialize the request reset form
    form = RequestResetForm()
    # If the form is valid
    if form.validate_on_submit():
        # Query the database for the user
        user = User.query.filter_by(email=form.email.data).first()
        # Send the reset password email
        send_reset_email(user)
        # Flash a information message
        flash('An email has been sent with instructions to reset your password.', 'info')
        # Redirect to the login page
        return(redirect(url_for('login')))
    # Render the reset request template
    return(render_template('reset_request.html', title='Reset Password', form=form))

# Reset password token URL directs to the reset password token page
@app.route("/reset_password/<token>", methods=['GET', 'POST']) # GET and POST requests allowed for form submission
def reset_token(token):
    # If the user is already logged in, redirect to the home page
    if current_user.is_authenticated:
        # Redirect to the home page
        return(redirect(url_for('home')))
    # Verify the token
    user = User.verify_reset_token(token)
    # If the token is invalid or expired
    if user is None:
        # Flash a warning message
        flash('Invalid or expired token.', 'warning')
        # Redirect to the reset request page
        return(redirect(url_for('reset_request')))
    # Otherwise, nitialize the reset password form
    form = ResetPasswordForm()
    # If the form is valid
    if form.validate_on_submit():
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # Update the user's password
        user.password = hashed_password
        # Commit the changes to the database
        db.session.commit()
        # Flash a success message
        flash('Your password has been updated. You are now able to log in.', 'success')
        # Redirect to the login page
        return(redirect(url_for('login')))
    # Render the reset token template
    return(render_template('reset_token.html', title='Reset Password', form=form))

# Add restaurant page
# Add URL directs to the add restaurant page
@app.route("/add", methods=['GET', 'POST']) # GET and POST requests allowed for form submission
@login_required # Login required to access the add restaurant page
def add():
    # Initialize the search form
    search_form = SearchRestaurantForm()
    # Initialize the submit form
    submit_form = SubmitRestaurantForm()

    # If input to search form is valid
    if search_form.validate_on_submit():
        # Get the full restaurant name from the form (Google Places API includes address)
        restaurant_full_name = search_form.name.data
        # Get the coordinates of the restaurant from the form
        restaurant_coords = request.form['place_latlng']
        
        # Variable to store if restaurant is found in FourSquare database
        found = False
        
        # Check if restaurant searched is already in the database
        restaurant_exists = Restaurant.query.filter_by(full_name=restaurant_full_name).first()
        # If restaurant is not found in database, fetch from Foursquare Places API
        if not restaurant_exists:
            # Get name of restaurant from google autocomplete
            parts = restaurant_full_name.split(', ', 1)
            restaurant_name = parts[0] # Get the name of the restaurant
            
            # FourSquare API request URL with restaurant name and coordinates
            url = f"https://api.foursquare.com/v3/places/match?name={restaurant_name}&ll={restaurant_coords}&fields=fsq_id%2Ccategories%2Cmenu%2Cwebsite%2Cprice%2Ctastes%2Cfeatures%2Clocation%2Cdescription"
            
            # API settings and key
            # MAKE AN APP/ENVIRONMENT VARIABLE
            headers = {
                "accept": "application/json",
                "Authorization": foursquare
            }
            
            # Make the API request and store the response
            response = requests.get(url, headers=headers)
            # Parse the JSON data
            parsed_data = response.json()
            
            print(response.text)

            # Check if a match is found
            if 'place' in parsed_data and 'location' in parsed_data['place']:  
                
                # Extract the restaurant id from the response in a session variable
                fsq_id = parsed_data['place']['fsq_id']
                # Store the restaurant id in the session
                session['fsq_id'] = fsq_id  
                
                # Extract the category information
                categories = [f"{category['short_name']}:{category['id']}" for category in parsed_data['place']['categories']]
                # Store the categories as a comma-separated string
                categories_str = ",".join(categories) 
                
                # Extract the menu information
                menu = parsed_data['place'].get('menu')
                # Extract the website information
                website = parsed_data['place'].get('website')

                # Check if restaurant tastes information is available
                tastes = parsed_data['place'].get('tastes')
                # If tastes is not None, store the tastes as a comma-separated string
                tastes_str = ",".join(tastes) if tastes else None

                # Extract the description information
                description = parsed_data['place'].get('description')
                # Extract the price information
                price = parsed_data['place'].get('price')
                # Get the address from the response
                address = parsed_data['place']['location']['formatted_address']

                # Add the information to the database
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
                
                # Check if restaurant price information is available
                if 'features' in parsed_data['place']:
                    # Get the price from the response
                    features_data = parsed_data['place']['features']
                else:
                    # Otherwise, set the features to None
                    features_data = None

                # Create a list of feature names based on the RestaurantFeature model columns
                feature_columns = [column.name for column in RestaurantFeature.__table__.columns]
                # Initialize the dictionary to store feature values
                feature_values = {}
                # Sections to ignore
                ignore_sections = ['payment', 'services', 'amenities']

                # Flatten nested structures in features_data
                def flatten_features(data, prefix=""):
                    # If data is None, return an empty dictionary
                    if data is None:
                        return {}

                    # Initialize the dictionary to store flattened features
                    flat_data = {}
                    # Iterate through the features
                    for key, value in data.items():
                        # Check if the key is in the ignore_sections list
                        if key in ignore_sections:
                            continue  # Skip sections to be ignored
                        # Check if the value is a dictionary
                        if isinstance(value, dict):
                            # If the value is a dictionary, flatten the dictionary and add the flattened features to the flat_data dictionary
                            flat_data.update(flatten_features(value, f"{prefix}{key}_"))
                        # Check if the value is a list
                        else:
                            # If the value is a list, add the value to the flat_data dictionary
                            flat_data[key] = value # Use only the last part of the prefix as the feature name
                    # Return the flattened features
                    return flat_data

                # Flatten the features
                flattened_features = flatten_features(features_data)

                # Iterate through features and check if the corresponding column exists
                for feature_name, feature_data in flattened_features.items():
                    # Check if the feature name is in the feature columns
                    if feature_name in feature_columns:
                        # If the feature column exists, set its value in the feature_values dictionary
                        feature_values[feature_name] = feature_data

                # Only create a RestaurantFeature object if feature_values is not empty
                if feature_values:
                    # Create a new RestaurantFeature object with the feature values
                    restaurant_features = RestaurantFeature(restaurant_id=restaurant.id, **feature_values)
                    # Add the restaurant features to the database
                    db.session.add(restaurant_features)

                # Add the restaurant to the database 
                db.session.add(restaurant)
                # Commit the changes to the database
                db.session.commit()

                # Set found to true
                found = True
            # If a match is not found in the FourSquare database
            else:
                # Redirect to the add restaurant page
                found = False
        else:
            # If restaurant is found in the culinary compass database
            found = True
        
        # If restaurant is found in the database
        if found:
            # Flash a success message
            flash('Restaurant found!', 'success')
            # Re-render page with submit form
            return render_template('add_restaurant.html', search_form=search_form, submit_form=submit_form, submit_form_visible=True)
        # If restaurant is not found in the database
        else:
            # Flash an error message
            flash('Restaurant not found.', 'danger')
            # Refresh page for user to start again
            return(redirect(url_for('add')))

    # If input to submit form is valid
    if submit_form.validate_on_submit():
        # Get the date from the form
        date = submit_form.date.data
        # Get the rating from the form
        rating = submit_form.rating.data
        
        # Create a new restaurant visit object in the database
        restaurant_visit = RestaurantVisit(user_id = current_user.id, restaurant_id = session['fsq_id'], date_visited = date, rating=rating)
        # Add the restaurant visit to the database
        db.session.add(restaurant_visit)
        # Commit the changes to the database
        db.session.commit()
        
        # Flash a success message
        flash('Added restaurant to my restaurants', 'success')
        # Redirect user to my restaurants page
        return(redirect(url_for('my')))
    # Render the add restaurant template
    return render_template('add_restaurant.html', title='Add Restaurant', search_form=search_form, key=google, api=True)

# My restaurants page
# My URL directs to the my restaurants page
@app.route("/my")
@login_required # Login required to access the my restaurants page
def my():
    # Get the current page
    page = request.args.get('page', default=1, type=int)
    # Get search query from the user
    search_query = request.args.get('q', '').strip()
    
    # Build the database query to filter by user and search query
    base_query = RestaurantVisit.query.filter_by(user_id=current_user.id)
    # If the user entered a search query
    if search_query:
        # Filter the query by the search query
        search_filter = or_(
            # Search by restaurant name
            RestaurantVisit.restaurant.has(Restaurant.name.ilike(f"%{search_query}%")),
            # Search by restaurant address
            RestaurantVisit.restaurant.has(Restaurant.address.ilike(f"%{search_query}%"))
        )
        # Filter the query by the search query in addition to the user
        # Order the query by date visited in descending order and paginate the query
        restaurant_visits = base_query.filter(search_filter).order_by(RestaurantVisit.date_visited.desc()).paginate(page=page, per_page=5)
    # If the user did not enter a search query
    else:
        # Filter the query by the user
        # Order the query by date visited in descending order and paginate the query
        restaurant_visits = base_query.order_by(RestaurantVisit.date_visited.desc()).paginate(page=page, per_page=5)
    # Render the my restaurants template
    return(render_template('my_restaurants.html', title='My Restaurants', restaurant_visits=restaurant_visits, search_query=search_query))

# Find restaurants page
# Update coordinates URL directs to the find restaurants page
@app.route("/update_coordinates", methods=['POST']) # POST requests allowed for form submission
def update_coordinates():
    # Get the latitude from the form
    lat = request.form.get('lat')
    # Get the longitude from the form
    lng = request.form.get('lng')
    # Store the as a comma-separated string
    coords = f"{lat},{lng}"
    # Store the coordinates in the session
    session['coordinates'] = coords
    # Return a success message
    return jsonify({'status': 'success'})

# Find URL directs to the find restaurants page
@app.route("/find", methods=['GET', 'POST']) # GET and POST requests allowed for form submission
@login_required # Login required to access the find restaurants page
def find():
    # Check if user has visited any restaurants
    has_visited = RestaurantVisit.query.filter_by(user_id=current_user.id).first() is not None
    # If user has not visited any restaurants
    if not has_visited:
        # Flash a warning message
        flash('Please add restaurants to your history before generating recommendations.', 'danger')
        return(redirect(url_for('my')))
    
    # Initialize the recommendation form
    form = RecommendationForm()
    # Get the coordinates from the session
    coords = session.get('coordinates', None)
    
    # If the form is valid
    if form.validate_on_submit():
        # Generate the recommendations
        recommended_ids = RecommendationGenerator.generate_recommendation(current_user.id, coords)
        # Get the recommended restaurants from the database        
        recommendations = [Restaurant.query.get(id) for id in recommended_ids]
        # Render the find restaurants template with the recommendations
        return(render_template('find_restaurants.html', title='Find Restaurants', key=google, form=form, api=True, recommendations=recommendations))
    # Render the find restaurants template without recommendations if the form has not been submitted
    return(render_template('find_restaurants.html', title='Find Restaurants', key=google, form=form, api=True))