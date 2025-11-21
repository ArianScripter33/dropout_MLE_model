
import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIONES DE CARGA DE ARTEFACTOS
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_resource
def load_model_artifacts():
    """
    Carga los artefactos del modelo con cache para evitar recarga innecesaria.
    
    Returns:
        tuple: (model, preprocessor, feature_names, class_names)
    """
    try:
        # Adjust path to be relative to this file or absolute
        # Assuming this file is in app/utils.py, parent is app/, parent.parent is root
        base = Path(__file__).resolve().parent.parent
        model_path = base / "models" / "xgboost_model.pkl"
        preprocessor_path = base / "models" / "preprocessor.pkl"
        features_path = base / "models" / "feature_names.pkl"
        
        # Cargar artefactos
        model = joblib.load(str(model_path))
        preprocessor = joblib.load(str(preprocessor_path))
        feature_names = joblib.load(str(features_path))
        
        # Nombres de clases (orden del encoder usado al entrenar)
        class_names = np.array(['Dropout', 'Enrolled', 'Graduate'])
        
        return model, preprocessor, feature_names, class_names
        
    except FileNotFoundError as e:
        st.error(f"❌ No se encontraron los artefactos del modelo. {e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error al cargar artefactos: {e}")
        st.stop()

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIONES DE LÓGICA DE NEGOCIO
# ═══════════════════════════════════════════════════════════════════════════

def classify_risk_level(dropout_probability: float):
    """Retorna (nivel, color, tag) según probabilidad de abandono."""
    if dropout_probability > 0.7:
        return "🔴 ALTO RIESGO", "#d32f2f", "danger"
    elif dropout_probability > 0.4:
        return "🟠 RIESGO MODERADO", "#f57c00", "warning"
    else:
        return "🟢 BAJO RIESGO", "#388e3c", "success"


def create_student_input_df(inputs_dict: dict, feature_names) -> pd.DataFrame:
    """Construye un DataFrame de una fila con todos los features esperados."""
    full = {feat: 0 for feat in feature_names}
    full.update(inputs_dict)
    return pd.DataFrame([full])


def make_prediction(student_input_df: pd.DataFrame, model, preprocessor, class_names) -> dict:
    """Aplica preprocesamiento y predice probabilidades/clase."""
    try:
        # with st.spinner("⏳ Calculando riesgo..."): # Removed spinner for cleaner UI logic
        X = preprocessor.transform(student_input_df)
        proba = model.predict_proba(X)[0]
        pred = int(np.argmax(proba))
        return {
            'prediction': pred,
            'class': class_names[pred],
            'probabilities': {
                'Dropout': float(proba[0]),
                'Enrolled': float(proba[1]),
                'Graduate': float(proba[2]),
            },
            'success': True,
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def calculate_contextual_risk_score(unrc_inputs):
    """
    Calcula una puntuación de riesgo contextual (0-1) basada en la evidencia estadística.
    """
    risk_score = 0.0
    
    # 1. SATISFACCIÓN VOCACIONAL
    if unrc_inputs.get('satisfaccion') == "Insatisfecho":
        risk_score += 0.5
    elif unrc_inputs.get('satisfaccion') == "Parcialmente Satisfecho":
        risk_score += 0.25
    
    # 2. RENDIMIENTO ACADÉMICO - MOMENTUM
    momentum = unrc_inputs.get('momentum', 0)
    if momentum < -0.2:
        risk_score += 0.4
    elif momentum < 0:
        risk_score += 0.15
    
    # 3. DESAFÍO SOCIOECONÓMICO
    if risk_score > 0:
        desafio = unrc_inputs.get('desafio')
        if desafio == "Dificultades Económicas":
            risk_score += 0.1
        elif desafio == "Conflicto Trabajo-Estudio":
            risk_score += 0.08
        elif desafio == "Problemas Personales/Salud":
            risk_score += 0.05
    
    # 4. MODALIDAD A DISTANCIA
    if unrc_inputs.get('modalidad') == "A Distancia":
        risk_score += 0.1
    
    return min(risk_score, 1.0)


def map_unrc_to_model_inputs(unrc_inputs):
    """
    Traduce variables contextuales de UNRC a las variables esperadas por el modelo XGBoost.
    """
    model_inputs = {}
    
    # MAPEO DIRECTO
    model_inputs['Ratio_Aprobacion_S2'] = unrc_inputs.get('momentum', 0)
    model_inputs['Age at enrollment'] = unrc_inputs.get('age', 20)
    model_inputs['Curricular units 1st sem (approved)'] = unrc_inputs.get('s1_aprobadas', 0)
    model_inputs['Curricular units 1st sem (enrolled)'] = unrc_inputs.get('s1_inscritas', 0)
    model_inputs['Curricular units 2nd sem (approved)'] = unrc_inputs.get('s2_aprobadas', 0)
    model_inputs['Curricular units 2nd sem (enrolled)'] = unrc_inputs.get('s2_inscritas', 0)
    
    # MAPEO INTELIGENTE
    contextual_risk = calculate_contextual_risk_score(unrc_inputs)
    
    if contextual_risk > 0.6:
        model_inputs['Tuition fees up to date'] = 0
    else:
        model_inputs['Tuition fees up to date'] = 1
    
    if contextual_risk < 0.3 and unrc_inputs.get('desafio') != "Dificultades Económicas":
        model_inputs['Scholarship holder'] = 1
    else:
        model_inputs['Scholarship holder'] = 0
    
    # AJUSTE POR MODALIDAD
    if unrc_inputs.get('modalidad') == "A Distancia" and model_inputs['Curricular units 2nd sem (enrolled)'] > 5:
        ratio_actual = (
            model_inputs['Curricular units 2nd sem (approved)'] / 
            model_inputs['Curricular units 2nd sem (enrolled)']
            if model_inputs['Curricular units 2nd sem (enrolled)'] > 0 
            else 0
        )
        model_inputs['Curricular units 2nd sem (enrolled)'] = 5
        model_inputs['Curricular units 2nd sem (approved)'] = int(5 * ratio_actual)
    
    return model_inputs
