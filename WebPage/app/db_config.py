"""
Archivo de configuración específico para la base de datos.
Permite separar la configuración de la base de datos del resto de la configuración.
"""

# Configuración de la base de datos
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "fantasydb"
DB_USER = "fantasyuser"
DB_PASSWORD = "password123"

# Función para generar la URI de conexión
def get_database_uri():
    """
    Crea una URI de conexión segura para PostgreSQL
    Evita caracteres especiales y problemas de codificación
    """
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"