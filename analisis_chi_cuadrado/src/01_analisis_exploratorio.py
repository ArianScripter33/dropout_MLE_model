import pandas as pd
import os
import json
from pathlib import Path

# --- Configuración de Rutas ---
# Determinar si estamos ejecutando desde el directorio raíz o desde analisis_chi_cuadrado/src
if os.path.basename(os.getcwd()) == 'src':
    # Estamos en analisis_chi_cuadrado/src
    PROCESSED_DATA_PATH = os.path.join("..", "data", "processed", "datos_limpios.csv")
    RESULTS_PATH = os.path.join("..", "results")
    METRICS_PATH = os.path.join("..", "metrics", "exploratory.json")
else:
    # Estamos en el directorio raíz
    PROCESSED_DATA_PATH = os.path.join("data", "processed", "datos_limpios.csv")
    RESULTS_PATH = os.path.join("results")
    METRICS_PATH = os.path.join("metrics", "exploratory.json")

# Crear directorios si no existen
os.makedirs(RESULTS_PATH, exist_ok=True)

# --- Carga de Datos ---
try:
    df = pd.read_csv(PROCESSED_DATA_PATH)
except Exception as e:
    print(f"Error al cargar o procesar el archivo: {e}")
    exit()

# --- Análisis Descriptivo Básico ---

print("--- Análisis Exploratorio Inicial ---")

# 1. Porcentaje de estudiantes que consideraron abandonar
print("\n1. ¿Consideró abandonar sus estudios?")
considero_counts = df['abandono_considerado'].value_counts()
considero_perc = df['abandono_considerado'].value_counts(normalize=True) * 100
print(pd.concat([considero_counts, considero_perc], axis=1, keys=['Frecuencia', 'Porcentaje (%)']))

# 2. Distribución por licenciatura
print("\n2. Distribución por Licenciatura")
licenciatura_counts = df['licenciatura'].value_counts()
licenciatura_perc = df['licenciatura'].value_counts(normalize=True) * 100
print(pd.concat([licenciatura_counts, licenciatura_perc], axis=1, keys=['Frecuencia', 'Porcentaje (%)']))

# 3. Distribución de la frecuencia de pensamientos de abandono
print("\n3. Frecuencia de pensamientos de abandono (1-5)")
print(df['frecuencia_abandono'].describe())
print("\nDistribución de Frecuencia:")
print(df['frecuencia_abandono'].value_counts().sort_index())

# 4. Top desafíos no académicos
print("\n4. Desafíos no académicos más comunes")
# Limpiar y separar los desafíos
desafios = df['desafios_no_academicos'].str.split(', ').explode().str.strip()
desafios_counts = desafios.value_counts()
desafios_perc = desafios.value_counts(normalize=True) * 100
print(pd.concat([desafios_counts, desafios_perc], axis=1, keys=['Frecuencia', 'Porcentaje (%)']).head())

# --- Generar Métricas para DVC ---
metrics = {
    "total_estudiantes": len(df),
    "consideraron_abandonar": int(df['abandono_considerado'].value_counts().get('Sí', 0)),
    "porcentaje_abandono": float(considero_perc.get('Sí', 0)),
    "count_licenciaturas": int(len(df['licenciatura'].unique())),
    "licenciatura_mayoritaria": str(df['licenciatura'].value_counts().index[0]),
    "frecuencia_abandono_promedio": float(df['frecuencia_abandono'].mean()),
    "frecuencia_abandono_mediana": float(df['frecuencia_abandono'].median()),
    "total_respustas_desafios": int(len(desafios)),
    "desafio_mas_comun": str(desafios_counts.index[0]),
    "desafios_unicos": int(desafios_counts.nunique())
}

# Guardar las métricas en formato JSON
metrics_path = METRICS_PATH
Path(os.path.dirname(metrics_path)).mkdir(parents=True, exist_ok=True)
with open(metrics_path, 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"\nMétricas guardadas en: {metrics_path}")
print(f"Análisis completado con {len(df)} estudiantes.")
