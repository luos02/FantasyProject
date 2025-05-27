from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from app.controllers.auth_controller import authenticate_user, register_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Se requiere nombre de usuario y contraseña', 'error')
            return redirect(url_for('auth.login'))
        
        user = authenticate_user(username, password)
        
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('content.home'))
        else:
            flash('Credenciales inválidas', 'error')
            return redirect(url_for('auth.login'))
    
    return render_template('Login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        nombre_completo = request.form.get('nombre_completo')
        
        if not username or not email or not password:
            flash('Faltan campos requeridos', 'error')
            return redirect(url_for('auth.register'))
        
        user, message = register_user(username, email, password, nombre_completo)
        
        if user:
            flash('Registro exitoso. Por favor inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')  # Asume que tienes una plantilla register.html

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('auth.login'))