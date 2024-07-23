from culinarycompass import app 
from culinarycompass import routes

# Only run app if run.py is called directly
if __name__ == '__main__':
    app.run(debug=False)

# Development
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=3000, debug=True)