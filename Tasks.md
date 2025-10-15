# Tasks.md

## Fase 2: Análisis y Desarrollo del Modelo (Localmente)

### 1. Análisis Exploratorio de Datos (EDA) en `notebooks/01-EDA.ipynb`
- [x] **Carga y Configuración Inicial:**
    - [x] Cargar el dataset `data/raw/data.csv`.
    - [x] Configurar el entorno de visualización (Seaborn, Matplotlib).
- [x] **Análisis de Calidad y Estructura de Datos:**
    - [x] Inspección de tipos de datos, dimensiones y valores nulos (se confirmó que no hay nulos).
    - [x] Verificación de registros duplicados (se confirmó que no hay duplicados).
    - [x] Detección de inconsistencias lógicas (ej. aprobación de materias entre semestres).
    - [x] Identificación de valores atípicos (ej. `Age at enrollment`).
- [x] **Análisis de Variable Objetivo (`Target`):**
    - [x] Cálculo y visualización de la distribución de clases ('Dropout', 'Enrolled', 'Graduate').
    - [x] Análisis de la relación de la variable objetivo con género y edad.
- [x] **Análisis Univariado y Bivariado:**
    - [x] Generación de estadísticas descriptivas detalladas para todas las variables.
    - [x] Creación de histogramas y boxplots para visualizar distribuciones numéricas vs. `Target`.
    - [x] Creación de una matriz de correlación con heatmap para identificar relaciones lineales.
- [x] **Segmentación y Perfiles de Riesgo:**
    - [x] Análisis de la tasa de abandono por grupos de edad y rendimiento académico.
    - [x] Cálculo del riesgo relativo para variables socioeconómicas clave (`Debtor`, `Scholarship holder`).
- [x] **Documentación y Resultados:**
    - [x] Generación de un resumen de insights y hallazgos clave.
    - [x] Formulación de recomendaciones para preprocesamiento y modelado.
    - [x] Extracción y guardado de todas las gráficas generadas en la carpeta `app/static/imagenes/`.

### 2. Preprocesamiento y Feature Engineering en `notebooks/02-Preprocessing.ipynb`
- [x] **Actualizar Plan de Preprocesamiento:** Basado en los hallazgos del EDA, refinar las siguientes tareas.
- [x] **Limpieza de Datos:**
    - [x] Implementar una estrategia para manejar valores faltantes (ej. imputación con la media/mediana/moda, o eliminación si es apropiado).
- [x] **Codificación de Variables:**
    - [x] Aplicar One-Hot Encoding a variables categóricas nominales.
    - [x] Aplicar Label Encoding o Ordinal Encoding a variables categóricas ordinales.
- [x] **Creación de Nuevas Características (Feature Engineering):**
    - [x] Implementar `Ratio_Aprobacion_S1` (Curricular units approved / Curricular units enrolled en el 1er semestre).
    - [x] Implementar `Ratio_Aprobacion_S2` (Curricular units approved / Curricular units enrolled en el 2do semestre).
    - [x] Implementar `Delta_Ratio_Aprobacion` (`Ratio_Aprobacion_S2` - `Ratio_Aprobacion_S1`).
    - [x] Crear características adicionales basadas en EDA: indicadores de rendimiento temprano, categorías de edad, riesgos socioeconómicos.
- [x] **Guardar Datos Procesados:**
    - [x] Guardar el DataFrame limpio y transformado en `data/processed/preprocessed_data.parquet`.
- [x] **Modularización:**
    - [x] Crear funciones en `src/data_processing.py` para cada paso del preprocesamiento (ej. `load_data`, `preprocess_features`).

### 3. Modelado y Evaluación en `notebooks/03-Modeling.ipynb`
- [ ] **Preparación:**
    - [ ] Cargar `data/processed/preprocessed_data.parquet`.
    - [ ] Separar las características (X) y la variable objetivo (y).
    - [ ] Dividir los datos en conjuntos de entrenamiento y prueba (`train_test_split`).
- [ ] **Entrenamiento del Modelo Base:**
    - [ ] Instanciar y entrenar un `XGBoost Classifier` con los hiperparámetros por defecto.
- [ ] **Evaluación del Modelo:**
    - [ ] Realizar predicciones en el conjunto de prueba.
    - [ ] Calcular el **AUC (Area Under the Curve)**.
    - [ ] Generar y visualizar una matriz de confusión.
    - [ ] Calcular otras métricas relevantes (Precision, Recall, F1-score).
- [ ] **Modularización:**
    - [ ] Crear funciones en `src/model.py` para el entrenamiento y la evaluación (ej. `train_model`, `evaluate_model`).
