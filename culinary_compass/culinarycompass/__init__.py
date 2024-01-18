# Import os module for environment variables
import os
# Import flask for web app framework
from flask import Flask
# Import SQLAlchemy for database management
from flask_sqlalchemy import SQLAlchemy
# Import Bcrypt for password hashing
from flask_bcrypt import Bcrypt
# Import LoginManager for managing user sessions
from flask_login import LoginManager
# Import Mail for sending password reset emails
from flask_mail import Mail

# App and database configuration
app = Flask(__name__)

# Set a secret key for securing session data
app.config['SECRET_KEY'] = '0321e05b9aff462378618d5d21b91117'

# Configure the SQLite3 database URI for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Initialize SQLAlchemy for database management
db = SQLAlchemy(app)

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Initialize LoginManager for managing user sessions
login_manager = LoginManager(app)
# Set the login route for redirecting unauthorized users
login_manager.login_view = 'login'
# Set the login message for unauthorized users
login_manager.login_message_category = 'info'

# Set mail server to googlemail
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
# Set mail server port to googlemail port
app.config['MAIL_PORT'] = 587
# Set mail server to use Transport Layer Security, a security protocol that encrypts email for privacy
app.config['MAIL_USE_TLS'] = True
# Get email from environment variable
app.config['MAIL_USERNAME'] = os.environ.get('DEV_EMAIL_USER')
# Get password from environment variable
app.config['MAIL_PASSWORD'] = os.environ.get('DEV_EMAIL_PASS')
# Initialize Mail for sending password reset emails
mail = Mail(app)

# API Keys
# Google Maps API key
google = ''
# Foursquare API key
foursquare = ''