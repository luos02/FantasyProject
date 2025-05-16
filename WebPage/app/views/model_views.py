from flask import Blueprint, request, jsonify, render_template, flash, session, redirect, url_for
from werkzeug.utils import secure_filename
import os
import json
from app.controllers.model_controller import ModelController

model_bp = Blueprint('model', __name__, url_prefix='/model')

@model_bp.route('/upload', methods=['POST'])
def upload_csv():
    """
    Endpoint para cargar un archivo CSV para entrenamiento
    """
    if 'file' not in request.files:
        return jsonify({"error": "No se ha enviado ningún archivo"}), 400
    
    file = request.files['file']
    
    # Procesar el archivo CSV
    result = ModelController.process_csv_file(file)
    
    if 'error' in result:
        return jsonify(result), 400
    
    # Guardar información del archivo en la sesión para usarla en el proceso de entrenamiento
    session['csv_data'] = result
    
    return jsonify(result)

@model_bp.route('/train', methods=['POST'])
def train_model():
    """
    Endpoint para entrenar el modelo con los parámetros proporcionados
    """
    if 'csv_data' not in session:
        return jsonify({"error": "No hay datos de entrenamiento. Por favor, suba un archivo CSV primero."}), 400
    
    # Obtener parámetros del modelo
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No se proporcionaron parámetros para el entrenamiento"}), 400
    
    # Simular entrenamiento del modelo
    model_parameters = {
        "growth": data.get("growth", "linear"),
        "changepoints": int(data.get("changepoints", 25)),
        "seasonality_mode": data.get("seasonality_mode", "additive"),
        "weekly_seasonality": data.get("weekly_seasonality", True),
        "yearly_seasonality": data.get("yearly_seasonality", True),
        "include_holidays": data.get("include_holidays", True),
        "holidays_scale": float(data.get("holidays_scale", 0.5))
    }
    
    # Aquí llamaríamos a la función real de entrenamiento
    result = ModelController.train_prophet_model(None, model_parameters)
    
    # Limpiar datos de la sesión después del entrenamiento
    session.pop('csv_data', None)
    
    # Redirigir a la página de historial de entrenamientos
    if result.get("success"):
        flash("Modelo reentrenado exitosamente", "success")
    else:
        flash(f"Error al reentrenar el modelo: {result.get('error', 'Error desconocido')}", "error")
    
    return jsonify(result)

@model_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """
    Endpoint para obtener las métricas de validación del modelo
    """
    # En una implementación real, aquí recuperaríamos las métricas actuales del modelo
    # Para este ejemplo, devolveremos métricas simuladas
    metrics = {
        "current_model": {
            "rmse": 245.78,
            "mae": 189.32,
            "mape": 8.5,
            "r2": 0.87
        }
    }
    
    if 'csv_data' in session and 'model_metrics' in session['csv_data']:
        metrics["new_model"] = session['csv_data']['model_metrics']['new_model']
    
    return jsonify(metrics)