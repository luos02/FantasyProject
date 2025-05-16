from flask import Blueprint, request, jsonify, render_template, session, abort, current_app
from app.controllers.prophet_training_controller import ProphetTrainingController
import traceback

# Crear Blueprint para las rutas relacionadas con Prophet
prophet_bp = Blueprint('prophet', __name__, url_prefix='/model')

@prophet_bp.route('/upload', methods=['POST'])
def upload_csv():
    """
    Procesa la carga de un archivo CSV para el entrenamiento
    """
    # Verificar que el usuario está autenticado
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401
    
    # Verificar que el usuario tiene permisos (admin o analyst)
    if session.get('user_role') not in ['admin', 'analyst']:
        return jsonify({"error": "No tiene permisos para realizar esta acción"}), 403
    
    # Verificar que se ha enviado un archivo
    if 'file' not in request.files:
        return jsonify({"error": "No se ha enviado ningún archivo"}), 400
    
    file = request.files['file']
    
    try:
        # Procesar el archivo CSV
        result = ProphetTrainingController.process_csv_file(file, session['user_id'])
        
        if 'error' in result:
            return jsonify(result), 400
        
        # Guardar los datos en la sesión para uso posterior
        session['prophet_training_data'] = result
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error al procesar archivo CSV: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

@prophet_bp.route('/train', methods=['POST'])
def train_model():
    """
    Entrena el modelo Prophet con los parámetros proporcionados
    """
    # Verificar que el usuario está autenticado
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401
    
    # Verificar que el usuario tiene permisos (admin o analyst)
    if session.get('user_role') not in ['admin', 'analyst']:
        return jsonify({"error": "No tiene permisos para realizar esta acción"}), 403
    
    # Verificar que hay datos de entrenamiento en la sesión
    if 'prophet_training_data' not in session:
        return jsonify({"error": "No hay datos de entrenamiento. Por favor, cargue un archivo CSV primero."}), 400
    
    # Obtener datos de entrenamiento y parámetros
    training_data = session['prophet_training_data']
    params = request.get_json()
    
    if not params:
        return jsonify({"error": "No se proporcionaron parámetros para el entrenamiento"}), 400
    
    try:
        # Entrenar el modelo
        result = ProphetTrainingController.train_model(training_data, params)
        
        if 'error' in result:
            return jsonify(result), 400
        
        # Limpiar datos de sesión después de entrenar
        session.pop('prophet_training_data', None)
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error al entrenar modelo Prophet: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

@prophet_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """
    Obtiene las métricas actuales del modelo
    """
    from app.models.models import ProphetModel
    
    # Obtener el modelo activo
    active_model = ProphetModel.query.filter_by(is_active=True).first()
    
    if not active_model:
        return jsonify({"error": "No hay un modelo activo"}), 404
    
    # Obtener métricas
    metrics = active_model.get_metrics()
    
    # Si hay datos de entrenamiento en la sesión, incluir las métricas proyectadas
    if 'prophet_training_data' in session and 'model_metrics' in session['prophet_training_data']:
        return jsonify({
            "current_model": metrics,
            "new_model": session['prophet_training_data']['model_metrics']['new_model']
        })
    
    return jsonify({"current_model": metrics})

@prophet_bp.route('/history', methods=['GET'])
def get_training_history():
    """
    Obtiene el historial de entrenamientos del modelo
    """
    from app.controllers.prophet_controller import ProphetController
    
    # Verificar que el usuario está autenticado
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401
    
    # Parámetros de paginación y filtros
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    offset = (page - 1) * limit
    
    # Filtros opcionales
    filters = {}
    if 'date_from' in request.args:
        filters['date_from'] = request.args.get('date_from')
    if 'date_to' in request.args:
        filters['date_to'] = request.args.get('date_to')
    if 'training_type' in request.args:
        filters['training_type'] = request.args.get('training_type')
    if 'status' in request.args:
        filters['status'] = request.args.get('status')
    
    try:
        # Obtener historial de entrenamientos
        history = ProphetController.get_training_history(limit, offset, filters)
        return jsonify(history)
    except Exception as e:
        current_app.logger.error(f"Error al obtener historial de entrenamientos: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500