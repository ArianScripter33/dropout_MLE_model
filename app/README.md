# 🎓 SAREP: Dashboard del Tutor - Prototipo Ilustrativo

## 📋 Descripción

Este dashboard es una prueba de concepto que demuestra cómo un modelo de Machine Learning puede transformar datos de estudiantes en insights accionables para tutores y personal académico.

**Stack tecnológico:**
- **Framework**: Streamlit
- **Modelo**: XGBoost Multi-clase (AUC ≈ 0.89)
- **Dataset**: Estudiantes portugueses (4,424 muestras)
- **Classes**: Dropout, Enrolled, Graduate

## 🚀 Cómo ejecutar

### Requisitos previos
- Python 3.9+
- Las dependencias necesarias están instaladas (ver requirements.txt)

### Ejecución rápida
```bash
# Desde la raíz del proyecto
streamlit run app/dashboard.py
```

### Opción alternativa (ejecución detallada)
```bash
# 1. Activar entorno virtual si aplica
source venv/bin/activate  # macOS/Linux

# 2. Ejecutar en modo desarrollo (con refresh automático)
streamlit run app/dashboard.py --server.port 8501 --server.headless false
```

El dashboard abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📁 Estructura del proyecto

```
├── app/
│   ├── dashboard.py           # Dashboard principal
│   └── README.md             # Este documento
├── models/
│   ├── xgboost_model.pkl     # Modelo entrenado
│   ├── preprocessor.pkl      # StandardScaler
│   └── feature_names.pkl     # Lista de features
└── data/
    └── processed/
        └── preprocessed_data.parquet  # Dataset procesado
```

## 🎯 Funcionalidades principales

### 1. Perfil del Estudiante (Barra lateral)
- **Ratio Aprobación S2**: Proporción de unidades aprobadas vs inscritas segundo semestre
- **Unidades académicas**: Aprobadas e inscritas en ambos semestres
- **Situación financiera**: Pagos al día y estatus de beca
- **Edad al ingreso**: Para edad académica

### 2. Evaluación de Riesgo
- **Probabilidades de clase**: Dropout/Enrolled/Graduate
- **Clasificación de riesgo**: ALTO/MODERADO/BAJO basado en umbrales personalizables
- **Visualización gráfica**: Barras para las 3 clases

### 3. Interpretabilidad
- **Factores académicos**: Rendimiento bajo o caída entre semestres
- **Factores financieros**: Pagos atrasados o falta de beca
- **Combinaciones de riesgo**: Detección de múltiples factores simultáneos

### 4. Recomendaciones de Intervención
- **Nivel de urgencia**: Timeline recomendado (24-72h, semanal)
- **Tipo de acción**: Académica, financiera o integral
- **Responsables**: Tutores, servicios estudiantiles, etc.

## ⚙️ Technical Details

### Modelo cargado
```python
# XGBoost Classifier (multi:softprob)
XGBClassifier(
    objective='multi:softprob',
    eval_metric='mlogloss',
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)
```

### Features más importantes
1. Ratio_Aprobacion_S2 (24.9% de importancia)
2. Tuition fees up to date (7.3%)
3. Scholarship holder (4.2%)
4. Curricular units 1st sem (approved) (3.6%)
5. Age at enrollment (1.9%)

### Umbrales de riesgo
- **Alto riesgo**: Prob > 0.7 (70%)
- **Moderado**: 0.4 ≤ Prob ≤ 0.7 (40-70%)
- **Bajo riesgo**: Prob < 0.4 (40%)

## 📊 Casos de uso

### Ejemplo 1: Estudiante de Alto Riesgo
- **Inputs**: Ratio 0.3, Sin beca, Pagos atrasados, 3 unidades aprobadas S1
- **Predicción**: 85% Dropout
- **Factores**: Rendimiento bajo + Estrés financiero (combo riesgo)
- **Acción**: Intervención integral inmediata (24-48h)

### Ejemplo 2: Estudiante de Bajo Riesgo
- **Inputs**: Ratio 0.9, Con beca, Pagos al día, 8 unidades aprobadas S1
- **Predicción**: 15% Dropout
- **Factores**: Ningún factor crítico
- **Acción**: Monitoreo regular

## 🚨 Limitaciones y Disclaimers

- **Dataset portugués**: No representa contexto específico de UNRC ni Argentina
- **Momento temporal**: Modelo entrenado con datos históricos pre-COVID
- **Variables externas**: No captura eventos personales (crisis familiares, mudanzas)
- **Validación**: Prototipo para demostración, no sistema de producción

## 🔄 Flujo operativo sugerido

1. **Tutor/Asesor** ingresa datos del estudiante en el sidebar
2. **Dashboard** muestra probabilidades y nivel de riesgo
3. **Sistema** identifica factores específicos de riesgo
4. **Dashboard** sugiere acciones específicas según caso
5. **Tutor** documenta intervención y programa seguimiento

## 📈 Métricas de modelo

- **AUC (One-vs-Rest)**: 0.8868
- **Precision (Dropout)**: 0.49
- **Recall (Dropout)**: 0.48
- **F1-Score (Dropout)**: 0.48
- **Accuracy Global**: 76%

## 🐛 Solución de problemas

### Mensajes de error más comunes

1. **"No se encontraron los artefactos del modelo"**
   - Verificar que los archivos existan en `models/`
   - Comprobar la ruta de ejecución (desde raíz del proyecto)

2. **"Error al cargar artefactos"**
   - Asegurarse que fue entrenado el modelo
   - Revisar que los artefactos no estén corruptos

3. **Error de Shape mismatch**
   - Reiniciar el servidor (Streamlit cache problema)
   - Verificar que los feature names correspondan

## 📞 Contacto y soporte

Para dudas sobre el dashboard:
- Revisar documentación técnica interna
- Contactar al equipo de desarrollo de SAREP
- Corregir errores en issues del repositorio

---

**SAREP v1.0** - Prototipo de Dashboard para Tutores  
Dataset Portugués | Desarrollo: Nov 2024-2025