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
