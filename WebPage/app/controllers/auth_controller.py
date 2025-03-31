from app.models.models import UserModel

# Autenticates user
def authenticate_user(username, password):
    return UserModel.authenticate(username, password)