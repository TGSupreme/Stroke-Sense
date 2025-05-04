from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Authentication routes
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

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

@app.route('/data-collection')
def data_collection():
    return render_template('data_collection.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
