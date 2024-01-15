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

class RecommendationGenerator():
    @staticmethod
    def get_user_preferences(id):
        # Initialize two empty Counter objects
        category_counts = Counter()
        feature_counts = Counter()

        # Get all visits made by the user
        visits = RestaurantVisit.query.filter_by(user_id=id).all()

        # For each visit
        for visit in visits:
            # Split the visited restaurant's category string into individual categories
            categories = visit.restaurant.category.split(',')

            # Only consider the first category
            first_category = categories[0]

            # Split the category into the name and id
            category_name, category_id = first_category.split(':')

            # Increment the count of the category tuple (name, id)
            category_counts[(category_name, category_id)] += 1

            # Get the RestaurantFeature instance for the visited restaurant
            features = RestaurantFeature.query.filter_by(restaurant_id=visit.restaurant.id).first()

            # For each attribute of the RestaurantFeature instance
            for attr, value in features.__dict__.items():
                # If the attribute is True
                if value is True:
                    # Increment the count in feature_counts
                    feature_counts[attr] += 1

        # Get the most common categories and features
        top_categories = [category for category, count in category_counts.most_common(3)]
        top_features = [feature for feature, count in feature_counts.most_common(3)]

        # Return the most common categories and features
        return top_categories, top_features
    
    @staticmethod
    def get_local_restaurants(coords):    
        # SEARCH FOR STUFF WITH FILTERS
        
        
        pass
    
    @staticmethod
    def cosine_similarity(user_preferences):
        pass
    
    @staticmethod
    def generate_recommendation(id, coords):
        # Get the user's preferences
        top_categories, top_features = RecommendationGenerator.get_user_preferences(id)
        print(top_categories, top_features)
        
        # Get local restaurants
        local_restaurants = RecommendationGenerator.get_local_restaurants(coords)
        print(local_restaurants)
        
        return("Recommendation generated!")