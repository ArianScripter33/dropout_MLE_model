# Arquitectura del Sistema SAREP: Un Enfoque Híbrido

## 1. Visión General: Un Enfoque Híbrido y Fásico

Este proyecto adopta una estrategia de desarrollo en dos fases, diseñada para maximizar la velocidad de entrega de valor y, al mismo tiempo, construir una narrativa sólida para una solución escalable y de nivel de producción.

*   **Fase 1: Construcción y Validación Local (Implementación Actual):** Enfocada en la creación rápida de un modelo de alto rendimiento en un entorno local (PC, Google Colab). El objetivo es validar la hipótesis, obtener métricas clave y tener un artefacto funcional sin la sobrecarga de la infraestructura en la nube.
*   **Fase 2: Arquitectura de Producción Escalable (Visión para el Informe):** Describe la arquitectura ideal y robusta en Google Cloud Platform (GCP) que tomaría este prototipo y lo convertiría en un servicio empresarial sostenible, escalable y automatizado.

---

## 2. Fase 1: Prototipado y Validación Local (Implementación Actual)

El flujo de trabajo actual se ejecuta íntegramente en un entorno local para agilizar la experimentación y el desarrollo.

1.  **Entorno de Desarrollo:**
    *   **IDE:** Jupyter Notebooks o Google Colab.
    *   **Librerías Principales:** Pandas, Scikit-learn, XGBoost, Matplotlib, Seaborn, y **Optuna** para la optimización de hiperparámetros.

2.  **Pipeline de Datos y Modelo:**
    *   **Carga y Preprocesamiento:** Los datos se cargan desde un archivo CSV local (`data/raw/data.csv`) en un DataFrame de Pandas. Todas las tareas de limpieza, transformación y ingeniería de características se realizan en memoria con Pandas.
    *   **Optimización de Hiperparámetros:** Se utiliza **Optuna** para encontrar la combinación óptima de hiperparámetros para el modelo XGBoost de manera eficiente.
    *   **Entrenamiento y Serialización:** El modelo final se entrena con los mejores hiperparámetros y se guarda como un archivo `xgboost_model.pkl` en el directorio local `/models`.

3.  **Dashboard de Simulación Local:**
    *   La aplicación de Streamlit (`app/dashboard.py`) se ejecuta localmente.
    *   Carga el modelo `xgboost_model.pkl` desde el disco local para realizar inferencias en tiempo real.

**Ventaja de esta fase:** Rapidez, agilidad y enfoque total en la ciencia de datos para obtener un modelo funcional y métricas de rendimiento rápidamente.

---

## 3. Fase 2: Arquitectura de Producción Escalable (Visión a Futuro)

Esta sección describe cómo el prototipo local evolucionaría hacia una solución de producción robusta en Google Cloud Platform (GCP).

### 3.1. Pipeline de Datos (ELT en BigQuery)

*   **Justificación:** Procesar grandes volúmenes de datos con Pandas en una máquina virtual tiene límites. **BigQuery** ofrece una capacidad de procesamiento masivamente paralela y un enfoque ELT (Extract, Load, Transform) que es ideal para la escala.
*   **Flujo:**
    1.  **Extracción y Carga (E/L):** El dataset crudo se ingesta y almacena en una tabla de BigQuery (`raw_student_data`).
    2.  **Transformación (T):** Se ejecutan **consultas SQL** sobre BigQuery para realizar todo el preprocesamiento. Esto es órdenes de magnitud más rápido y escalable. El resultado es una tabla limpia y lista para el modelo (`processed_student_features`).

### 3.2. Pipeline de Entrenamiento y Optimización (Vertex AI)

*   **Justificación:** **Vertex AI** proporciona un entorno gestionado para MLOps, eliminando la necesidad de administrar infraestructura y facilitando la automatización y reproducibilidad.
*   **Flujo:**
    1.  **Entrenamiento Personalizado:** El código de `src/` se empaqueta en un contenedor Docker y se ejecuta como un **trabajo de entrenamiento personalizado** en Vertex AI, que lee los datos directamente desde BigQuery.
    2.  **Optimización de Hiperparámetros con Vertex AI Vizier:** En lugar de Optuna, se utiliza **Vertex AI Vizier**. Vizier es un servicio de optimización de caja negra totalmente gestionado, ideal para realizar búsquedas inteligentes de hiperparámetros a gran escala y gestionar cientos de "trials" de forma automática.
    3.  **Registro y Serialización:** El mejor modelo se registra en el **Vertex AI Model Registry** y el artefacto (`.pkl`) se guarda en un bucket de **Google Cloud Storage (GCS)**.

### 3.3. Frontend de Inferencia (Dashboard en Cloud Run)

*   **Justificación:** Para que el dashboard sea una aplicación web pública, segura y autoescalable, **Cloud Run** es la solución perfecta.
*   **Flujo:**
    1.  **Contenerización:** La aplicación de Streamlit se empaqueta en un contenedor Docker.
    2.  **Despliegue:** Se despliega como un servicio en Cloud Run. Cloud Run escala automáticamente (incluso a cero) según el tráfico, por lo que solo se paga por el uso real.
    3.  **Inferencia:** La aplicación en Cloud Run se autentica de forma segura, descarga el modelo desde GCS al iniciar y sirve las predicciones.

## 4. Visión a Largo Plazo: Hacia un Cerebro Analítico Autónomo con MLE-Star

La arquitectura de producción (Fase 2) es la base para una visión aún más ambiciosa, inspirada en los agentes de ML de nueva generación como **MLE-Star de Google**. En una futura versión, el sistema no solo predeciría, sino que se auto-mejoraría continuamente:

*   **Ingeniería de Características Automatizada:** Un agente de IA propondría nuevas características para mejorar el modelo.
*   **Pipeline de Auto-Sanación:** El sistema detectaría y corregiría problemas como el *data leakage* de forma autónoma.
*   **Monitoreo y Re-entrenamiento Proactivo:** El agente monitorearía el *model drift* y lanzaría ciclos de re-entrenamiento automáticamente para mantener la precisión del modelo a lo largo del tiempo.

Esta visión transforma a SAREP de una herramienta predictiva a una **plataforma de inteligencia viva**, asegurando su relevancia y eficacia a largo plazo.