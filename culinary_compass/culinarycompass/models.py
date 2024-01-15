# Import datetime for storing visit dates
from datetime import datetime
# Import itsdangerous for generating password reset tokens
from itsdangerous import URLSafeTimedSerializer as Serializer
# Import db, login_manager, and app from the __init__.py file
from culinarycompass import db, login_manager, app
# Import UserMixin for Flask-Login
from flask_login import UserMixin

# Load user callback for Flask-Login
@login_manager.user_loader
# Load user by ID
def load_user(user_id):
    # Returns the user with the given ID
    return User.query.get(int(user_id))

# Define the User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # User ID, primary key
    username = db.Column(db.String(20), unique=True, nullable=False)  # User's username
    email = db.Column(db.String(120), unique=True, nullable=False)  # User's email
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')  # Profile image file
    password = db.Column(db.String(60), nullable=False)  # User's hashed password
    dietary_preference = db.Column(db.String(20), default='neither')  # User's dietary preference
    gluten = db.Column(db.Boolean, default=False)  # User's gluten preference
    allergies = db.Column(db.Boolean, default=False)  # User's allergies preference
    alcohol = db.Column(db.Boolean, default=False)  # User's alcohol preference
    restaurant_visits = db.relationship('RestaurantVisit', backref='user', lazy=True) # User's visits to restaurants (relationship)

    # Generate a password reset token
    def get_reset_token(self):
        # Generates a password reset token for the user
        s = Serializer(app.config['SECRET_KEY'])
        # Returns the token
        return s.dumps({'user_id': self.id})

    # Static method to verify a password reset token
    @staticmethod
    # Parameters: token, time until expiration (seconds)
    def verify_reset_token(token, expires_sec=1800):
        # Verifies the reset token and returns the associated user
        s = Serializer(app.config['SECRET_KEY'])
        try:
            # Returns the user ID associated with the token
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except:
            # Returns None if the token is invalid or expired
            return None
        # Returns the user with the given ID
        return User.query.get(user_id)

    # String representation of the User object
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

# Define the Restaurant model
class Restaurant(db.Model):
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

    # String representation of the Restaurant object
    def __repr__(self):
        return f"Restaurant('{self.name}', '{self.address}')"

# Define the RestaurantFeature model
class RestaurantFeature(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Feature ID, primary key
    restaurant_id = db.Column(db.String(200), db.ForeignKey('restaurant.id'), nullable=False) # Restaurant ID associated with the features
    
    # Food and drink features
    bar_service = db.Column(db.Boolean, default=False) # If the restaurant has a bar
    beer = db.Column(db.Boolean, default=False) # If the restaurant serves beer
    byo = db.Column(db.Boolean, default=False) # If the restaurant allows BYO
    cocktails = db.Column(db.Boolean, default=False) # If the restaurant serves cocktails
    full_bar = db.Column(db.Boolean, default=False) # If the restaurant has a full bar
    wine = db.Column(db.Boolean, default=False) # If the restaurant serves wine

    # Meals features
    bar_snacks = db.Column(db.Boolean, default=False) # If the restaurant serves bar snacks
    breakfast = db.Column(db.Boolean, default=False) # If the restaurant serves breakfast
    brunch = db.Column(db.Boolean, default=False) # If the restaurant serves brunch
    lunch = db.Column(db.Boolean, default=False) # If the restaurant serves lunch
    happy_hour = db.Column(db.Boolean, default=False) # If the restaurant has happy hour
    dessert = db.Column(db.Boolean, default=False) # If the restaurant serves dessert
    dinner = db.Column(db.Boolean, default=False) # If the restaurant serves dinner
    tasting_menu = db.Column(db.Boolean, default=False) # If the restaurant has a tasting menu

    # Other attributes
    business_meeting = db.Column(db.String(200)) # If the restaurant is good for business meetings
    clean = db.Column(db.String(200)) # If the restaurant is clean
    crowded = db.Column(db.String(200)) # If the restaurant is crowded
    dates_popular = db.Column(db.String(200)) # If the restaurant is good for dates
    dressy = db.Column(db.String(200)) # If the restaurant is dressy
    families_popular = db.Column(db.String(200)) # If the restaurant is good for families
    gluten_free_diet = db.Column(db.String(200)) # If the restaurant has gluten-free options
    good_for_dogs = db.Column(db.String(200)) # If the restaurant is good for dogs
    groups_popular = db.Column(db.String(200)) # If the restaurant is good for groups
    healthy_diet = db.Column(db.String(200)) # If the restaurant has healthy options
    late_night = db.Column(db.String(200)) # If the restaurant is open late
    noisy = db.Column(db.String(200)) # If the restaurant is noisy
    quick_bite = db.Column(db.String(200)) # If the restaurant is good for a quick bite
    romantic = db.Column(db.String(200)) # If the restaurant is romantic
    service_quality = db.Column(db.String(200)) # If the restaurant has good service
    singles_popular = db.Column(db.String(200)) # If the restaurant is good for singles  
    special_occasion = db.Column(db.String(200)) # If the restaurant is good for special occasions
    trendy = db.Column(db.String(200)) # If the restaurant is trendy
    value_for_money = db.Column(db.String(200)) # If the restaurant is good value for money
    vegan_diet = db.Column(db.String(200)) # If the restaurant has vegan options
    vegetarian_diet = db.Column(db.String(200)) # If the restaurant has vegetarian options

# Define the RestaurantVisit model
class RestaurantVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Visit ID, primary key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User ID associated with the visit
    restaurant_id = db.Column(db.String(200), db.ForeignKey('restaurant.id'), nullable=False)  # Restaurant ID associated with the visit
    date_visited = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Date and time of the visit
    rating = db.Column(db.Integer, nullable=False)  # Rating given by the user for the restaurant visit
    
    # String representation of the RestaurantVisit object
    def __repr__(self):
        return f"Restaurant Visit('{self.user_id}', '{self.date_visited}', '{self.rating}')"