import os
import json

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)

# Load the config file

# For development
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, 'config.json')

with open(config_path) as config_file:
    config = json.load(config_file)

# For production
# with open('/etc/config.json') as config_file:
#     config = json.load(config_file)

# Set app variables
app.config['SECRET_KEY'] = config.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = config.get('SQLALCHEMY_DATABASE_URI')

# Initialize db and bcrypt
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Mail settings (google mail)
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = config.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = config.get('EMAIL_PASS')
mail = Mail(app)

# API Keys
google = config.get('GOOGLE')
foursquare = config.get('FOURSQUARE')