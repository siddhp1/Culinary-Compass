from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from culinarycompass import db, login_manager, app
from flask_login import UserMixin

# Load user callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Models
class User(db.Model, UserMixin):
    # User model representing user data
    id = db.Column(db.Integer, primary_key=True)  # User ID, primary key
    username = db.Column(db.String(20), unique=True, nullable=False)  # User's username
    email = db.Column(db.String(120), unique=True, nullable=False)  # User's email
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')  # Profile image file
    password = db.Column(db.String(60), nullable=False)  # User's hashed password
    dietary_preference = db.Column(db.String(20), default='neither')  # User's dietary preference
    gluten = db.Column(db.Boolean, default=False)  # User's gluten preference
    allergies = db.Column(db.Boolean, default=False)  # User's allergies preference
    alcohol = db.Column(db.Boolean, default=False)  # User's alcohol preference
    restaurant_visits = db.relationship('RestaurantVisit', backref='user', lazy=True)  # User's restaurant visits

    def get_reset_token(self):
        # Generates a reset token for password reset
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        # Verifies the reset token and returns the associated user
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        # String representation of the User object
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Restaurant(db.Model):
    # Restaurant model representing restaurant data
    id = db.Column(db.String(200), primary_key=True)  # Restaurant ID, primary key
    name = db.Column(db.String(100), nullable=False)  # Restaurant name
    address = db.Column(db.String(100), nullable=False)  # Restaurant address
    keywords = db.Column(db.Text, nullable=False, default='Test')  # Keywords associated with the restaurant
    restaurant_visits = db.relationship('RestaurantVisit', backref='restaurant', lazy=True)  # Restaurant's visits
    # Add other rich information after

    def __repr__(self):
        # String representation of the Restaurant object
        return f"Restaurant('{self.name}', '{self.address}')"

class RestaurantVisit(db.Model):
    # RestaurantVisit model representing user visits to restaurants
    id = db.Column(db.Integer, primary_key=True)  # Visit ID, primary key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User ID associated with the visit
    restaurant_id = db.Column(db.String(200), db.ForeignKey('restaurant.id'), nullable=False)  # Restaurant ID associated with the visit
    date_visited = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Date and time of the visit
    rating = db.Column(db.Integer, nullable=False)  # Rating given by the user for the restaurant visit

    def __repr__(self):
        # String representation of the RestaurantVisit object
        return f"Restaurant Visit('{self.user_id}', '{self.date_visited}', '{self.rating}')"