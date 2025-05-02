from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class UserModel(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    nombre_completo = db.Column(db.String(100))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime)
    activo = db.Column(db.Boolean, default=True)
    
    def __init__(self, username, email, password, nombre_completo=None):
        self.username = username
        self.email = email
        self.set_password(password)
        self.nombre_completo = nombre_completo
    
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
            }
        }
        return content_data.get(content_id)