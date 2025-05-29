from flask import Blueprint, request, jsonify, render_template, session, abort, current_app
from app.controllers.prophet_training_controller import ProphetTrainingController
from app.middleware.auth_middleware import login_required, analyst_or_admin_required
import traceback

# Create Blueprint for Prophet-related routes
prophet_bp = Blueprint('prophet', __name__, url_prefix='/model')

@prophet_bp.route('/upload', methods=['POST'])
@analyst_or_admin_required
def upload_csv():
    """
    Process CSV file upload for training - requires analyst or admin role
    """
    # Check if file was sent
    if 'file' not in request.files:
        return jsonify({"error": "No file was sent"}), 400
    
    file = request.files['file']
    
    try:
        # Process CSV file
        result = ProphetTrainingController.process_csv_file(file, session['user_id'])
        
        if 'error' in result:
            return jsonify(result), 400
        
        # Save data in session for later use
        session['prophet_training_data'] = result
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error processing CSV file: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@prophet_bp.route('/train', methods=['POST'])
@analyst_or_admin_required
def train_model():
    """
    Train Prophet model with provided parameters - requires analyst or admin role
    """
    # Check if training data exists in session
    if 'prophet_training_data' not in session:
        return jsonify({"error": "No training data found. Please upload a CSV file first."}), 400
    
    # Get training data and parameters
    training_data = session['prophet_training_data']
    params = request.get_json()
    
    if not params:
        return jsonify({"error": "No training parameters provided"}), 400
    
    try:
        # Train the model
        result = ProphetTrainingController.train_model(training_data, params)
        
        if 'error' in result:
            return jsonify(result), 400
        
        # Clear session data after training
        session.pop('prophet_training_data', None)
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error training Prophet model: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@prophet_bp.route('/metrics', methods=['GET'])
@login_required
def get_metrics():
    """
    Get current model metrics - requires login
    """
    from app.models.models import ProphetModel
    
    # Get active model
    active_model = ProphetModel.query.filter_by(is_active=True).first()
    
    if not active_model:
        return jsonify({"error": "No active model found"}), 404
    
    # Get metrics
    metrics = active_model.get_metrics()
    
    # If training data exists in session, include projected metrics
    if 'prophet_training_data' in session and 'model_metrics' in session['prophet_training_data']:
        return jsonify({
            "current_model": metrics,
            "new_model": session['prophet_training_data']['model_metrics']['new_model']
        })
    
    return jsonify({"current_model": metrics})

@prophet_bp.route('/history', methods=['GET'])
@analyst_or_admin_required
def get_training_history():
    """
    Get model training history - requires analyst or admin role
    """
    from app.controllers.prophet_controller import ProphetController
    
    # Pagination and filter parameters
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    offset = (page - 1) * limit
    
    # Optional filters
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
        # Get training history
        history = ProphetController.get_training_history(limit, offset, filters)
        return jsonify(history)
    except Exception as e:
        current_app.logger.error(f"Error getting training history: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500