from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# App and database configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = '0321e05b9aff462378618d5d21b91117'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Importing after initialization of app to prevent circular import
from culinarycompass import routes
