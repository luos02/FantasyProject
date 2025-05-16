from app.models.models import db, ProphetModel, ModelTrainingHistory
from flask import current_app, session
from datetime import datetime
import traceback
import json
import os
import pandas as pd

class ProphetController:
    """
    Controlador para gestionar los modelos Prophet y su entrenamiento
    """
    
    @staticmethod
    def get_active_model():
        """
        Obtiene el modelo Prophet activo
        """
        return ProphetModel.get_active_model()
    
    @staticmethod
    def get_model_metrics():
        """
        Obtiene las métricas del modelo activo
        """
        model = ProphetController.get_active_model()
        if model:
            return model.get_metrics()
        return {}
    
    @staticmethod
    def get_training_history(limit=10, offset=0, filters=None):
        """
        Obtiene el historial de entrenamientos con paginación y filtros
        
        Args:
            limit: Número máximo de resultados
            offset: Desplazamiento para la paginación
            filters: Diccionario con filtros a aplicar
            
        Returns:
            dict: Diccionario con resultados y total
        """
        query = ModelTrainingHistory.query.order_by(ModelTrainingHistory.start_time.desc())
        
        # Aplicar filtros si existen
        if filters:
            if 'date_from' in filters and filters['date_from']:
                query = query.filter(ModelTrainingHistory.start_time >= filters['date_from'])
            
            if 'date_to' in filters and filters['date_to']:
                query = query.filter(ModelTrainingHistory.start_time <= filters['date_to'])
            
            if 'training_type' in filters and filters['training_type'] != 'all':
                query = query.filter(ModelTrainingHistory.training_type == filters['training_type'])
            
            if 'status' in filters and filters['status'] != 'all':
                query = query.filter(ModelTrainingHistory.status == filters['status'])
        
        # Contar el total antes de la paginación
        total = query.count()
        
        # Aplicar paginación
        results = query.limit(limit).offset(offset).all()
        
        # Formatear resultados
        formatted_results = []
        
        for training in results:
            # Calcular mejora para RMSE
            improvement = training.calculate_improvement('rmse')
            
            # Formatear duración
            duration_str = ""
            if training.duration_seconds:
                minutes = training.duration_seconds // 60
                seconds = training.duration_seconds % 60
                duration_str = f"{minutes}m {seconds}s"
            
            # Obtener información de datos
            data_info = training.get_data_info()
            data_summary = ""
            
            if data_info:
                rows = data_info.get('rows', 0)
                date_range = data_info.get('date_range', {})
                if date_range:
                    start = date_range.get('start', '')
                    end = date_range.get('end', '')
                    date_str = f"{start} a {end}" if start and end else ""
                    data_summary = f"{rows} registros" + (f" ({date_str})" if date_str else "")
            
            # Métricas
            prev_metrics = training.get_previous_metrics()
            new_metrics = training.get_new_metrics()
            
            formatted_results.append({
                'id': training.id,
                'start_time': training.start_time.strftime('%d/%b/%Y %H:%M'),
                'training_type': training.training_type,
                'data_summary': data_summary,
                'duration': duration_str,
                'prev_rmse': prev_metrics.get('rmse', '-'),
                'new_rmse': new_metrics.get('rmse', '-'),
                'improvement': f"{improvement:.1f}%" if improvement else "-",
                'status': training.status,
                'user_id': training.user_id
            })
        
        return {
            'results': formatted_results,
            'total': total
        }
    
    @staticmethod
    def process_csv_for_training(file, user_id, parameters=None):
        """
        Procesa un archivo CSV para entrenar el modelo Prophet
        
        Args:
            file: El archivo CSV cargado
            user_id: ID del usuario que realiza el entrenamiento
            parameters: Parámetros de configuración para el modelo
            
        Returns:
            dict: Resultados del procesamiento y/o entrenamiento
        """
        if file is None or file.filename == '':
            return {"error": "No se ha seleccionado ningún archivo"}
        
        if not file.filename.endswith('.csv'):
            return {"error": "El archivo debe tener extensión .csv"}
        
        # Guardar el archivo temporalmente
        filename = file.filename
        upload_folder = os.path.join(current_app.root_path, 'uploads')
        
        # Crear directorio si no existe
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        try:
            # Obtener el modelo activo
            active_model = ProphetController.get_active_model()
            
            if not active_model:
                return {"error": "No existe un modelo activo para reentrenar"}
            
            # Cargar y procesar el archivo CSV
            df = pd.read_csv(file_path)
            
            # Verificar que el CSV tiene las columnas necesarias
            required_columns = ["fecha", "ventas"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return {
                    "error": f"El CSV debe contener las columnas: {', '.join(required_columns)}. "
                            f"Columnas faltantes: {', '.join(missing_columns)}"
                }
            
            # Convertir la columna fecha a datetime
            df['fecha'] = pd.to_datetime(df['fecha'])
            
            # Ordenar por fecha
            df = df.sort_values('fecha')
            
            # Generar resumen de los datos
            data_summary = {
                "total_rows": len(df),
                "date_range": {
                    "start": df['fecha'].min().strftime('%Y-%m-%d'),
                    "end": df['fecha'].max().strftime('%Y-%m-%d')
                },
                "sales_summary": {
                    "min": float(df['ventas'].min()),
                    "max": float(df['ventas'].max()),
                    "mean": float(df['ventas'].mean()),
                    "total": float(df['ventas'].sum())
                },
                "preview_data": ProphetController._generate_preview_data(df)
            }
            
            # Obtener métricas actuales del modelo
            current_metrics = active_model.get_metrics()
            
            # Simulación de entrenamiento y nuevas métricas
            # En una implementación real, aquí se entrenaría el modelo Prophet
            # y se obtendrían las métricas reales
            
            # Simular mejora del 10% (esto sería reemplazado por entrenamiento real)
            new_metrics = {
                "rmse": round(current_metrics.get('rmse', 245.78) * 0.9, 2),
                "mae": round(current_metrics.get('mae', 189.32) * 0.9, 2),
                "mape": round(current_metrics.get('mape', 8.5) * 0.9, 2),
                "r2": round(min(current_metrics.get('r2', 0.87) * 1.02, 0.99), 2)
            }
            
            # Crear objeto para almacenar en la sesión
            training_data = {
                "file_info": {
                    "name": filename,
                    "size": os.path.getsize(file_path),
                    "upload_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                "data_summary": data_summary,
                "model_metrics": {
                    "current_model": current_metrics,
                    "new_model": new_metrics
                },
                "model_id": active_model.id,
                "user_id": user_id
            }
            
            return {
                "success": True,
                **training_data
            }
            
        except Exception as e:
            return {"error": f"Error al procesar el archivo: {str(e)}"}
        finally:
            # Eliminar el archivo temporal
            if os.path.exists(file_path):
                os.remove(file_path)
    
    @staticmethod
    def _generate_preview_data(df, max_rows=10):
        """Genera datos de vista previa para visualización"""
        preview_df = df.head(max_rows).copy()
        
        # Convertir fechas a formato string para serialización JSON
        preview_df['fecha'] = preview_df['fecha'].dt.strftime('%Y-%m-%d')
        
        return preview_df.to_dict(orient='records')
    
    @staticmethod
    def train_model(training_data, parameters):
        """
        Entrena el modelo Prophet con los datos proporcionados
        
        Args:
            training_data: Datos para el entrenamiento (de la sesión)
            parameters: Parámetros de configuración para el modelo
            
        Returns:
            dict: Resultados del entrenamiento
        """
        try:
            if not training_data:
                return {"error": "No hay datos de entrenamiento disponibles"}
            
            model_id = training_data.get('model_id')
            user_id = training_data.get('user_id')
            
            if not model_id or not user_id:
                return {"error": "Información de modelo o usuario incompleta"}
            
            # Obtener el modelo
            model = ProphetModel.query.get(model_id)
            
            if not model:
                return {"error": "Modelo no encontrado"}
            
            # Crear registro de entrenamiento
            training = ModelTrainingHistory(
                model_id=model_id,
                user_id=user_id,
                training_type="Retrain",
                data_info=training_data.get('data_summary'),
                previous_metrics=training_data.get('model_metrics', {}).get('current_model', {})
            )
            
            db.session.add(training)
            
            # Simulamos el tiempo de entrenamiento
            import time
            start_time = time.time()
            
            # En una implementación real, aquí se realizaría el entrenamiento real
            # con Prophet usando los parámetros proporcionados
            
            # Convertir parámetros booleanos de string a bool
            cleaned_parameters = {}
            for key, value in parameters.items():
                if key in ['weekly_seasonality', 'yearly_seasonality', 'include_holidays']:
                    cleaned_parameters[key] = value == 'true' or value == True
                else:
                    cleaned_parameters[key] = value
            
            # Simulamos un tiempo de entrenamiento (2 segundos)
            time.sleep(2)
            
            # Tiempo transcurrido
            duration = int(time.time() - start_time)
            
            # Obtener nuevas métricas (simuladas, del análisis previo)
            new_metrics = training_data.get('model_metrics', {}).get('new_model', {})
            
            # Completar entrenamiento
            training.complete_training(
                new_metrics, 
                duration,
                f"Entrenamiento exitoso con parámetros personalizados: {json.dumps(cleaned_parameters)}"
            )
            
            # Actualizar el modelo con nuevos parámetros y métricas
            model.set_parameters(cleaned_parameters)
            model.set_metrics(new_metrics)
            model.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return {
                "success": True,
                "training_id": training.id,
                "duration": duration,
                "metrics": new_metrics,
                "improvement": {
                    "rmse": ProphetController._calculate_improvement(
                        training_data.get('model_metrics', {}).get('current_model', {}).get('rmse', 0),
                        new_metrics.get('rmse', 0)
                    ),
                    "mae": ProphetController._calculate_improvement(
                        training_data.get('model_metrics', {}).get('current_model', {}).get('mae', 0),
                        new_metrics.get('mae', 0)
                    )
                }
            }
            
        except Exception as e:
            # Si hay un error, registrar el entrenamiento como fallido
            if 'training' in locals():
                training.fail_training(f"Error en entrenamiento: {str(e)}")
                db.session.commit()
            
            current_app.logger.error(f"Error en entrenamiento Prophet: {str(e)}")
            traceback.print_exc()
            
            return {"error": f"Error al entrenar el modelo: {str(e)}"}
    
    @staticmethod
    def _calculate_improvement(previous, current):
        """
        Calcula el porcentaje de mejora entre dos valores
        Para métricas donde menor es mejor (como RMSE, MAE)
        """
        if previous == 0:
            return 0
        
        return ((previous - current) / previous) * 100