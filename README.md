# SAREP: Modelo Predictivo de Deserción Estudiantil

## 1. Visión General del Proyecto

Este repositorio contiene el código y la documentación para el desarrollo del "Cerebro Analítico" del Sistema de Acompañamiento y Retención Estudiantil Proactivo (SAREP). El objetivo es construir un modelo de Machine Learning capaz de predecir la probabilidad de que un estudiante universitario abandone sus estudios, permitiendo intervenciones tempranas y proactivas.

Este proyecto sirve como una prueba de concepto técnica para el caso de negocio presentado en el informe "De la Puerta Giratoria a la Vía de Graduación".

## 2. Dataset Utilizado

Ante la ausencia de datos públicos granulares de la UNRC, este prototipo se ha desarrollado utilizando un dataset proxy de alta calidad:

*   **Nombre:** Predict Students' Dropout and Academic Success
*   **Fuente:** UCI Machine Learning Repository
*   **Origen:** Datos empíricos de una institución de educación superior en Portugal.
*   **Características:** 4,424 registros, 37 variables (36 predictoras, 1 objetivo).

El dataset original se encuentra en la carpeta `/data/raw/`.

## 3. Metodología y Arquitectura Tecnológica

El proyecto sigue un flujo de trabajo de MLOps moderno nativo de la nube (Google Cloud Platform), desde el procesamiento de datos hasta el despliegue del modelo.


*   **Procesamiento de Datos:** **Google BigQuery** (Enfoque ELT basado en SQL).
*   **Modelo Principal:** `XGBoost Classifier`.
*   **Entrenamiento y Optimización:** **Vertex AI Training** con **Vertex AI Vizier** (sucesor de MLE-Star).
*   **Despliegue del Modelo:** Artefacto guardado en **Google Cloud Storage**.
*   **Dashboard de Prototipo:** Aplicación de **Streamlit** desplegada en **Cloud Run**.

*La visión a largo plazo de la arquitectura está inspirada en los principios de los agentes de ingeniería de ML de vanguardia como **MLE-Star de Google**, apuntando a un sistema que no solo predice, sino que se auto-optimiza y se mantiene en el tiempo.*


## 4. Estructura del Repositorio

*   **/data:** Contiene los datasets raw y procesados.
*   **/notebooks:** Jupyter Notebooks para EDA, preprocesamiento y modelado.
*   **/src:** Scripts de Python con el código modularizado.
*   **/app:** Código para el dashboard interactivo.
*   **/models:** Almacena los artefactos del modelo entrenado.

## 5. Cómo Ejecutar el Proyecto

1.  **Configuración de GCP:**
    *   Crea un proyecto en Google Cloud.
    *   Habilita las APIs de BigQuery, Vertex AI y Cloud Run.
    *   Crea un bucket en Google Cloud Storage.
2.  **Pipeline de Datos:**
    *   Carga `data/raw/student-dropout-dataset.csv` a una tabla en BigQuery.
    *   Ejecuta las consultas SQL de transformación para crear la tabla procesada.
3.  **Pipeline de Entrenamiento:**
    *   Empaqueta el código de `src/` en un contenedor y súbelo a Google Container Registry.
    *   Lanza el trabajo de entrenamiento en Vertex AI, configurando el estudio de Vizier para la optimización.
4.  **Despliegue del Dashboard:**
    *   Empaqueta la app de `app/` en un contenedor y despliégala en Cloud Run.
## 6. Resultados Clave

*El modelo final alcanzó un rendimiento de [Placeholder para métrica clave, ej. AUC de 0.93], demostrando una alta capacidad para distinguir entre estudiantes en riesgo y aquellos que probablemente persistirán. El análisis de Feature Importance reveló que el rendimiento académico en el primer semestre es el predictor más potente.*

