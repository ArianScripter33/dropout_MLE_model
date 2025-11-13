
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

def create_final_disparity_graph():
    """
    Generates a bar chart comparing teacher workload for the latest quarter,
    using a 60/40 student distribution estimate.
    """
    try:
        matricula_df = clean_and_prepare_data('CSV UNRC/Matricula.csv')
        docentes_df = clean_and_prepare_data('CSV UNRC/Docentes.csv')
    except FileNotFoundError as e:
        print(f"Error: No se pudo encontrar el archivo {e.filename}.")
        return

    # Create a Combined DataFrame
    df = pd.merge(matricula_df, docentes_df, on='date', how='inner')

    # 1. Use Data from the Last Quarter
    last_quarter_data = df.iloc[-1]
    last_quarter_date = df.index[-1]

    # 2. Calculate Final Ratios using 60/40 split
    matricula_total = last_quarter_data['m_licenciatura']
    docentes_p = last_quarter_data['d_licenciatura_PH']
    docentes_d = last_quarter_data['d_licenciatura_D']

    matricula_d = matricula_total * 0.6
    matricula_p = matricula_total * 0.4

    ratio_p = matricula_p / docentes_p if docentes_p else 0
    ratio_d = matricula_d / docentes_d if docentes_d else 0
    
    # 3. Generate the Bar Chart
    modalidades = ['Modalidad Presencial-Híbrida', 'Modalidad a Distancia-Híbrida']
    ratios = [ratio_p, ratio_d]
    colors = ['skyblue', 'lightgreen']

    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.bar(modalidades, ratios, color=colors)

    # Add data labels on top of each bar
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2f}', va='bottom', ha='center', fontsize=12)

    ax.set_ylabel('Ratio Estudiantes por Docente')
    ax.set_title(f'Disparidad de Carga Docente por Modalidad (Estimación 60/40, {last_quarter_date.strftime("Q%q %Y")})', fontsize=14)
    ax.set_ylim(0, max(ratios) * 1.2) # Adjust y-axis limit for better visualization

    # 4. Add Disparity Percentage
    disparity_percentage = ((ratio_d / ratio_p) - 1) * 100
    disparity_text = f"La carga docente en la modalidad a distancia\nes un {disparity_percentage:.0f}% mayor."
    
    ax.text(0.95, 0.95, disparity_text,
            transform=ax.transAxes,
            fontsize=12,
            verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.7))

    plt.tight_layout()

    # 5. Save the Graph
    plt.savefig('exhibit_4_disparidad_carga_docente_FINAL.png')
    print("Graph saved as exhibit_4_disparidad_carga_docente_FINAL.png")

if __name__ == "__main__":
    create_final_disparity_graph()
