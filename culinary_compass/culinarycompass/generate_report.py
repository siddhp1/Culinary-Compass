import os
import secrets
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg before importing pyplot
import matplotlib.pyplot as plt
from collections import Counter
from culinarycompass.models import User, Restaurant, RestaurantVisit, RestaurantFeature
from culinarycompass import app, db
from sqlalchemy import func, extract

class ReportGenerator:
    @staticmethod
    def draw_text(canvas, text, font_size, font_colour, y_val=70, x_val=None):
        canvas.setFont("DM Sans", font_size)
        font_colour_rgb = tuple(component / 255.0 for component in font_colour)
        canvas.setFillColorRGB(*font_colour_rgb)
        text_width = canvas.stringWidth(text, "DM Sans", font_size)
        page_width, page_height = letter

        if x_val:
            center_x = x_val - text_width / 2
            canvas.drawString(center_x, page_height - y_val, text)
        else:
            center_x = (page_width - text_width) / 2
            canvas.drawString(center_x, page_height - y_val, text)
    
    @staticmethod  
    def create_pdf(pdf_path, username):
        # Font path
        font_path = os.path.join(app.root_path, 'static/fonts/DMSans-Regular.ttf')
        # Register the custom font
        pdfmetrics.registerFont(TTFont("DM Sans", font_path))
        # Create a PDF document
        pdf_canvas = canvas.Canvas(pdf_path, pagesize=letter)

        # TITLE
        ReportGenerator.draw_text(pdf_canvas, "Culinary Mapped", 48, (232, 93, 4))
        
        # GET DATA
        user_data = User.query.filter_by(username=username).first()
        
        if user_data:
            # Get the current year
            current_year = datetime.now().year

            # SECTION 1 (GENERAL)

            # Query to get the total number of restaurant visits for the user this year
            total_visits_this_year = RestaurantVisit.query \
                .filter_by(user_id=user_data.id) \
                .filter(db.extract('year', RestaurantVisit.date_visited) == current_year) \
                .count()

            # Query to get the number of unique restaurants visited by the user this year
            unique_restaurants_this_year = db.session.query(db.distinct(Restaurant.name)) \
                .join(RestaurantVisit, RestaurantVisit.restaurant_id == Restaurant.id) \
                .filter_by(user_id=user_data.id) \
                .filter(db.extract('year', RestaurantVisit.date_visited) == current_year) \
                .count()
                
            # Query to get the restaurant with the most visits and highest average rating
            most_visited_restaurant_name = db.session.query(Restaurant.name) \
                .join(RestaurantVisit, RestaurantVisit.restaurant_id == Restaurant.id) \
                .filter_by(user_id=user_data.id) \
                .filter(extract('year', RestaurantVisit.date_visited) == current_year) \
                .group_by(Restaurant.id, Restaurant.name) \
                .order_by(func.count(RestaurantVisit.id).desc(), func.avg(RestaurantVisit.rating).desc()) \
                .first()
            
            # Strip
            most_visited_restaurant_name = most_visited_restaurant_name[0]
         
            ReportGenerator.draw_text(pdf_canvas, f"Here's a Recap of Your {current_year} in Food.", 32, (232, 93, 4), 120)
            ReportGenerator.draw_text(pdf_canvas, f"You visited {total_visits_this_year} restaurants this year.", 24, (68, 68, 68), 160)
            ReportGenerator.draw_text(pdf_canvas, f"{unique_restaurants_this_year} of those were unique.", 24, (68, 68, 68), 190)
            ReportGenerator.draw_text(pdf_canvas, f"{most_visited_restaurant_name} was your favourite restaurant.", 24, (68, 68, 68), 220)
            
            # SECTION 2
            
            # Extract the first category's name for each restaurant visit
            # Initialize categories as an empty list
            categories = []

            # Extract the first category's name for each restaurant visit
            current_year = datetime.now().year
            visits_current_year = RestaurantVisit.query.filter_by(user_id=user_data.id).filter(
                db.extract('year', RestaurantVisit.date_visited) == current_year
            ).all()

            for visit in visits_current_year:
                restaurant = visit.restaurant
                all_categories = restaurant.category.strip('[]').split(',')  # Remove brackets and split by comma
                if all_categories:
                    first_category_name = all_categories[0].split(':')[0].strip("'\"")  # Extract the name from the first category
                    categories.append(first_category_name)

            # Rest of the code for counting and analyzing categories remains the same
            category_counts = Counter(categories)

            # Get the top 5 most common categories
            top_categories = category_counts.most_common(5)

            # Extract names and frequencies for plotting
            categories, frequencies = zip(*top_categories)

            # Create a bar graph
            plt.bar(categories, frequencies, color=(244/255, 140/255, 6/255))
            plt.ylabel('Number of Visits')
            plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
            plt.yticks(range(max(frequencies) + 1))  # Set y-axis scale to integers
            plt.tight_layout()

            # Save the plot as an image
            random_hex = secrets.token_hex(8)
            image_path = os.path.join(app.root_path, f'static/reports/{random_hex}.png')
            plt.savefig(image_path, format='png')
            plt.clf()

            # Draw the image on the PDF
            pdf_canvas.drawImage(image_path, x=50, y=265, width=500, height=250)
            os.remove(os.path.join(app.root_path, f'static/reports/{random_hex}.png'))
            ReportGenerator.draw_text(pdf_canvas, f"Your Favourite Foods", 32, (232, 93, 4), 270)
            
            # SECTION 3
            
            # Query for all restaurant visits of the user in the current year
            user_restaurant_visits = RestaurantVisit.query \
                .filter_by(user_id=user_data.id) \
                .filter(extract('year', RestaurantVisit.date_visited) == current_year) \
                .all()

            # Initialize counters for breakfast, lunch, and dinner
            breakfast_count = 0
            lunch_count = 0
            dinner_count = 0

            # Iterate through the user's restaurant visits and count meals
            for visit in user_restaurant_visits:
                restaurant_id = visit.restaurant_id
                # Assuming you have a reference to the RestaurantFeature model
                restaurant_feature = RestaurantFeature.query.filter_by(restaurant_id=restaurant_id).first()

                # Check the meal types for the current restaurant visit
                if restaurant_feature and restaurant_feature.breakfast:
                    breakfast_count += 1
                if restaurant_feature and restaurant_feature.lunch:
                    lunch_count += 1
                if restaurant_feature and restaurant_feature.dinner:
                    dinner_count += 1
                                
            # Time of the day (pie chart)
            # Assuming you have the counts from the previous code
            labels = ['Breakfast', 'Lunch', 'Dinner']
            sizes = [breakfast_count, lunch_count, dinner_count]

            # Filter out labels with zero values
            non_zero_labels = [label for label, size in zip(labels, sizes) if size > 0]
            non_zero_sizes = [size for size in sizes if size > 0]

            # Plotting the pie chart
            rgb_colors = [(255/255, 186/255, 8/255), (244/255, 140/255, 6/255), (220/255, 47/255, 2/255)]
            plt.pie(non_zero_sizes, labels=non_zero_labels, startangle=140, colors=rgb_colors)
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            random_hex = secrets.token_hex(8)

            # Save the plot as an image
            image_path = os.path.join(app.root_path, f'static/reports/{random_hex}.png')
            plt.savefig(image_path, format='png')
            plt.clf()

            # Average price
            # Query for all restaurant visits of the user in the current year
            user_restaurant_visits = RestaurantVisit.query \
                .filter_by(user_id=user_data.id) \
                .filter(extract('year', RestaurantVisit.date_visited) == current_year) \
                .all()

            # Extract the price category for each visit
            price_categories = [visit.restaurant.price for visit in user_restaurant_visits]

            # Use SQLAlchemy's func mode to find the most common price category
            most_common_price_category = max(set(price_categories), key=price_categories.count)
    
            price_mapping = {
                1: '$',
                2: '$$',
                3: '$$$',
                4: '$$$$'
            }

            # Map the most common price category to its symbol
            most_common_price_symbol = price_mapping.get(most_common_price_category, 'Unknown')
            
            # Draw the stuff on the PDF
            pdf_canvas.drawImage(image_path, x=-20, y=-20, width=350, height=250)
            ReportGenerator.draw_text(pdf_canvas, f"Your Culinary Habits", 32, (232, 93, 4), 560)
            ReportGenerator.draw_text(pdf_canvas, f"{most_common_price_symbol}", 100, (68, 68, 68), 680, 420)
            ReportGenerator.draw_text(pdf_canvas, f"Your Favourite Price Category", 18, (68, 68, 68), 720, 420)
            os.remove(os.path.join(app.root_path, f'static/reports/{random_hex}.png'))
            
        else:
            print("Error code here")

        # Save the PDF file
        pdf_canvas.save()