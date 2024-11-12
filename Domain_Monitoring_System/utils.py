import json
import os

# Path to the JSON files
USERS_FILE = 'users.json'
DOMAINS_FILE ='domains.json'

def read_json_file(filename):
    """Helper function to read a JSON file and return its contents."""
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as file:
        return json.load(file)

def write_json_file(filename, data):
    """Helper function to write data to a JSON file."""
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def get_all_users():
    """Return a list of all users from users.json."""
    return read_json_file(USERS_FILE)

def get_user_by_email(email):
    """Return a user by their email."""
    users = get_all_users()
    for user in users:
        if user['email'] == email:
            return user
    return None

def get_user_domains(user_id):
    """Return all domains for a given user."""
    domains = read_json_file(DOMAINS_FILE)
    user_domains = [domain for domain in domains if domain['user_id'] == user_id]
    return user_domains

def save_user(user):
    """Save a new or updated user to users.json."""
    users = get_all_users()
    users.append(user)
    write_json_file(USERS_FILE, users)

def save_domain(domain):
    """Save a new or updated domain to domains.json."""
    domains = read_json_file(DOMAINS_FILE)
    domains.append(domain)
    write_json_file(DOMAINS_FILE, domains)
