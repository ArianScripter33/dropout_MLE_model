
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def clean_and_prepare_data(filepath):
    """Loads a CSV, removes duplicates, and sets a sorted date index."""
    df = pd.read_csv(filepath)
    df = df.drop_duplicates()
    df['date'] = pd.to_datetime(df['año'].astype(str) + '-' + (df['trimestre'] * 3).astype(str))
    df = df.set_index('date').sort_index()
    return df

def create_workload_graph_with_kpis():
    """
    Generates an enriched time series graph of teacher workload, including a
    box with key performance indicators (KPIs) about the disparity.
    """
    try:
        matricula_df = clean_and_prepare_data('CSV UNRC/Matricula.csv')
        docentes_df = clean_and_prepare_data('CSV UNRC/Docentes.csv')
    except FileNotFoundError as e:
        print(f"Error: No se pudo encontrar el archivo {e.filename}.")
        return

    # --- Data Preparation ---
    df = pd.merge(matricula_df, docentes_df, on='date', how='inner')
    df['Matricula_Distancia'] = df['m_licenciatura'] * 0.6
    df['Matricula_Presencial'] = df['m_licenciatura'] * 0.4
    df['Ratio_Presencial'] = df['Matricula_Presencial'].divide(df['d_licenciatura_PH']).replace(np.inf, np.nan)
    df['Ratio_Distancia'] = df['Matricula_Distancia'].divide(df['d_licenciatura_D']).replace(np.inf, np.nan)

    # 2. Calculate Disparity KPIs
    df['Disparidad_Porcentual'] = ((df['Ratio_Distancia'] / df['Ratio_Presencial']) - 1) * 100
    
    # Handle potential NaN or Inf values before calculating KPIs
    valid_disparity = df['Disparidad_Porcentual'].dropna()

    # KPI 1: Current Disparity
    disparidad_actual = valid_disparity.iloc[-1]
    ultimo_trimestre = valid_disparity.index[-1]

    # KPI 2: Average Disparity
    disparidad_promedio = valid_disparity.mean()

    # KPI 3: Maximum Disparity
    disparidad_maxima = valid_disparity.max()
    trimestre_pico = valid_disparity.idxmax()

    # --- Plotting ---
    # 1. Maintain Base Graph
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(df.index, df['Ratio_Presencial'], color='tab:blue', marker='o', linestyle='-', label='Ratio Presencial-Híbrida')
    ax.plot(df.index, df['Ratio_Distancia'], color='tab:orange', marker='o', linestyle='-', label='Ratio Distancia-Híbrida')

    # 4. Style and Title
    ax.set_title('Evolución de la Carga Docente: Una Disparidad Estructural (Estimación 60/40)', fontsize=16)
    ax.set_xlabel('Año y Trimestre')
    ax.set_ylabel('Ratio Estudiantes por Docente')
    ax.grid(True, which='both', linestyle=':', linewidth=0.6, color='grey')
    ax.legend(loc='upper right')

    # 3. Integrate KPIs in an "Insights Box"
    kpi_text = (
        f"Disparidad Máxima ({trimestre_pico.strftime('Q%q %Y')}): {disparidad_maxima:.0f}%\n"
        f"Disparidad Promedio Histórica: {disparidad_promedio:.0f}%\n"
        f"Disparidad Actual ({ultimo_trimestre.strftime('Q%q %Y')}): {disparidad_actual:.0f}%"
    )
    
    props = dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.8)
    ax.text(0.03, 0.97, kpi_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=props)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # 5. Save the Graph
    plt.savefig('exhibit_4_evolucion_carga_docente_CON_KPIS.png')
    print("Graph saved as exhibit_4_evolucion_carga_docente_CON_KPIS.png")

if __name__ == "__main__":
    create_workload_graph_with_kpis()
