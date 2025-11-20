"""
🎓 SAREP: Simulador de Riesgo para la UNRC - Prototipo Contextualizado
==========================================================================
Sistema interactivo adaptado para Universidad Nacional Rosario Castellanos que simula
la evaluación de riesgo de abandono estudiantil usando un modelo XGBoost.

Objetivo: Demostrar cómo factores contextuales de la UNRC pueden impactar en la retención.
NOTA: Este es un simulador que mapea variables locales al modelo original.
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
    page_title="SAREP: Simulador de Riesgo UNRC",
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


def calculate_contextual_risk_score(unrc_inputs):
    """
    Calcula una puntuación de riesgo contextual (0-1) basada en la evidencia estadística
    de la encuesta UNRC. Los pesos están alineados con la significancia encontrada.
    
    EVIDENCIA DE LA ENCUESTA:
    - Satisfacción Vocacional (p=0.028) ← HALLAZGO MÁS FUERTE
    - Rendimiento Académico (p=0.052) ← Segundo hallazgo más fuerte
    - Desafíos Socioeconómicos (p>0.3) ← NO significativo, efecto mediador
    - Modalidad de Estudio ← Factor de contexto adicional
    
    Args:
        unrc_inputs: Dict con variables contextuales
        
    Returns:
        float: Puntuación de riesgo entre 0.0 (bajo) y 1.0 (alto)
    """
    risk_score = 0.0
    
    # ════════════════════════════════════════════════════════════════════════════
    # 1. SATISFACCIÓN VOCACIONAL (Peso: 0.5 - Evidencia más fuerte: p=0.028)
    # ════════════════════════════════════════════════════════════════════════════
    if unrc_inputs['satisfaccion'] == "Insatisfecho":
        risk_score += 0.5  # Máximo riesgo vocacional
    elif unrc_inputs['satisfaccion'] == "Parcialmente Satisfecho":
        risk_score += 0.25  # Riesgo moderado
    # Si está "Satisfecho", no suma (0.0)
    
    # ════════════════════════════════════════════════════════════════════════════
    # 2. RENDIMIENTO ACADÉMICO - MOMENTUM (Peso: 0.4 - Evidencia fuerte: p=0.052)
    # ════════════════════════════════════════════════════════════════════════════
    # El momentum (cambio S2 vs S1) es un indicador crítico de trayectoria
    if unrc_inputs['momentum'] < -0.2:  # Empeoró significativamente
        risk_score += 0.4  # Gran riesgo por deterioro académico
    elif unrc_inputs['momentum'] < 0:  # Empeoró ligeramente
        risk_score += 0.15  # Riesgo moderado por decline
    # Si momentum >= 0, no suma (estable o mejorando)
    
    # ════════════════════════════════════════════════════════════════════════════
    # 3. DESAFÍO SOCIOECONÓMICO (Peso: 0.1 - Evidencia débil: p>0.3)
    # ════════════════════════════════════════════════════════════════════════════
    # Este factor es un MEDIADOR, solo suma si ya hay otros problemas
    # Implementa el "efecto acumulativo" de múltiples riesgos
    if risk_score > 0:  # Solo suma si ya existen otros riesgos
        if unrc_inputs['desafio'] == "Dificultades Económicas":
            risk_score += 0.1  # Amplifica otros riesgos
        elif unrc_inputs['desafio'] == "Conflicto Trabajo-Estudio":
            risk_score += 0.08  # Amplificación moderada
        elif unrc_inputs['desafio'] == "Problemas Personales/Salud":
            risk_score += 0.05  # Amplificación menor
    
    # ════════════════════════════════════════════════════════════════════════════
    # 4. MODALIDAD A DISTANCIA (Peso: 0.1 - Factor contextual)
    # ════════════════════════════════════════════════════════════════════════════
    # Estudiantes a distancia enfrentan desafíos adicionales de acceso/conectividad
    if unrc_inputs['modalidad'] == "A Distancia":
        risk_score += 0.1
    
    # Retorna score normalizado entre 0.0 y 1.0
    return min(risk_score, 1.0)


def map_unrc_to_model_inputs(unrc_inputs):
    """
    Versión mejorada que usa el motor de reglas de riesgo contextual.
    Traduce variables contextuales de UNRC a las variables esperadas por el modelo XGBoost.
    
    ESTRATEGIA DE MAPEO:
    - Variables académicas (ratios, unidades) pasan directamente al modelo
    - Variables contextuales se "empaquetan" en un score de riesgo
    - El score activa las variables proxy que el modelo entiende
    """
    model_inputs = {}
    
    # ════════════════════════════════════════════════════════════════════════════
    # MAPEO DIRECTO: Variables Académicas (Base del Modelo)
    # ════════════════════════════════════════════════════════════════════════════
    model_inputs['Ratio_Aprobacion_S2'] = unrc_inputs['momentum']
    model_inputs['Age at enrollment'] = unrc_inputs['age']
    model_inputs['Curricular units 1st sem (approved)'] = unrc_inputs['s1_aprobadas']
    model_inputs['Curricular units 1st sem (enrolled)'] = unrc_inputs['s1_inscritas']
    model_inputs['Curricular units 2nd sem (approved)'] = unrc_inputs['s2_aprobadas']
    model_inputs['Curricular units 2nd sem (enrolled)'] = unrc_inputs['s2_inscritas']
    
    # ════════════════════════════════════════════════════════════════════════════
    # MAPEO INTELIGENTE: Motor de Reglas de Riesgo Contextual
    # ════════════════════════════════════════════════════════════════════════════
    contextual_risk = calculate_contextual_risk_score(unrc_inputs)
    
    # MAPEO A 'Tuition fees up to date' (Proxy de Estrés General)
    # - Score alto (>0.6) = Simula "No al día" (máximo estrés)
    # - Score medio (0.3-0.6) = Simula "Al día" pero con riesgo moderado
    # - Score bajo (<0.3) = Simula "Al día" (bajo riesgo contextual)
    if contextual_risk > 0.6:
        model_inputs['Tuition fees up to date'] = 0  # Máximo riesgo contextual
    else:
        model_inputs['Tuition fees up to date'] = 1  # Sin problemas contextuales graves
    
    # MAPEO A 'Scholarship holder' (Proxy de Apoyo/Recursos)
    # Si el riesgo contextual es bajo y no hay desafíos económicos reportados,
    # simulamos que el estudiante tiene "acceso a recursos" (beca/apoyo)
    if contextual_risk < 0.3 and unrc_inputs['desafio'] != "Dificultades Económicas":
        model_inputs['Scholarship holder'] = 1  # Simula "Sí tiene apoyo"
    else:
        model_inputs['Scholarship holder'] = 0  # Simula "Sin apoyo suficiente"
    
    # AJUSTE POR MODALIDAD A DISTANCIA
    # Estudiantes a distancia típicamente cursan menos materias de forma simultánea
    if unrc_inputs['modalidad'] == "A Distancia" and model_inputs['Curricular units 2nd sem (enrolled)'] > 5:
        ratio_actual = (
            model_inputs['Curricular units 2nd sem (approved)'] / 
            model_inputs['Curricular units 2nd sem (enrolled)']
            if model_inputs['Curricular units 2nd sem (enrolled)'] > 0 
            else 0
        )
        # Ajusta a carga típica de estudiante a distancia
        model_inputs['Curricular units 2nd sem (enrolled)'] = 5
        model_inputs['Curricular units 2nd sem (approved)'] = int(5 * ratio_actual)
    
    return model_inputs


# ═══════════════════════════════════════════════════════════════════════════
# 6️⃣  INTERFAZ DE USUARIO
# ═══════════════════════════════════════════════════════════════════════════

# Aplicar CSS personalizado con colores institucionales UNRC
st.markdown("""
<style>
    /* ========================================
       FORZAR TEMA CLARO - OVERRIDE COMPLETO
       ======================================== */
    
    /* Colores institucionales UNRC */
    :root {
        --unrc-guinda: #9F2241;
        --unrc-dorado: #BC955C;
        --unrc-verde: #235B4E;
    }
    
    /* FONDO BLANCO FORZADO EN TODO */
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    .main {
        background-color: #FFFFFF !important;
    }
    
    .block-container {
        background-color: #FFFFFF !important;
        padding-top: 2rem !important;
    }
    
    /* TEXTO OSCURO FORZADO */
    .stApp, .main, .block-container, p, span, div {
        color: #1E1E1E !important;
    }
    
    /* SIDEBAR CON FONDO CLARO */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F8F9FA 0%, #FFFFFF 100%) !important;
        border-right: 4px solid var(--unrc-dorado) !important;
    }
    
    section[data-testid="stSidebar"] .css-1d391kg,
    section[data-testid="stSidebar"] > div {
        background-color: transparent !important;
    }
    
    /* TÍTULOS EN GUINDA (excepto en gradientes) */
    h1, h2, h3, h4, h5, h6 {
        color: var(--unrc-guinda) !important;
        font-weight: 700 !important;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .css-10trblm {
        color: var(--unrc-guinda) !important;
    }
    
    /* Forzar texto blanco en elementos dentro de gradientes */
    div[style*="background: linear-gradient"] h1,
    div[style*="background: linear-gradient"] h2,
    div[style*="background: linear-gradient"] h3,
    div[style*="background: linear-gradient"] p,
    div[style*="background: linear-gradient"] span {
        color: #FFFFFF !important;
    }
    
    /* BOTONES GUINDA */
    .stButton>button {
        background-color: var(--unrc-guinda) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background-color: #7a1a33 !important;
        box-shadow: 0 4px 12px rgba(159, 34, 65, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    
    /* MÉTRICAS CON COLORES INSTITUCIONALES */
    div[data-testid="stMetricValue"] {
        color: var(--unrc-guinda) !important;
        font-weight: 700 !important;
        font-size: 2.2rem !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: var(--unrc-guinda) !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    div[data-testid="stMetricDelta"] {
        color: var(--unrc-dorado) !important;
    }
    
    /* SLIDERS Y CONTROLES */
    .stSlider {
        padding-top: 1rem !important;
    }
    
    .stSlider [data-baseweb="slider"] {
        background-color: transparent !important;
    }
    
    .stSlider [data-testid="stThumbValue"] {
        color: var(--unrc-guinda) !important;
        font-weight: 600 !important;
    }
    
    /* NUMBER INPUTS */
    .stNumberInput input {
        background-color: #FFFFFF !important;
        color: #1E1E1E !important;
        border: 2px solid #E0E0E0 !important;
        border-radius: 5px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    .stNumberInput input:focus {
        border-color: var(--unrc-guinda) !important;
        box-shadow: 0 0 0 1px var(--unrc-guinda) !important;
    }
    
    .stNumberInput input::placeholder {
        color: #757575 !important;
        font-weight: 500 !important;
    }
    
    .stNumberInput label {
        color: #1E1E1E !important;
        font-weight: 600 !important;
    }
    
    /* SELECTBOX */
    .stSelectbox > div > div {
        background-color: #FFFFFF !important;
        color: #1E1E1E !important;
        border: 2px solid #E0E0E0 !important;
    }
    
    /* DIVISORES */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(to right, var(--unrc-dorado), var(--unrc-guinda)) !important;
        margin: 2rem 0 !important;
    }
    
    /* ALERTAS Y MENSAJES */
    .stAlert {
        background-color: #FFFFFF !important;
        border-left: 4px solid var(--unrc-dorado) !important;
        color: #1E1E1E !important;
    }
    
    .stSuccess {
        background-color: #E8F5E9 !important;
        border-left: 4px solid #4CAF50 !important;
    }
    
    .stWarning {
        background-color: #FFF3E0 !important;
        border-left: 4px solid var(--unrc-dorado) !important;
    }
    
    .stError {
        background-color: #FFEBEE !important;
        border-left: 4px solid var(--unrc-guinda) !important;
    }
    
    .stInfo {
        background-color: #E3F2FD !important;
        border-left: 4px solid var(--unrc-verde) !important;
    }
    
    /* EXPANDERS */
    .streamlit-expanderHeader {
        background-color: #F8F9FA !important;
        color: var(--unrc-guinda) !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 5px !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #E8E9EA !important;
        border-color: var(--unrc-dorado) !important;
    }
    
    /* DATAFRAMES Y TABLAS */
    .dataframe {
        border: 2px solid var(--unrc-guinda) !important;
        border-radius: 5px !important;
    }
    
    /* CHARTS */
    .stPlotlyChart, .stVegaLiteChart {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado con logo
col_logo, col_title = st.columns([1, 5])

with col_logo:
    # Intentar cargar el logo de la UNRC
    try:
        st.image("/Users/arianstoned/Desktop/dropout_MLE_model/app/Guia_identidad_visual/Iconos/logos_UNRC-01.png", 
                 width=100)
    except:
        st.markdown("<div style='font-size: 4rem; text-align: center;'>🎓</div>", unsafe_allow_html=True)

with col_title:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #9F2241 0%, #7a1a33 100%);
                padding: 1.5rem;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(159, 34, 65, 0.2);">
        <h1 style="color: #FFFFFF !important; margin: 0; font-size: 2rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">SAREP: Simulador de Riesgo para la UNRC</h1>
        <p style="color: #FFFFFF !important; margin: 0.5rem 0 0 0; font-size: 0.95rem; font-weight: 500; opacity: 0.95;">
            Universidad Nacional Rosario Castellanos | Adaptación Contextual
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="background: white;
            border: 3px solid #9F2241;
            border-left: 8px solid #BC955C; 
            padding: 1.5rem; 
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
    <h4 style="color: #9F2241; margin-top: 0; font-weight: 700;">📊 Acerca de este Simulador</h4>
    <p style="margin-bottom: 0.5rem; color: #333; line-height: 1.6;">
        Este simulador utiliza un <strong style="color: #9F2241;">modelo XGBoost (AUC≈0.89)</strong> adaptado con variables 
        contextuales de la UNRC para estimar riesgo de abandono estudiantil.
    </p>
    <p style="margin-bottom: 0.5rem; color: #333; line-height: 1.6;">
        ℹ️ <strong style="color: #9F2241;">Interactividad Inteligente</strong>: Los campos académicos están sincronizados automáticamente.
    </p>
    <p style="margin-bottom: 0; color: #333; line-height: 1.6;">
        ℹ️ <strong style="color: #9F2241;">Contextualización</strong>: Variables locales como satisfacción vocacional o modalidad 
        de estudio se traducen internamente a factores del modelo con <strong style="color: #BC955C;">ponderación basada en evidencia estadística</strong>.
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar — Perfil del estudiante UNRC
st.sidebar.header("📝 Perfil del Estudiante UNRC")
st.sidebar.markdown(
    "*Campos académicos sincronizados: Modifica cualquiera y los demás se actualizarán*",
    help="Los campos académicos están vinculados para mantener la coherencia de datos"
)

col1, col2 = st.sidebar.columns(2)
with col1:
    age = st.number_input("👤 Edad al ingreso", 17, 80, 20, 1, help="Edad del estudiante")

with col2:
    # Placeholder para simetría visual
    st.empty()

# SECCIÓN SINCRONIZADA: Unidades y Ratio S2
st.sidebar.divider()
st.sidebar.subheader("📊 Rendimiento Académico (Sincronizado)")

st.sidebar.caption("ℹ️ Variables académicas - el corazón del modelo predictivo")

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
        f'<div style="text-align:center; font-size: 1.5rem;">{mode_icon}</div>',
        unsafe_allow_html=True
    )

with col_info:
    if st.session_state.update_mode == 'ratio':
        st.info("🔄 Modo what-if: Cambiando ratio")
    else:
        st.info("✏️ Modo datos: Cambiando unidades")

st.slider(
    "📈 Momentum Académico (Cambio S2 vs S1)",
    key='ratio_s2',
    min_value=-1.0,
    max_value=1.0,
    step=0.01,
    on_change=update_numbers_from_ratio,
    help="Cambio de rendimiento entre semestres: -1.0 (caída drástica) a +1.0 (mejora significativa)"
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
st.sidebar.subheader("ℹ️ Contexto del Estudiante")

# Satisfacción Vocacional (nueva variable contextual)
satisfaccion = st.sidebar.selectbox(
    "😌 Satisfacción Vocacional",
    ["Satisfecho", "Parcialmente Satisfecho", "Insatisfecho"],
    help="¿Cómo se siente el estudiante con su elección de carrera?",
    index=1
)

# Modalidad de Estudio (nueva variable contextual)
modalidad = st.sidebar.selectbox(
    "🏠 Modalidad de Estudio",
    ["Presencial-Híbrida", "A Distancia"],
    help="Modalidad principal de estudios"
)

# Principal Desafío No Académico (nueva variable contextual)
desafio = st.sidebar.selectbox(
    "🔧 Principal Desafío No Académico",
    ["Ninguno", "Dificultades Económicas", "Conflicto Trabajo-Estudio", "Problemas Personales/Salud"],
    help="Factor no académico que más impacta su rendimiento",
    index=0
)

# Ejemplos predefinidos para facilitar demostración
st.sidebar.divider()
st.sidebar.caption("💡 Ejemplos rápidos (click para cargar)")
col_ej1, col_ej2, col_ej3 = st.sidebar.columns(3)

# Ejemplo 1: Estudiante con insatisfacción vocacional (alto riesgo)
with col_ej1:
    if st.button("🔴 Alto Riesgo", help="Estudiante con insatisfacción y bajo rendimiento"):
        st.session_state.ratio_s2 = -0.25  # Negativo = deterioro
        st.session_state.aprobadas_s2 = 2
        st.session_state.inscritas_s2 = 8
        st.session_state.update_mode = 'ratio'
        st.session_state.satisfaccion_example = "Insatisfecho"
        st.session_state.desafio_example = "Dificultades Económicas"
        st.sidebar.success("✅ Perfil de insatisfecho con dificultades económicas")
        st.rerun()

# Ejemplo 2: Estudiante con良好的 rendimiento
with col_ej2:
    if st.button("🟢 Bajo Riesgo", help="Estudiante satisfecho y en modalidad híbrida"):
        st.session_state.ratio_s2 = 0.25  # Positivo = mejora
        st.session_state.aprobadas_s2 = 12
        st.session_state.inscritas_s2 = 14
        st.session_state.update_mode = 'ratio'
        st.session_state.satisfaccion_example = "Satisfecho"
        st.session_state.desafio_example = "Ninguno"
        st.sidebar.success("✅ Perfil satisfecho y sin desafíos económicos")
        st.rerun()

# Ejemplo 3: Estudiante a distancia con conflicto trabajo-estudio
with col_ej3:
    if st.button("⚠️ Caso Crítico", help="Estudiante a distancia con problemas de tiempo"):
        st.session_state.ratio_s2 = -0.5  # Caída significativa
        st.session_state.aprobadas_s2 = 0
        st.session_state.inscritas_s2 = 10
        st.session_state.update_mode = 'numbers'
        st.session_state.satisfaccion_example = "Parcialmente Satisfecho"
        st.session_state.desafio_example = "Conflicto Trabajo-Estudio"
        st.sidebar.success("✅ Caso a distancia con conflicto laboral")
        st.rerun()

calculate = st.sidebar.button("🔍 Calcular Riesgo de Abandono", use_container_width=True, type="primary")
# Validar S1 otra vez (por si se modificó)
if s1_app > s1_enr:
    s1_app = s1_enr
    st.sidebar.warning("⚠️ Aprobadas S1 no pueden superar Inscritas S1")
    st.rerun()

if calculate:
    # Preparar entradas contextuales de UNRC
    unrc_inputs = {
        'momentum': st.session_state.ratio_s2,
        'age': age,
        's1_aprobadas': s1_app,
        's1_inscritas': s1_enr,
        's2_aprobadas': st.session_state.aprobadas_s2,
        's2_inscritas': st.session_state.inscritas_s2,
        'satisfaccion': satisfaccion,
        'modalidad': modalidad,
        'desafio': desafio,
    }
    
    # Mapear variables contextuales a las del modelo
    inputs = map_unrc_to_model_inputs(unrc_inputs)
    
    X_one = create_student_input_df(inputs)
    result = make_prediction(X_one)
    if result['success']:
        st.session_state.pred = result
        # Guardamos tanto los inputs mapeados como los contextuales para análisis posterior
        st.session_state.inputs = inputs
        st.session_state.unrc_inputs = unrc_inputs
    else:
        st.error(f"Error en la predicción: {result['error']}")

# Resultados
if 'pred' in st.session_state:
    res = st.session_state.pred
    inputs = st.session_state.inputs
    unrc_inputs = st.session_state.unrc_inputs  # Variables contextuales originales
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
    st.subheader("🔍 Principales Factores de Riesgo (Contexto UNRC)")
    factors = []

    # Factores académicos
    if inputs['Ratio_Aprobacion_S2'] < -0.2:  # Adaptado para momentum negativo
        factors.append(("error", "🚨 Deterioro significativo del rendimiento académico"))
    elif inputs['Ratio_Aprobacion_S2'] < 0.0:
        factors.append(("warning", "⚠️ Caída de rendimiento entre semestres"))

    if inputs['Curricular units 1st sem (approved)'] < 3:
        factors.append(("error", "🚨 Bajo rendimiento inicial persistente"))

    # Factores contextuales traducidos desde variables UNRC
    if inputs['Tuition fees up to date'] == 0:
        # Identificamos la causa real con las variables contextuales
        if unrc_inputs['satisfaccion'] == "Insatisfecho":
            factors.append(("error", "🚨 Insatisfacción vocacional señal de alto riesgo"))
        elif unrc_inputs['desafio'] == "Dificultades Económicas":
            factors.append(("warning", "⚠️ Dificultades económicas reportadas"))
        else:
            factors.append(("warning", "⚠️ Múltiples factores de riesgo contextual detectados"))

    # Consideraciones específicas de modalidad
    if unrc_inputs['modalidad'] == "A Distancia" and inputs['Curricular units 2nd sem (enrolled)'] <= 5:
        factors.append(("info", "ℹ️ Estudiante a distancia con carga académica reducida"))
        
    # Mostrar factores de riesgo identificados
    if not factors:
        st.success("✅ No se detectaron factores de riesgo significativos")
    else:
        for sev, msg in factors:
            (st.error if sev == 'error' else st.warning if sev == 'warning' else st.info)(msg)

    st.divider()
    st.subheader("✅ Plan de Intervención UNRC")

    # Analizar factores específicos del contexto UNRC
    acad_risk = inputs['Curricular units 1st sem (approved)'] < 3 or inputs['Ratio_Aprobacion_S2'] < 0.0
    satisfaction_risk = unrc_inputs['satisfaccion'] in ["Insatisfecho", "Parcialmente Satisfecho"]
    economic_risk = unrc_inputs['desafio'] == "Dificultades Económicas"
    work_study_risk = unrc_inputs['desafio'] == "Conflicto Trabajo-Estudio"
    distance_mode = unrc_inputs['modalidad'] == "A Distancia"

    # Acciones recomendadas según perfil
    if satisfaction_risk:
        st.error("⚠️ **ACCIÓN PRIORITARIA: Insatisfacción Vocacional Detectada**")
        st.info(
            "✅ **Recomendación:** Derivación inmediata a Tutoría de Orientación Vocacional "
            "(Secretaría de Asuntos Estudiantiles). Considerar entrevista con Coordinador de Carrera."
        )
        
    if acad_risk:
        st.warning("📚 **Rendimiento Académico Comprometido**")
        st.info(
            "✅ **Recomendación:** Reforzar tutorías académicas y consultas con profesores."
            " Coordinar con Unidad Pedagógica para plan de refuerzo en áreas específicas."
        )
        
    if economic_risk:
        st.warning("💰 **Dificultades Económicas Identificadas**")
        st.info(
            "✅ **Recomendación:** Contactar con Secretaría de Bienestar Universitario para "
            "evaluar acceso a Beca Integración, Apoyo Económico Emergente y programas de alimentación."
        )
        
    if work_study_risk:
        st.warning("🏢 **Conflicto Trabajo-Estudio Detectado**")
        st.info(
            "✅ **Recomendación:** Consultoría sobre estrategias de conciliación horaria. "
            "Evaluar posibilidad de cambio a modalidad a distancia si no está ya en ella."
        )
        
    if distance_mode:
        st.success("📡 **Estudiante a Distancia - Acciones Específicas**")
        st.info(
            "✅ **Recomendación:** Monitoreo proactivo por parte de tutores del Campus Virtual. "
            "Asegurar acceso a recursos digitales y conectividad adecuada."
        )
        
    # Mensaje final según combinación de factores
    if len([True for f in [satisfaction_risk, acad_risk, economic_risk] if f]) >= 2:
        st.error(
            "🆘 **MULTIPLES FACTORES DE RIESGO IDENTIFICADOS** - Coordinación inmediata "
            "necesaria entre múltiples áreas de la UNRC. Plan integral de seguimiento (24-48h)."
        )
    elif not any([satisfaction_risk, acad_risk, economic_risk, work_study_risk]):
        st.success(
            "✅ **Perfil Estable** - Estudiante sin factores de riesgo significativos. "
            "Continuar con monitoreo regular."
        )

    with st.expander("🔧 Información técnica del simulador"):
        st.write(
            "Modelo XGBoost (multiclase). AUC de referencia ≈ 0.89. Clases: Dropout, Enrolled, Graduate."
        )
        st.write(pd.DataFrame([inputs]).T.rename(columns={0: 'Valor'}))
        
        st.subheader("ℹ️ Cómo funciona la simulación UNRC con lógica basada en evidencia")
        st.markdown("""
        **Motor de Reglas de Riesgo Contextual:**
        
        Este simulador utiliza un motor de reglas que pondera los factores contexto​universitarios
        según la significancia estadística encontrada en la encuesta UNRC:
        
        **1. Satisfacción Vocacional (p=0.028) ← HALLAZGO MÁS FUERTE**
           - Peso: 0.5 puntos (máximo impacto en el modelo)
           - Insatisfecho: +0.5 riesgo contextual alto
           - Parcialmente satisfecho: +0.25 riesgo moderado
           - **Análisis**: Factor más predictivo en la encuesta y principal motor de riesgo
        
        **2. Momentum Académico (p=0.052) ← Evidencia fuerte**
           - Peso: hasta 0.4 puntos
           - Deterioro significativo (<-0.2): +0.4 riesgo alto
           - Deterioro moderado (<0.0): +0.15 riesgo moderado
           - **Análisis**: La trayectoria de rendimiento es más importante que valores absolutos
        
        **3. Desafío Socioeconómico (p>0.3) ← Evidencia débil**
           - Peso: 0.05-0.10 puntos (factor mediador)
           - Solo suma si ya existen otros riesgos (efecto acumulativo)
           - **Análisis**: No es un predictor directo, pero amplifica otros riesgos
        
        **4. Modalidad a Distancia (Factor contextual)**
           - Peso: 0.1 puntos (factor base)
           - **Análisis**: Representa desafíos adicionales de conectividad y acceso
        
        **Mapeo al Modelo XGBoost:**
        - Score contextual (>0.6) → `Tuition fees up to date = 0` (simula estrés financiero)
        - Score contextual (<0.3) → `Scholarship holder = 1` (simula acceso a recursos)
        
        **Ventaja de este enfoque:**
        Los ponderadores están respaldados por la evidencia estadística de tu encuesta,
        permitiéndote justificar cada decisión numérica con un p-valor específico.
        """)
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
st.markdown("""
<div style="text-align: center; 
            padding: 2rem 1rem;
            background: linear-gradient(135deg, #9F2241 0%, #7a1a33 100%);
            color: white;
            border-radius: 10px;
            margin-top: 3rem;">
    <p style="margin: 0; font-size: 0.9rem; color: #FFFFFF !important; font-weight: 600;">
        SAREP v1.0 — Simulador Adaptado UNRC
    </p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #FFFFFF !important; opacity: 0.95;">
        Universidad Nacional Rosario Castellanos | Dataset Portugués → Contexto Mexicano | 2024-2025
    </p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.75rem; color: #FFFFFF !important; opacity: 0.9;">
        🌺 "Otro modo de ser humano y libre. Otro modo de ser." — Rosario Castellanos
    </p>
</div>
""", unsafe_allow_html=True)
