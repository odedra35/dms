from flask import render_template, request
from app import app
import requests
import ssl
import socket
import datetime

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Add your login validation logic here
        return render_template('domain.html')
    return render_template('login.html')

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