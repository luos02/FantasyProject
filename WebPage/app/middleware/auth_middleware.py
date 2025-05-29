from functools import wraps
from flask import session, redirect, url_for, request, abort
from app.models.models import UserModel

def login_required(f):
    """
    Decorator to require login for accessing any route
    Redirects to login page if user is not authenticated
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if 'user_id' not in session:
            # Save the original URL they were trying to access
            session['next_url'] = request.url
            return redirect(url_for('auth.login'))
        
        # Verify user still exists and is active
        user = UserModel.query.get(session['user_id'])
        if not user or not user.activo:
            # Clear invalid session
            session.clear()
            session['next_url'] = request.url
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_roles):
    """
    Decorator to require specific roles for accessing routes
    Args:
        required_roles: List of roles allowed (e.g., ['admin', 'analyst'])
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # First check if user is logged in
            if 'user_id' not in session:
                session['next_url'] = request.url
                return redirect(url_for('auth.login'))
            
            # Get user role from session or database
            user_role = session.get('user_role')
            if not user_role:
                # Get role from database if not in session
                user = UserModel.query.get(session['user_id'])
                if user:
                    user_role = user.roles
                    session['user_role'] = user_role
                else:
                    session.clear()
                    return redirect(url_for('auth.login'))
            
            # Check if user has required role
            if user_role not in required_roles:
                abort(403)  # Forbidden
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """
    Shortcut decorator for admin-only routes
    """
    return role_required(['admin'])(f)

def analyst_or_admin_required(f):
    """
    Shortcut decorator for analyst and admin routes
    """
    return role_required(['admin', 'analyst'])(f)