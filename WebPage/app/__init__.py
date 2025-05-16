from flask import Flask
from app.models.models import db
import traceback
from config import get_config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    app.config.from_object(get_config())
    
    # Inicializar la base de datos
    db.init_app(app)
    
    # Crear todas las tablas si no existen
    with app.app_context():
        try:
            db.create_all()
            print("Base de datos inicializada correctamente")
        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")
            traceback.print_exc()
            # No fallar completamente, permitir que la aplicación continúe
    
    from app.controllers.user_controller import user_bp as config_bp
    from app.views.auth_views import auth_bp
    from app.views.content_views import content_bp
    from app.views.prophet_views import prophet_bp  # Nuevo blueprint para Prophet
    
    app.register_blueprint(config_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(prophet_bp)  # Registrar el nuevo blueprint
    
    # Asegurar que los directorios necesarios existen
    _ensure_directories(app)
    
    return app

def _ensure_directories(app):
    """
    Asegura que los directorios necesarios para la aplicación existen
    """
    # Directorio para cargas de archivos
    uploads_dir = os.path.join(app.root_path, 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        
    # Directorio para modelos guardados
    models_dir = os.path.join(app.root_path, 'models')
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)