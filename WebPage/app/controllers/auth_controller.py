from app.models.models import UserModel, db

def authenticate_user(username, password):
    """
    Autentica al usuario contra la base de datos PostgreSQL
    """
    return UserModel.authenticate(username, password)

def register_user(username, email, password, nombre_completo=None):
    """
    Registra un nuevo usuario en la base de datos
    """
    # Verificar si el usuario ya existe
    existing_user = UserModel.query.filter_by(username=username).first()
    if existing_user:
        return None, "El nombre de usuario ya está en uso"
    
    # Verificar si el email ya existe
    existing_email = UserModel.query.filter_by(email=email).first()
    if existing_email:
        return None, "El correo electrónico ya está registrado"
    
    # Crear nuevo usuario
    new_user = UserModel(
        username=username,
        email=email,
        password=password,
        nombre_completo=nombre_completo
    )
    
    # Guardar en la base de datos
    db.session.add(new_user)
    db.session.commit()
    
    return new_user, "Usuario registrado exitosamente"