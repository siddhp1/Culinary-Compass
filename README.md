# Culinary Compass

A restaurant tracking and recommendation web application that helps users remember restaurant visits and find restaurant recommendations. Built with Flask and Bootstrap.

## Table of Contents

1. [About Culinary Compass](#about-culinary-compass)
2. [Usage](#usage)
3. [License](#license)

## About Culinary Compass

Culinary Compass lets users track their restaurant history by inputting the restaurant, the date they visited, and a rating out of 5 stars. The Google Places Autocomplete API is implemented to assist users in entering restaurants they have visited. The Foursquare Places API is then used to fetch data about the restaurant and build a user profile.

From there, recommendations can be made by selecting a location and search radius through an embedded Google Map. Restaurants that fall within the radius are compared to the user profile using a Scikit-Learn cosine similarity algorithm, which outputs a list of recommendations sorted in order of predicted preference.

Users can choose to generate an end-of-the-year report that contains data about their favorite restaurants, cuisines, price categories, and dining times. This PDF report is generated with ReportLab and Matplotlib and is emailed to the user.

User information is securely stored in a SQLite database, with bcrypt password hashing. Users are also able to securely reset passwords through email.

Culinary Compass is deployed on an Ubuntu virtual machine hosted on Azure, using Nginx as a web server to serve static files and act as a reverse proxy to Gunicorn, the WSGI server. The deployment is managed by Supervisor and secured with TLS encryption via Certbot.

## Usage

Visit the website at [Culinary Compass](http://www.culinarycompass.siddhp.com) and follow the tutorial at the bottom of the home page.

## License

This project is licensed under the GNU GPL 3.0 licence.
