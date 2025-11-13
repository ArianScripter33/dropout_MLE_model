"""
🎓 SAREP: Dashboard del Tutor - Prototipo Ilustrativo
======================================================
Sistema interactivo para evaluar riesgo de abandono estudiantil
usando un modelo XGBoost entrenado con datos portugueses.

Objetivo: Demostrar cómo los datos se convierten en predicciones accionables.
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════════
# 1️⃣  CONFIGURACIÓN DE PÁGINA
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SAREP: Dashboard del Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════
# 2️⃣  FUNCIONES DE CARGA DE ARTEFACTOS (CACHEADAS)
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_resource
def load_model_artifacts():
    """
    Carga los artefactos del modelo con cache para evitar recarga innecesaria.
    
    Returns:
        tuple: (model, preprocessor, feature_names, class_names)
    """
    try:
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
# 3️⃣  CARGAR ARTEFACTOS AL INICIALIZAR
# ═══════════════════════════════════════════════════════════════════════════

model, preprocessor, feature_names, class_names = load_model_artifacts()


# ═══════════════════════════════════════════════════════════════════════════
# 4️⃣  FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════

def classify_risk_level(dropout_probability: float):
    """Retorna (nivel, color, tag) según probabilidad de abandono."""
    if dropout_probability > 0.7:
        return "🔴 ALTO RIESGO", "#d32f2f", "danger"
    elif dropout_probability > 0.4:
        return "🟠 RIESGO MODERADO", "#f57c00", "warning"
    else:
        return "🟢 BAJO RIESGO", "#388e3c", "success"


def create_student_input_df(inputs_dict: dict) -> pd.DataFrame:
    """Construye un DataFrame de una fila con todos los features esperados."""
    full = {feat: 0 for feat in feature_names}
    full.update(inputs_dict)
    return pd.DataFrame([full])


def make_prediction(student_input_df: pd.DataFrame) -> dict:
    """Aplica preprocesamiento y predice probabilidades/clase."""
    try:
        with st.spinner("⏳ Calculando riesgo..."):
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


# ═══════════════════════════════════════════════════════════════════════════
# 5️⃣  INICIALIZAR SESSION STATE PARA CALLBACKS BIDIRECCIONALES
# ═══════════════════════════════════════════════════════════════════════════

if 'ratio_s2' not in st.session_state:
    st.session_state.ratio_s2 = 0.8
if 'aprobadas_s2' not in st.session_state:
    st.session_state.aprobadas_s2 = 8
if 'inscritas_s2' not in st.session_state:
    st.session_state.inscritas_s2 = 10
if 'update_mode' not in st.session_state:  # 'ratio' o 'numbers'
    st.session_state.update_mode = 'ratio'


def update_ratio_from_numbers():
    """Actualiza el ratio basado en las unidades aprobadas e inscritas."""
    if st.session_state.inscritas_s2 > 0:
        st.session_state.ratio_s2 = round(
            st.session_state.aprobadas_s2 / st.session_state.inscritas_s2, 2
        )
        st.session_state.update_mode = 'numbers'


def update_numbers_from_ratio():
    """Actualiza las aprobadas basado en el ratio (inscritas se mantiene constante)."""
    st.session_state.aprobadas_s2 = round(
        st.session_state.ratio_s2 * st.session_state.inscritas_s2
    )
    st.session_state.update_mode = 'ratio'


def validate_s2_numbers():
    """Valida que las aprobadas no superen las inscritas."""
    if st.session_state.aprobadas_s2 > st.session_state.inscritas_s2:
        st.session_state.aprobadas_s2 = st.session_state.inscritas_s2
        st.warning("⚠️ Aprobadas no pueden superar Inscritas. Ajustando automáticamente.")
    update_ratio_from_numbers()


# ═══════════════════════════════════════════════════════════════════════════
# 6️⃣  INTERFAZ DE USUARIO
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(
    """
    <div style='text-align:center;padding:16px'>
      <h1>🎓 SAREP: Dashboard del Tutor</h1>
      <p style='color:#666'>Prototipo ilustrativo para evaluación de riesgo de abandono</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    """
    📊 Este prototipo carga un modelo XGBoost entrenado (AUC≈0.89) y permite
    ingresar un perfil de estudiante para estimar el riesgo de abandono.
    ℹ️ **Interactividad Inteligente**: Los campos de unidades y ratio están sincronizados.
    Modifica cualquiera y los demás se actualizarán automáticamente.
    """
)

# Sidebar — Perfil del estudiante
st.sidebar.header("📝 Perfil del Estudiante")
st.sidebar.markdown(
    "*Campos sincronizados: Modifica unidades o ratio y los demás se actualizan*",
    help="Los tres campos están vinculados para mantener la coherencia de datos"
)

col1, col2 = st.sidebar.columns(2)
with col1:
    age = st.number_input("👤 Edad al ingreso", 17, 80, 20, 1, help="Edad del estudiante")

with col2:
    # Placeholder para simetría visual
    st.empty()

# SECCIÓN SINCRONIZADA: Unidades y Ratio S2
st.sidebar.divider()
st.sidebar.subheader("🔄 Unidades 2do Semestre (Sincronizadas)")

c1, c2 = st.sidebar.columns(2)
with c1:
    st.number_input(
        "✅ Aprobadas S2",
        key='aprobadas_s2',
        min_value=0,
        max_value=30,
        step=1,
        on_change=validate_s2_numbers,
        help="Unidades curriculares aprobadas (cambia esto para recalcular ratio)"
    )

with c2:
    st.number_input(
        "📋 Inscritas S2",
        key='inscritas_s2',
        min_value=1,  # Evita división por cero
        max_value=30,
        step=1,
        on_change=update_ratio_from_numbers,
        help="Unidades curriculares inscritas (cambia esto para recalcular ratio)"
    )

# Sección con información what-if
col_info, col_toggle = st.sidebar.columns([3, 1])
with col_toggle:
    # Indicador visual del modo actual
    mode_icon = "🔄" if st.session_state.update_mode == 'ratio' else "✏️"
    st.markdown(
        f'<div style="text-align:center">{mode_icon}</div>',
        help="🔄: Cambio reciente en ratio | ✏️: Cambio reciente en unidades"
    )

with col_info:
    if st.session_state.update_mode == 'ratio':
        st.caption("ℹ️ Modo what-if activo: Cambiando ratio")
    else:
        st.caption("ℹ️ Modo datos: Cambiando unidades")

st.slider(
    "📈 Ratio Aprobación S2",
    key='ratio_s2',
    min_value=0.0,
    max_value=1.0,
    step=0.01,
    on_change=update_numbers_from_ratio,
    help="Explora escenarios what-if: El ratio actualiza las unidades aprobadas"
)

# SECCIÓN NORMAL: Otros datos
st.sidebar.divider()
st.sidebar.subheader("📊 Primer Semestre")

c3, c4 = st.sidebar.columns(2)
with c3:
    s1_app = st.number_input("✅ Aprobadas S1", 0, 30, 8, 1, help="Unidades aprobadas en 1er semestre")
with c4:
    s1_enr = st.number_input("📋 Inscritas S1", 1, 30, 10, 1, help="Unidades inscritas en 1er semestre")

# Validar S1
if s1_app > s1_enr:
    st.sidebar.warning("⚠️ Aprobadas S1 no pueden superar Inscritas S1")
    s1_app = s1_enr

st.sidebar.divider()
st.sidebar.subheader("💳 Situación del Estudiante")

c7, c8 = st.sidebar.columns(2)
with c7:
    tuition_ok = st.selectbox("💳 Pagos al día", ["Sí", "No"], help="¿Está al día con los pagos?") == "Sí"
with c8:
    scholarship = st.selectbox("🎓 Becario", ["Sí", "No"], help="¿Posee beca?") == "Sí"

# Ejemplos predefinidos para facilitar demostración
st.sidebar.divider()
st.sidebar.caption("💡 Ejemplos rápidos (click para cargar)")
col_ej1, col_ej2, col_ej3 = st.sidebar.columns(3)

# Ejemplo 1: Estudiante de alto riesgo
with col_ej1:
    if st.button("🔴 Alto Riesgo", help="Estudiante con problemas académicos y financieros"):
        st.session_state.ratio_s2 = 0.25
        st.session_state.aprobadas_s2 = 2
        st.session_state.inscritas_s2 = 8
        st.session_state.update_mode = 'ratio'
        st.sidebar.success("✅ Perfil de alto riesgo cargado")
        st.rerun()

# Ejemplo 2: Estudiante de bajo riesgo
with col_ej2:
    if st.button("🟢 Bajo Riesgo", help="Estudiante con buen rendimiento académico"):
        st.session_state.ratio_s2 = 0.85
        st.session_state.aprobadas_s2 = 12
        st.session_state.inscritas_s2 = 14
        st.session_state.update_mode = 'ratio'
        st.sidebar.success("✅ Perfil de bajo riesgo cargado")
        st.rerun()

# Ejemplo 3: Caso límite
with col_ej3:
    if st.button("⚠️ Caso Límite", help="Estudiante en situación crítica"):
        st.session_state.ratio_s2 = 0.0
        st.session_state.aprobadas_s2 = 0
        st.session_state.inscritas_s2 = 10
        st.session_state.update_mode = 'numbers'
        st.sidebar.success("✅ Caso límite cargado")
        st.rerun()

calculate = st.sidebar.button("🔍 Calcular Riesgo de Abandono", use_container_width=True, type="primary")
# Validar S1 otra vez (por si se modificó)
if s1_app > s1_enr:
    s1_app = s1_enr
    st.sidebar.warning("⚠️ Aprobadas S1 no pueden superar Inscritas S1")
    st.rerun()

if calculate:
    # Usar valores del session_state para los campos sincronizados
    inputs = {
        'Ratio_Aprobacion_S2': st.session_state.ratio_s2,
        'Age at enrollment': age,
        'Curricular units 1st sem (approved)': s1_app,
        'Curricular units 1st sem (enrolled)': s1_enr,
        'Curricular units 2nd sem (approved)': st.session_state.aprobadas_s2,
        'Curricular units 2nd sem (enrolled)': st.session_state.inscritas_s2,
        'Tuition fees up to date': 1 if tuition_ok else 0,
        'Scholarship holder': 1 if scholarship else 0,
    }
    X_one = create_student_input_df(inputs)
    result = make_prediction(X_one)
    if result['success']:
        st.session_state.pred = result
        st.session_state.inputs = inputs
    else:
        st.error(f"Error en la predicción: {result['error']}")

# Resultados
if 'pred' in st.session_state:
    res = st.session_state.pred
    inputs = st.session_state.inputs
    p_dropout = res['probabilities']['Dropout']

    st.subheader("📊 Evaluación de Riesgo")
    m1, m2, m3 = st.columns(3)
    with m1:
        level, color, _ = classify_risk_level(p_dropout)
    # Panel de métricas principales
        st.metric(
            "Riesgo de Abandono", 
            f"{p_dropout*100:.1f}%", 
            delta=level
        )
        
        # Indicador de consistencia de datos
        coherence_score = 1.0 - abs(inputs['Ratio_Aprobacion_S2'] - (inputs['Curricular units 2nd sem (approved)'] / inputs['Curricular units 2nd sem (enrolled)'] if inputs['Curricular units 2nd sem (enrolled)'] > 0 else 1.0))
        if coherence_score < 0.95:
            st.error("⚠️ Datos inconsistentes detectados")
            with st.expander("ℹ️ Detalles de inconsistencia"):
                delta = abs(inputs['Ratio_Aprobacion_S2'] - (inputs['Curricular units 2nd sem (approved)'] / inputs['Curricular units 2nd sem (enrolled)'] if inputs['Curricular units 2nd sem (enrolled)'] > 0 else 0))
                st.write(f"Diferencia entre ratio y calculado: {delta:.4f}")
        
        # Análisis what-if
        if st.session_state.update_mode == 'ratio':
            st.caption("💡 Análisis de sensibilidad explorando escenarios de ratio")
        else:
            st.caption("📊 Predicción basada en datos insertados")
            
    with m2:
        st.metric("Prob. Graduación", f"{res['probabilities']['Graduate']*100:.1f}%")
    with m3:
        st.metric("Prob. Continuidad", f"{res['probabilities']['Enrolled']*100:.1f}%")

    st.markdown("### 📈 Distribución de probabilidades")
    chart_df = pd.DataFrame({
        'Clase': ['Dropout', 'Enrolled', 'Graduate'],
        'Probabilidad': [
            res['probabilities']['Dropout'],
            res['probabilities']['Enrolled'],
            res['probabilities']['Graduate'],
        ],
    }).set_index('Clase')
    st.bar_chart(chart_df, height=300, use_container_width=True)

    st.divider()
    st.subheader("🔍 Principales Factores de Riesgo")
    factors = []
    if inputs['Ratio_Aprobacion_S2'] < 0.5:
        factors.append(("error", "🚨 Caída crítica del rendimiento en el 2do semestre"))
    if inputs['Curricular units 1st sem (approved)'] < 3:
        factors.append(("error", "🚨 Bajo rendimiento en el 1er semestre"))
    if inputs['Tuition fees up to date'] == 0:
        factors.append(("warning", "⚠️ Indicador de estrés financiero (pagos no al día)"))
    if inputs['Scholarship holder'] == 0 and inputs['Tuition fees up to date'] == 0:
        factors.append(("error", "⚠️ Riesgo financiero acumulado (sin beca y pagos atrasados)"))

    if not factors:
        st.success("✅ No se detectaron factores de riesgo significativos")
    else:
        for sev, msg in factors:
            (st.error if sev == 'error' else st.warning)(msg)

    st.divider()
    st.subheader("✅ Recomendaciones de Intervención")
    acad = any(sev == 'error' and 'rendimiento' in msg for sev, msg in factors)
    fin = any('financier' in msg for _, msg in factors)
    if acad and fin:
        st.warning("🎯 Atención integral (académica + financiera). Coordinar plan inmediato (24-48h).")
    elif acad:
        st.info("📚 Tutoría académica y revisión de plan de estudios. Seguimiento semanal.")
    elif fin:
        st.info("💰 Contacto con programas de apoyo económico y becas de emergencia (48-72h).")
    else:
        st.success("Sin intervención inmediata. Monitoreo regular.")

    with st.expander("🔧 Información técnica"):
        st.write(
            "Modelo XGBoost (multiclase). AUC de referencia ≈ 0.89. Clases: Dropout, Enrolled, Graduate."
        )
        st.write(pd.DataFrame([inputs]).T.rename(columns={0: 'Valor'}))
else:
    st.markdown(
        """
        <div style='text-align:center;padding:32px;color:#666'>
          <h3>👈 Ingresa el perfil del estudiante en el sidebar y presiona "Calcular"</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()
st.caption("SAREP v1.0 — Prototipo | Dataset Portugués | 2024-2025")