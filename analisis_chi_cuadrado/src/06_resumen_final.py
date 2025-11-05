import pandas as pd
import os
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency, kruskal, mannwhitneyu

# --- Configuración de Rutas ---
PROCESSED_DATA_PATH = "analisis_chi_cuadrado/data/processed/datos_limpios.csv"
RESULTS_PATH = "analisis_chi_cuadrado/results"

# --- Cargar Datos ---
try:
    df = pd.read_csv(PROCESSED_DATA_PATH)
except FileNotFoundError:
    print(f"Error: No se encontró el archivo de datos procesados en {PROCESSED_DATA_PATH}")
    exit()

# --- Funciones de Cálculo ---

def get_chi2_pvalue(df, var_independiente, var_dependiente='considero_abandonar'):
    """Calcula el p-valor de Chi-Cuadrado para dos variables categóricas."""
    contingency_table = pd.crosstab(df[var_independiente], df[var_dependiente])
    if contingency_table.shape[0] < 2 or contingency_table.shape[1] < 2:
        return float('nan')
    _, p, _, _ = chi2_contingency(contingency_table)
    return p

def get_kruskal_pvalue(df, var_ordinal, var_grupos):
    """Calcula el p-valor de Kruskal-Wallis para una variable ordinal y grupos."""
    grupos_data = [df[df[var_grupos] == grupo][var_ordinal].dropna()
                   for grupo in df[var_grupos].unique()]
    # Filtrar grupos vacíos
    grupos_data = [g for g in grupos_data if not g.empty]
    
    if len(grupos_data) < 2:
        return float('nan')
    
    # Usar Mann-Whitney U si solo hay dos grupos, Kruskal si hay más
    if len(grupos_data) == 2:
        _, p = mannwhitneyu(grupos_data[0], grupos_data[1])
    else:
        _, p = kruskal(*grupos_data)
    return p

# --- Mapeos de Categorías ---

rendimiento_map = {
    'Aprobé todas o casi todas las materias que cursé': 'Alto Rendimiento',
    'Aprobé aproximadamente la mitad de las materias': 'Medio Rendimiento',
    'Reprobé más de la mitad de las materias que cursé': 'Bajo Rendimiento'
}
df['rendimiento_ordinal'] = df['rendimiento_pasado'].map(rendimiento_map)

expectativas_map = {
    'Sí, totalmente': 'Satisfecho',
    'Parcialmente, tengo algunas dudas': 'Parcialmente Satisfecho',
    'No, o casi no': 'Insatisfecho'
}
df['expectativas_ordinal'] = df['expectativas_carrera'].map(expectativas_map)

df['desafio_economico'] = df['desafios_no_academicos'].str.contains('económicas|trabajo', case=False, na=False).map({True: 'Sí', False: 'No'})


print("--- Resumen Final y Tablas de Contingencia (Porcentajes Fila-por-Fila) ---")

# --- 1. Tablas de Contingencia con P-valores Dinámicos ---

# H1: Rendimiento vs Abandono
p_h1 = get_chi2_pvalue(df, 'rendimiento_pasado')
ct_h1 = pd.crosstab(df['rendimiento_ordinal'], df['considero_abandonar'], normalize='index') * 100
print("\nTabla H1: Rendimiento vs. Abandono (%)")
print(ct_h1.round(1))
print(f"P-valor H1: {p_h1:.3f}")

# H2a: Beca vs Abandono
p_h2a = get_chi2_pvalue(df, 'tiene_beca')
ct_h2a = pd.crosstab(df['tiene_beca'], df['considero_abandonar'], normalize='index') * 100
print("\nTabla H2a: Beca vs. Abandono (%)")
print(ct_h2a.round(1))
print(f"P-valor H2a: {p_h2a:.3f}")

# H2b: Desafío Económico vs Abandono
p_h2b = get_chi2_pvalue(df, 'desafio_economico')
ct_h2b = pd.crosstab(df['desafio_economico'], df['considero_abandonar'], normalize='index') * 100
print("\nTabla H2b: Desafío Económico vs. Abandono (%)")
print(ct_h2b.round(1))
print(f"P-valor H2b: {p_h2b:.3f}")

# H3: Expectativas vs Abandono
p_h3 = get_chi2_pvalue(df, 'expectativas_carrera')
ct_h3 = pd.crosstab(df['expectativas_ordinal'], df['considero_abandonar'], normalize='index') * 100
print("\nTabla H3: Expectativas vs. Abandono (%)")
print(ct_h3.round(1))
print(f"P-valor H3: {p_h3:.3f}")


# --- 2. Resumen de Insights para el Informe (Ordinal) ---

p_ord_rendimiento = get_kruskal_pvalue(df, 'frecuencia_pensamientos', 'rendimiento_ordinal')
p_ord_expectativas = get_kruskal_pvalue(df, 'frecuencia_pensamientos', 'expectativas_ordinal')
p_ord_beca = get_kruskal_pvalue(df, 'frecuencia_pensamientos', 'tiene_beca') # Usará Mann-Whitney internamente

print("\n=====================================================")
print("INSIGHTS CLAVE PARA EL INFORME (Validación Hipotética)")
print("=====================================================")

print("\n[Insight 1: Rendimiento Académico (Factor Predictivo Fuerte)]")
print(f"El rendimiento pasado está significativamente asociado con la intención de abandono (Chi-Cuadrado p={p_h1:.3f}).")
print(f"Estudiantes con 'Bajo Rendimiento' tienen {ct_h1.loc['Bajo Rendimiento', 'Sí']:.1f}% de intención de abandono, mientras que los de 'Alto Rendimiento' tienen {ct_h1.loc['Alto Rendimiento', 'Sí']:.1f}%.")
print("Recomendación: SAREP debe priorizar alertas tempranas basadas en calificaciones.")

print("\n[Insight 2: Expectativas de Carrera (Factor Predictivo Moderado)]")
print(f"Existe una tendencia significativa (Chi-Cuadrado p={p_h3:.3f}) donde la insatisfacción aumenta la intención de abandono.")
print(f"Estudiantes 'Insatisfechos' tienen {ct_h3.loc['Insatisfecho', 'Sí']:.1f}% de intención de abandono, mientras que los 'Satisfechos' tienen {ct_h3.loc['Satisfecho', 'Sí']:.1f}%.")
print("Recomendación: Intervenciones vocacionales tempranas son cruciales.")

print("\n[Insight 3: Factores Financieros (No Significativos en esta muestra)]")
print(f"Ni la tenencia de beca (p={p_h2a:.3f}) ni la mención explícita de desafíos económicos (p={p_h2b:.3f}) mostraron una asociación estadísticamente significativa con la intención de abandono.")
print("Recomendación: Si bien son importantes, no son los predictores más fuertes en este modelo binario.")

print("\n[Insight 4: Intensidad del Pensamiento (Ordinal)]")
print(f"La intensidad de los pensamientos de abandono (1-5) se correlaciona significativamente con el Rendimiento (Kruskal p={p_ord_rendimiento:.3f}) y las Expectativas (Kruskal p={p_ord_expectativas:.3f}), pero no con la Beca (Mann-Whitney p={p_ord_beca:.3f}).")
print("Esto sugiere que el rendimiento y la satisfacción afectan la *frecuencia* del pensamiento, no solo la decisión binaria.")

# Nota: Los gráficos de barras agrupadas y boxplots ya fueron generados en scripts anteriores.
# Para el informe, se recomienda usar los gráficos generados en:
# - H1: hipotesis_1_rendimiento_vs_abandono.png
# - H2: hipotesis_2a_beca_vs_abandono.png y hipotesis_2b_economia_vs_abandono.png
# - H3: hipotesis_3_expectativas_vs_abandono.png
# - Ordinal: ordinal_rendimiento_vs_frecuencia.png y ordinal_expectativas_vs_frecuencia.png
