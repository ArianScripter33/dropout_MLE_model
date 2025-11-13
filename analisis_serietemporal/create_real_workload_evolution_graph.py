
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

def create_workload_evolution_graph():
    """
    Generates a time series graph of teacher workload evolution using a 60/40
    student distribution estimate.
    """
    try:
        matricula_df = clean_and_prepare_data('CSV UNRC/Matricula.csv')
        docentes_df = clean_and_prepare_data('CSV UNRC/Docentes.csv')
    except FileNotFoundError as e:
        print(f"Error: No se pudo encontrar el archivo {e.filename}.")
        return

    # 1. & 2. Create a Combined DataFrame and apply 60/40 estimate
    df = pd.merge(matricula_df, docentes_df, on='date', how='inner')
    df['Matricula_Distancia'] = df['m_licenciatura'] * 0.6
    df['Matricula_Presencial'] = df['m_licenciatura'] * 0.4

    # 3. Calculate the REAL Historical Ratios
    df['Ratio_Presencial'] = df['Matricula_Presencial'].divide(df['d_licenciatura_PH']).replace(np.inf, np.nan)
    df['Ratio_Distancia'] = df['Matricula_Distancia'].divide(df['d_licenciatura_D']).replace(np.inf, np.nan)

    # 4. Generate the Line Plot
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(df.index, df['Ratio_Presencial'], color='tab:blue', marker='o', linestyle='-', label='Ratio Presencial-Híbrida')
    ax.plot(df.index, df['Ratio_Distancia'], color='tab:orange', marker='o', linestyle='-', label='Ratio Distancia-Híbrida')

    ax.set_title('Evolución de la Carga Docente por Modalidad (Estimación 60/40)', fontsize=16)
    ax.set_xlabel('Año y Trimestre')
    ax.set_ylabel('Ratio Estudiantes por Docente')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend()

    # 5. Add Impactful Annotations
    # Peak Distance Load
    peak_distancia_val = df['Ratio_Distancia'].max()
    peak_distancia_date = df['Ratio_Distancia'].idxmax()
    ax.annotate(f"Pico de Carga a Distancia:\n{peak_distancia_val:.1f} Est./Docente",
                xy=(peak_distancia_date, peak_distancia_val),
                xytext=(peak_distancia_date, peak_distancia_val + 5),
                arrowprops=dict(facecolor='black', shrink=0.05),
                ha='center', fontsize=10, bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="black", lw=1, alpha=0.8))

    # Current Load
    last_date = df.index[-1]
    last_ratio_p = df['Ratio_Presencial'].iloc[-1]
    last_ratio_d = df['Ratio_Distancia'].iloc[-1]
    ax.annotate(f"Carga Actual ({last_date.strftime('Q%q %Y')}):\n{last_ratio_d:.1f} a Distancia vs. {last_ratio_p:.1f} Presencial",
                xy=(last_date, last_ratio_d),
                xytext=(last_date - pd.DateOffset(months=18), last_ratio_d + 10),
                arrowprops=dict(facecolor='black', shrink=0.05),
                ha='center', fontsize=10, bbox=dict(boxstyle="round,pad=0.3", fc="lightblue", ec="black", lw=1, alpha=0.8))

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # 6. Save the Graph
    plt.savefig('exhibit_4_evolucion_carga_docente_REAL.png')
    print("Graph saved as exhibit_4_evolucion_carga_docente_REAL.png")

if __name__ == "__main__":
    create_workload_evolution_graph()
