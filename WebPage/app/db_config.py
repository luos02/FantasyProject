"""
Archivo de configuración específico para la base de datos.
Permite separar la configuración de la base de datos del resto de la configuración.
"""
import os
from dotenv import load_dotenv

# Cargar variables desde el archivo .env
load_dotenv()

# Obtener configuración de la base de datos desde variables de entorno
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "fantasydb")
DB_USER = os.environ.get("DB_USER", "fantasyuser")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password123")

# Función para generar la URI de conexión
def get_database_uri():
    """
    Crea una URI de conexión segura para PostgreSQL
    Evita caracteres especiales y problemas de codificación
    """
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"