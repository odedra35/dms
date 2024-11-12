from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from services.user_service import register_user, verify_user
from config import Config

# Initialize the Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Load the user from the user data (JSON "db")
@login_manager.user_loader
def load_user(user_id):
    return user_id

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if verify_user(username, password):
            login_user(username)
            return redirect(url_for('dashboard'))
        return 'Invalid credentials', 401

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if register_user(username, password):
            return redirect(url_for('login'))
        return 'User already exists', 400

    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user}! This is your dashboard.'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)
