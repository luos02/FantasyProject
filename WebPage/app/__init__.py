# app/__init__.py - Updated with session configuration
from flask import Flask
from app.models.models import db
import traceback
from config import get_config
import os
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.config.from_object(get_config())
    
    # Session configuration for security
    app.config['SESSION_COOKIE_SECURE'] = True if os.environ.get('FLASK_ENV') == 'production' else False
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookies
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)  # Session expires after 8 hours
    
    # Initialize database
    db.init_app(app)
    
    # Create all tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
            traceback.print_exc()
            # Don't fail completely, allow app to continue
    
    # Import and register blueprints
    from app.controllers.user_controller import user_bp as config_bp
    from app.views.auth_views import auth_bp
    from app.views.content_views import content_bp
    from app.views.prophet_views import prophet_bp
    
    app.register_blueprint(config_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(prophet_bp)
    
    # Ensure necessary directories exist
    _ensure_directories(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Add security headers
    _add_security_headers(app)
    
    return app

def _ensure_directories(app):
    """
    Ensure necessary directories for the application exist
    """
    # Directory for file uploads
    uploads_dir = os.path.join(app.root_path, 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        
    # Directory for saved models
    models_dir = os.path.join(app.root_path, 'models')
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

def _register_error_handlers(app):
    """
    Register custom error handlers
    """
    @app.errorhandler(401)
    def unauthorized(error):
        from flask import render_template, redirect, url_for
        return redirect(url_for('auth.login'))
    
    @app.errorhandler(403)
    def forbidden(error):
        from flask import render_template
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500

def _add_security_headers(app):
    """
    Add security headers to all responses
    """
    @app.after_request
    def add_security_headers(response):
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Add Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self';"
        )
        
        return response