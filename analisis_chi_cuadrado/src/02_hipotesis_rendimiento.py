import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency
import os

# --- Configuración de Rutas ---
PROCESSED_DATA_PATH = "analisis_chi_cuadrado/data/processed/datos_limpios.csv"
RESULTS_PATH = "analisis_chi_cuadrado/results"
os.makedirs(RESULTS_PATH, exist_ok=True)

# --- Cargar Datos ---
try:
    df = pd.read_csv(PROCESSED_DATA_PATH)
except FileNotFoundError:
    print(f"Error: No se encontró el archivo de datos procesados en {PROCESSED_DATA_PATH}")
    print("Por favor, ejecuta primero el script '01_analisis_exploratorio.py'")
    exit()

# --- Hipótesis 1: Rendimiento Académico vs. Intención de Abandono ---

print("--- Análisis de Hipótesis 1: Rendimiento Académico y Abandono ---")

# Crear tabla de contingencia
contingency_table = pd.crosstab(df['rendimiento_pasado'], df['considero_abandonar'])

# Reordenar las filas para una mejor visualización
order = [
    'Aprobé todas o casi todas las materias que cursé',
    'Aprobé aproximadamente la mitad de las materias',
    'Reprobé más de la mitad de las materias que cursé'
]
contingency_table = contingency_table.reindex(order)

print("\nTabla de Contingencia:")
print(contingency_table)

# Realizar la prueba de Chi-Cuadrado
chi2, p, dof, expected = chi2_contingency(contingency_table)

print(f"\nEstadístico Chi-Cuadrado: {chi2:.4f}")
print(f"P-valor: {p:.4f}")
print(f"Grados de libertad: {dof}")

# Interpretación del resultado
alpha = 0.05
if p < alpha:
    print("\nResultado: La asociación es estadísticamente significativa (p < 0.05).")
    print("Se rechaza la hipótesis nula. El rendimiento pasado está asociado con la intención de abandono.")
else:
    print("\nResultado: La asociación no es estadísticamente significativa (p >= 0.05).")
    print("No se puede rechazar la hipótesis nula.")

# --- Visualización ---

# Calcular porcentajes para el gráfico
ct_percent = contingency_table.div(contingency_table.sum(axis=1), axis=0) * 100

# Crear el gráfico
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(12, 7))

ct_percent.plot(kind='bar',
                ax=ax,
                color=['#2ca02c', '#d62728'], # Verde para 'No', Rojo para 'Sí'
                width=0.8)

# Añadir etiquetas de porcentaje
for container in ax.containers:
    ax.bar_label(container, fmt='%.1f%%', label_type='center', color='white', fontsize=10, fontweight='bold')

# Configurar títulos y etiquetas
ax.set_title(f'Intención de Abandono según Rendimiento Académico Pasado\nAsociación Significativa (p={p:.3f})', fontsize=16, fontweight='bold')
ax.set_xlabel('Rendimiento del Semestre Pasado', fontsize=12)
ax.set_ylabel('Porcentaje de Estudiantes (%)', fontsize=12)
ax.set_xticklabels([label.replace(' ', '\n') for label in order], rotation=0, ha='center')
ax.legend(title='¿Consideró Abandonar?')
ax.set_ylim(0, 100)

plt.tight_layout()

# Guardar el gráfico
output_path = os.path.join(RESULTS_PATH, "hipotesis_1_rendimiento_vs_abandono.png")
plt.savefig(output_path)

print(f"\nGráfico guardado en: {output_path}")
