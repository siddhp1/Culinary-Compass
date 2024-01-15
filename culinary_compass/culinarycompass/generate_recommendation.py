# Import os for file path operations
import os
# Import models from models.py
from culinarycompass.models import User, Restaurant, RestaurantVisit, RestaurantFeature
# Import app and db from __init__.py
from culinarycompass import app, db
# Import func and extract from sqlalchemy for querying
from sqlalchemy import func, extract


import requests
from collections import Counter

from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RecommendationGenerator():
    @staticmethod
    def get_user_preferences(id):
        # Initialize two empty Counter objects
        category_counts = Counter()
        feature_counts = Counter()
        
        # Initialize a list to store the user's preferered restaurants
        preferred_restaurants = []

        # Get all visits made by the user
        visits = RestaurantVisit.query.filter_by(user_id=id).filter(RestaurantVisit.rating >= 3).all()

        # For each visit
        for visit in visits:
            # Split the visited restaurant's category string into individual categories
            categories = visit.restaurant.category.split(',')
            
            # For each category
            for category in categories:
                 # Split the category into the name and id
                category_name, category_id = category.split(':')
                # Increment the count of the category tuple (name, id)
                category_counts[(category_name, category_id)] += 1

            # Add the restaurant's ID to the list of preferred restaurants
            preferred_restaurants.append(visit.restaurant.id)

        # Get the most common categories and features
        top_categories = [category for category, count in category_counts.most_common(5)]

        # Return the most common categories and features
        return top_categories, preferred_restaurants
    
    @staticmethod
    def get_local_restaurants(coords, top_categories):   
        # Process the categories into a comma-separated string of the IDs
        categories = ','.join(category_id for category_name, category_id in top_categories)
        
        # FourSquare API request URL with restaurant name and coordinates
        url = f"https://api.foursquare.com/v3/places/search?&ll={coords}&radius=10000&categories={categories}&limit=2&fields=name%2Cfsq_id%2Ccategories%2Cmenu%2Cwebsite%2Cprice%2Ctastes%2Cfeatures%2Clocation%2Cdescription"
        
        # API settings and key
        # MAKE AN APP/ENVIRONMENT VARIABLE
        headers = {
            "accept": "application/json",
            "Authorization": "fsq3891kysJBh536fngR4yL2X7D8lqkaNSF8vzQTtQNZqs0="
        }
        
        # Make the API request and store the response
        response = requests.get(url, headers=headers)
        
        # Parse the JSON data
        parsed_data = response.json()
        
        # List of restaurants that were found
        restaurant_ids = []
        
        # Check if a match is found
        if parsed_data['results'] is not None:
            for place_data in parsed_data['results']:
                restaurant_exists = Restaurant.query.filter_by(id=place_data['fsq_id']).first()
                if not restaurant_exists:
                    # Extract necessary information from the place_data
                    fsq_id = place_data['fsq_id']
                    restaurant_full_name = place_data['name']
                    categories = [f"{category['short_name']}:{category['id']}" for category in place_data['categories']]
                    categories_str = ",".join(categories)
                    address = place_data['location']['formatted_address']
                    website = place_data.get('website', None)
                    menu = place_data.get('menu', None)
                    description = place_data.get('description', None)
                    price = place_data.get('price', None)
                    tastes_str = ",".join(place_data.get('tastes', []))
                    
                    # Append the restaurant's ID to the list of restaurant IDs
                    restaurant_ids.append(fsq_id)

                    # Create a new Restaurant object
                    restaurant = Restaurant(
                        id=fsq_id,
                        full_name=restaurant_full_name,
                        name=restaurant_full_name,
                        address=address,
                        category=categories_str,
                        website=website,
                        menu=menu,
                        description=description,
                        price=price,
                        tastes=tastes_str
                    )

                    # Check if features information is available
                    if 'features' in place_data:
                        features_data = place_data['features']
                    else:
                        features_data = None

                    # Create a list of feature names based on the RestaurantFeature model columns
                    feature_columns = [column.name for column in RestaurantFeature.__table__.columns]
                    # Initialize the dictionary to store feature values
                    feature_values = {}
                    # Sections to ignore
                    ignore_sections = ['payment', 'services', 'amenities']

                    # Flatten nested structures in features_data
                    def flatten_features(data, prefix=""):
                        if data is None:
                            return {}

                        flat_data = {}
                        for key, value in data.items():
                            if key in ignore_sections:
                                continue
                            if isinstance(value, dict):
                                flat_data.update(flatten_features(value, f"{prefix}{key}_"))
                            else:
                                flat_data[key] = value
                        return flat_data

                    # Flatten the features
                    flattened_features = flatten_features(features_data)

                    # Iterate through features and check if the corresponding column exists
                    for feature_name, feature_data in flattened_features.items():
                        if feature_name in feature_columns:
                            feature_values[feature_name] = feature_data

                    # Only create a RestaurantFeature object if feature_values is not empty
                    if feature_values:
                        restaurant_features = RestaurantFeature(restaurant_id=restaurant.id, **feature_values)
                        db.session.add(restaurant_features)

                    # Add the restaurant to the database
                    db.session.add(restaurant)
                else:
                    pass
            # Commit the changes to the database
            db.session.commit()
        return(restaurant_ids)
    
    @staticmethod
    def user_preferred_attributes(preferred_restaurants):
        # Access each preferred restaurant visits features and user questionnaire data and place in a dictionary (this is the user profile)
        
        
        
        
        pass

        # # Get the RestaurantFeature instance for the visited restaurant
        #             features = RestaurantFeature.query.filter_by(restaurant_id=visit.restaurant.id).first()

        #             # For each attribute of the RestaurantFeature instance
        #             if features is not None:
        #                 for attr, value in features.__dict__.items():
        #                     # If the attribute is True
        #                     if value is True:
        #                         # Increment the count in feature_counts
        #                         feature_counts[attr] += 1


    @staticmethod
    def cosine_similarity(restaurant_ids, preferred_restaurants):
        # get the user profile from previous function
        
        # make a profile of each restaurant in the restaurant_ids list
        
        # rank using cosine similarity
        
        # return the ranked list
        return(restaurant_ids)
    
    @staticmethod
    def generate_recommendation(id, coords):
        # Get the user's preferences
        top_categories, preferred_restaurants = RecommendationGenerator.get_user_preferences(id)
        print(top_categories, preferred_restaurants)
        
        # Get local restaurants
        restaurant_ids = RecommendationGenerator.get_local_restaurants(coords, top_categories)
        print(restaurant_ids)
        
        # Get the user's preferred attributes
        preferred_attributes = RecommendationGenerator.user_preferred_attributes(preferred_restaurants)
        print(preferred_attributes)
        
        # Cosine similarity
        recommendation_order = RecommendationGenerator.cosine_similarity(restaurant_ids, preferred_restaurants)
        print(recommendation_order)
        
        
        # Return the recommendation
        
        return("Recommendation generated!")