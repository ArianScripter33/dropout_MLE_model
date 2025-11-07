import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency
import os

# --- Configuración de Rutas ---
PROCESSED_DATA_PATH = os.path.join("..", "data", "processed", "datos_limpios.csv")
RESULTS_PATH = os.path.join("..", "results")
os.makedirs(RESULTS_PATH, exist_ok=True)

# --- Cargar Datos ---
try:
    df = pd.read_csv(PROCESSED_DATA_PATH)
except FileNotFoundError:
    print(f"Error: No se encontró el archivo de datos procesados en {PROCESSED_DATA_PATH}")
    exit()

# --- Función para Análisis y Visualización ---
def analizar_y_visualizar(dataframe, variable_independiente, titulo, nombre_archivo):
    print(f"\n--- Análisis: {titulo} ---")
    
    # Tabla de contingencia
    contingency_table = pd.crosstab(dataframe[variable_independiente], dataframe['abandono_considerado'])
    print("\nTabla de Contingencia:")
    print(contingency_table)

    # Prueba de Chi-Cuadrado
    if contingency_table.shape[0] < 2 or contingency_table.shape[1] < 2:
        print("No hay suficientes datos para realizar la prueba de Chi-Cuadrado.")
        return

    chi2, p, dof, expected = chi2_contingency(contingency_table)
    print(f"\nEstadístico Chi-Cuadrado: {chi2:.4f}")
    print(f"P-valor: {p:.4f}")

    # Interpretación
    alpha = 0.05
    if p < alpha:
        print("Resultado: La asociación es estadísticamente significativa.")
    else:
        print("Resultado: La asociación no es estadísticamente significativa.")

    # Visualización
    ct_percent = contingency_table.div(contingency_table.sum(axis=1), axis=0) * 100
    
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 6))
    ct_percent.plot(kind='bar', ax=ax, color=['#2ca02c', '#d62728'], width=0.7)

    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%', label_type='center', color='white', fontsize=10, fontweight='bold')

    ax.set_title(f'{titulo}\n(p={p:.3f})', fontsize=14, fontweight='bold')
    ax.set_xlabel(variable_independiente.replace('_', ' ').title(), fontsize=12)
    ax.set_ylabel('Porcentaje de Estudiantes (%)', fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.legend(title='¿Consideró Abandonar?')
    ax.set_ylim(0, 100)
    
    plt.tight_layout()
    output_path = os.path.join(RESULTS_PATH, nombre_archivo)
    plt.savefig(output_path)
    print(f"Gráfico guardado en: {output_path}")

# --- Hipótesis 2a: Beca vs. Abandono ---
analizar_y_visualizar(df, 'beca_actual', 'Intención de Abandono según Tenencia de Beca', 'hipotesis_2a_beca_vs_abandono.png')

# --- Hipótesis 2b: Desafío Económico vs. Abandono ---
# Crear variable derivada 'desafio_economico'
df['desafio_economico'] = df['desafios_no_academicos'].str.contains('económicas|trabajo', case=False, na=False).map({True: 'Sí', False: 'No'})
analizar_y_visualizar(df, 'desafio_economico', 'Intención de Abandono por Desafíos Económicos', 'hipotesis_2b_economia_vs_abandono.png')