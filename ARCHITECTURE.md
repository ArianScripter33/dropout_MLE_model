# Arquitectura del Sistema SAREP (Prototipo Cloud-Native)

## 1. Visión General de la Arquitectura

La arquitectura de este prototipo simula un entorno de producción en la nube, utilizando Google Cloud Platform (GCP) para asegurar la escalabilidad, reproducibilidad y eficiencia. El flujo de trabajo se centra en un enfoque ELT (Extract, Load, Transform) utilizando BigQuery como el motor principal de procesamiento de datos.

## 2. Pipeline de Datos (ELT en BigQuery)

1.  **Extracción y Carga (Extract & Load):**
    *   El dataset crudo (`student-dropout-dataset.csv`) se carga manualmente en una tabla de BigQuery llamada `raw_student_data`.

2.  **Transformación (Transform):**
    *   Se utiliza una serie de **consultas SQL o vistas materializadas** en BigQuery para realizar todo el preprocesamiento. Esto es mucho más rápido y escalable que usar Pandas en un notebook.
    *   Las transformaciones incluyen:
        *   Tipado de datos y limpieza.
        *   Codificación de variables categóricas (usando `CASE WHEN ... THEN ...`).
        *   Creación de nuevas características (Feature Engineering), como `Ratio_Aprobacion` y `Delta_Ratio_Aprobacion`.
    *   El resultado final es una tabla limpia y lista para el modelo llamada `processed_student_features`.

## 3. Pipeline de Entrenamiento y Optimización (Vertex AI)

1.  **Entrenamiento (Vertex AI Training):**
    *   Se empaqueta el código de `src/` en un contenedor de Docker.
    *   Se lanza un **trabajo de entrenamiento personalizado** en Vertex AI. El script de entrenamiento se conecta a la tabla `processed_student_features` en BigQuery para obtener los datos.
2.  **Optimización de Hiperparámetros (Vertex AI Vizier):**
    *   El trabajo de entrenamiento en Vertex AI está configurado para usar **Vertex AI Vizier (el sucesor de MLE-Star)**.
    *   Vizier gestiona el bucle de optimización: sugiere combinaciones de hiperparámetros, el trabajo de entrenamiento evalúa esa combinación, reporta el resultado (ej. AUC), y Vizier sugiere la siguiente combinación.
3.  **Serialización (Google Cloud Storage):**
    *   Una vez que Vizier encuentra la mejor combinación, el modelo final se entrena y se guarda como un artefacto (`xgboost_model.pkl`) en un bucket de Google Cloud Storage (GCS).

## 4. Frontend de Inferencia (Dashboard en Cloud Run)

1.  **Aplicación Contenerizada:** La aplicación de Streamlit (`app/dashboard.py`) se empaqueta en su propio contenedor de Docker.
2.  **Despliegue:** Se despliega como un servicio en **Cloud Run**, lo que lo hace una aplicación web pública y escalable.
3.  **Carga del Modelo:** Al iniciar, la aplicación se autentica con GCS y descarga/carga el modelo `xgboost_model.pkl` en memoria.
4.  **Inferencia:** Realiza predicciones en tiempo real como se diseñó previamente.


## 5. Hoja de Ruta de Arquitectura Futura: Hacia un Cerebro Analítico Autónomo

La arquitectura actual del prototipo (v1.0) está diseñada para ser robusta y reproducible. Sin embargo, la visión a largo plazo para SAREP se inspira en los paradigmas de AutoML de nueva generación, como el sistema **MLE-Star de Google** (Google Research, 2025).

En una versión de producción (v2.0), el "Cerebro Analítico" evolucionaría de un modelo estático a un **sistema de auto-mejora continua**, incorporando las capacidades clave de MLE-Star:

*   **Ingeniería de Características Automatizada (Automated Feature Engineering):** Un agente de IA, basado en un LLM, analizaría continuamente los datos de entrada y propondría nuevas características (features) para mejorar el poder predictivo del modelo, yendo más allá de la ingeniería manual inicial.
*   **Pipeline de Auto-Sanación (Self-Healing Pipeline):** El sistema sería capaz de detectar problemas comunes como el **data leakage** o el **training-serving skew** (desajuste entre entrenamiento e inferencia) y sugerir o aplicar correcciones de forma autónoma.
*   **Monitoreo y Re-entrenamiento Proactivo (Proactive Monitoring and Retraining):** El agente monitorearía el rendimiento del modelo en producción para detectar el **model drift** (degradación del modelo con el tiempo). Al detectar una caída en el rendimiento, podría iniciar automáticamente un ciclo de re-entrenamiento con datos frescos para mantener la precisión.

Esta visión transforma a SAREP de una herramienta predictiva a una **plataforma de inteligencia viva**, que aprende y se adapta, asegurando la sostenibilidad y la eficacia a largo plazo de la inversión.

**Referencia Clave:**
*   Google Research. (2025). *MLE-Star: A State-of-the-Art Machine Learning Engineering Agent*. Google Research Blog. [Enlace del blog: https://research.google/blog/mle-star-a-state-of-the-art-machine-learning-engineering-agents/]