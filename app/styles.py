
def get_css():
    return """
    <style>
        /* ========================================
           IMPORTAR FUENTES
           ======================================== */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* ========================================
           FORZAR TEMA CLARO - OVERRIDE COMPLETO
           ======================================== */
        
        /* Colores institucionales UNRC */
        :root {
            --unrc-guinda: #9F2241;
            --unrc-dorado: #BC955C;
            --unrc-verde: #235B4E;
            --bg-light: #F5F7FA; /* Slightly darker/cooler gray for contrast */
            --text-dark: #1E1E1E;
            --card-bg: #FFFFFF;
            --sidebar-bg: #0e1117;
        }
        
        /* FONDO BLANCO FORZADO EN TODO */
        .stApp {
            background-color: var(--bg-light) !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        .main {
            background-color: var(--bg-light) !important;
        }
        
        .block-container {
            background-color: var(--bg-light) !important;
            padding-top: 1rem !important; /* Reduced top padding */
            padding-bottom: 2rem !important;
            max-width: 1200px !important;
        }
        
        /* TEXTO OSCURO FORZADO */
        .stApp, .main, .block-container, p, span, div, h1, h2, h3, h4, h5, h6 {
            color: var(--text-dark) !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        h1, h2, h3 {
            font-weight: 700 !important;
            letter-spacing: -0.5px;
        }

        /* SIDEBAR CON FONDO CLARO */
        section[data-testid="stSidebar"] {
            background-color: var(--sidebar-bg) !important;
            color: white !important;
        }
        
        section[data-testid="stSidebar"] p, 
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div,
        section[data-testid="stSidebar"] label {
             color: rgba(255,255,255,0.9) !important;
        }
        
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: white !important;
        }

        /* CARDS */
        .student-card {
            background-color: var(--card-bg);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            margin-bottom: 20px;
            border: 1px solid rgba(0,0,0,0.05);
            transition: transform 0.2s ease;
        }
        
        .student-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }

        .risk-card {
            background-color: #FFF5F5;
            border-left: 4px solid #FFCDD2;
            border-radius: 8px;
            padding: 16px;
            margin-top: 10px;
        }

        .risk-title {
            color: #C62828 !important;
            font-weight: 700;
            font-size: 1.05rem;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* BOTONES */
        .stButton>button {
            background-color: var(--unrc-guinda) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            padding: 0.6rem 1.5rem !important;
            transition: all 0.2s ease !important;
            width: 100%;
            box-shadow: 0 2px 5px rgba(159, 34, 65, 0.2) !important;
        }
        
        .stButton>button:hover {
            background-color: #7a1a33 !important;
            box-shadow: 0 4px 12px rgba(159, 34, 65, 0.4) !important;
            transform: translateY(-1px) !important;
        }
        
        .stButton>button:active {
            transform: translateY(0) !important;
        }

        /* METRICS */
        div[data-testid="stMetricValue"] {
            color: var(--unrc-guinda) !important;
            font-weight: 700 !important;
            font-size: 1.6rem !important;
        }
        
        div[data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
            color: #666 !important;
            font-weight: 500 !important;
        }
        
        /* CUSTOM LIST ITEM */
        .list-item-container {
            transition: all 0.2s ease;
            cursor: pointer;
        }
        
        .list-item-container:hover {
            transform: translateX(4px);
        }

        /* CIRCLE PROGRESS */
        .progress-ring__circle {
            transition: stroke-dashoffset 1s ease-in-out;
            transform: rotate(-90deg);
            transform-origin: 50% 50%;
        }
        
        /* INPUTS */
        .stNumberInput input {
            border-radius: 6px !important;
            border: 1px solid #ddd !important;
        }
        
        .stNumberInput input:focus {
            border-color: var(--unrc-guinda) !important;
            box-shadow: 0 0 0 1px var(--unrc-guinda) !important;
        }

    </style>
    """
