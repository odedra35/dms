import os
import json

from collections import defaultdict
from loggers.app_logger import get_app_logger

logger = get_app_logger()
users_db = "users.json"
users_cache = defaultdict(dict)
index = 1

if not os.path.isfile(users_db):
    with open(users_db, "w") as f:
        f.write("{}")


def _user_already_exists(user_name: str) -> tuple[bool, str]:
    """Checks if username is found inside users.json file.

    :param user_name: string of username
    :return: bool - False is user not found in file
    """
    with open(users_db, "r") as f:
        users = json.load(f)

    for user, user_details in users.items():
        if user_details["username"] == user_name:
            return True, user_details["password"]
    return False, ""


def add_user_to_db(user_name: str, password: str) -> bool:
    """Add new user to user_db file."""
    if _user_already_exists(user_name)[0]:
        logger.error(f"user {user_name!r} already exists in users.json.")
        return False
    try:
        idx = globals()["index"]
        users_cache[f"User{idx}"] = {"username": user_name, "password": password}
        globals()["index"] += 1
    except Exception as e:
        logger.error(f"{e}")

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
    if user_password != password:
        return False
    return True


def remove_user_from_db(username: str) -> bool:
    """Remove a user from the users database (users.json)."""
    try:
        with open(users_db, 'r') as f:
            users = json.load(f)

        # אם המשתמש קיים תמחק אותו
        if username in users:
            del users[username]

            # תעדכן את הרשימה
            with open(users_db, 'w') as f:
                json.dump(users, f)

            logger.info(f"User {username} deleted successfully.")
            return True
        else:
            return False  # User not found
    except Exception as e:
        logger.error(f"Error removing user {username}: {e}")
        return False