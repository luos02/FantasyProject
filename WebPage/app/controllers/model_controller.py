import os
import pandas as pd
import json
from datetime import datetime
from flask import current_app, jsonify
from werkzeug.utils import secure_filename

class ModelController:
    @staticmethod
    def process_csv_file(file, parameters=None):
        """
        Procesa un archivo CSV para el entrenamiento del modelo Prophet
        
        Args:
            file: El archivo CSV cargado por el usuario
            parameters: Parámetros de configuración para el modelo Prophet
            
        Returns:
            dict: Un diccionario con los resultados del procesamiento
        """
        if file is None or file.filename == '':
            return {"error": "No se ha seleccionado ningún archivo"}
        
        if not file.filename.endswith('.csv'):
            return {"error": "El archivo debe tener extensión .csv"}
        
        # Guardar el archivo temporalmente
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, 'uploads')
        
        # Crear directorio si no existe
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        try:
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
            
            # Generar resumen básico de los datos
            summary = {
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
                "preview_data": self._generate_preview_data(df)
            }
            
            # Simular métricas de modelo anterior y nuevo
            model_metrics = {
                "current_model": {
                    "rmse": 245.78,
                    "mae": 189.32,
                    "mape": 8.5,
                    "r2": 0.87
                },
                "new_model": {
                    "rmse": 218.43,
                    "mae": 172.15,
                    "mape": 7.8,
                    "r2": 0.89
                }
            }
            
            # Combinar resultados
            result = {
                "success": True,
                "file_info": {
                    "name": filename,
                    "size": os.path.getsize(file_path),
                    "upload_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                "data_summary": summary,
                "model_metrics": model_metrics
            }
            
            return result
            
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
    def train_prophet_model(file_path, parameters):
        """
        Entrena un modelo Prophet con los datos del CSV
        
        Args:
            file_path: Ruta al archivo CSV
            parameters: Parámetros de configuración para Prophet
            
        Returns:
            dict: Resultados del entrenamiento
        """
        # Aquí iría la lógica real de entrenamiento con Prophet
        # Para este ejemplo, solo simularemos resultados
        
        # Simulación de entrenamiento (tiempo artificial)
        import time
        time.sleep(2)  # Simular procesamiento
        
        # Resultados simulados
        return {
            "success": True,
            "training_time": "2m 45s",
            "evaluation_metrics": {
                "rmse": 218.43,
                "mae": 172.15,
                "mape": 7.8,
                "r2": 0.89
            },
            "model_info": {
                "id": f"prophet-model-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "parameters": parameters
            }
        }