# accessing features from visit

# Iterate through the restaurant visits
for visit in restaurant_visits.items:
    # Access the associated restaurant
    restaurant = visit.restaurant

    # Access the features of the restaurant
    features = RestaurantFeature.query.filter_by(restaurant_id=restaurant.id).first()

    # Print the features
    print("Features for Restaurant:", restaurant.name)
    print("Payment: Amex -", features.cocktails)
    print("Delivery -", features.full_bar)
    # Add more feature prints as needed

    # Access other information from the RestaurantVisit instance if needed
    print("Date Visited:", visit.date_visited)
    # Add more visit information prints as needed