import os
import secrets
from datetime import datetime
from collections import Counter

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import matplotlib
matplotlib.use('Agg') # Set the backend to Agg before importing pyplot to prevent Tkinter errors
import matplotlib.pyplot as plt

from culinarycompass.models import User, Restaurant, RestaurantVisit, RestaurantFeature
from culinarycompass import app, db
from sqlalchemy import func, extract

class ReportGenerator:

    # Method for drawing text on the PDF
    @staticmethod
    def draw_text(canvas, text, font_size, font_colour, y_val=70, x_val=None):
        canvas.setFont("DM Sans", font_size)
        font_colour_rgb = tuple(component / 255.0 for component in font_colour)
        canvas.setFillColorRGB(*font_colour_rgb)
        text_width = canvas.stringWidth(text, "DM Sans", font_size)
        page_width, page_height = letter

        # If x value is provided
        if x_val:
            center_x = x_val - text_width / 2
            canvas.drawString(center_x, page_height - y_val, text)
        # Otherwise draw the text in the center of the page
        else:
            center_x = (page_width - text_width) / 2
            canvas.drawString(center_x, page_height - y_val, text)
    
    # Method for generating a PDF report
    @staticmethod  
    def create_pdf(pdf_path, username):
        font_path = os.path.join(app.root_path, 'static/fonts/DMSans-Regular.ttf')
        pdfmetrics.registerFont(TTFont("DM Sans", font_path))
        pdf_canvas = canvas.Canvas(pdf_path, pagesize=letter)

        # Draw the title of the report
        ReportGenerator.draw_text(pdf_canvas, "Culinary Mapped", 48, (232, 93, 4))
        
        # Get the user data
        user_data = User.query.filter_by(username=username).first()
        if user_data:
            current_year = datetime.now().year
            
            # Section 1 of the report
            ReportGenerator.draw_text(pdf_canvas, f"Here's a Recap of Your {current_year} in Food.", 32, (232, 93, 4), 120)

            # Total number of restaurant visits for the user this year
            total_visits_this_year = RestaurantVisit.query \
                .filter_by(user_id=user_data.id) \
                .filter(db.extract('year', RestaurantVisit.date_visited) == current_year) \
                .count()
            ReportGenerator.draw_text(pdf_canvas, f"You visited {total_visits_this_year} restaurants this year.", 24, (68, 68, 68), 160)

            # Number of unique restaurants visited by the user this year
            unique_restaurants_this_year = db.session.query(db.distinct(Restaurant.name)) \
                .join(RestaurantVisit, RestaurantVisit.restaurant_id == Restaurant.id) \
                .filter_by(user_id=user_data.id) \
                .filter(db.extract('year', RestaurantVisit.date_visited) == current_year) \
                .count()
            ReportGenerator.draw_text(pdf_canvas, f"{unique_restaurants_this_year} of those were unique.", 24, (68, 68, 68), 190)
                
            # Favourite restaurant (most visits, highest average rating as a tiebreaker)
            most_visited_restaurant_name = db.session.query(Restaurant.name) \
                .join(RestaurantVisit, RestaurantVisit.restaurant_id == Restaurant.id) \
                .filter_by(user_id=user_data.id) \
                .filter(extract('year', RestaurantVisit.date_visited) == current_year) \
                .group_by(Restaurant.id, Restaurant.name) \
                .order_by(func.count(RestaurantVisit.id).desc(), func.avg(RestaurantVisit.rating).desc()) \
                .first()
            # If there is a most visited restaurant
            if most_visited_restaurant_name is not None:
                most_visited_restaurant_name = most_visited_restaurant_name[0]
                ReportGenerator.draw_text(pdf_canvas, f"{most_visited_restaurant_name} was your favourite restaurant.", 24, (68, 68, 68), 220)
         
            # Section 2 of the report
            ReportGenerator.draw_text(pdf_canvas, f"Your Favourite Foods", 32, (232, 93, 4), 270)
            
            categories = []

            # Query for the type of food for each restaurant visit this year
            visits_current_year = RestaurantVisit.query.filter_by(user_id=user_data.id).filter(
                db.extract('year', RestaurantVisit.date_visited) == current_year
            ).all()

            for visit in visits_current_year:
                restaurant = visit.restaurant
                all_categories = restaurant.category.strip('[]').split(',')  # Remove brackets and split by comma
                if all_categories:
                    first_category_name = all_categories[0].split(':')[0].strip("'\"")  # Extract the name from the first category
                    if first_category_name.lower() == "restaurant":
                        continue
                    # If the category contains the word "restaurant", remove it
                    first_category_name = first_category_name.replace("Restaurant", "").replace("restaurant", "").strip()
                    categories.append(first_category_name)
                
            # If there are categories
            if categories:
                category_counts = Counter(categories)
                top_categories = category_counts.most_common(5)
                categories, frequencies = zip(*top_categories)

                # Create a bar graph for the top 5 categories
                plt.bar(categories, frequencies, color=(244/255, 140/255, 6/255))
                plt.ylabel('Number of Visits')
                plt.xticks(rotation=0, ha='center')
                plt.yticks(range(max(frequencies) + 1))
                plt.tight_layout()

                # Save the plot as an image
                random_hex = secrets.token_hex(8)
                image_path = os.path.join(app.root_path, f'static/reports/{random_hex}.png')
                plt.savefig(image_path, format='png')
                plt.clf()

                page_width, _ = letter # Get dimensions of the page
                pdf_canvas.drawImage(image_path, x=(page_width - 400) / 2 - 10, y=265, width=400, height=250)
                os.remove(os.path.join(app.root_path, f'static/reports/{random_hex}.png'))
                
            # Section 3 of the report
            ReportGenerator.draw_text(pdf_canvas, f"Your Culinary Habits", 32, (232, 93, 4), 560)
            
            # Query for all restaurant visits of the user in the current year
            user_restaurant_visits = RestaurantVisit.query \
                .filter_by(user_id=user_data.id) \
                .filter(extract('year', RestaurantVisit.date_visited) == current_year) \
                .all()

            breakfast_count = 0
            lunch_count = 0
            dinner_count = 0

            for visit in user_restaurant_visits:
                restaurant_id = visit.restaurant_id
                restaurant_feature = RestaurantFeature.query.filter_by(restaurant_id=restaurant_id).first()

                if restaurant_feature and restaurant_feature.breakfast:
                    breakfast_count += 1
                if restaurant_feature and restaurant_feature.lunch:
                    lunch_count += 1
                if restaurant_feature and restaurant_feature.dinner:
                    dinner_count += 1
                                
            # Create a pie chart for the meal types
            labels = ['Breakfast', 'Lunch', 'Dinner']
            sizes = [breakfast_count, lunch_count, dinner_count]

            # Filter out labels with zero values
            non_zero_labels = [label for label, size in zip(labels, sizes) if size > 0]
            non_zero_sizes = [size for size in sizes if size > 0]

            rgb_colors = [(255/255, 186/255, 8/255), (244/255, 140/255, 6/255), (220/255, 47/255, 2/255)]
            plt.pie(non_zero_sizes, labels=non_zero_labels, startangle=140, colors=rgb_colors)
            plt.axis('equal') 

            random_hex = secrets.token_hex(8)
            image_path = os.path.join(app.root_path, f'static/reports/{random_hex}.png')
            plt.savefig(image_path, format='png')
            plt.clf()
            
            pdf_canvas.drawImage(image_path, x=0, y=0, width=300, height=220)
            os.remove(os.path.join(app.root_path, f'static/reports/{random_hex}.png'))
            
            # Get the most common price category for the user's restaurant visits this year
            user_restaurant_visits = RestaurantVisit.query \
                .filter_by(user_id=user_data.id) \
                .filter(extract('year', RestaurantVisit.date_visited) == current_year) \
                .all()
            price_categories = [visit.restaurant.price for visit in user_restaurant_visits]
            
            if price_categories:
                # Find the most common price category
                most_common_price_category = max(set(price_categories), key=price_categories.count)
        
                # Mapping for price categories to symbols
                price_mapping = {
                    1: '$',
                    2: '$$',
                    3: '$$$',
                    4: '$$$$'
                }
                most_common_price_symbol = price_mapping.get(most_common_price_category, 'Unknown')
                
                ReportGenerator.draw_text(pdf_canvas, f"{most_common_price_symbol}", 100, (68, 68, 68), 680, 420)
                ReportGenerator.draw_text(pdf_canvas, f"Your Favourite Price Category", 18, (68, 68, 68), 720, 420)
        else:
            # If the user does not exist, draw an error message on the PDF
            ReportGenerator.draw_text(pdf_canvas, "There was an error generating your Culinary Mapped.", 24, (68, 68, 68))

        pdf_canvas.save()