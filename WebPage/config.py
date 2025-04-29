from app.db_config import get_database_uri

class Config:
    # Configuración general
    SECRET_KEY = 'tu_clave_secreta_aqui'
    DEBUG = True
    
    # Configuración de la base de datos PostgreSQL
    # Obtiene la URI de la función en db_config.py
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False