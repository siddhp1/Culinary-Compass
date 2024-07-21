from culinarycompass import app, db

# Script to reset the database (development use)
with app.app_context():
    db.create_all()
