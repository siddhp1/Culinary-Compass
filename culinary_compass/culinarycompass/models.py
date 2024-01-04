from datetime import datetime
from culinarycompass import db, login_manager
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
    restaurants = db.relationship('Restaurant', backref='user', lazy=True)

    def __repr__(self):
        return(f"User('{self.username}', '{self.email}', '{self.image_file}')")
    
class Restaurant(db.Model):
    visit_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_visited = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    keywords = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Restaurant('{self.name}', '{self.date_visited}')"