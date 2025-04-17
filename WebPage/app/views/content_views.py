from flask import Blueprint, render_template
from app.controllers.content_controller import get_content

# Crear un Blueprint para las rutas de contenido
content_bp = Blueprint('content', __name__)

@content_bp.route("/index")
def home():
    return render_template("index.html")

@content_bp.route("/TrainingHistory")
def subopcion2():
    content = get_content("trainingHistory")
    return render_template("config/ManageModel/trainingHistory.html", content=content)

@content_bp.route("/ViewReports")
def subopcion3():
    content = get_content("ViewReports")
    return render_template("reports/view_reports_list.html", content=content)

@content_bp.route("/GenerateReports")
def subopcion4():
    content = get_content("GenerateReports")
    return render_template("reports/generateReport.html", content=content)

@content_bp.route("/Config")
def subopcion5():
    content = get_content("Config")
    return render_template("config/manageUsers/manageUsers.html", content=content)

@content_bp.route("/Config/addUsers")
def subopcion5_1():
    content = get_content("addUsers")
    return render_template("config/manageUsers/addUsers.html", content=content)

@content_bp.route("/Config/ManageModel")
def subopcion6():
    content = get_content("viewProphetModel")
    return render_template("config/ManageModel/viewProphetModel.html", content=content)

@content_bp.route("/Config/ManageModel/TrainModel")
def subopcion6_1():
    content = get_content("retrainProphetModel")
    return render_template("config/ManageModel/retrainProphetModel.html", content=content)

@content_bp.route("/ViewReports/GenerateReports")
def subopcion7():
    content = get_content("generateCustomReport")
    return render_template("reports/generateCustomReport.html", content=content)

@content_bp.route("/subopcion99")
def subopcion99():
    content = get_content("subopcion99")
    return render_template("content.html", content=content)