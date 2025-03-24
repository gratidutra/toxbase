from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user, login_required

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return abort(403)  # Retorna erro "403 Forbidden"
        return f(*args, **kwargs)
    return wrap
