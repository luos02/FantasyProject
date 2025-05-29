from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from app.controllers.auth_controller import authenticate_user, register_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    """Login route - handles both GET and POST requests"""
    # If user is already logged in, redirect to home
    if 'user_id' in session:
        return redirect(url_for('content.home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('auth.login'))
        
        user = authenticate_user(username, password)
        
        if user:
            # Set session variables
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.roles
            session.permanent = True  # Make session permanent
            
            # Redirect to originally requested URL or home
            next_url = session.pop('next_url', None)
            if next_url:
                return redirect(next_url)
            return redirect(url_for('content.home'))
        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('auth.login'))
    
    return render_template('Login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration route - only accessible if not logged in"""
    # If user is already logged in, redirect to home
    if 'user_id' in session:
        return redirect(url_for('content.home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        nombre_completo = request.form.get('nombre_completo')
        
        if not username or not email or not password:
            flash('All required fields must be filled', 'error')
            return redirect(url_for('auth.register'))
        
        user, message = register_user(username, email, password, nombre_completo)
        
        if user:
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """Logout route - clears session and redirects to login"""
    # Clear all session data
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.before_app_request
def check_session_validity():
    """
    Check session validity before each request
    This runs before every request in the app
    """
    # Skip validation for static files and auth routes
    if (request.endpoint and 
        (request.endpoint.startswith('static') or 
         request.endpoint.startswith('auth.'))):
        return
    
    # If user claims to be logged in, verify the user still exists and is active
    if 'user_id' in session:
        from app.models.models import UserModel
        user = UserModel.query.get(session['user_id'])
        
        # If user doesn't exist or is inactive, clear session
        if not user or not user.activo:
            session.clear()
            flash('Your session has expired. Please log in again.', 'error')
            return redirect(url_for('auth.login'))