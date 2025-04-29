from flask import Flask
from werkzeug.security import generate_password_hash
import psycopg2
import sys
from datetime import datetime

# Configuración de la base de datos - actualiza con tus credenciales
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "fantasydb"
DB_USER = "fantasyuser"
DB_PASSWORD = "password123"

def create_user(username, email, password, nombre_completo=None):
    """
    Crea un nuevo usuario en la tabla 'usuarios'
    
    Args:
        username (str): Nombre de usuario único
        email (str): Correo electrónico único
        password (str): Contraseña del usuario (se hasheará antes de almacenarla)
        nombre_completo (str, optional): Nombre completo del usuario
    
    Returns:
        tuple: (éxito (bool), mensaje (str))
    """
    # Generar hash de la contraseña
    password_hash = generate_password_hash(password)
    
    # Obtener la fecha y hora actual
    now = datetime.now()
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        # Crear un cursor
        cursor = conn.cursor()
        
        # Verificar si el usuario ya existe
        cursor.execute("SELECT username FROM usuarios WHERE username = %s", (username,))
        if cursor.fetchone():
            conn.close()
            return False, f"El usuario '{username}' ya existe"
        
        # Verificar si el email ya existe
        cursor.execute("SELECT email FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            conn.close()
            return False, f"El email '{email}' ya está registrado"
        
        # Insertar el nuevo usuario
        cursor.execute("""
            INSERT INTO usuarios (username, email, password_hash, nombre_completo, fecha_creacion, activo)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (username, email, password_hash, nombre_completo, now, True))
        
        # Obtener el ID del usuario creado
        user_id = cursor.fetchone()[0]
        
        # Confirmar la transacción
        conn.commit()
        
        # Cerrar la conexión
        cursor.close()
        conn.close()
        
        return True, f"Usuario '{username}' creado exitosamente con ID: {user_id}"
        
    except Exception as e:
        # En caso de error, revertir la transacción
        if 'conn' in locals() and conn:
            conn.rollback()
            conn.close()
        return False, f"Error al crear el usuario: {str(e)}"

def verify_table_exists():
    """Verifica si la tabla 'usuarios' existe, y la crea si no existe"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'usuarios'
            );
        """)
        
        if not cursor.fetchone()[0]:
            print("La tabla 'usuarios' no existe. Creándola...")
            
            # Crear la tabla
            cursor.execute("""
                CREATE TABLE usuarios (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(128) NOT NULL,
                    nombre_completo VARCHAR(100),
                    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    ultimo_login TIMESTAMP WITH TIME ZONE,
                    activo BOOLEAN DEFAULT TRUE
                );
            """)
            
            conn.commit()
            print("Tabla 'usuarios' creada exitosamente.")
        else:
            print("La tabla 'usuarios' ya existe.")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al verificar/crear la tabla: {e}")
        return False

def main():
    # Verificar que la tabla existe
    if not verify_table_exists():
        print("No se pudo verificar o crear la tabla 'usuarios'. Abortando.")
        return
    
    # Solicitar datos al usuario
    if len(sys.argv) >= 4:
        # Datos proporcionados como argumentos de línea de comandos
        username = sys.argv[1]
        email = sys.argv[2]
        password = sys.argv[3]
        nombre_completo = sys.argv[4] if len(sys.argv) > 4 else None
    else:
        # Solicitar datos interactivamente
        username = input("Nombre de usuario: ")
        email = input("Correo electrónico: ")
        password = input("Contraseña: ")
        nombre_completo = input("Nombre completo (opcional, presiona Enter para omitir): ") or None
    
    # Crear el usuario
    success, message = create_user(username, email, password, nombre_completo)
    print(message)

if __name__ == "__main__":
    main()