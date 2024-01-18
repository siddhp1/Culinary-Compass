# Import requests library to make API requests
import requests
# Import collections library to use Counter and OrderedDict
from collections import Counter, OrderedDict
# Import DictVectorizer for converting dictionaries to vectors
from sklearn.feature_extraction import DictVectorizer
# Import cosine_similarity for computing cosine similarity
from sklearn.metrics.pairwise import cosine_similarity
# Import models from models.py
from culinarycompass.models import User, Restaurant, RestaurantVisit, RestaurantFeature
# Import db and foursquare API key from __init__.py
from culinarycompass import db, foursquare

# Class for generating restaurant recommendations
class RecommendationGenerator():
    # Static method for getting the user's preferred categories and restaurants
    @staticmethod
    # Parameter: user ID
    def get_user_preferences(id):
        # Initialize two empty Counter objects
        category_counts = Counter()
        # Initialize a list to store the user's preferered restaurants
        preferred_restaurants = []

        # Get all visits made by the user
        visits = RestaurantVisit.query.filter_by(user_id=id).filter(RestaurantVisit.rating >= 3).all()

        # For each visit
        for visit in visits:
            # Split the visited restaurant's category string into individual categories
            categories = visit.restaurant.category.split(',')
            
            # Skip the restaurant if it has no categories
            if not categories or categories == ['']:
                continue
            
            # For each category
            for category in categories:
                # Skip the restaurant if the categories have no id
                if ':' not in category:
                    continue
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
    
    # Static method for getting the user's preferred attributes
    @staticmethod
    # Parameters: list of preferred restaurants, user ID
    def user_preferred_attributes(preferred_restaurants, id):
        # Access each preferred restaurant visits features and user questionnaire data and place in a dictionary (this is the user profile)
        preferred_attributes = {
            'bar_service': 0.0,
            'beer': 0.0,
            'byo': 0.0,
            'cocktails': 0.0,
            'full_bar': 0.0,
            'wine': 0.0,
            'bar_snacks': 0.0,
            'breakfast': 0.0,
            'brunch': 0.0,
            'lunch': 0.0,
            'happy_hour': 0.0,
            'dessert': 0.0,
            'dinner': 0.0,
            'tasting_menu': 0.0,
            'business_meeting': 0.0,
            'clean': 0.0,
            'crowded': 0.0,
            'dates_popular': 0.0,
            'dressy': 0.0,
            'families_popular': 0.0,
            'gluten_free_diet': 0.0,
            'good_for_dogs': 0.0,
            'groups_popular': 0.0,
            'healthy_diet': 0.0,
            'late_night': 0.0,
            'noisy': 0.0,
            'quick_bite': 0.0,
            'romantic': 0.0,
            'service_quality': 0.0,
            'singles_popular': 0.0,
            'special_occasion': 0.0,
            'trendy': 0.0,
            'value_for_money': 0.0,
            'vegan_diet': 0.0,
            'vegetarian_diet': 0.0
        }
        
        # Iterate through preferred restaurants and update feature frequencies
        for fsd_id in preferred_restaurants:
            # Get the restaurant's features
            features = RestaurantFeature.query.filter_by(restaurant_id=fsd_id).first()
            # Check if features exist
            if features:
                # Iterate through the preferred attributes
                for feature_name in preferred_attributes.keys():
                    # Check if the feature is True for the restaurant and update frequency
                    if hasattr(features, feature_name):
                        # Get the feature value
                        feature_value = getattr(features, feature_name)
                    # If the feature is not True
                    else:
                        # Set the feature value to None
                        feature_value = None
                    # Update the frequency
                    if feature_value:
                        # Increment the frequency
                        preferred_attributes[feature_name] += 1

        # Calculate the relative frequency for each feature
        # This is done to normalize the frequencies
        total_restaurants = len(preferred_restaurants)
        # Iterate through the preferred attributes
        for feature_name, frequency in preferred_attributes.items():
            # Calculate the relative frequency
            feature_value = frequency / total_restaurants
            # Update the feature value
            preferred_attributes[feature_name] = feature_value
            
        # Override frequencies with user questionnaire data
        user = User.query.filter_by(id=id).first()
        # Check if user has vegetarianism data
        if user.vegetarianism == "vegetarian":
            # Set the vegetarian_diet feature to 1.0 if the user is vegetarian
            preferred_attributes['vegetarian_diet'] = 1.0
        # Check if user has veganism data
        elif user.vegetarianism == "vegan":
            # Set the vegan_diet feature to 1.0 if the user is vegan
            preferred_attributes['vegan_diet'] = 1.0
        # Check if user has gluten data
        if user.gluten:
            # Set the gluten_free_diet feature to 1.0 if the user is gluten-free
            preferred_attributes['gluten_free_diet'] = 1.0
        # Check if user has healthy data
        if user.healthy:
            # Set the healthy_diet feature to 1.0 if the user is healthy
            preferred_attributes['healthy_diet'] = 1.0
        # Check if user has alcohol data
        if user.no_alcohol:
            # List of alcohol features
            keys = ['bar_service', 'beer', 'byo', 'cocktails', 'full_bar', 'wine']
            # Set the alcohol features to 0.0 if the user does not drink alcohol
            for key in keys:
                # Set the feature value to 0.0
                preferred_attributes[key] = 0.0
        # Return the user's preferred attributes
        return preferred_attributes
    
    # Static method for getting local restaurants with the user's preferred categories
    @staticmethod
    # Parameters: coordinates, list of preferred categories
    def get_local_restaurants(coords, top_categories, radius):   
        # Process the categories into a comma-separated string of the IDs
        categories = ','.join(category_id for category_name, category_id in top_categories)
        
        # FourSquare API request URL with restaurant name and coordinates
        url = f"https://api.foursquare.com/v3/places/search?&ll={coords}&radius={radius * 1000}&categories={categories}&limit=10&fields=name%2Cfsq_id%2Ccategories%2Cmenu%2Cwebsite%2Cprice%2Ctastes%2Cfeatures%2Clocation%2Cdescription"
        
        # API settings and key
        headers = {
            "accept": "application/json",
            "Authorization": foursquare
        }
        
        # Make the API request and store the response
        response = requests.get(url, headers=headers)
        
        # Parse the JSON data
        parsed_data = response.json()
        
        # List of restaurants that were found
        restaurant_ids = []
        
        # Check if a match is found
        if parsed_data['results'] is not None:
            # Iterate through the results
            for place_data in parsed_data['results']:
                # Check if the restaurant already exists in the database
                restaurant_exists = Restaurant.query.filter_by(id=place_data['fsq_id']).first()
                
                # Append the restaurant's ID to the list of restaurant IDs
                restaurant_ids.append(place_data['fsq_id'])
                
                # If the restaurant does not exist
                if not restaurant_exists:
                    # Extract necessary information from the place_data
                    # Extract Foursquare ID
                    fsq_id = place_data['fsq_id']
                    # Extract restaurant name
                    restaurant_full_name = place_data['name']
                    # Extract restaurant categories
                    categories = [f"{category['short_name']}:{category['id']}" for category in place_data['categories']]
                    # Convert the list of categories into a comma-separated string
                    categories_str = ",".join(categories)
                    # Extract restaurant address
                    address = place_data['location']['formatted_address']
                    # Extract restaurant website
                    website = place_data.get('website', None)
                    # Extract restaurant menu
                    menu = place_data.get('menu', None)
                    # Extract restaurant description
                    description = place_data.get('description', None)
                    # Extract restaurant price
                    price = place_data.get('price', None)
                    # Extract restaurant tastes
                    tastes_str = ",".join(place_data.get('tastes', []))

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
                        # Extract restaurant features
                        features_data = place_data['features']
                    # If features information is not available
                    else:
                        # Set features_data to None 
                        features_data = None

                    # Create a list of feature names based on the RestaurantFeature model columns
                    feature_columns = [column.name for column in RestaurantFeature.__table__.columns]
                    # Initialize the dictionary to store feature values
                    feature_values = {}
                    # Sections to ignore
                    ignore_sections = ['payment', 'services', 'amenities']

                    # Flatten nested structures in features_data
                    def flatten_features(data, prefix=""):
                        # Check if data is None
                        if data is None:
                            # Return an empty dictionary
                            return {}

                        # Initialize the dictionary to store flattened features
                        flat_data = {}
                        # Iterate through the data
                        for key, value in data.items():
                            # Check if the key is in the ignore_sections list
                            if key in ignore_sections:
                                # Skip the key
                                continue
                            # Check if the value is a dictionarys
                            if isinstance(value, dict):
                                # Flatten the dictionary
                                flat_data.update(flatten_features(value, f"{prefix}{key}_"))
                            # Check if the value is a list
                            else:
                                # Set the key to the value
                                flat_data[key] = value
                        # Return the flattened features
                        return flat_data

                    # Flatten the features
                    flattened_features = flatten_features(features_data)

                    # Iterate through features and check if the corresponding column exists
                    for feature_name, feature_data in flattened_features.items():
                        # Check if the feature name is in the feature_columns list
                        if feature_name in feature_columns:
                            # Update the feature_values dictionary
                            feature_values[feature_name] = feature_data

                    # Only create a RestaurantFeature object if feature_values is not empty
                    if feature_values:
                        # Create a new RestaurantFeature object
                        restaurant_features = RestaurantFeature(restaurant_id=restaurant.id, **feature_values)
                        # Add the restaurant features to the database
                        db.session.add(restaurant_features)

                    # Add the restaurant to the database
                    db.session.add(restaurant)
            # Commit the changes to the database
            db.session.commit()
        # Return the list of restaurant IDs
        return(restaurant_ids)
    
    # Static method for setting the float value of a feature
    @staticmethod
    # Parameter: feature
    def get_feature_value(feature):
        # Check if feature is None
        if feature is None:
            # Return 0.0
            return 0.0
        # Check if feature is a boolean
        elif isinstance(feature, bool):
            # Return 1.0 if feature is True, 0.0 if feature is False
            return 1.0 if feature else 0.0
        # Check if feature is a string
        elif isinstance(feature, str):
            # Return 0.3 if feature is Poor
            if feature == 'Poor':
                # Return 0.3
                return 0.3
            # Return 0.5 if feature is Average
            elif feature == 'Average':
                # Return 0.5
                return 0.5
            # Return 0.8 if feature is Great
            elif feature == 'Great':
                # Return 0.8
                return 0.8
        # Return 0.0 if feature is not a boolean or string
        return 0.0
    
    # Static method for computing cosine similarity
    @staticmethod
    # Parameters: list of restaurant IDs, user's preferred attributes
    def rank_restaurants(restaurant_ids, preferred_attributes):
        # Get the restaurants from the database
        suggested_restaurants = [Restaurant.query.get(id) for id in restaurant_ids]

        # Create a dictionary to store the restaurant attributes
        restaurant_attributes = {}

        # Iterate through the suggested restaurants
        for restaurant in suggested_restaurants:
            # Get the restaurant's features
            restaurant_features = RestaurantFeature.query.filter_by(restaurant_id=restaurant.id).first()
            # Check if restaurant features exist
            if restaurant_features:
                # Add the restaurant's features to the dictionary
                restaurant_attributes[restaurant.name] = {
                    # Get the value of the feature for each feature in preferred_attributes
                    feature: RecommendationGenerator.get_feature_value(getattr(restaurant_features, feature))
                    for feature in preferred_attributes.keys()
                }
            # If restaurant features do not exist
            else:
                # Add an empty dictionary for the restaurant
                restaurant_attributes[restaurant.name] = {}
        
        # Preprocess user and restaurant attributes
        # Initialize DictVectorizer
        dict_vectorizer = DictVectorizer(sparse=True)
        # Convert the preferred_attributes dictionary into a vector
        user_attribute_vector = dict_vectorizer.fit_transform([preferred_attributes])
        # Convert the restaurant_attributes dictionary into a vector
        restaurant_attribute_vectors = dict_vectorizer.transform(restaurant_attributes.values())

        # Compute cosine similarity
        cs = cosine_similarity(user_attribute_vector, restaurant_attribute_vectors)
        # Convert the cosine similarity matrix into a list
        cs = cs.tolist()

        # Create an ordered dictionary to store the restaurant IDs and cosine similarity values
        restaurant_cs_values = OrderedDict()

        # Iterate through the suggested restaurants
        for i in range(len(suggested_restaurants)):
            # Get the restaurant's ID
            restaurant_id = suggested_restaurants[i].id
            # Check if the restaurant has a cosine similarity value
            if i < len(cs[0]):
                # Add the restaurant's ID and cosine similarity value to the dictionary
                restaurant_cs_values[restaurant_id] = cs[0][i]
            # If the restaurant does not have a cosine similarity value
            else:
                # Add the restaurant's ID and cosine similarity value of 0.0 to the dictionary
                restaurant_cs_values[restaurant_id] = 0.0

        # Sort the dictionary by cosine similarity value
        sorted_restaurants = sorted(restaurant_cs_values.items(), key=lambda x: x[1], reverse=True)
        # Get the restaurant IDs from the sorted dictionary
        sorted_restaurant_ids = [z[0] for z in sorted_restaurants]

        # Return the sorted restaurant IDs
        return sorted_restaurant_ids
    
    @staticmethod
    def generate_recommendation(id, coords, radius):
        # Get the user's preferred restaurants and categories
        top_categories, preferred_restaurants = RecommendationGenerator.get_user_preferences(id)
        # Get the user's preferred attributes
        preferred_attributes = RecommendationGenerator.user_preferred_attributes(preferred_restaurants, id)
        # Get local restaurants with the user's preferred categories
        restaurant_ids = RecommendationGenerator.get_local_restaurants(coords, top_categories, radius)
        # Cosine similarity to rank the restaurants
        recommendation_order = RecommendationGenerator.rank_restaurants(restaurant_ids, preferred_attributes)
        # Return the recommendation
        return(recommendation_order)