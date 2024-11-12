# services/user_service.py

import json
from werkzeug.security import generate_password_hash, check_password_hash

USER_DB_FILE = 'users.json'

def load_users():
    """Load user data from the JSON file."""
    try:
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    """Save the user data back to the JSON file."""
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f)

def register_user(username, password):
    """Register a new user."""
    users = load_users()
    
    if username in users:
        return False  # User already exists

    password_hash = generate_password_hash(password)
    users[username] = {'password': password_hash}
    save_users(users)
    return True

def verify_user(username, password):
    """Verify user credentials."""
    users = load_users()

    if username not in users:
        return False  # User does not exist

    password_hash = users[username]['password']
    return check_password_hash(password_hash, password)
