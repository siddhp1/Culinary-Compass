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
    category = db.Column(db.Text, nullable=False) # Restaurant category
    website = db.Column(db.String(200), nullable=True)  # Restaurant website
    menu = db.Column(db.String(200), nullable=True)  # Restaurant menu
    price = db.Column(db.Integer) # Restaurant price category
    description = db.Column(db.Text)  # Restaurant description
    tastes = db.Column(db.Text, nullable=True)  # List of tastes associated with the restaurant
    restaurant_visits = db.relationship('RestaurantVisit', backref='restaurant', lazy=True)  # Restaurant's visits
    features = db.relationship('RestaurantFeature', backref='restaurant', lazy=True)  # Relationship with Feature table

    def __repr__(self):
        # String representation of the Restaurant object
        return f"Restaurant('{self.name}', '{self.address}')"

class RestaurantFeature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.String(200), db.ForeignKey('restaurant.id'), nullable=False)
    
    # Food and drink features
    bar_service = db.Column(db.Boolean, default=False)
    beer = db.Column(db.Boolean, default=False)
    byo = db.Column(db.Boolean, default=False)
    cocktails = db.Column(db.Boolean, default=False)
    full_bar = db.Column(db.Boolean, default=False)
    wine = db.Column(db.Boolean, default=False)

    # Meals features
    bar_snacks = db.Column(db.Boolean, default=False)
    breakfast = db.Column(db.Boolean, default=False)
    brunch = db.Column(db.Boolean, default=False)
    lunch = db.Column(db.Boolean, default=False)
    happy_hour = db.Column(db.Boolean, default=False)
    dessert = db.Column(db.Boolean, default=False)
    dinner = db.Column(db.Boolean, default=False)
    tasting_menu = db.Column(db.Boolean, default=False)

    # Other attributes
    business_meeting = db.Column(db.String(200))
    clean = db.Column(db.String(200))
    crowded = db.Column(db.String(200))
    dates_popular = db.Column(db.String(200))
    dressy = db.Column(db.String(200))
    families_popular = db.Column(db.String(200))
    gluten_free_diet = db.Column(db.String(200))
    good_for_dogs = db.Column(db.String(200))
    groups_popular = db.Column(db.String(200))
    healthy_diet = db.Column(db.String(200))
    late_night = db.Column(db.String(200))
    noisy = db.Column(db.String(200))
    quick_bite = db.Column(db.String(200))
    romantic = db.Column(db.String(200))
    service_quality = db.Column(db.String(200))
    singles_popular = db.Column(db.String(200))
    special_occasion = db.Column(db.String(200))
    trendy = db.Column(db.String(200))
    value_for_money = db.Column(db.String(200))
    vegan_diet = db.Column(db.String(200))
    vegetarian_diet = db.Column(db.String(200))

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