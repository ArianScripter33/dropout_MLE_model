
"""
🎓 SAREP: Simulador de Riesgo para la UNRC - Dashboard Rediseñado
==========================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
try:
    from utils import (
        load_model_artifacts, 
        classify_risk_level, 
        create_student_input_df, 
        make_prediction, 
        map_unrc_to_model_inputs
    )
    from styles import get_css
    from data import get_student_list
except ImportError:
    # Fallback for when running from root as module
    from app.utils import (
        load_model_artifacts, 
        classify_risk_level, 
        create_student_input_df, 
        make_prediction, 
        map_unrc_to_model_inputs
    )
    from app.styles import get_css
    from app.data import get_student_list

# ═══════════════════════════════════════════════════════════════════════════
# 1️⃣  CONFIGURACIÓN DE PÁGINA
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SAREP: Dashboard del Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar CSS
st.markdown(get_css(), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# 2️⃣  ESTADO DE LA SESIÓN
# ═══════════════════════════════════════════════════════════════════════════

if 'selected_student_id' not in st.session_state:
    st.session_state.selected_student_id = 1  # Default to first student

if 'ratio_s2' not in st.session_state:
    st.session_state.ratio_s2 = 0.0
if 'aprobadas_s2' not in st.session_state:
    st.session_state.aprobadas_s2 = 0
if 'inscritas_s2' not in st.session_state:
    st.session_state.inscritas_s2 = 5
if 'update_mode' not in st.session_state:
    st.session_state.update_mode = 'ratio'

# Cargar modelo
model, preprocessor, feature_names, class_names = load_model_artifacts()

# Cargar datos simulados
students = get_student_list()
# Ordenar por riesgo descendente
students.sort(key=lambda x: x['risk_score'], reverse=True)

# ═══════════════════════════════════════════════════════════════════════════
# 3️⃣  SIDEBAR (NAVEGACIÓN)
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2991/2991148.png", width=50) # Placeholder logo
    st.markdown("### SAREP")
    
    st.markdown("---")
    
    # Navegación simple
    page = st.radio(
        "Navegación",
        ["Dashboard", "Estudiantes", "Calendario", "Configuración"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.caption("Universidad Nacional Rosario Castellanos")

# ═══════════════════════════════════════════════════════════════════════════
# 4️⃣  DASHBOARD PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

if page == "Dashboard":
    st.title("Dashboard del Tutor")
    st.markdown("SAREP traduce el análisis en intervención humana y proactiva.")
    
    col_list, col_profile = st.columns([1, 2.5])
    
    # ─── COLUMNA IZQUIERDA: LISTA DE ESTUDIANTES ─────────────────────────────
    with col_list:
        st.subheader("Lista Priorizada por Riesgo")
        st.caption("Los tutores ven inmediatamente quién necesita más atención.")
        
        for student in students:
            # Crear un contenedor clickeable (simulado con botón)
            # Usamos columnas para el layout del item
            c1, c2, c3 = st.columns([1, 3, 1])
            
            # Estilo condicional si está seleccionado
            is_selected = st.session_state.selected_student_id == student['id']
            bg_color = "#e3f2fd" if is_selected else "#ffffff"
            border_color = "#9F2241" if is_selected else "#eee"
            
            # Calcular color de riesgo para el badge
            _, color, _ = classify_risk_level(student['risk_score'])
            
            # Botón invisible que cubre todo el item sería ideal, pero en Streamlit
            # usamos un botón normal con el nombre
            
            with st.container():
                st.markdown(
                    f"""
                    <div class="list-item-container" style="
                        background-color: {bg_color}; 
                        border-left: 4px solid {border_color};
                        padding: 12px; 
                        border-radius: 8px; 
                        margin-bottom: 12px;
                        display: flex;
                        align-items: center;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                    ">
                        <img src="{student['avatar']}" style="width: 42px; height: 42px; border-radius: 50%; margin-right: 12px; border: 2px solid #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="flex-grow: 1;">
                            <div style="font-weight: 600; font-size: 0.95rem; color: #333;">{student['name']}</div>
                            <div style="font-size: 0.75rem; color: #888; margin-top: 2px;">Estudiante • ID: {student['id']}</div>
                        </div>
                        <div style="font-weight: 700; color: {color}; font-size: 0.9rem; background: #fff; padding: 4px 8px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">{int(student['risk_score']*100)}%</div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                if st.button(f"Ver Perfil", key=f"btn_{student['id']}", use_container_width=True):
                    st.session_state.selected_student_id = student['id']
                    # Cargar datos del estudiante en session state para edición
                    st.session_state.aprobadas_s2 = student['academic_data']['s2_aprobadas']
                    st.session_state.inscritas_s2 = student['academic_data']['s2_inscritas']
                    st.session_state.ratio_s2 = student['academic_data']['momentum']
                    st.rerun()

    # ─── COLUMNA DERECHA: PERFIL DEL ESTUDIANTE ──────────────────────────────
    with col_profile:
        # Obtener estudiante seleccionado
        selected_student = next((s for s in students if s['id'] == st.session_state.selected_student_id), students[0])
        
        # Calcular riesgo en tiempo real (para permitir simulación)
        # Usamos los valores de session_state si coinciden con el estudiante, sino los del estudiante
        # (Aquí simplificamos: siempre usamos session_state que se actualizó al clickear)
        
        # Inputs para el cálculo
        unrc_inputs = {
            'momentum': st.session_state.ratio_s2,
            'age': selected_student['academic_data']['age'],
            's1_aprobadas': selected_student['academic_data']['s1_aprobadas'],
            's1_inscritas': selected_student['academic_data']['s1_inscritas'],
            's2_aprobadas': st.session_state.aprobadas_s2,
            's2_inscritas': st.session_state.inscritas_s2,
            'satisfaccion': selected_student['context_data']['satisfaccion'],
            'modalidad': selected_student['context_data']['modalidad'],
            'desafio': selected_student['context_data']['desafio'],
        }
        
        # Mapeo y Predicción
        inputs = map_unrc_to_model_inputs(unrc_inputs)
        X_one = create_student_input_df(inputs, feature_names)
        result = make_prediction(X_one, model, preprocessor, class_names)
        
        current_risk = result['probabilities']['Dropout']
        level, color, _ = classify_risk_level(current_risk)

        # ─── HEADER DEL PERFIL ───
        st.markdown(f"### Student Profile")
        
        with st.container():
            st.markdown('<div class="student-card">', unsafe_allow_html=True)
            
            p_col1, p_col2, p_col3 = st.columns([1, 3, 1.5])
            
            with p_col1:
                st.image(selected_student['avatar'], width=100)
            
            with p_col2:
                st.markdown(f"## {selected_student['name']}")
                st.markdown(f"**Email:** {selected_student['email']}")
                st.markdown(f"**Edad:** {selected_student['academic_data']['age']} años")
                
                # Mini stats
                s1, s2, s3 = st.columns(3)
                s1.metric("Academic", f"{st.session_state.aprobadas_s2}/{st.session_state.inscritas_s2}")
                s2.metric("Dapis", "16") # Placeholder
                s3.metric("Dvairolan", "2020") # Placeholder
            
            with p_col3:
                # Risk Circle HTML/SVG
                risk_percent = int(current_risk * 100)
                stroke_dash = 251.2 * (risk_percent / 100) # 2 * pi * r (r=40) approx
                
                st.markdown(f"""
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div style="position: relative; width: 100px; height: 100px;">
                        <svg width="100" height="100" viewBox="0 0 100 100">
                            <circle cx="50" cy="50" r="40" stroke="#eee" stroke-width="8" fill="none"></circle>
                            <circle cx="50" cy="50" r="40" stroke="{color}" stroke-width="8" fill="none"
                                    stroke-dasharray="251.2" stroke-dashoffset="{251.2 - (251.2 * risk_percent / 100)}"
                                    transform="rotate(-90 50 50)"></circle>
                            <text x="50" y="55" text-anchor="middle" font-size="20" font-weight="bold" fill="{color}">{risk_percent}%</text>
                        </svg>
                    </div>
                    <div style="margin-top: 5px; font-weight: bold; color: {color};">{level.split(' ')[1]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

        # ─── DETALLES Y SIMULACIÓN ───
        d_col1, d_col2 = st.columns([1.2, 1])
        
        with d_col1:
            st.markdown("#### 📝 Academic Data (Simulador)")
            st.info("Modifica los valores para simular cambios en el riesgo.")
            
            # Formulario de edición
            # Usamos keys dinámicas para forzar la actualización cuando cambia el estudiante
            new_aprobadas = st.number_input(
                "Aprobadas S2", 
                0, 30, 
                st.session_state.aprobadas_s2,
                key=f"ni_aprobadas_{selected_student['id']}"
            )
            new_inscritas = st.number_input(
                "Inscritas S2", 
                1, 30, 
                st.session_state.inscritas_s2,
                key=f"ni_inscritas_{selected_student['id']}"
            )
            
            if new_aprobadas != st.session_state.aprobadas_s2 or new_inscritas != st.session_state.inscritas_s2:
                st.session_state.aprobadas_s2 = new_aprobadas
                st.session_state.inscritas_s2 = new_inscritas
                
                # Recalcular momentum (S2 Ratio - S1 Ratio)
                if new_inscritas > 0:
                    s2_ratio = new_aprobadas / new_inscritas
                    
                    # Obtener datos S1 del estudiante actual
                    s1_app = selected_student['academic_data']['s1_aprobadas']
                    s1_ins = selected_student['academic_data']['s1_inscritas']
                    s1_ratio = s1_app / s1_ins if s1_ins > 0 else 0
                    
                    # Momentum es la diferencia
                    st.session_state.ratio_s2 = round(s2_ratio - s1_ratio, 2)
                
                st.rerun()

            # Context inputs
            st.markdown("#### 🌍 Contexto")
            st.markdown(f"**Satisfacción:** {selected_student['context_data']['satisfaccion']}")
            st.markdown(f"**Modalidad:** {selected_student['context_data']['modalidad']}")
            st.markdown(f"**Desafío:** {selected_student['context_data']['desafio']}")

        with d_col2:
            # Riesgo Principal Box
            st.markdown(f"""
            <div class="risk-card">
                <div class="risk-title">Riesgo Principal: {selected_student['risk_diagnosis']}</div>
                <p>{selected_student['risk_description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### Sugerencia de Intervención")
            st.info(f"💡 {selected_student['intervention']}")
            
            st.button("📅 Agendar sesión", type="primary", use_container_width=True)

else:
    st.info("Página en construcción")

