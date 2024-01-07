from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from culinarycompass import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    restaurant_visits = db.relationship('RestaurantVisit', backref='user', lazy=True)

    def get_reset_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return(s.dumps({'user_id': self.id}))
    
    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except:
            return None
        return(User.query.get(user_id))

    def __repr__(self):
        return(f"User('{self.username}', '{self.email}', '{self.image_file}')")
    
class Restaurant(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    keywords = db.Column(db.Text, nullable=False, default='Test')
    restaurant_visits = db.relationship('RestaurantVisit', backref='restaurant', lazy=True)
    # price, so on (add other RICH features later)

    def __repr__(self):
        return f"Restaurant('{self.name}', '{self.address}')"
    
class RestaurantVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.String(200), db.ForeignKey('restaurant.id'), nullable=False)
    date_visited = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rating = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f"Restaurant Visit('{self.user_id}', '{self.date_visited}', '{self.rating}')"
    