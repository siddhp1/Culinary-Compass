from culinarycompass import app, db
from culinarycompass.models import User, Restaurant
with app.app_context():
    # user_id_to_query = 1  # Replace with the actual user_id you want to query
    
    # restaurants = Restaurant.query.filter_by(user_id=user_id_to_query).all()
    
    # for restaurant in restaurants:
    #     print(restaurant.name, restaurant.address, restaurant.date_visited, restaurant.rating)

    db.create_all()
