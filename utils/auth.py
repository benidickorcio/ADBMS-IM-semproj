# login validation, session
from database import get_connection, get_current_user as db_get_user
import hashlib

_current_user = None


def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def login(username, password):
    """Try login. Return user dict on success or None on failure."""
    hashed = _hash_password(password)
    user = db_get_user(username, hashed)
    if user:
        global _current_user
        _current_user = user
        return user
    return None


def get_current_user():
    return _current_user


def set_current_user(user):
    global _current_user
    _current_user = user


def logout():
    global _current_user
    _current_user = None


def is_admin():
    user = get_current_user()
    return bool(user and user.get("role") == "ADMIN")


def is_cashier():
    user = get_current_user()
    return bool(user and user.get("role") == "CASHIER")
