
import requests
import ssl
import socket
import concurrent.futures
import json
import datetime

def check_liveness(domain_name):
    try:
        response = requests.get(f'https://{domain_name}')
        return response.status_code == 200
    except:
        return False
    
def get_ssl_info(domain_name):
    try:
        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(), server_hostname=domain_name) as s:
            s.connect((domain_name, 443))
            cert = s.getpeercert()
            expiration_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            issuer = cert['issuer'][0][0][1]
            return expiration_date, issuer
    except:
        return None, None

def scan_domains(domains):
    domains = domains if isinstance(domains, list) else [domains]
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        liveness_futures = {executor.submit(check_liveness, domain): domain for domain in domains}
        ssl_info_futures = {executor.submit(get_ssl_info, domain): domain for domain in domains}

        for future in concurrent.futures.as_completed(liveness_futures):
            domain = liveness_futures[future]
            is_live = future.result()
            ssl_expiration_date, ssl_issuer = ssl_info_futures[executor.submit(get_ssl_info, domain)].result()
            results.append({
                'domain': domain,
                'is_live': is_live,
                'ssl_expiration_date': ssl_expiration_date,
                'ssl_issuer': ssl_issuer
            })

    return results

def store_results(username, results):
    file_name = f'{username}_domains.json'
    with open(file_name, 'w') as file:
        json.dump(results, file, indent=4)

