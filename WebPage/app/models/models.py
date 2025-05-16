from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class UserModel(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    nombre_completo = db.Column(db.String(100))
    roles = db.Column(db.String(20), default='viewer')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime)
    activo = db.Column(db.Boolean, default=True)
    
    # Relación con los entrenamientos de modelos
    trainings = db.relationship('ModelTrainingHistory', backref='user', lazy=True)
    
    def __init__(self, username, email, password, nombre_completo=None, roles='viewer', activo=True):
        self.username = username
        self.email = email
        self.set_password(password)
        self.nombre_completo = nombre_completo
        self.roles = roles
        self.activo = activo
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # Actualizar la fecha del último login
            user.ultimo_login = datetime.utcnow()
            db.session.commit()
            return user
        return None

class ProphetModel(db.Model):
    """
    Modelo para almacenar la configuración y estado del modelo Prophet
    """
    __tablename__ = 'prophet_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Parámetros del modelo en formato JSON
    parameters_json = db.Column(db.Text)
    
    # Métricas del modelo en formato JSON
    metrics_json = db.Column(db.Text)
    
    # Relación con el historial de entrenamiento
    training_history = db.relationship('ModelTrainingHistory', backref='model', lazy=True)
    
    def __init__(self, name, description=None, parameters=None, metrics=None):
        self.name = name
        self.description = description
        
        if parameters:
            self.set_parameters(parameters)
        
        if metrics:
            self.set_metrics(metrics)
    
    def set_parameters(self, parameters):
        """Almacena los parámetros del modelo en formato JSON"""
        self.parameters_json = json.dumps(parameters)
    
    def get_parameters(self):
        """Recupera los parámetros del modelo como diccionario"""
        if self.parameters_json:
            return json.loads(self.parameters_json)
        return {}
    
    def set_metrics(self, metrics):
        """Almacena las métricas del modelo en formato JSON"""
        self.metrics_json = json.dumps(metrics)
    
    def get_metrics(self):
        """Recupera las métricas del modelo como diccionario"""
        if self.metrics_json:
            return json.loads(self.metrics_json)
        return {}
    
    @classmethod
    def get_active_model(cls):
        """Obtiene el modelo activo actual"""
        return cls.query.filter_by(is_active=True).first()

class ModelTrainingHistory(db.Model):
    """
    Modelo para almacenar el historial de entrenamientos
    """
    __tablename__ = 'model_training_history'
    
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('prophet_models.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    training_type = db.Column(db.String(50))  # 'Initial', 'Retrain', 'Maintenance'
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)
    status = db.Column(db.String(20))  # 'success', 'failed', 'in_progress'
    
    # Métricas antes y después del entrenamiento
    previous_metrics_json = db.Column(db.Text)
    new_metrics_json = db.Column(db.Text)
    
    # Datos utilizados para el entrenamiento
    data_info_json = db.Column(db.Text)
    
    # Notas o comentarios sobre el entrenamiento
    notes = db.Column(db.Text)
    
    def __init__(self, model_id, user_id, training_type, data_info=None, previous_metrics=None):
        self.model_id = model_id
        self.user_id = user_id
        self.training_type = training_type
        self.status = 'in_progress'
        
        if data_info:
            self.set_data_info(data_info)
        
        if previous_metrics:
            self.set_previous_metrics(previous_metrics)
    
    def complete_training(self, new_metrics, duration_seconds, notes=None):
        """Marca el entrenamiento como completado con las nuevas métricas"""
        self.end_time = datetime.utcnow()
        self.duration_seconds = duration_seconds
        self.status = 'success'
        self.notes = notes
        self.set_new_metrics(new_metrics)
    
    def fail_training(self, error_message):
        """Marca el entrenamiento como fallido con el mensaje de error"""
        self.end_time = datetime.utcnow()
        self.status = 'failed'
        self.notes = error_message
    
    def set_previous_metrics(self, metrics):
        """Almacena las métricas anteriores en formato JSON"""
        self.previous_metrics_json = json.dumps(metrics)
    
    def get_previous_metrics(self):
        """Recupera las métricas anteriores como diccionario"""
        if self.previous_metrics_json:
            return json.loads(self.previous_metrics_json)
        return {}
    
    def set_new_metrics(self, metrics):
        """Almacena las nuevas métricas en formato JSON"""
        self.new_metrics_json = json.dumps(metrics)
    
    def get_new_metrics(self):
        """Recupera las nuevas métricas como diccionario"""
        if self.new_metrics_json:
            return json.loads(self.new_metrics_json)
        return {}
    
    def set_data_info(self, data_info):
        """Almacena información sobre los datos de entrenamiento en formato JSON"""
        self.data_info_json = json.dumps(data_info)
    
    def get_data_info(self):
        """Recupera información sobre los datos de entrenamiento como diccionario"""
        if self.data_info_json:
            return json.loads(self.data_info_json)
        return {}
    
    def calculate_improvement(self, metric_name='rmse'):
        """Calcula la mejora porcentual para una métrica específica"""
        prev_metrics = self.get_previous_metrics()
        new_metrics = self.get_new_metrics()
        
        if metric_name in prev_metrics and metric_name in new_metrics:
            prev_value = prev_metrics[metric_name]
            new_value = new_metrics[metric_name]
            
            if prev_value != 0:
                if metric_name in ['rmse', 'mae', 'mape']:  # Métricas donde menor es mejor
                    return ((prev_value - new_value) / prev_value) * 100
                else:  # Métricas donde mayor es mejor (como R²)
                    return ((new_value - prev_value) / prev_value) * 100
        
        return 0

class ContentModel:
    @staticmethod
    def get_content(content_id):
        content_data = {
            "subopcion1": {
                "title": "Subopción 1",
                "description": "Este es el contenido de la subopción 1."
            },
            "subopcion2": {
                "title": "Subopción 2",
                "description": "Este es el contenido de la subopción 2."
            },
            "subopcion3": {
                "title": "Subopción 3",
                "description": "Este es el contenido de la subopción 3."
            },
            "subopcion4": {
                "title": "Subopción 4",
                "description": "Este es el contenido de la subopción 4."
            },
            "viewProphetModel": {
                "title": "Modelo de Predicción Prophet",
                "description": "Visualización y gestión del modelo de predicción de ventas."
            },
            "retrainProphetModel": {
                "title": "Reentrenar Modelo Prophet",
                "description": "Formulario para reentrenar el modelo Prophet con nuevos datos."
            },
            "trainingHistory": {
                "title": "Historial de Entrenamientos",
                "description": "Registro histórico de entrenamientos del modelo Prophet."
            },
            "ViewReports": {
                "title": "Ver Reportes",
                "description": "Visualización de reportes de ventas y proyecciones."
            },
            "GenerateReports": {
                "title": "Generar Reportes",
                "description": "Generación de reportes personalizados."
            },
            "generateCustomReport": {
                "title": "Reporte Personalizado",
                "description": "Creación de reportes personalizados con métricas específicas."
            }
        }
        return content_data.get(content_id)