from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient, errors
from werkzeug.security import generate_password_hash  # For password hashing
import os


# MongoDB URI
MONGO_URI = "mongodb://localhost:27017/"

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    # Test the connection by accessing the "admin" database (default MongoDB database)
    client.admin.command('ping')
    print("MongoDB connection successful!")
    db = client['stroke-sense']  # Your specific database
    users_collection = db['users']  # Your users collection
    feedback_collection = db['feedbacks']  # Your feedback collection
except errors.ConnectionError as e:  # Catch the connection error
    print(f"MongoDB connection failed: {e}")
    db = None





app = Flask(__name__)

app.secret_key = os.urandom(24) # Generates a random 24-byte string


# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Authentication routes
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if email already exists
        if users_collection.find_one({"email": email}):
            flash("Email already exists! Please try another.", "danger")  # Flash error message for email
            return redirect(url_for('register'))  # Redirect to the register form

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "danger")  # Flash error message for password mismatch
            return redirect(url_for('register'))  # Redirect to the register form

        # Hash password and store the user data in session
        session['full_name'] = full_name
        session['email'] = email
        session['password'] = generate_password_hash(password)

        # Redirect to another page (details page)
        return redirect(url_for('details'))  

    return render_template('register.html')


# Route to render the second form (data collection)
@app.route('/details', methods=['GET', 'POST'])
def details():
    # Ensure that user is registered and session has necessary info
    if 'email' not in session:
        return redirect(url_for('register'))  # Redirect if session is empty
    
    if request.method == 'POST':
        # Collect additional information from second form
        gender = "Female" if request.form.get('gender') == "0" else "Male"
        hypertension = bool(int(request.form.get('hypertension')))
        heart_disease = bool(int(request.form.get('heart_disease')))
        dob = request.form.get('dob')
        avg_glucose = float(request.form.get('avg_glucose_level'))
        bmi = float(request.form.get('bmi'))

        # Store the complete data in MongoDB
        users_collection.insert_one({
            "full_name": session['full_name'],
            "email": session['email'],
            "password": session['password'],  # You might want to hash this before using it
            "dob": dob,
            "gender": gender,
            "hypertension": hypertension,
            "heart_disease": heart_disease,
            "avg_glucose_level": avg_glucose,
            "bmi": bmi
        })

        # Clear session data after successful registration
        session.clear()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('login'))
    
    return render_template('data_collection.html')  # Show second form

# Dashboard/Main page
@app.route('/main')
def main():
    return render_template('main.html')

# Stroke prediction pages
@app.route('/stroke-input')
def stroke_input():
    return render_template('stroke_input.html')

@app.route('/stroke-prediction', methods=['POST'])
def stroke_prediction():
    # Dummy logic, replace with real model inference later
    age = request.form.get('age')
    gender = request.form.get('gender')
    # Add other fields and your model logic here
    prediction = "Low Risk"  # Placeholder
    return render_template('stroke_result.html', prediction=prediction)


# User and Admin profile
@app.route('/userprofile')
def user_profile():
    return render_template('userprofile.html')

@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

# Feedback view
@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

# Other pages
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/blog-details')
def blog_details():
    return render_template('blog_details.html')

@app.route('/elements')
def elements():
    return render_template('elements.html')



@app.route('/koa')
def koa():
    return render_template('comingsoon.html')  

@app.route('/skin-cancer')
def skin_cancer():
    return render_template('comingsoon.html')  

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
