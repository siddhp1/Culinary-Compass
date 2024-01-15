# Import app instance from culinarycompass package
from culinarycompass import app 
# Import routes from culinarycompass package
from culinarycompass import routes

# Only run app if run.py is called directly
if __name__ == '__main__':
    # Run app in debug mode (preproduction)
    app.run(debug=True)