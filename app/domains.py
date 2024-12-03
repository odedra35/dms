import json
import os.path
import ssl
import socket
from typing import Union
import requests
from concurrent import futures


def _get_ssl_expiration_date(hostname: str) -> tuple:
    """Get the SSL certificate expiration date."""
    try:

        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        # Extract info from cert
        expiration_date = cert['notAfter']
        issuer = cert.get("issuer", "Unknown")

        # Focus issuer name (or Unknown)
        issuer = issuer[2][0][1] if issuer != "Unknown" else issuer
    except ssl.SSLCertVerificationError:
        return "N/A", "N/A"
    return expiration_date, issuer


def _get_response_code(url: str) -> int:
    """Get the HTTP response code using aiohttp."""
    response = requests.get(url, timeout=3.5)
    return response.status_code


def check_ssl_and_status_bulk(urls, url_limit_per_user: int = 100) -> list:
    """Checks multiple urls at once based on given file."""

    # Remove duplicated urls
    if not isinstance(urls, list):
        urls = list(set(urls.splitlines()))

    if not urls or len(urls) > url_limit_per_user:
        return []

    # Execute status and ssl details check in parallel
    with futures.ThreadPoolExecutor(max_workers=url_limit_per_user) as executer:
        future = list(executer.map(_check_ssl_and_status,urls))
    return future


def _check_ssl_and_status(url: Union[str, bytes]) -> dict:
    """Check SSL expiration and response code concurrently."""
    url = url.decode() if not isinstance(url, str) else url
    hostname = url.split('//')[-1].split('/')[0]

    try:
        # Check response code and ssl details
        rc = _get_response_code(url)
        expiration_date, cert_issuer = _get_ssl_expiration_date(hostname)

        # create a response dict
        response = {
            "domain": url,
            "status": "Pending" if rc != 200 else "Alive",
            "ssl_expiration": f"{expiration_date}",
            "ssl_issuer": f"common name - {cert_issuer!r}",
        }
    except requests.exceptions.RequestException:
        return {
            "domain": url,
            "status": "N/A",
            "ssl_expiration": "N/A",
            "ssl_issuer": "N/A",
        }
    return response


def _create_user_domains_db(file_name: str) -> None:
    """Create a username_domains.json for given username if not already exists."""
    with open(file_name, "w") as fw:
        fw.write("{}")


def update_user_domains_db(username: str, domains: Union[dict, list[dict]]) -> str:
    """Updates user_domains.json with domain result.

    :param username: string representing the username
    :param domains: dict with domain, status, ssl_expiration, ssl_issuer
    """

    file_name = f"domains/{username}_domains.json"
    domains = domains if isinstance(domains, list) else [domains]
    print(domains)

    try:
        if not os.path.isfile(file_name):
            print(f"creating file {file_name!r}")
            _create_user_domains_db(file_name)

        write_domains = {}
        for domain in domains:
            print(f"domain: {domain}")

            # domain is empty = skip
            new_domain = domain.get("domain", "")
            if not new_domain:
                continue

            # Create temp dict with domain name as key
            write_domains.setdefault(new_domain, domain)

        # Read current state of known domains
        print(f"Loading file: {file_name}")
        with open(file_name, "r") as fr:
            current_domains = dict(json.load(fr))

        # Overwrite with updated domain info OR concat new domains
        current_domains.update(write_domains)

        # Write updated domain information into db
        print(f"Writing to file {file_name!r} info:\n{current_domains}")
        print(f"{os.path.isfile(file_name)=}")
        with open(file_name, "w") as fw:
            json.dump(current_domains, fw)

    except Exception as e:
        print(f"{e}")
        return f"{e}"
    return ""


def error_check(answer_list: list) -> float:
    """Check if URL(s) with 'N/A' status request exceeds limit."""
    if not answer_list:
        return 0

    errors = list(filter(lambda x: x['status'] == "N/A" and x['ssl_expiration'] == 'N/A', answer_list))
    return len(errors) / len(answer_list) * 100
