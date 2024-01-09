import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

# App and database configuration
app = Flask(__name__)

# Set a secret key for securing session data
app.config['SECRET_KEY'] = '0321e05b9aff462378618d5d21b91117'

# Configure the database URI for SQLAlchemy (using SQLite in this case)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Initialize SQLAlchemy for database management
db = SQLAlchemy(app)

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Initialize LoginManager for managing user sessions
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Configure mail settings for sending password reset emails
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('DEV_EMAIL_USER')  # Use environment variables for security
app.config['MAIL_PASSWORD'] = os.environ.get('DEV_EMAIL_PASS')  # Use environment variables for security
mail = Mail(app)

# Import routes after initialization of the app to prevent circular import
from culinarycompass import routes
