document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos DOM
    const uploadBox = document.getElementById('upload-box');
    const fileInput = document.getElementById('data-file');
    const nextButtons = document.querySelectorAll('.next-step');
    const prevButtons = document.querySelectorAll('.prev-step');
    const confirmCheckbox = document.querySelector('.confirm-checkbox input');
    const confirmButton = document.querySelector('.confirm-button');
    const holidaysScale = document.getElementById('holidays-scale');
    const rangeValue = document.querySelector('.range-value');
    
    // Estado de la aplicación
    let currentStep = 1;
    let uploadedFileData = null;
    let charts = {};
    
    // Inicialización de eventos
    initFileUpload();
    initNavigation();
    initRangeInputs();
    initFormValidation();
    
    // Inicializa la carga de archivos
    function initFileUpload() {
        // Evento de clic en la caja de carga
        uploadBox.addEventListener('click', function() {
            fileInput.click();
        });
        
        // Evento de cambio para cuando se selecciona un archivo
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                handleFileUpload(this.files[0]);
            }
        });
        
        // Eventos de arrastrar y soltar
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadBox.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        // Resaltar la zona de carga
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadBox.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadBox.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            uploadBox.classList.add('drag-over');
        }
        
        function unhighlight() {
            uploadBox.classList.remove('drag-over');
        }
        
        // Manejar el evento de soltar
        uploadBox.addEventListener('drop', function(e) {
            const file = e.dataTransfer.files[0];
            if (file) {
                handleFileUpload(file);
            }
        });
    }
    
    // Manejar la carga del archivo
    function handleFileUpload(file) {
        // Validar que es un archivo CSV
        if (!file.name.endsWith('.csv')) {
            showMessage('Error', 'Por favor seleccione un archivo CSV válido.');
            return;
        }
        
        // Crear un formData para enviar el archivo
        const formData = new FormData();
        formData.append('file', file);
        
        // Mostrar indicador de carga
        showLoadingState('Procesando archivo, por favor espere...');
        
        // Enviar archivo al servidor
        fetch('/model/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la carga del archivo');
            }
            return response.json();
        })
        .then(data => {
            hideLoadingState();
            
            if (data.error) {
                showMessage('Error', data.error);
                return;
            }
            
            // Guardar datos para uso posterior
            uploadedFileData = data;
            
            // Mostrar vista previa de datos
            displayDataPreview(data);
            
            // Habilitar el botón de siguiente
            enableNextButton();
            
            // Actualizar resumen en el paso 4
            updateSummary(data);
        })
        .catch(error => {
            hideLoadingState();
            showMessage('Error', 'Error al procesar el archivo: ' + error.message);
        });
    }
    
    // Mostrar vista previa de los datos cargados
    function displayDataPreview(data) {
        // Crear y mostrar un div de vista previa
        const uploadArea = document.querySelector('.upload-area');
        
        let previewElement = document.getElementById('data-preview');
        if (!previewElement) {
            previewElement = document.createElement('div');
            previewElement.id = 'data-preview';
            previewElement.className = 'data-preview';
            uploadArea.after(previewElement);
        }
        
        // Verificar que tenemos la información de resumen de datos
        if (!data.data_summary) {
            showMessage('Error', 'No se pudo obtener el resumen de datos del servidor');
            return;
        }
        
        // Mostrar información resumida del archivo
        const summary = data.data_summary;
        
        // Construir la tabla HTML
        let tableHTML = `
            <h4>Vista previa de datos (${summary.total_rows} filas)</h4>
            <div class="table-wrapper">
                <table class="preview-table">
                    <thead>
                        <tr>
                            <th>Fecha</th>
                            <th>Ventas</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        // Verificar que tenemos datos de vista previa
        if (summary.preview_data && summary.preview_data.length > 0) {
            // Agregar filas de muestra (primeras 5 filas)
            const sampleData = summary.preview_data.slice(0, 5);
            sampleData.forEach(row => {
                tableHTML += `
                    <tr>
                        <td>${row.fecha}</td>
                        <td>$${formatNumber(row.ventas)}</td>
                    </tr>
                `;
            });
        } else {
            tableHTML += `
                <tr>
                    <td colspan="2">No hay datos disponibles para mostrar</td>
                </tr>
            `;
        }
        
        tableHTML += `
                    </tbody>
                </table>
            </div>
            
            <div class="data-stats">
                <div class="stat-item">
                    <span class="stat-label">Rango de fechas:</span>
                    <span class="stat-value">${summary.date_range ? summary.date_range.start + ' a ' + summary.date_range.end : 'No disponible'}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Venta mínima:</span>
                    <span class="stat-value">$${summary.sales_summary ? formatNumber(summary.sales_summary.min) : '0.00'}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Venta máxima:</span>
                    <span class="stat-value">$${summary.sales_summary ? formatNumber(summary.sales_summary.max) : '0.00'}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Venta promedio:</span>
                    <span class="stat-value">$${summary.sales_summary ? formatNumber(summary.sales_summary.mean) : '0.00'}</span>
                </div>
            </div>
        `;
        
        previewElement.innerHTML = tableHTML;
        previewElement.style.display = 'block';
    }
    
    // Actualizar la información de resumen en el paso 4
    function updateSummary(data) {
        if (!data) return;
        
        // Verificar que los elementos existen antes de actualizar
        const summaryElements = document.querySelectorAll('.summary-value');
        if (summaryElements.length < 5) {
            console.error('No se encontraron suficientes elementos para el resumen');
            return;
        }
        
        // Actualizar los campos del resumen
        summaryElements[0].textContent = data.file_info ? data.file_info.name : 'No disponible';
        summaryElements[1].textContent = data.data_summary ? data.data_summary.total_rows.toLocaleString() : '0';
        
        // Verificar que date_range existe
        if (data.data_summary && data.data_summary.date_range) {
            summaryElements[2].textContent = `${data.data_summary.date_range.start} - ${data.data_summary.date_range.end}`;
        } else {
            summaryElements[2].textContent = 'No disponible';
        }
        
        // Calcular mejora estimada solo si tenemos métricas
        if (data.model_metrics && data.model_metrics.current_model && data.model_metrics.new_model) {
            const currentRMSE = data.model_metrics.current_model.rmse;
            const newRMSE = data.model_metrics.new_model.rmse;
            const improvementPct = ((currentRMSE - newRMSE) / currentRMSE * 100).toFixed(1);
            
            const improvementElement = document.querySelector('.summary-value.improvement');
            if (improvementElement) {
                improvementElement.textContent = `${improvementPct}% en precisión`;
            }
        }
    }
    
    // Manejar la navegación entre pasos
    function initNavigation() {
        // Botones siguiente
        nextButtons.forEach(button => {
            button.addEventListener('click', function() {
                const nextStep = parseInt(this.dataset.next);
                if (nextStep) {
                    goToStep(nextStep);
                }
            });
        });
        
        // Botones anterior
        prevButtons.forEach(button => {
            button.addEventListener('click', function() {
                const prevStep = parseInt(this.dataset.prev);
                if (prevStep) {
                    goToStep(prevStep);
                }
            });
        });
    }
    
    // Ir a un paso específico
    function goToStep(step) {
        // Solo permitir avanzar si hay datos cargados (después del paso 1)
        if (step > 1 && !uploadedFileData && currentStep === 1) {
            showMessage('Información', 'Por favor cargue un archivo CSV antes de continuar.');
            return;
        }
        
        // Si vamos al paso de validación, inicializar el gráfico
        if (step === 3) {
            initValidationChart();
            updateMetricsTable();
        }
        
        // Si vamos al paso final, actualizar los parámetros seleccionados
        if (step === 4) {
            updateParametersSummary();
        }
        
        // Actualizar la UI
        document.querySelectorAll('.step').forEach((stepElem, index) => {
            if (index + 1 === step) {
                stepElem.classList.add('active');
            } else {
                stepElem.classList.remove('active');
            }
        });
        
        document.querySelectorAll('.step-content').forEach((content) => {
            if (parseInt(content.dataset.step) === step) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });
        
        currentStep = step;
    }
    
    // Inicializar gráficos de validación
    function initValidationChart() {
        if (!uploadedFileData) return;
        
        const canvasElement = document.getElementById('validationChart');
        if (!canvasElement) {
            console.error('No se encontró el elemento canvas para el gráfico');
            return;
        }
        
        const ctx = canvasElement.getContext('2d');
        
        // Destruir gráfico anterior si existe
        if (charts.validation) {
            charts.validation.destroy();
        }
        
        // Comprobar que tenemos los datos necesarios
        if (!uploadedFileData.data_summary || !uploadedFileData.data_summary.preview_data) {
            console.error('No hay datos disponibles para el gráfico');
            return;
        }
        
        // Obtener datos para el gráfico
        const summary = uploadedFileData.data_summary;
        const previewData = summary.preview_data;
        
        // Extraer fechas y valores
        const dates = previewData.map(row => row.fecha);
        const values = previewData.map(row => row.ventas);
        
        // Generar datos de predicción simulados
        const currentModelPredictions = values.map(val => val * (1 + (Math.random() - 0.5) * 0.3));
        const newModelPredictions = values.map(val => val * (1 + (Math.random() - 0.5) * 0.15));
        
        // Crear el gráfico
        charts.validation = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: 'Datos reales',
                        data: values,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        fill: false,
                        tension: 0.3
                    },
                    {
                        label: 'Modelo actual',
                        data: currentModelPredictions,
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        fill: false,
                        borderDash: [5, 5],
                        tension: 0.3
                    },
                    {
                        label: 'Modelo nuevo',
                        data: newModelPredictions,
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        fill: false,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    },
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Ventas ($)'
                        }
                    }
                }
            }
        });
    }
    
    // Actualizar tabla de métricas
    function updateMetricsTable() {
        if (!uploadedFileData || !uploadedFileData.model_metrics) return;
        
        const currentMetrics = uploadedFileData.model_metrics.current_model;
        const newMetrics = uploadedFileData.model_metrics.new_model;
        
        if (!currentMetrics || !newMetrics) return;
        
        // Verificar que los elementos existen
        const metricsTable = document.querySelector('.metric-comparison table tbody');
        if (!metricsTable) {
            console.error('No se encontró la tabla de métricas');
            return;
        }
        
        // Actualizar valores en la tabla usando las filas directamente
        const rows = metricsTable.querySelectorAll('tr');
        if (rows.length >= 4) {
            // RMSE
            const rmseRow = rows[0];
            const rmseCells = rmseRow.querySelectorAll('td');
            if (rmseCells.length >= 3) {
                rmseCells[1].textContent = currentMetrics.rmse;
                rmseCells[2].innerHTML = `${newMetrics.rmse} <i class="fas fa-arrow-down"></i>`;
            }
            
            // MAE
            const maeRow = rows[1];
            const maeCells = maeRow.querySelectorAll('td');
            if (maeCells.length >= 3) {
                maeCells[1].textContent = currentMetrics.mae;
                maeCells[2].innerHTML = `${newMetrics.mae} <i class="fas fa-arrow-down"></i>`;
            }
            
            // MAPE
            const mapeRow = rows[2];
            const mapeCells = mapeRow.querySelectorAll('td');
            if (mapeCells.length >= 3) {
                mapeCells[1].textContent = currentMetrics.mape + '%';
                mapeCells[2].innerHTML = `${newMetrics.mape}% <i class="fas fa-arrow-down"></i>`;
            }
            
            // R2
            const r2Row = rows[3];
            const r2Cells = r2Row.querySelectorAll('td');
            if (r2Cells.length >= 3) {
                r2Cells[1].textContent = currentMetrics.r2;
                r2Cells[2].innerHTML = `${newMetrics.r2} <i class="fas fa-arrow-up"></i>`;
            }
        }
    }
    
    // Actualizar resumen de parámetros
    function updateParametersSummary() {
        const growth = document.getElementById('growth');
        const changepoints = document.getElementById('changepoints');
        const seasonalityMode = document.getElementById('seasonality-mode');
        const weeklySeasonality = document.getElementById('weekly-seasonality');
        const yearlySeasonality = document.getElementById('yearly-seasonality');
        
        // Verificar que todos los elementos existen
        if (!growth || !changepoints || !seasonalityMode || !weeklySeasonality || !yearlySeasonality) {
            console.error('No se encontraron todos los elementos de parámetros');
            return;
        }
        
        // Construir texto de resumen
        let paramSummary = '';
        
        if (seasonalityMode.value === 'multiplicative') {
            paramSummary += 'Estacionalidad multiplicativa';
        } else {
            paramSummary += 'Estacionalidad aditiva';
        }
        
        paramSummary += `, ${changepoints.value} puntos de cambio`;
        
        if (growth.value === 'logistic') {
            paramSummary += ', crecimiento logístico';
        }
        
        if (!weeklySeasonality.checked && !yearlySeasonality.checked) {
            paramSummary += ', sin estacionalidad';
        } else if (!weeklySeasonality.checked) {
            paramSummary += ', sin estacionalidad semanal';
        } else if (!yearlySeasonality.checked) {
            paramSummary += ', sin estacionalidad anual';
        }
        
        // Actualizar elemento de resumen
        const paramElement = document.querySelector('.summary-item:nth-child(4) .summary-value');
        if (paramElement) {
            paramElement.textContent = paramSummary;
        }
    }
    
    // Inicializar controles de rango
    function initRangeInputs() {
        if (holidaysScale && rangeValue) {
            holidaysScale.addEventListener('input', function() {
                rangeValue.textContent = this.value;
            });
        }
    }
    
    // Inicializar validación del formulario
    function initFormValidation() {
        // Habilitar/deshabilitar botón de confirmación
        if (confirmCheckbox && confirmButton) {
            confirmCheckbox.addEventListener('change', function() {
                confirmButton.disabled = !this.checked;
            });
        }
        
        // Evento de envío para reentrenar
        if (confirmButton) {
            confirmButton.addEventListener('click', trainModel);
        }
    }
    
    // Función para entrenar el modelo
    function trainModel() {
        if (!uploadedFileData) {
            showMessage('Error', 'No hay datos para entrenar el modelo');
            return;
        }
        
        // Verificar que todos los elementos de parámetros existen
        const growth = document.getElementById('growth');
        const changepoints = document.getElementById('changepoints');
        const seasonalityMode = document.getElementById('seasonality-mode');
        const weeklySeasonality = document.getElementById('weekly-seasonality');
        const yearlySeasonality = document.getElementById('yearly-seasonality');
        const includeHolidays = document.getElementById('include-holidays');
        const holidaysScale = document.getElementById('holidays-scale');
        
        if (!growth || !changepoints || !seasonalityMode || 
            !weeklySeasonality || !yearlySeasonality || 
            !includeHolidays || !holidaysScale) {
            showMessage('Error', 'No se pudieron encontrar todos los elementos de parámetros');
            return;
        }
        
        // Recopilar parámetros del formulario
        const parameters = {
            growth: growth.value,
            changepoints: changepoints.value,
            seasonality_mode: seasonalityMode.value,
            weekly_seasonality: weeklySeasonality.checked,
            yearly_seasonality: yearlySeasonality.checked,
            include_holidays: includeHolidays.checked,
            holidays_scale: holidaysScale.value
        };
        
        // Mostrar estado de carga
        showLoadingState('Entrenando modelo, esto puede tomar varios minutos...');
        
        // Enviar solicitud para entrenar
        fetch('/model/train', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(parameters)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al entrenar el modelo');
            }
            return response.json();
        })
        .then(data => {
            hideLoadingState();
            
            if (data.error) {
                showMessage('Error', data.error);
                return;
            }
            
            // Mostrar mensaje de éxito y redirigir
            showMessage('Éxito', 'Modelo reentrenado exitosamente. Redirigiendo a la página principal...');
            
            // Redirigir después de un breve retraso
            setTimeout(() => {
                window.location.href = '/Config/ManageModel';
            }, 2000);
        })
        .catch(error => {
            hideLoadingState();
            showMessage('Error', 'Error al entrenar el modelo: ' + error.message);
        });
    }
    
    // Habilitar el botón de siguiente después de cargar un archivo
    function enableNextButton() {
        const nextButton = document.getElementById('next-to-parameters');
        if (nextButton) {
            nextButton.disabled = false;
        }
    }
    
    // Funciones de utilidad
    
    // Mostrar estado de carga
    function showLoadingState(message) {
        let loadingOverlay = document.getElementById('loading-overlay');
        if (!loadingOverlay) {
            loadingOverlay = document.createElement('div');
            loadingOverlay.id = 'loading-overlay';
            loadingOverlay.className = 'loading-overlay';
            
            const spinner = document.createElement('div');
            spinner.className = 'spinner';
            
            const messageElem = document.createElement('div');
            messageElem.className = 'loading-message';
            messageElem.id = 'loading-message';
            
            loadingOverlay.appendChild(spinner);
            loadingOverlay.appendChild(messageElem);
            document.body.appendChild(loadingOverlay);
        }
        
        const loadingMessage = document.getElementById('loading-message');
        if (loadingMessage) {
            loadingMessage.textContent = message;
        }
        
        loadingOverlay.style.display = 'flex';
    }
    
    // Ocultar estado de carga
    function hideLoadingState() {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }
    
    // Mostrar mensaje
    function showMessage(title, message) {
        alert(`${title}: ${message}`);
    }
    
    // Formatear números
    function formatNumber(num) {
        if (num === undefined || num === null) return '0.00';
        return parseFloat(num).toLocaleString('es-ES', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
});