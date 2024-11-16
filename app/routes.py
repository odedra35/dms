from flask import Flask, render_template, request, redirect, url_for, session
from dms.app.users.users_db_manager import add_user_to_db, check_user_in_db
from dms.app.loggers.app_logger import get_app_logger
import requests
import ssl
import socket
import datetime

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
            check_user_in_db(username, password)
            session["user"] = username
        except Exception as e:
            logger.error(f"Error on login: {e}")
            return {"status": "Error", "message": f"Error on login: {e}"}

    return render_template('domain.html')


@app.route('/domain', methods=['GET', 'POST'])
def domain():
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
    session.pop('username', None)  # Remove the username from the session
    return redirect(url_for('home'))


app.run(host="0.0.0.0", port=8080, debug=True)