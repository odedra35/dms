import os
import json

from collections import defaultdict
from dms.app.loggers.app_logger import get_app_logger

logger = get_app_logger()
users_db = "users/users.json"
users_cache = defaultdict(dict)

if not os.path.isfile(users_db):
    with open(users_db, "w") as f:
        f.write("{}")


def _user_already_exists(user_name: str) -> tuple[bool, str]:
    """Checks if username is found inside users.json file.

    :param user_name: string of username
    :return: bool - False is user not found in file
    """
    with open(users_db, "r") as fr:
        users = json.load(fr)

    if not user_name.strip():
        return False, ""

    if f"{user_name}" not in users:
        return False, ""

    return True, users[f"{user_name}"]["password"]


def add_user_to_db(user_name: str, password: str) -> bool:
    """Add new user to user_db file.

    :return: False if user already in db, else True
    """
    if _user_already_exists(user_name)[0]:
        logger.error(f"user {user_name!r} already exists in users.json.")
        return False

    users_cache.setdefault(f"{user_name}", {"username": user_name, "password": password})
    with open(users_db, "w") as fw:
        json.dump(users_cache, fw)
    return True


def authenticate_user(user_name: str, password: str) -> bool:
    """Authenticate user and password in users file.

    :return: True - if user found in db and password is correct
    """
    user_found, user_password = _user_already_exists(user_name)
    if not user_found:
        return False
    return user_password == password


def check_user_in_db(username: str) -> tuple[str, str]:
    """Returns username and password if user found in db."""
    # db is empty
    if not users_cache:
        return "", ""

    found, password = _user_already_exists(username)
    return ("", "") if not found else (username, password)
