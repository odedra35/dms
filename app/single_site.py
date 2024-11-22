import requests
import ssl
import socket
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_site_status(url):
    try:
        response = requests.get(url, timeout=0.5)
        if response.status_code == 200:
            return 'alive'
        else:
            return f'status code {response.status_code}'
    except requests.exceptions.RequestException:
        return 'dead'

def check_certificate(url):
    try:
        # Remove "https://", "http://", "www." from the URL if present
        hostname = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
        
        # Establish a secure connection to fetch the SSL certificate
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
        # Get the certificate's expiration date
        expiry_date_str = cert['notAfter']
        expiry_date = datetime.strptime(expiry_date_str, "%b %d %H:%M:%S %Y %Z")
        
        # Get the issuer's name
        issuer = dict(x[0] for x in cert['issuer'])
        issuer_name = issuer.get('organizationName', 'Unknown issuer')
        
        # Convert expiration date to a readable string format
        expiry_date_formatted = expiry_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if the certificate is expired
        if expiry_date < datetime.utcnow():
            return 'expired', expiry_date_formatted, issuer_name
        else:
            return 'valid', expiry_date_formatted, issuer_name
    except Exception as e:
        return 'failed', str(e), 'Unknown issuer'

def check_site_and_certificate(domain):
    with ThreadPoolExecutor() as executor:
        future_status = executor.submit(check_site_status, f"https://{domain}")
        future_certificate = executor.submit(check_certificate, domain)
        
        status = ''
        cert_status = ''
        expiry_date = ''
        issuer_name = ''
        
        for future in as_completed([future_status, future_certificate]):
            if future == future_status:
                status = future.result()
            else:
                cert_status, expiry_date, issuer_name = future.result()
                
    return status, cert_status, expiry_date, issuer_name

def append_to_json_file(filename, data):
    try:
        with open(filename, 'r') as json_file:
            existing_data = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.append(data)

    with open(filename, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)

# Example usage
username = input("Enter your username: ")
domain = input("Pick a domain to check SSL: ")

status, cert_status, expiry_date, issuer_name = check_site_and_certificate(domain)

data = {
    "domain": domain,
    "status": status,
    "ssl_certificate": {
        "status": cert_status,
        "expiry_date": expiry_date,
        "issuer": issuer_name
    }
}

filename = f"{username}_domains.json"
append_to_json_file(filename, data)

print(f"The site {domain} is {status}.")
print(f"The SSL certificate for {domain} is {cert_status}, issued by {issuer_name}, and expires on {expiry_date}.")
print(f"Results saved to {filename}")
