import psycopg2
import sys

def test_connection(host, port, dbname, user, password):
    """Prueba la conexión a la base de datos PostgreSQL e imprime información detallada"""
    connection_string = f"host={host} port={port} dbname={dbname} user={user} password={password}"
    
    print(f"Intentando conectar a PostgreSQL con: host={host}, port={port}, dbname={dbname}, user={user}")
    
    try:
        # Intentar conexión
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        
        # Verificar la conexión
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        db_version = cursor.fetchone()
        
        print(f"Conexión exitosa a PostgreSQL.")
        print(f"Versión de PostgreSQL: {db_version[0]}")
        
        # Probar listar tablas
        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print("\nTablas en la base de datos:")
        for table in tables:
            print(f"- {table[0]}")
        
        # Si existe la tabla 'users', verificar su estructura
        if ('users',) in tables:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users';
            """)
            
            columns = cursor.fetchall()
            print("\nColumnas en la tabla 'users':")
            for column in columns:
                print(f"- {column[0]} ({column[1]})")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error al conectar a PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    # Valores por defecto
    host = "localhost"
    port = "5432"
    dbname = "fantasydb"
    user = "fantasyuser"
    password = "password123"
    
    # Permitir sobreescribir desde línea de comandos
    if len(sys.argv) >= 6:
        host = sys.argv[1]
        port = sys.argv[2]
        dbname = sys.argv[3]
        user = sys.argv[4]
        password = sys.argv[5]
    
    # Probar la conexión
    success = test_connection(host, port, dbname, user, password)
    
    if not success:
        print("\nImportante: Asegúrate de que:")
        print("1. PostgreSQL esté instalado y en ejecución")
        print("2. La base de datos exista")
        print("3. El usuario tenga permisos adecuados")
        print("4. Los datos de conexión sean correctos")
        print("5. No haya caracteres especiales en contraseñas o nombres")
        print("\nPuedes ejecutar este script con tus propios parámetros:")
        print("python test_db_connection.py host puerto nombre_db usuario contraseña")