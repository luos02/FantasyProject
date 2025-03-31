from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.controllers.auth_controller import authenticate_user

# Crear un Blueprint para las rutas de autenticación
auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if authenticate_user(username, password):
            # Autenticación exitosa
            return redirect(url_for("content.home"))
        else:
            # Autenticación fallida
            flash("Usuario o contraseña incorrectos", "error")
            return render_template("login.html")

    return render_template("login.html")