from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from app.controllers.auth_controller import authenticate_user, register_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return jsonify({"error": "Se requiere nombre de usuario y contraseña"}), 400
        
        user = authenticate_user(username, password)
        
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('content.home'))
        else:
            return jsonify({"error": "Credenciales inválidas"}), 401
    
    # Si es GET, mostrar formulario de login
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        nombre_completo = request.form.get('nombre_completo')
        
        if not username or not email or not password:
            return jsonify({"error": "Faltan campos requeridos"}), 400
        
        user, message = register_user(username, email, password, nombre_completo)
        
        if user:
            return redirect(url_for('auth.login'))
        else:
            return jsonify({"error": message}), 400
    
    # Si es GET, mostrar formulario de registro
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))