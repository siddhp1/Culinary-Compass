import requests
from collections import Counter, OrderedDict

from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from culinarycompass.models import User, Restaurant, RestaurantVisit, RestaurantFeature
from culinarycompass import db, foursquare

class RecommendationGenerator():

    # Method for getting the user's preferred categories and restaurants
    @staticmethod
    def get_user_preferences(id):
        category_counts = Counter()
        preferred_restaurants = []

        visits = RestaurantVisit.query.filter_by(user_id=id).filter(RestaurantVisit.rating >= 3).all()

        for visit in visits:
            categories = visit.restaurant.category.split(',')
            
            # Skip the restaurant if it has no categories
            if not categories or categories == ['']:
                continue
            
            for category in categories:
                # Skip the restaurant if the categories have no id
                if ':' not in category:
                    continue
                category_name, category_id = category.split(':')
                category_counts[(category_name, category_id)] += 1

            preferred_restaurants.append(visit.restaurant.id)

        top_categories = [category for category, count in category_counts.most_common(5)]
        return top_categories, preferred_restaurants
    
    # Method for getting the user's preferred attributes
    @staticmethod
    def user_preferred_attributes(preferred_restaurants, id):
        # Access each preferred restaurant visits features and user questionnaire data and place in a dictionary
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
        
        for fsd_id in preferred_restaurants:
            features = RestaurantFeature.query.filter_by(restaurant_id=fsd_id).first()
            if features:
                for feature_name in preferred_attributes.keys():
                    if hasattr(features, feature_name):
                        feature_value = getattr(features, feature_name)
                    else:
                        feature_value = None
                    if feature_value:
                        preferred_attributes[feature_name] += 1

        # Normalize frequencies between 0 and 1
        total_restaurants = len(preferred_restaurants)
        for feature_name, frequency in preferred_attributes.items():
            feature_value = frequency / total_restaurants
            preferred_attributes[feature_name] = feature_value
            
        # Override frequencies with user questionnaire data
        user = User.query.filter_by(id=id).first()
        if user.vegetarianism == "vegetarian":
            preferred_attributes['vegetarian_diet'] = 1.0
        elif user.vegetarianism == "vegan":
            preferred_attributes['vegan_diet'] = 1.0
        if user.gluten:
            preferred_attributes['gluten_free_diet'] = 1.0
        if user.healthy:
            preferred_attributes['healthy_diet'] = 1.0
        if user.no_alcohol:
            keys = ['bar_service', 'beer', 'byo', 'cocktails', 'full_bar', 'wine']
            for key in keys:
                preferred_attributes[key] = 0.0
        return preferred_attributes
    
    # Method for getting local restaurants with the user's preferred categories
    @staticmethod
    def get_local_restaurants(coords, top_categories, radius):   
        categories = ','.join(category_id for category_name, category_id in top_categories)
        
        # FourSquare API request
        url = f"https://api.foursquare.com/v3/places/search?&ll={coords}&radius={radius * 1000}&categories={categories}&limit=10&fields=name%2Cfsq_id%2Ccategories%2Cmenu%2Cwebsite%2Cprice%2Ctastes%2Cfeatures%2Clocation%2Cdescription"
        headers = {
            "accept": "application/json",
            "Authorization": foursquare
        }
        response = requests.get(url, headers=headers)
        parsed_data = response.json()
        
        restaurant_ids = []
        if parsed_data['results'] is not None:
            for place_data in parsed_data['results']:
                restaurant_exists = Restaurant.query.filter_by(id=place_data['fsq_id']).first()
                restaurant_ids.append(place_data['fsq_id'])
                
                if not restaurant_exists:
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

                    if 'features' in place_data:
                        features_data = place_data['features']
                    else:
                        features_data = None

                    # Create a list of feature names based on the RestaurantFeature model columns
                    feature_columns = [column.name for column in RestaurantFeature.__table__.columns]
                    feature_values = {}
                    ignore_sections = ['payment', 'services', 'amenities']

                    # Function to flatten nested JSON structures
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
                    flattened_features = flatten_features(features_data)

                    # Iterate through features and check if the corresponding column exists
                    for feature_name, feature_data in flattened_features.items():
                        if feature_name in feature_columns:
                            feature_values[feature_name] = feature_data

                    # Only create a RestaurantFeature object if feature_values is not empty
                    if feature_values:
                        restaurant_features = RestaurantFeature(restaurant_id=restaurant.id, **feature_values)
                        db.session.add(restaurant_features)

                    # Add the restaurant to the local database
                    db.session.add(restaurant)
            db.session.commit()
        return(restaurant_ids)
    
    # Method for setting the float value of a feature
    @staticmethod
    def get_feature_value(feature):
        if feature is None:
            return 0.0
        elif isinstance(feature, bool):
            return 1.0 if feature else 0.0
        elif isinstance(feature, str):
            # Return 0.3 if feature is Poor
            if feature == 'Poor':
                return 0.3
            # Return 0.5 if feature is Average
            elif feature == 'Average':
                return 0.5
            # Return 0.8 if feature is Great
            elif feature == 'Great':
                return 0.8
        return 0.0
    
    # Method for computing cosine similarity
    @staticmethod
    def rank_restaurants(restaurant_ids, preferred_attributes):
        suggested_restaurants = [Restaurant.query.get(id) for id in restaurant_ids]
        restaurant_attributes = {}

        for restaurant in suggested_restaurants:
            restaurant_features = RestaurantFeature.query.filter_by(restaurant_id=restaurant.id).first()
            if restaurant_features:
                restaurant_attributes[restaurant.name] = {
                    feature: RecommendationGenerator.get_feature_value(getattr(restaurant_features, feature))
                    for feature in preferred_attributes.keys()
                }
            else:
                restaurant_attributes[restaurant.name] = {}
        
        # Preprocess user and restaurant attributes
        dict_vectorizer = DictVectorizer(sparse=True)
        user_attribute_vector = dict_vectorizer.fit_transform([preferred_attributes])
        restaurant_attribute_vectors = dict_vectorizer.transform(restaurant_attributes.values())

        # Compute cosine similarity
        cs = cosine_similarity(user_attribute_vector, restaurant_attribute_vectors)
        cs = cs.tolist()

        # Dictionary to rank cosine similarity values
        restaurant_cs_values = OrderedDict()
        for i in range(len(suggested_restaurants)):
            restaurant_id = suggested_restaurants[i].id
            if i < len(cs[0]):
                restaurant_cs_values[restaurant_id] = cs[0][i]
            else:
                restaurant_cs_values[restaurant_id] = 0.0
        sorted_restaurants = sorted(restaurant_cs_values.items(), key=lambda x: x[1], reverse=True)
        sorted_restaurant_ids = [z[0] for z in sorted_restaurants]
        return sorted_restaurant_ids
    
    # Method to generate recommendations
    @staticmethod
    def generate_recommendation(id, coords, radius):
        top_categories, preferred_restaurants = RecommendationGenerator.get_user_preferences(id)
        preferred_attributes = RecommendationGenerator.user_preferred_attributes(preferred_restaurants, id)
        restaurant_ids = RecommendationGenerator.get_local_restaurants(coords, top_categories, radius)
        recommendation_order = RecommendationGenerator.rank_restaurants(restaurant_ids, preferred_attributes)
        return(recommendation_order)