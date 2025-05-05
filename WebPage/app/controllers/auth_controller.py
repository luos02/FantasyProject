from app.models.models import UserModel, db
from flask import session

def authenticate_user(username, password):
    """
    Autentica al usuario contra la base de datos PostgreSQL
    """
    user = UserModel.authenticate(username, password)
    if user:
        session['user_role'] = user.roles  # Guardar el rol en la sesión
    return user

def register_user(username, email, password, nombre_completo=None):
    """
    Registra un nuevo usuario en la base de datos
    """
    existing_user = UserModel.query.filter_by(username=username).first()
    if existing_user:
        return None, "El nombre de usuario ya está en uso"
    
    existing_email = UserModel.query.filter_by(email=email).first()
    if existing_email:
        return None, "El correo electrónico ya está registrado"
    
    new_user = UserModel(
        username=username,
        email=email,
        password=password,
        nombre_completo=nombre_completo,
        roles='viewer'  # Rol por defecto para nuevos usuarios
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return new_user, "Usuario registrado exitosamente"