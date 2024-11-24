import time

from flask import Flask, render_template, redirect, request, url_for, session

from users.users import add_user_to_db, authenticate_user, check_user_in_db
from domains.domains import check_ssl_and_status, update_user_domains_db, check_ssl_and_status_bulk

app = Flask(__name__)
# todo remove before upload
app.secret_key = 'LAnNDiKNAiD1238785ddjfdgroasdflknq10)/*|*\-l34ne134190u23ie-039i-e4091i(*_(&U1341/3.,4e,;;'

URLS_LIMIT = 100
TIME_LIMIT = 5
ERROR_LIMIT_PCT = 2

@app.route('/')
def home():
    # Check if the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    user = session.get("username")

    return render_template('home.html', username=user)


@app.route('/add_domain', methods=['POST'])
def check_single():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = session.get("username")

    if request.method == 'POST':
        url = request.form['single-url']

        start = time.time()
        # Perform singly url check
        answer = check_ssl_and_status(url)
        err = update_user_domains_db(session.get("username"), answer)

        timed = time.time() - start
        print(f"{timed=} seconds")
        return render_template('home.html', username=user, answer=answer, timed=timed, error=err)
    return render_template('home.html')


def error_check(answer_list) -> float:
    """Check if URL(s) with 'N/A' status request exceeds limit."""
    if not answer_list:
        return 0

    errors = list(filter(lambda x: x['status'] == "N/A" and x['ssl_expiration'] == 'N/A', answer_list))
    return len(errors) / len(answer_list) * 100


@app.route('/bulk_upload', methods=['POST'])
def bulk_upload():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = session.get("username")

    if "file-upload" not in request.files:
        return render_template("home.html")

    if request.method == 'POST':
        url_file = request.files['file-upload']

        # Only accept .txt files
        if not url_file.filename.endswith(".txt"):
            return render_template("home.html", username=user, error="File type should be '.txt'")

        start = time.time()
        answer_list = check_ssl_and_status_bulk(url_file.stream.read(), URLS_LIMIT)

        # File is empty or too large (>100 urls per user)
        if not answer_list:
            render_template('home.html', username=user, error=f"file is empty or exceeded urls limit - {URLS_LIMIT}")

        # Save domains into user db
        err = update_user_domains_db(user, answer_list)
        if err:
            render_template('home.html', username=user, error=f"General error - {err}")

        # Operation time limit calculation
        timed = round(time.time() - start, 2)

        # Status and SSL Error limit calculation
        error_pct = error_check(answer_list)

        print(f"{error_pct=}%")
        if error_pct > ERROR_LIMIT_PCT:
            return render_template("home.html", username=user, timed=timed, answer_list=answer_list, error=f"URL status and SSL error ({error_pct}%) limit ({ERROR_LIMIT_PCT}%) was exceeded!")

        print(f"{timed=}")
        if timed > TIME_LIMIT:
            return render_template("home.html", username=user, timed=timed, answer_list=answer_list, error=f"Operation time limit ({TIME_LIMIT} seconds) was exceeded!")

        return render_template('home.html', username=user, answer_list=answer_list, timed=timed)
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data (username and password)
        username = request.form['username']
        password = request.form['password']

        # Check if user exists and the password is correct
        if authenticate_user(username, password):
            session['username'] = username  # Store username in session
            return redirect(url_for('home'))  # Redirect to home page if login is successful
        else:
            return render_template('login.html', error='Invalid credentials')  # Show error if login fails
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        db_user, db_password = check_user_in_db(username)
        # Check if username already exists
        if db_user:
            return render_template('register.html', error='Username already taken')

        # Check if passwords match
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        # Register the user
        add_user_to_db(username, password)
        return redirect(url_for('login'))  # Redirect to login page after successful registration

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the user from the session
    return redirect(url_for('login'))  # Redirect to login page


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
