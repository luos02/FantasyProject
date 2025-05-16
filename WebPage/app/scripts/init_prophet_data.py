from app import create_app
from app.models.models import db, ProphetModel, ModelTrainingHistory, UserModel
from datetime import datetime, timedelta
import random
import json

def init_prophet_data():
    """
    Función para inicializar datos de ejemplo para el modelo Prophet
    y su historial de entrenamientos.
    """
    # Crear la aplicación y contexto
    app = create_app()
    
    with app.app_context():
        # Verificar si ya existen datos
        if ProphetModel.query.count() > 0:
            print("Ya existen datos del modelo Prophet en la base de datos.")
            return
        
        print("Inicializando datos de ejemplo para Prophet...")
        
        # Parámetros iniciales del modelo
        initial_parameters = {
            "growth": "linear",
            "changepoints": 25,
            "n_changepoints": 25,
            "changepoint_range": 0.8,
            "yearly_seasonality": True,
            "weekly_seasonality": True,
            "daily_seasonality": False,
            "holidays": None,
            "seasonality_mode": "additive",
            "seasonality_prior_scale": 10.0,
            "holidays_prior_scale": 10.0,
            "changepoint_prior_scale": 0.05,
            "mcmc_samples": 0,
            "interval_width": 0.8,
            "uncertainty_samples": 1000
        }
        
        # Métricas iniciales del modelo
        initial_metrics = {
            "rmse": 245.78,
            "mae": 189.32,
            "mape": 8.5,
            "r2": 0.87
        }
        
        # Crear modelo Prophet inicial
        model = ProphetModel(
            name="Modelo de ventas inicial",
            description="Modelo Prophet para predicción de ventas con datos históricos 2020-2023",
            parameters=initial_parameters,
            metrics=initial_metrics
        )
        
        db.session.add(model)
        db.session.commit()
        
        # Obtener un usuario admin para los entrenamientos
        admin_user = UserModel.query.filter_by(roles='admin').first()
        
        if not admin_user:
            # Crear usuario admin si no existe
            admin_user = UserModel(
                username="admin",
                email="admin@ejemplo.com",
                password="admin123",
                nombre_completo="Administrador Sistema",
                roles="admin"
            )
            db.session.add(admin_user)
            db.session.commit()
        
        # Crear historial de entrenamientos simulado
        create_training_history(model.id, admin_user.id)
        
        print("Datos de ejemplo para Prophet inicializados correctamente.")

def create_training_history(model_id, user_id):
    """
    Crea un historial simulado de entrenamientos para el modelo
    """
    # Tipo de entrenamientos
    training_types = ["Initial", "Retrain", "Maintenance"]
    
    # Fechas de entrenamiento simuladas (empezando hace 1 año)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Generar 15 entrenamientos aleatorios
    for i in range(15):
        # Calcular fecha aleatoria entre start_date y end_date
        random_days = random.randint(0, (end_date - start_date).days)
        training_date = start_date + timedelta(days=random_days)
        
        # Determinar tipo de entrenamiento
        if i == 0:
            training_type = "Initial"  # El primero siempre es inicial
        else:
            training_type = random.choice(training_types[1:])  # Los demás son retrain o maintenance
        
        # Crear datos para el entrenamiento
        data_info = {
            "source": f"ventas_historicas_{training_date.strftime('%Y%m%d')}.csv",
            "rows": random.randint(800, 1500),
            "date_range": {
                "start": (training_date - timedelta(days=180)).strftime("%Y-%m-%d"),
                "end": training_date.strftime("%Y-%m-%d")
            }
        }
        
        # Generar métricas previas con pequeñas variaciones
        prev_metrics = {
            "rmse": round(random.uniform(240, 260), 2),
            "mae": round(random.uniform(180, 200), 2),
            "mape": round(random.uniform(8, 9), 1),
            "r2": round(random.uniform(0.85, 0.88), 2)
        }
        
        # Crear el registro de entrenamiento
        training = ModelTrainingHistory(
            model_id=model_id,
            user_id=user_id,
            training_type=training_type,
            data_info=data_info,
            previous_metrics=prev_metrics
        )
        
        # Simular duración aleatoria entre 20 y 60 minutos
        duration = random.randint(1200, 3600)
        
        # Determinar si el entrenamiento mejoró las métricas (80% de probabilidad)
        if random.random() < 0.8:
            # Métricas mejoradas
            new_metrics = {
                "rmse": round(prev_metrics["rmse"] * random.uniform(0.9, 0.98), 2),
                "mae": round(prev_metrics["mae"] * random.uniform(0.9, 0.98), 2),
                "mape": round(prev_metrics["mape"] * random.uniform(0.9, 0.98), 1),
                "r2": round(prev_metrics["r2"] * random.uniform(1.01, 1.03), 2)
            }
            notes = "Entrenamiento exitoso con mejora de métricas."
        else:
            # Métricas ligeramente peores
            new_metrics = {
                "rmse": round(prev_metrics["rmse"] * random.uniform(1.01, 1.05), 2),
                "mae": round(prev_metrics["mae"] * random.uniform(1.01, 1.05), 2),
                "mape": round(prev_metrics["mape"] * random.uniform(1.01, 1.05), 1),
                "r2": round(prev_metrics["r2"] * random.uniform(0.98, 0.99), 2)
            }
            notes = "Entrenamiento completado pero sin mejora significativa en métricas."
        
        # Completar entrenamiento
        training.complete_training(new_metrics, duration, notes)
        
        # Ajustar fecha de inicio y fin manual (para tener fechas en el pasado)
        training.start_time = training_date
        training.end_time = training_date + timedelta(seconds=duration)
        
        db.session.add(training)
    
    db.session.commit()
    print(f"Creados {15} entrenamientos de ejemplo en el historial.")

if __name__ == "__main__":
    init_prophet_data()