
import random

def get_student_list():
    """
    Genera una lista de estudiantes simulados para el dashboard.
    """
    students = [
        {
            "id": 1,
            "name": "Sofia Garcés",
            "email": "sofia.garces@universidad.edu",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sofia",
            "risk_score": 0.88,
            "academic_data": {
                "age": 20,
                "s1_aprobadas": 4,
                "s1_inscritas": 6,
                "s2_aprobadas": 2,
                "s2_inscritas": 6,
                "momentum": -0.33
            },
            "context_data": {
                "satisfaccion": "Insatisfecho",
                "modalidad": "Presencial-Híbrida",
                "desafio": "Dificultades Económicas"
            },
            "risk_diagnosis": "Desajuste Vocacional",
            "risk_description": "El estudiante reporta baja satisfacción con la carrera y dificultades económicas.",
            "intervention": "Agendar sesión de orientación vocacional."
        },
        {
            "id": 2,
            "name": "Andrés Kametta",
            "email": "andres.kametta@universidad.edu",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Andres",
            "risk_score": 0.85,
            "academic_data": {
                "age": 22,
                "s1_aprobadas": 3,
                "s1_inscritas": 5,
                "s2_aprobadas": 1,
                "s2_inscritas": 5,
                "momentum": -0.4
            },
            "context_data": {
                "satisfaccion": "Parcialmente Satisfecho",
                "modalidad": "A Distancia",
                "desafio": "Conflicto Trabajo-Estudio"
            },
            "risk_diagnosis": "Conflicto Laboral",
            "risk_description": "Bajo rendimiento asociado a falta de tiempo por trabajo.",
            "intervention": "Consultoría sobre estrategias de conciliación horaria."
        },
        {
            "id": 3,
            "name": "Mariana Garcés",
            "email": "mariana.garces@universidad.edu",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Mariana",
            "risk_score": 0.79,
            "academic_data": {
                "age": 19,
                "s1_aprobadas": 5,
                "s1_inscritas": 6,
                "s2_aprobadas": 3,
                "s2_inscritas": 6,
                "momentum": -0.2
            },
            "context_data": {
                "satisfaccion": "Parcialmente Satisfecho",
                "modalidad": "Presencial-Híbrida",
                "desafio": "Problemas Personales/Salud"
            },
            "risk_diagnosis": "Problemas Personales",
            "risk_description": "Caída moderada en rendimiento y reportes de salud.",
            "intervention": "Derivación a bienestar estudiantil."
        },
        {
            "id": 4,
            "name": "Carlos Ruiz",
            "email": "carlos.ruiz@universidad.edu",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Carlos",
            "risk_score": 0.45,
            "academic_data": {
                "age": 21,
                "s1_aprobadas": 6,
                "s1_inscritas": 6,
                "s2_aprobadas": 5,
                "s2_inscritas": 6,
                "momentum": -0.1
            },
            "context_data": {
                "satisfaccion": "Satisfecho",
                "modalidad": "Presencial-Híbrida",
                "desafio": "Ninguno"
            },
            "risk_diagnosis": "Riesgo Moderado",
            "risk_description": "Ligera disminución en el rendimiento, monitorear.",
            "intervention": "Refuerzo académico puntual."
        },
        {
            "id": 5,
            "name": "Lucía Méndez",
            "email": "lucia.mendez@universidad.edu",
            "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Lucia",
            "risk_score": 0.12,
            "academic_data": {
                "age": 20,
                "s1_aprobadas": 6,
                "s1_inscritas": 6,
                "s2_aprobadas": 6,
                "s2_inscritas": 6,
                "momentum": 0.0
            },
            "context_data": {
                "satisfaccion": "Satisfecho",
                "modalidad": "Presencial-Híbrida",
                "desafio": "Ninguno"
            },
            "risk_diagnosis": "Bajo Riesgo",
            "risk_description": "Trayectoria académica estable y positiva.",
            "intervention": "Ninguna acción requerida."
        }
    ]
    return students
