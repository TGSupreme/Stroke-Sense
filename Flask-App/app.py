from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient, errors
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing
from datetime import timedelta, datetime
import numpy as np
import pickle
import os


# <------------------------model ------------------------>
with open('stroke-prediction.pkl', 'rb') as model_file:
    model = pickle.load(model_file)
# <------------------------model ------------------------>


# <------------------------MongoDB ------------------------>
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

#<------------------------MongoDB------------------------>




app = Flask(__name__)

app.secret_key = os.urandom(24) # Generates a random 24-byte string
app.permanent_session_lifetime = timedelta(days=7)

def calculate_age(dob_str):
    if not dob_str:
        return "N/A"
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
        today = datetime.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except:
        return "Invalid DOB"
    


# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')  

        user = users_collection.find_one({"email": email})

        if user:
            if check_password_hash(user['password'], password):
                session['user_id'] = str(user['_id'])
                session['email'] = user['email']

                # Handle "Remember Me"
                if remember == "on":
                    session.permanent = True
                else:
                    session.permanent = False

                flash("Login successful!", "success")
                return redirect(url_for('home'))
            else:
                flash("Invalid password. Please try again.", "danger")
        else:
            flash("Email not found. Please check your credentials.", "danger")
    
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

# Route to handle prediction
@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Get form inputs
        gender = request.form['gender']
        age = request.form['age']
        hypertension = request.form['hypertension']
        heart_disease = request.form['heart_disease']
        glucose = request.form['avg_glucose_level']
        bmi = request.form['bmi']

        # Prepare input for model
        input_features = np.array([[float(gender), float(age), float(hypertension),
                                    float(heart_disease), float(glucose), float(bmi)]])

        # Predict using the model
        prediction = model.predict(input_features)

        # Interpret result
        result = "The person is likely to have a stroke." if prediction[0] == 1 else "The person is unlikely to have a stroke."

        # Render result page
        return render_template('stroke_result.html', prediction=result)


# User and Admin profile
@app.route('/userprofile')
def user_profile():
    # Ensure user is logged in
    if 'email' not in session:
        flash("Please log in to view your profile.", "warning")
        return redirect(url_for('login'))

    # Fetch user details from MongoDB
    user = users_collection.find_one({"email": session['email']})

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('home'))

    # Convert ObjectId to string and prepare user dict
    user_profile_data = {
        "name": user.get("full_name", "N/A"),
        "email": user.get("email", "N/A"),
        "gender": user.get("gender", "N/A"),
        "hypertension": "Yes" if user.get("hypertension") else "No",
        "heart_disease": "Yes" if user.get("heart_disease") else "No",
        "avg_glucose_level": user.get("avg_glucose_level", "N/A"),
        "bmi": user.get("bmi", "N/A"),
        'age': calculate_age(user.get('dob'))
    }

    return render_template("userprofile.html", user=user_profile_data)

@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
       return render_template('editprofile.html')  # Render the edit profile form with current user data


@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

# Feedback view
@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/koa')
def koa():
    return render_template('comingsoon.html')  

@app.route('/skin-cancer')
def skin_cancer():
    return render_template('comingsoon.html')  

# Logout Route
@app.route('/home')
def logout():
    # Clear all session data
    session.clear()

    flash("You have been logged out.", "info")
    return redirect(url_for('home'))  # You can also redirect to 'home' if preferred


@app.route('/tp')
def tp():
    return render_template('tp.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
