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

# --- Hipótesis 3: Expectativas de Carrera vs. Intención de Abandono ---

print("--- Análisis de Hipótesis 3: Expectativas de Carrera y Abandono ---")

# Crear tabla de contingencia
contingency_table = pd.crosstab(df['expectativas_carrera'], df['abandono_considerado'])

# Reordenar para una mejor visualización
order = [
    'Sí, totalmente',
    'Parcialmente, tengo algunas dudas',
    'No, o casi no'
]
contingency_table = contingency_table.reindex(order)

print("\nTabla de Contingencia:")
print(contingency_table)

# Realizar la prueba de Chi-Cuadrado
chi2, p, dof, expected = chi2_contingency(contingency_table)

print(f"\nEstadístico Chi-Cuadrado: {chi2:.4f}")
print(f"P-valor: {p:.4f}")

# Interpretación del resultado
alpha = 0.05
if p < alpha:
    print("\nResultado: La asociación es estadísticamente significativa.")
else:
    print("\nResultado: La asociación no es estadísticamente significativa.")

# --- Visualización ---
ct_percent = contingency_table.div(contingency_table.sum(axis=1), axis=0) * 100

plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(12, 7))

ct_percent.plot(kind='bar',
                ax=ax,
                color=['#2ca02c', '#d62728'],
                width=0.8)

for container in ax.containers:
    ax.bar_label(container, fmt='%.1f%%', label_type='center', color='white', fontsize=10, fontweight='bold')

ax.set_title(f'Intención de Abandono según Cumplimiento de Expectativas\n(p={p:.3f})', fontsize=16, fontweight='bold')
ax.set_xlabel('¿La carrera cumplió con tus expectativas?', fontsize=12)
ax.set_ylabel('Porcentaje de Estudiantes (%)', fontsize=12)
ax.set_xticklabels(order, rotation=0, ha='center')
ax.legend(title='¿Consideró Abandonar?')
ax.set_ylim(0, 100)

plt.tight_layout()

output_path = os.path.join(RESULTS_PATH, "hipotesis_3_expectativas_vs_abandono.png")
plt.savefig(output_path)

print(f"\nGráfico guardado en: {output_path}")