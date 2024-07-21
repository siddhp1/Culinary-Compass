from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from culinarycompass import db, login_manager, app
from flask_login import UserMixin

# Load user callback for flask-login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    vegetarianism = db.Column(db.String(20), default='neither')
    gluten = db.Column(db.Boolean, default=False)
    healthy = db.Column(db.Boolean, default=False)
    no_alcohol = db.Column(db.Boolean, default=False)
    restaurant_visits = db.relationship('RestaurantVisit', backref='user', lazy=True)

    # Generate a password reset token
    def get_reset_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    # Static method to verify a password reset token
    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except:
            # Returns none if the token is invalid or expired
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

# Restaurant model
class Restaurant(db.Model):
    id = db.Column(db.String(24), primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    category = db.Column(db.Text, nullable=False)
    website = db.Column(db.String(200), nullable=True)
    menu = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Integer)
    description = db.Column(db.Text)
    tastes = db.Column(db.Text, nullable=True)
    restaurant_visits = db.relationship('RestaurantVisit', backref='restaurant', lazy=True)
    features = db.relationship('RestaurantFeature', backref='restaurant', lazy=True)

    def __repr__(self):
        return f"Restaurant('{self.name}', '{self.address}')"

# Restaurant feature model
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
    
    def get_all_data(self):
        return {
            'bar_service': self.bar_service,
            'beer': self.beer,
            'byo': self.byo,
            'cocktails': self.cocktails,
            'full_bar': self.full_bar,
            'wine': self.wine,
            'bar_snacks': self.bar_snacks,
            'breakfast': self.breakfast,
            'brunch': self.brunch,
            'lunch': self.lunch,
            'happy_hour': self.happy_hour,
            'dessert': self.dessert,
            'dinner': self.dinner,
            'tasting_menu': self.tasting_menu,
            'business_meeting': self.business_meeting,
            'clean': self.clean,
            'crowded': self.crowded,
            'dates_popular': self.dates_popular,
            'dressy': self.dressy,
            'families_popular': self.families_popular,
            'gluten_free_diet': self.gluten_free_diet,
            'good_for_dogs': self.good_for_dogs,
            'groups_popular': self.groups_popular,
            'healthy_diet': self.healthy_diet,
            'late_night': self.late_night,
            'noisy': self.noisy,
            'quick_bite': self.quick_bite,
            'romantic': self.romantic,
            'service_quality': self.service_quality,
            'singles_popular': self.singles_popular,
            'special_occasion': self.special_occasion,
            'trendy': self.trendy,
            'value_for_money': self.value_for_money,
            'vegan_diet': self.vegan_diet,
            'vegetarian_diet': self.vegetarian_diet,
        }

# Restaurant visit model
class RestaurantVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.String(200), db.ForeignKey('restaurant.id'), nullable=False)
    date_visited = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rating = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f"Restaurant Visit('{self.user_id}', '{self.date_visited}', '{self.rating}')"