import os
from app.db_config import get_database_uri
from dotenv import load_dotenv

# Cargar variables desde el archivo .env
load_dotenv()

class Config:
    # Configuración general desde variables de entorno
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback_secret_key')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Configuración de la base de datos PostgreSQL
    # Obtiene la URI de la función en db_config.py
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    
class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    # Puedes agregar una base de datos de prueba diferente aquí
    
# Diccionario de configuraciones
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Función para obtener la configuración según el entorno
def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    return config_dict.get(env, config_dict['default'])