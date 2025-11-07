import pandas as pd
import os

# --- Configuración de Rutas ---
PROCESSED_DATA_PATH = os.path.join("..", "data", "processed", "datos_limpios.csv")
RESULTS_PATH = os.path.join("..", "results")

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

print(f"\nAnálisis completado.")