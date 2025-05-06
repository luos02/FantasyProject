from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from datetime import datetime
from werkzeug.security import generate_password_hash
from app.models.models import UserModel, db
from functools import wraps

user_bp = Blueprint('config', __name__, url_prefix='/Config',
                   template_folder='templates')

# Decorador para requerir rol admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_role') != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Decorador para requerir no ser viewer
def not_viewer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_role') == 'viewer':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route('/', methods=['GET'])
@not_viewer_required
def list_users():
    users = UserModel.query.order_by(UserModel.username).all()
    return render_template('config/manageUsers/manageUsers.html', users=users)

@user_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            nombre_completo = request.form.get('nombre_completo', '').strip()
            roles = request.form.get('roles', 'viewer')
            activo = request.form.get('activo', '0') == '1'

            if not all([username, email, password]):
                flash('Faltan campos obligatorios', 'error')
                return redirect(url_for('config.add_user'))

            if UserModel.query.filter_by(username=username).first():
                flash('Nombre de usuario ya existe', 'error')
                return redirect(url_for('config.add_user'))

            if UserModel.query.filter_by(email=email).first():
                flash('Email ya registrado', 'error')
                return redirect(url_for('config.add_user'))

            new_user = UserModel(
                username=username,
                email=email,
                password=password,
                nombre_completo=nombre_completo or None,
                roles=roles,
                activo=activo
            )

            db.session.add(new_user)
            db.session.commit()
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('config.list_users'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'error')
            return redirect(url_for('config.add_user'))

    return render_template('config/manageUsers/addUsers.html')

@user_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = UserModel.query.get_or_404(user_id)

    if request.method == 'POST':
        try:
            user.username = request.form['username']
            user.email = request.form['email']
            user.nombre_completo = request.form.get('nombre_completo', '').strip() or None
            user.roles = request.form.get('roles', 'viewer')
            user.activo = request.form.get('activo', '0') == '1'
            
            new_password = request.form.get('new_password')
            if new_password and len(new_password) >= 8:
                user.set_password(new_password)

            db.session.commit()
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('config.list_users'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar usuario: {str(e)}', 'error')

    return render_template('config/manageUsers/addUsers.html', user=user, edit_mode=True)

@user_bp.route('/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = UserModel.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Usuario eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar usuario: {str(e)}', 'error')
    return redirect(url_for('config.list_users'))