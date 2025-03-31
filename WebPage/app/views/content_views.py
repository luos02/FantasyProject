from flask import Blueprint, render_template
from app.controllers.content_controller import get_content

# Crear un Blueprint para las rutas de contenido
content_bp = Blueprint('content', __name__)

@content_bp.route("/index")
def home():
    return render_template("index.html")

@content_bp.route("/ViewStudents")
def subopcion1():
    content = get_content("ViewStudents")
    return render_template("students/watch_student_list.html", content=content)

@content_bp.route("/ManageStudents")
def subopcion2():
    content = get_content("ManageStudents")
    return render_template("students/manage_students.html", content=content)

@content_bp.route("/ViewTeachers")
def subopcion3():
    content = get_content("ViewTeachers")
    return render_template("teachers/watch_teachers_list.html", content=content)

@content_bp.route("/ManageTeachers")
def subopcion4():
    content = get_content("ManageTeachers")
    return render_template("teachers/manage_teachers.html", content=content)

@content_bp.route("/subopcion5")
def subopcion5():
    content = get_content("subopcion5")
    return render_template("content.html", content=content)