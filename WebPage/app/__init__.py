from flask import Flask
from app.models.models import db
import psycopg2
import traceback

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
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
    
    app.register_blueprint(config_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(content_bp)
    
    return app