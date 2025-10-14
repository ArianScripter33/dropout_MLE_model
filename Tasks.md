# Tasks.md

## Fase 2: Análisis y Desarrollo del Modelo (Localmente)

### 1. Análisis Exploratorio de Datos (EDA) en `notebooks/01-EDA.ipynb`
- [ ] Cargar `data/raw/student-dropout-dataset.csv` en un DataFrame de Pandas.
- [ ] **Análisis Inicial de Datos:**
    - [ ] `df.info()`: Verificar tipos de datos y conteo de no nulos.
    - [ ] `df.describe()`: Obtener estadísticas descriptivas para las columnas numéricas.
    - [ ] `df.isnull().sum()`: Cuantificar valores faltantes por columna.
- [ ] **Análisis de la Variable Objetivo (`Target`):**
    - [ ] `df['Target'].value_counts()`: Contar las ocurrencias de cada clase ('Dropout', 'Enrolled', 'Graduate').
    - [ ] Crear un gráfico de barras para visualizar el desbalance de clases.
- [ ] **Análisis Univariado y Bivariado:**
    - [ ] Crear histogramas para las principales variables numéricas (ej. `Admission grade`, `Age at enrollment`).
    - [ ] Crear gráficos de barras para las variables categóricas clave (ej. `Course`, `Marital status`).
    - [ ] Crear boxplots para visualizar la distribución de variables numéricas en relación con la variable `Target`.
    - [ ] Crear una matriz de correlación para identificar relaciones lineales entre variables numéricas.
- [ ] **Documentar Hallazgos Clave:**
    - [ ] Resumir los principales insights sobre la calidad de los datos.
    - [ ] Identificar las variables que parecen más correlacionadas con la deserción.
    - [ ] Formular hipótesis iniciales para el feature engineering.

### 2. Preprocesamiento y Feature Engineering en `notebooks/02-Preprocessing.ipynb`
- [ ] **Actualizar Plan de Preprocesamiento:** Basado en los hallazgos del EDA, refinar las siguientes tareas.
- [ ] **Limpieza de Datos:**
    - [ ] Implementar una estrategia para manejar valores faltantes (ej. imputación con la media/mediana/moda, o eliminación si es apropiado).
- [ ] **Codificación de Variables:**
    - [ ] Aplicar One-Hot Encoding a variables categóricas nominales.
    - [ ] Aplicar Label Encoding o Ordinal Encoding a variables categóricas ordinales.
- [ ] **Creación de Nuevas Características (Feature Engineering):**
    - [ ] Implementar `Ratio_Aprobacion_S1` (Curricular units approved / Curricular units enrolled en el 1er semestre).
    - [ ] Implementar `Ratio_Aprobacion_S2` (Curricular units approved / Curricular units enrolled en el 2do semestre).
    - [ ] Implementar `Delta_Ratio_Aprobacion` (`Ratio_Aprobacion_S2` - `Ratio_Aprobacion_S1`).
- [ ] **Guardar Datos Procesados:**
    - [ ] Guardar el DataFrame limpio y transformado en `data/processed/preprocessed_data.parquet`.
- [ ] **Modularización:**
    - [ ] Crear funciones en `src/data_processing.py` para cada paso del preprocesamiento (ej. `load_data`, `preprocess_features`).

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
