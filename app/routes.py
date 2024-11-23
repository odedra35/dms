from flask import Flask, render_template, request, redirect, url_for, session
from users.users_db_manager import add_user_to_db, authenticate_user
from loggers.app_logger import get_app_logger
import requests
import ssl
import socket
import datetime
import json

logger = get_app_logger()
person_index: int = 1

app = Flask(__name__)
# required for session stored user data
app.secret_key = "MyVerySecretKeyHere!111"


@app.route('/')
def home():
    return render_template("index.html")


@app.route("/<filename>", methods=["GET"])
def get_file(filename: str):
    return app.send_static_file(filename)


@app.route("/register", methods=['POST'])
def register_user():
    if request.method == "POST":
        username = request.json['username']
        password = request.json['password']

        if not username.strip() or not password.strip():
            return {"status": "Error", "message": "Username and Password can't be empty."}

        if len(username) > 50 or len(password) > 20:
            return {"status": "Error", "message": "Please limit your username to 50 and password to 20 characters."}

        # Feel free to add username and password validations here.

        logger.info(f"Performing register for user {username!r} into DB...")
        try:
            add_user_to_db(username, password)
        except Exception as e:
            return {"status": "Error", "message": f"Error on login: {e}"}

        return {"status": "Pass", "message": ""}


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']

        if not username.strip() or not password.strip():
            logger.error("Username and Password can't be empty.")
            return {"status": "Error", "message": "Username and Password can't be empty."}

        logger.info(f"Performing login for user {username!r}...")
        try:
            authenticate_user(username, password)
            session["user"] = username
        except Exception as e:
            logger.error(f"Error on login: {e}")
            return {"status": "Error", "message": f"Error on login: {e}"}

        return {"status": "Pass", "message": ""}
    return redirect(url_for("home"))


@app.route('/domain', methods=['GET', 'POST'])
def domain():
    if 'user' not in session:
        return redirect(url_for('home'))  # Redirect to the home page if user is not logged in

    if request.method == 'POST':
        domain_name = request.form['domain']

        # Check if the domain is up
        try:
            response = requests.get(f'https://{domain_name}')
            domain_up = response.status_code == 200
        except:
            domain_up = False
        
        # Check if the SSL certificate is valid
        try:
            context = ssl.create_default_context()
            with context.wrap_socket(socket.socket(), server_hostname=domain_name) as s:
                s.connect((domain_name, 443))
                ssl_valid = True
        except ssl.CertificateError:
            ssl_valid = False
        
        # Check if the domain is expired
        try:
            domain_info = socket.gethostbyname_ex(domain_name)
            domain_expiration_date = domain_info[2][0]
            domain_expired = datetime.datetime.strptime(domain_expiration_date, '%Y-%m-%d') < datetime.datetime.now()
        except:
            domain_expired = False
        
        return f'Domain: {domain_name} is up: {domain_up}, SSL is valid: {ssl_valid}, Expired: {domain_expired}'
    return render_template('domain.html')


@app.route('/logout')
def logout():
    session.pop("user", None)  # Remove the username from the session
    return redirect(url_for('home'))

@app.route('/users', methods=['GET'])
def view_users():
    #קורא את המשתמשים מקובץ המשתמשים
    with open('users.json', 'r') as f:
        users = json.load(f)
    
    return render_template("users_list.html", users=users)

@app.route('/delete_user/<username>', methods=['POST'])
def delete_user(username):
    # טוען את קובץ המשתמשים
    with open('users.json', 'r') as f:
        users = json.load(f)
    
    # אם המשתמש קיים במערך, מוחק אותו
    if username in users:
        del users[username]
        
        # שומר את הקובץ לאחר המחיקה
        with open('users.json', 'w') as f:
            json.dump(users, f)
        
        logger.info(f"User {username} has been deleted.")
    else:
        logger.warning(f"User {username} not found.")
    
    # אחרי המחיקה, חוזר לדף המשתמשים
    return redirect(url_for('view_users'))

@app.route('/change_password/<username>', methods=['GET', 'POST'])
def change_password(username):
    if request.method == 'GET':
        # מציג את הדף של שינוי הסיסמה
        return render_template('change_password.html', username=username)
    
    if request.method == 'POST':
        new_password = request.form['new_password']
        
        # טוען את קובץ המשתמשים
        with open('users.json', 'r') as f:
            users = json.load(f)
        
        # בודק אם המשתמש קיים
        if username in users:
            # משנה את הסיסמה של המשתמש
            users[username]['password'] = new_password
            
            # שומר את הקובץ עם הסיסמה החדשה
            with open('users.json', 'w') as f:
                json.dump(users, f)
            
            logger.info(f"Password for {username} has been changed.")
            return redirect(url_for('view_users'))
        else:
            logger.warning(f"User {username} not found.")
            return redirect(url_for('view_users'))



app.run(host="0.0.0.0", port=8080, debug=True)
