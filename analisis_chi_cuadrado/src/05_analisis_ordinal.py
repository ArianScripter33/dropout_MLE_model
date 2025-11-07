import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import kruskal, mannwhitneyu
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

# --- Preprocesamiento para el análisis ordinal ---
# 1. Derivar 'desafio_economico' (necesario para H2b)
df['desafio_economico'] = df['desafios_no_academicos'].str.contains('económicas|trabajo', case=False, na=False).map({True: 'Sí', False: 'No'})

# 2. Limpiar categorías de rendimiento y expectativas para el análisis ordinal
rendimiento_map = {
    'Aprobé todas o casi todas las materias que cursé': 'Alto Rendimiento',
    'Aprobé aproximadamente la mitad de las materias': 'Medio Rendimiento',
    'Reprobé más de la mitad de las materias que cursé': 'Bajo Rendimiento'
}
df['rendimiento_ordinal'] = df['rendimiento_semestre_pasado'].map(rendimiento_map)

expectativas_map = {
    'Sí, totalmente': 'Satisfecho',
    'Parcialmente, tengo algunas dudas': 'Parcialmente Satisfecho',
    'No, o casi no': 'Insatisfecho'
}
df['expectativas_ordinal'] = df['expectativas_carrera'].map(expectativas_map)


print("--- Análisis de Frecuencia de Pensamientos (Ordinal) ---")

# --- Función para Análisis y Visualización (Boxplots) ---
def analizar_y_visualizar_ordinal(dataframe, variable_independiente, grupos_a_comparar, prueba_func, titulo, nombre_archivo):
    print(f"\n--- Análisis: {titulo} ---")
    
    # Filtrar para asegurar que solo tenemos las categorías relevantes
    df_filtrado = dataframe.dropna(subset=[variable_independiente, grupos_a_comparar])
    
    # Preparar datos para la prueba estadística
    grupos_data = [df_filtrado[df_filtrado[grupos_a_comparar] == grupo][variable_independiente] 
                   for grupo in set(df_filtrado[grupos_a_comparar])]
    
    # Ejecutar prueba
    if len(grupos_data) >= 2:
        if prueba_func == kruskal:
            stat, p = prueba_func(*grupos_data)
            prueba_nombre = "Kruskal-Wallis H"
        elif prueba_func == mannwhitneyu:
            # Mann-Whitney U solo acepta dos muestras, se usa para beca (2 grupos)
            if len(grupos_data) == 2:
                stat, p = prueba_func(grupos_data[0], grupos_data[1])
                prueba_nombre = "Mann-Whitney U"
            else:
                print(f"Error: Mann-Whitney U requiere exactamente 2 grupos, se encontraron {len(grupos_data)}.")
                return
        else:
            print(f"Prueba no soportada: {prueba_func.__name__}")
            return

        print(f"Estadístico {prueba_nombre}: {stat:.4f}")
        print(f"P-valor: {p:.4f}")

        # Interpretación
        alpha = 0.05
        if p < alpha:
            print("Resultado: La diferencia en la frecuencia de pensamientos es estadísticamente significativa.")
        else:
            print("Resultado: No hay diferencia significativa en la frecuencia de pensamientos.")

        # Visualización (Boxplots)
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(x=grupos_a_comparar, y=variable_independiente, data=df_filtrado, ax=ax, palette="viridis")
        
        ax.set_title(f'{titulo} (p={p:.3f})', fontsize=14, fontweight='bold')
        ax.set_xlabel(grupos_a_comparar.replace('_', ' ').title(), fontsize=12)
        ax.set_ylabel('Frecuencia de Pensamientos de Abandono (1-5)', fontsize=12)
        
        plt.tight_layout()
        output_path = os.path.join(RESULTS_PATH, nombre_archivo)
        plt.savefig(output_path)
        print(f"Gráfico guardado en: {output_path}")
    else:
        print("No hay suficientes grupos para comparar.")


# 5a. Frecuencia vs. Rendimiento (Ordinal) -> Kruskal-Wallis
analizar_y_visualizar_ordinal(df, 'frecuencia_abandono', 'rendimiento_ordinal', kruskal, 
                              "Frecuencia de Pensamientos vs. Rendimiento Académico", 
                              "ordinal_rendimiento_vs_frecuencia.png")

# 5b. Frecuencia vs. Beca (Binario) -> Mann-Whitney U
analizar_y_visualizar_ordinal(df, 'frecuencia_abandono', 'beca_actual', mannwhitneyu, 
                              "Frecuencia de Pensamientos vs. Tenencia de Beca", 
                              "ordinal_beca_vs_frecuencia.png")

# 5c. Frecuencia vs. Expectativas (Ordinal) -> Kruskal-Wallis
analizar_y_visualizar_ordinal(df, 'frecuencia_abandono', 'expectativas_ordinal', kruskal, 
                              "Frecuencia de Pensamientos vs. Expectativas de Carrera", 
                              "ordinal_expectativas_vs_frecuencia.png")