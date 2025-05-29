from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from app.controllers.content_controller import get_content
from app.controllers.user_controller import list_users, add_user
from app.controllers.dashboard_controller import DashboardController
from app.middleware.auth_middleware import login_required, admin_required, analyst_or_admin_required

# Create Blueprint for content routes
content_bp = Blueprint('content', __name__)

@content_bp.route("/index")
@login_required
def home():
    """Main dashboard - requires login"""
    dashboard_data = DashboardController.get_dashboard_data()
    return render_template("index.html", dashboard_data=dashboard_data)

@content_bp.route("/api/dashboard-data")
@login_required
def get_dashboard_data():
    """API endpoint for dashboard data - requires login"""
    dashboard_data = DashboardController.get_dashboard_data()
    return jsonify(dashboard_data)

@content_bp.route("/TrainingHistory")
@analyst_or_admin_required
def subopcion2():
    """Training history - requires analyst or admin role"""
    content = get_content("trainingHistory")
    return render_template("config/ManageModel/trainingHistory.html", content=content)

@content_bp.route("/ViewReports")
@login_required
def subopcion3():
    """View reports - requires login (all authenticated users can view)"""
    content = get_content("ViewReports")
    return render_template("reports/view_reports_list.html", content=content)

@content_bp.route("/GenerateReports")
@analyst_or_admin_required
def subopcion4():
    """Generate reports - requires analyst or admin role"""
    content = get_content("GenerateReports")
    return render_template("reports/generateReport.html", content=content)

@content_bp.route("/Config")
@admin_required
def subopcion5():
    """Configuration - admin only"""
    return list_users()

@content_bp.route("/Config/addUsers")
@admin_required
def subopcion5_1():
    """Add users - admin only"""
    return add_user()

@content_bp.route("/Config/ManageModel")
@analyst_or_admin_required
def subopcion6():
    """Model management - requires analyst or admin role"""
    content = get_content("viewProphetModel")
    return render_template("config/ManageModel/viewProphetModel.html", content=content)

@content_bp.route("/Config/ManageModel/TrainModel")
@analyst_or_admin_required
def subopcion6_1():
    """Model training - requires analyst or admin role"""
    return render_template("config/ManageModel/retrainProphetModel.html")

@content_bp.route("/ViewReports/GenerateReports")
@analyst_or_admin_required
def subopcion7():
    """Custom report generation - requires analyst or admin role"""
    content = get_content("generateCustomReport")
    return render_template("reports/generateCustomReport.html", content=content)

@content_bp.route("/subopcion99")
@login_required
def subopcion99():
    """Generic content - requires login"""
    content = get_content("subopcion99")
    return render_template("content.html", content=content)