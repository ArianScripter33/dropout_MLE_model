# Documento de Requisitos del Producto (PRD): SAREP - Cerebro Analítico v1.0

## 1. Visión del Producto

Construir un prototipo funcional del componente de análisis predictivo de SAREP, capaz de demostrar la viabilidad de identificar proactivamente a estudiantes en riesgo de deserción en la UNRC.

## 2. User Personas y Casos de Uso

*   **Usuario Principal:** **Carlos, el Tutor/Asesor Académico.**
    *   **Necesidad:** Necesita saber en qué estudiantes enfocar su tiempo limitado. Quiere pasar de un seguimiento reactivo a intervenciones proactivas.
    *   **Caso de Uso:** Carlos introduce los datos de un nuevo estudiante en el sistema y recibe un puntaje de riesgo instantáneo, junto con una lista de los factores que más contribuyen a ese riesgo.

## 3. Requisitos Funcionales (Lo que el sistema DEBE hacer)

*   **FR-01: Ingesta de Datos:** El sistema debe ser capaz de procesar el dataset proxy especificado.
*   **FR-02: Predicción de Riesgo:** El sistema debe generar un puntaje de probabilidad de abandono (de 0.0 a 1.0) para un estudiante individual.
*   **FR-03: Interpretabilidad del Modelo:** El sistema debe ser capaz de identificar y mostrar las 3-5 características principales que influyeron en la predicción de un estudiante específico (explicabilidad local, ej. usando SHAP).
*   **FR-04: Dashboard de Simulación:** Debe existir una interfaz web simple (dashboard) que permita a un usuario introducir datos de un estudiante y ver la predicción y sus factores.

## 4. Requisitos No Funcionales (Cómo DEBE ser el sistema)

*   **NFR-01: Rendimiento del Modelo:** El modelo predictivo debe alcanzar un Área Bajo la Curva (AUC) mínima de **0.85** en el conjunto de datos de prueba para ser considerado viable.
*   **NFR-02: Documentación:** Todo el código debe estar comentado y el proceso debe ser reproducible a través de los Jupyter Notebooks.
*   **NFR-03: Modularidad:** El código para el preprocesamiento de datos y el entrenamiento del modelo debe estar en funciones reutilizables dentro de la carpeta `/src`.

## 5. Fuera de Alcance (Lo que NO haremos en esta versión)

*   Integración con bases de datos en tiempo real de la UNRC.
*   Sistemas de autenticación de usuarios.
*   El dashboard para la "Directora Laura" (vista agregada).
*   Envío automatizado de notificaciones.