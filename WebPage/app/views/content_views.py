from flask import Blueprint, render_template, redirect, url_for
from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from app.controllers.content_controller import get_content
from app.controllers.user_controller import list_users, add_user
from app.controllers.dashboard_controller import DashboardController

# Crear un Blueprint para las rutas de contenido
content_bp = Blueprint('content', __name__)

@content_bp.route("/index")
def home():
    dashboard_data = DashboardController.get_dashboard_data()
    return render_template("index.html", dashboard_data=dashboard_data)

@content_bp.route("/api/dashboard-data")
def get_dashboard_data():
    dashboard_data = DashboardController.get_dashboard_data()
    return jsonify(dashboard_data)

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
    return list_users()

@content_bp.route("/Config/addUsers")
def subopcion5_1():
    return add_user()

@content_bp.route("/Config/ManageModel")
def subopcion6():
    content = get_content("viewProphetModel")
    return render_template("config/ManageModel/viewProphetModel.html", content=content)

@content_bp.route("/Config/ManageModel/TrainModel")
def subopcion6_1():
    return render_template("config/ManageModel/retrainProphetModel.html")

@content_bp.route("/ViewReports/GenerateReports")
def subopcion7():
    content = get_content("generateCustomReport")
    return render_template("reports/generateCustomReport.html", content=content)

@content_bp.route("/subopcion99")
def subopcion99():
    content = get_content("subopcion99")
    return render_template("content.html", content=content)