# Import os for file path operations
import os
# Import secrets for generating random hex
import secrets
# Import datetime for getting the current year
from datetime import datetime
# Import reportlab for PDF generation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
# Import TTFont for custom fonts
from reportlab.pdfbase.ttfonts import TTFont
# Import matplotlib for data visualization
import matplotlib
# Set the backend to Agg before importing pyplot to prevent Tkinter errors
matplotlib.use('Agg')
# Import pyplot for plotting
import matplotlib.pyplot as plt
# Import Counter for counting categories
from collections import Counter
# Import models from models.py
from culinarycompass.models import User, Restaurant, RestaurantVisit, RestaurantFeature
# Import app and db from __init__.py
from culinarycompass import app, db
# Import func and extract from sqlalchemy for querying
from sqlalchemy import func, extract

# Class for generating Culinary Mapped reports
class ReportGenerator:
    # Static method for drawing text on the PDF
    @staticmethod
    # Parameters: canvas, text, font size, font colour, y coordinate, x coordinate
    def draw_text(canvas, text, font_size, font_colour, y_val=70, x_val=None):
        # Set the font family and size
        canvas.setFont("DM Sans", font_size)
        # Convert RGB values to floats between 0 and 1
        font_colour_rgb = tuple(component / 255.0 for component in font_colour)
        # Set the font colour
        canvas.setFillColorRGB(*font_colour_rgb)
        # Get the width of the text
        text_width = canvas.stringWidth(text, "DM Sans", font_size)
        # Get the page width and height
        page_width, page_height = letter

        # Check if x_val is provided
        if x_val:
            # Calculate the center x coordinate
            center_x = x_val - text_width / 2
            # Draw the text
            canvas.drawString(center_x, page_height - y_val, text)
        # If x_val is not provided, draw the text in the center of the page
        else:
            # Calculate the center x coordinate
            center_x = (page_width - text_width) / 2
            # Draw the text
            canvas.drawString(center_x, page_height - y_val, text)
    
    # Static method for generating a PDF report
    @staticmethod  
    # Parameters: pdf file path, username
    def create_pdf(pdf_path, username):
        # Get the font path
        font_path = os.path.join(app.root_path, 'static/fonts/DMSans-Regular.ttf')
        # Register the custom font
        pdfmetrics.registerFont(TTFont("DM Sans", font_path))
        # Create a PDF document
        pdf_canvas = canvas.Canvas(pdf_path, pagesize=letter)

        # Draw the title of the report
        ReportGenerator.draw_text(pdf_canvas, "Culinary Mapped", 48, (232, 93, 4))
        
        # Query the user data using the username
        user_data = User.query.filter_by(username=username).first()
        
        # If the user exists
        if user_data:
            # Get the current year
            current_year = datetime.now().year
            
            # Section 1 of the report
            # Draw the subheading for section 1 of the report
            ReportGenerator.draw_text(pdf_canvas, f"Here's a Recap of Your {current_year} in Food.", 32, (232, 93, 4), 120)

            # Query to get the total number of restaurant visits for the user this year
            total_visits_this_year = RestaurantVisit.query \
                .filter_by(user_id=user_data.id) \
                .filter(db.extract('year', RestaurantVisit.date_visited) == current_year) \
                .count()
            # Draw the total number of visits on the PDF
            ReportGenerator.draw_text(pdf_canvas, f"You visited {total_visits_this_year} restaurants this year.", 24, (68, 68, 68), 160)

            # Query to get the number of unique restaurants visited by the user this year
            unique_restaurants_this_year = db.session.query(db.distinct(Restaurant.name)) \
                .join(RestaurantVisit, RestaurantVisit.restaurant_id == Restaurant.id) \
                .filter_by(user_id=user_data.id) \
                .filter(db.extract('year', RestaurantVisit.date_visited) == current_year) \
                .count()
            # Draw the number of unique restaurants on the PDF
            ReportGenerator.draw_text(pdf_canvas, f"{unique_restaurants_this_year} of those were unique.", 24, (68, 68, 68), 190)
                
            # Query to get the restaurant with the most visits and use highest average rating as a tiebreaker
            most_visited_restaurant_name = db.session.query(Restaurant.name) \
                .join(RestaurantVisit, RestaurantVisit.restaurant_id == Restaurant.id) \
                .filter_by(user_id=user_data.id) \
                .filter(extract('year', RestaurantVisit.date_visited) == current_year) \
                .group_by(Restaurant.id, Restaurant.name) \
                .order_by(func.count(RestaurantVisit.id).desc(), func.avg(RestaurantVisit.rating).desc()) \
                .first()
                
            # If there is a most visited restaurant
            if most_visited_restaurant_name is not None:
                # Get the name of the most visited restaurant
                most_visited_restaurant_name = most_visited_restaurant_name[0]
                # Draw the most visited restaurant on the PDF
                ReportGenerator.draw_text(pdf_canvas, f"{most_visited_restaurant_name} was your favourite restaurant.", 24, (68, 68, 68), 220)
         
            # Section 2 of the report
            # Draw the subheading for section 2 of the report
            ReportGenerator.draw_text(pdf_canvas, f"Your Favourite Foods", 32, (232, 93, 4), 270)
            
            # Empty list to store the categories
            categories = []

            # Query for the first category's name (which is the type of food) for each restaurant visit this year
            visits_current_year = RestaurantVisit.query.filter_by(user_id=user_data.id).filter(
                db.extract('year', RestaurantVisit.date_visited) == current_year
            ).all()

            # For each visit, extract the first category name and append it to the list
            for visit in visits_current_year:
                # Get restaurant object from the visit
                restaurant = visit.restaurant
                # Split the categories string into a list
                all_categories = restaurant.category.strip('[]').split(',')  # Remove brackets and split by comma
                # Check if the list is not empty
                if all_categories:
                    # Extract the name from the first category
                    first_category_name = all_categories[0].split(':')[0].strip("'\"")  # Extract the name from the first category
                    # Append the name to the list
                    categories.append(first_category_name)

            # Count the number of occurrences of each category
            category_counts = Counter(categories)
            # Get the top 5 most common categories
            top_categories = category_counts.most_common(5)
            # Extract names and frequencies for plotting
            categories, frequencies = zip(*top_categories)

            # Create a bar graph for the top 5 categories
            # Set the data and colours
            plt.bar(categories, frequencies, color=(244/255, 140/255, 6/255))
            # Get y-axis label
            plt.ylabel('Number of Visits')
            # Set x-axis label rotation and alignment
            plt.xticks(rotation=45, ha='right')
            # Set y-axis scale to integers
            plt.yticks(range(max(frequencies) + 1))
            # Set the layout to tight (reduced padding between elements)
            plt.tight_layout()

            # Save the plot as an image
            # Generate a random hex string for the image name
            random_hex = secrets.token_hex(8)
            # Get the image path
            image_path = os.path.join(app.root_path, f'static/reports/{random_hex}.png')
            # Save the plot as an image
            plt.savefig(image_path, format='png')
            # Clear the plot
            plt.clf()

            # Draw the image on the PDF
            pdf_canvas.drawImage(image_path, x=50, y=265, width=500, height=250)
            # Remove the image from the static folder
            os.remove(os.path.join(app.root_path, f'static/reports/{random_hex}.png'))
            
            # Section 3 of the report
            # Draw the subheading for section 3 of the report 
            ReportGenerator.draw_text(pdf_canvas, f"Your Culinary Habits", 32, (232, 93, 4), 560)
            
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
                # Get the restaurant ID from the visit
                restaurant_id = visit.restaurant_id
                # Query for the restaurant features of the current restaurant
                restaurant_feature = RestaurantFeature.query.filter_by(restaurant_id=restaurant_id).first()

                # Check the meal types for the current restaurant visit
                if restaurant_feature and restaurant_feature.breakfast:
                    # Increment the breakfast counter if the restaurant serves breakfast
                    breakfast_count += 1
                if restaurant_feature and restaurant_feature.lunch:
                    # Increment the lunch counter if the restaurant serves lunch
                    lunch_count += 1
                if restaurant_feature and restaurant_feature.dinner:
                    # Increment the dinner counter if the restaurant serves dinner
                    dinner_count += 1
                                
            # Create a pie chart for the meal types
            # Set the labels for the pie chart
            labels = ['Breakfast', 'Lunch', 'Dinner']
            # Set the sizes for the pie chart
            sizes = [breakfast_count, lunch_count, dinner_count]

            # Filter out labels with zero values
            # This is done to prevent the pie chart from displaying labels with zero values
            non_zero_labels = [label for label, size in zip(labels, sizes) if size > 0]
            non_zero_sizes = [size for size in sizes if size > 0]

            # Plotting the pie chart
            # Set the colours for each label on the pie chart
            rgb_colors = [(255/255, 186/255, 8/255), (244/255, 140/255, 6/255), (220/255, 47/255, 2/255)]
            # Plot the pie chart
            plt.pie(non_zero_sizes, labels=non_zero_labels, startangle=140, colors=rgb_colors)
            # Equal aspect ratio ensures that pie is drawn as a circle
            plt.axis('equal') 

            # Save the plot as an image
            # Generate a random hex string for the image name
            random_hex = secrets.token_hex(8)
            # Get the image path
            image_path = os.path.join(app.root_path, f'static/reports/{random_hex}.png')
            # Save the plot as an image
            plt.savefig(image_path, format='png')
            # Clear the plot
            plt.clf()
            
            # Draw the image on the PDF
            pdf_canvas.drawImage(image_path, x=-20, y=-20, width=350, height=250)
            # Remove the image from the static folder
            os.remove(os.path.join(app.root_path, f'static/reports/{random_hex}.png'))
            
            # Get the most common price category for the user's restaurant visits this year
            # Query for all restaurant visits of the user in the current year
            user_restaurant_visits = RestaurantVisit.query \
                .filter_by(user_id=user_data.id) \
                .filter(extract('year', RestaurantVisit.date_visited) == current_year) \
                .all()

            # Extract the price category for each visit
            price_categories = [visit.restaurant.price for visit in user_restaurant_visits]
            # Find the most common price category
            most_common_price_category = max(set(price_categories), key=price_categories.count)
    
            # Mapping for price categories to symbols
            price_mapping = {
                1: '$',
                2: '$$',
                3: '$$$',
                4: '$$$$'
            }
            # Map the most common price category to its symbol
            most_common_price_symbol = price_mapping.get(most_common_price_category, 'Unknown')
            
            # Draw the most common price category on the PDF
            ReportGenerator.draw_text(pdf_canvas, f"{most_common_price_symbol}", 100, (68, 68, 68), 680, 420)
            # Draw the caption for the most common price category on the PDF
            ReportGenerator.draw_text(pdf_canvas, f"Your Favourite Price Category", 18, (68, 68, 68), 720, 420)
        else:
            # If the user does not exist, draw an error message on the PDF
            ReportGenerator.draw_text(pdf_canvas, "There was an error generating your Culinary Mapped.", 24, (68, 68, 68))

        # Save the PDF file
        pdf_canvas.save()