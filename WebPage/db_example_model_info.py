import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine

# Configuración de conexión a PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'database': 'fantasydb',
    'user': 'fantasyuser',
    'password': 'password123',
    'port': '5432'
}

def generate_sample_data():
    # Generar datos de clientes
    clients = [
        {'client_id': 1, 'client_name': 'Distribuidora Norte', 'client_type': 'Distribuidor', 'contact_email': 'contacto@distribuidoranorte.com', 'contact_phone': '555-100-1000'},
        {'client_id': 2, 'client_name': 'Restaurante La Parrilla', 'client_type': 'Restaurante', 'contact_email': 'compras@laparrilla.com', 'contact_phone': '555-200-2000'},
        {'client_id': 3, 'client_name': 'Supermercados Central', 'client_type': 'Minorista', 'contact_email': 'proveedores@supercentral.com', 'contact_phone': '555-300-3000'},
        {'client_id': 4, 'client_name': 'Mayorista Plásticos SA', 'client_type': 'Mayorista', 'contact_email': 'ventas@mayoristaplast.com', 'contact_phone': '555-400-4000'},
        {'client_id': 5, 'client_name': 'Cadenas de Restaurantes UNO', 'client_type': 'Restaurante', 'contact_email': 'compras@cadenasuno.com', 'contact_phone': '555-500-5000'}
    ]
    clients_df = pd.DataFrame(clients)
    
    # Generar datos de moldes
    molds = [
        {'mold_id': 1, 'mold_code': 'MOLD-001', 'description': 'Plato redondo estándar', 'cavity_number': 8, 'manufacturing_date': '2020-01-15', 'last_maintenance': '2023-06-01', 'status': 'Activo'},
        {'mold_id': 2, 'mold_code': 'MOLD-002', 'description': 'Plato hondo sopero', 'cavity_number': 6, 'manufacturing_date': '2020-03-10', 'last_maintenance': '2023-05-15', 'status': 'Activo'},
        {'mold_id': 3, 'mold_code': 'MOLD-003', 'description': 'Plato rectangular', 'cavity_number': 4, 'manufacturing_date': '2021-02-20', 'last_maintenance': '2023-07-10', 'status': 'Activo'},
        {'mold_id': 4, 'mold_code': 'MOLD-004', 'description': 'Plato infantil', 'cavity_number': 10, 'manufacturing_date': '2019-11-05', 'last_maintenance': '2023-04-20', 'status': 'En mantenimiento'}
    ]
    molds_df = pd.DataFrame(molds)
    
    # Generar tipos de platos (asegurando que plate_type_id comience en 1)
    plate_types = [
        {'plate_type_id': 1, 'type_code': 'PLATO-001', 'description': 'Plato redondo 20cm', 'diameter_cm': 20.0, 'weight_grams': 45.0, 'color': 'Blanco', 'material': 'PP', 'mold_id': 1},
        {'plate_type_id': 2, 'type_code': 'PLATO-002', 'description': 'Plato redondo 25cm', 'diameter_cm': 25.0, 'weight_grams': 60.0, 'color': 'Blanco', 'material': 'PP', 'mold_id': 1},
        {'plate_type_id': 3, 'type_code': 'PLATO-003', 'description': 'Plato hondo 18cm', 'diameter_cm': 18.0, 'weight_grams': 55.0, 'color': 'Transparente', 'material': 'PS', 'mold_id': 2},
        {'plate_type_id': 4, 'type_code': 'PLATO-004', 'description': 'Plato rectangular 22x15cm', 'diameter_cm': 0.0, 'weight_grams': 50.0, 'color': 'Rojo', 'material': 'PP', 'mold_id': 3},
        {'plate_type_id': 5, 'type_code': 'PLATO-005', 'description': 'Plato infantil 15cm', 'diameter_cm': 15.0, 'weight_grams': 35.0, 'color': 'Azul', 'material': 'PP', 'mold_id': 4}
    ]
    plate_types_df = pd.DataFrame(plate_types)
    
    # Generar producción diaria (últimos 90 días)
    production_dates = pd.date_range(end=datetime.today(), periods=90).date
    production_data = []
    
    for date in production_dates:
        for _, plate_type in plate_types_df.iterrows():  # Cambiado a iterrows()
            # Producción base más variación aleatoria
            base_production = 500 if plate_type['mold_id'] != 4 else 800  # Plato infantil tiene más producción
            good_units = int(base_production * random.uniform(0.9, 1.1))
            defective_units = int(good_units * random.uniform(0.01, 0.05))  # 1-5% defectuosos
            
            production_data.append({
                'production_date': date,
                'plate_type_id': plate_type['plate_type_id'],  # Acceso correcto al campo
                'mold_id': plate_type['mold_id'],
                'good_units': good_units,
                'defective_units': defective_units,
                'machine_hours': round(random.uniform(6.0, 8.5), 2),
                'operator_id': f'OP-{random.randint(1, 5)}',
                'notes': random.choice(['', 'Cambio de material', 'Ajuste de temperatura', 'Mantenimiento rutinario'])
            })
    
    production_df = pd.DataFrame(production_data)
    
    # Generar ventas (últimos 180 días)
    sale_dates = pd.date_range(end=datetime.today(), periods=180).date
    sales_data = []
    
    for date in sale_dates:
        # Generar entre 3-10 ventas por día
        for _ in range(random.randint(3, 10)):
            plate_type = plate_types_df.sample(1).iloc[0]  # Obtener una fila aleatoria correctamente
            client_id = random.randint(1, len(clients_df))
            
            # Precios base con variación según cliente
            base_price = {
                1: 2.50,  # Plato-001
                2: 3.00,  # Plato-002
                3: 2.80,  # Plato-003
                4: 3.20,  # Plato-004
                5: 1.80   # Plato-005
            }.get(plate_type['plate_type_id'], 2.00)  # Precio por defecto si no coincide
            
            # Descuentos para mayoristas
            if client_id == 4:  # Mayorista
                unit_price = round(base_price * 0.7, 2)  # 30% descuento
            elif client_id == 1:  # Distribuidor
                unit_price = round(base_price * 0.8, 2)  # 20% descuento
            else:
                unit_price = round(base_price * random.uniform(0.9, 1.1), 2)
            
            quantity = random.randint(50, 500) if client_id in [1, 4] else random.randint(10, 100)
            
            sales_data.append({
                'sale_date': date,
                'client_id': client_id,
                'plate_type_id': plate_type['plate_type_id'],
                'quantity': quantity,
                'unit_price': unit_price,
                'payment_method': random.choice(['Efectivo', 'Transferencia', 'Tarjeta', 'Crédito']),
                'invoice_number': f'FAC-{date.strftime("%Y%m%d")}-{random.randint(100, 999)}'
            })
    
    sales_df = pd.DataFrame(sales_data)
    
    # Generar inventario (stock actual)
    inventory_data = []
    for _, plate_type in plate_types_df.iterrows():
        inventory_data.append({
            'record_date': datetime.today().date(),
            'plate_type_id': plate_type['plate_type_id'],
            'quantity': random.randint(500, 3000),
            'warehouse_location': random.choice(['Almacén A', 'Almacén B', 'Almacén C'])
        })
    
    inventory_df = pd.DataFrame(inventory_data)
    
    return {
        'clients': clients_df,
        'molds': molds_df,
        'plate_types': plate_types_df,
        'production': production_df,
        'sales': sales_df,
        'inventory': inventory_df
    }

def save_to_csv(data_dict):
    """Guarda los DataFrames en archivos CSV"""
    for name, df in data_dict.items():
        df.to_csv(f'{name}.csv', index=False)
        print(f'Archivo {name}.csv generado con {len(df)} registros')

def load_to_postgres(data_dict):
    """Carga los datos a PostgreSQL"""
    try:
        engine = create_engine(
            f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        )
        
        for name, df in data_dict.items():
            df.to_sql(name, engine, if_exists='append', index=False)
            print(f'Datos cargados en tabla {name}')
        
        print("¡Todos los datos han sido cargados exitosamente!")
    except Exception as e:
        print(f"Error al cargar datos: {e}")

if __name__ == "__main__":
    print("Generando datos de ejemplo...")
    sample_data = generate_sample_data()
    
    print("\nGuardando datos en archivos CSV...")
    save_to_csv(sample_data)
    
    print("\n¿Desea cargar los datos a PostgreSQL? (s/n)")
    if input().lower() == 's':
        print("\nCargando datos a PostgreSQL...")
        load_to_postgres(sample_data)