import pandas as pd
import os

# --- Configuración de Rutas ---
RAW_DATA_PATH = "analisis_chi_cuadrado/data/raw/_Pulso de la Trayectoria Estudiantil UNRC_ (Respuestas) - Respuestas de formulario 1.csv"
PROCESSED_DATA_PATH = "analisis_chi_cuadrado/data/processed/datos_limpios.csv"
RESULTS_PATH = "analisis_chi_cuadrado/results"

# Crear directorios si no existen
os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
os.makedirs(RESULTS_PATH, exist_ok=True)

# --- Carga y Limpieza de Datos ---

# Nombres de columnas originales (exactos del CSV)
original_cols = [
    'Marca temporal',
    '2. En los últimos 6 meses, ¿has considerado seriamente la posibilidad de abandonar tus estudios o darte de baja temporal?',
    '3. En una escala del 1 al 5, ¿con qué frecuencia has tenido estos pensamientos?\n(1) Nunca\n(2) Rara vez\n(3) A veces\n(4) Frecuentemente\n(5) Constantemente',
    '4. Pensando en tu rendimiento del semestre pasado, ¿cuál de estas frases te describe mejor?',
    '5. ¿Sientes que la carrera que elegiste ha cumplido con tus expectativas?',
    '1. De la siguiente lista, por favor selecciona los 3 desafíos NO académicos más importantes que has enfrentado en el último año.',
    '2. ¿Cuentas actualmente con alguna beca (académica, de manutención, etc.)?',
    '3. ¿Conoces los servicios de tutoría o apoyo psicopedágico que ofrece la UNRC?',
    '1. ¿Cual es tu licenciatura?'
]

# Nombres de columnas nuevos (cortos y descriptivos)
new_cols = [
    "timestamp",
    "considero_abandonar",
    "frecuencia_pensamientos",
    "rendimiento_pasado",
    "expectativas_carrera",
    "desafios_no_academicos",
    "tiene_beca",
    "conoce_servicios",
    "licenciatura"
]

# Diccionario para renombrar columnas
rename_dict = dict(zip(original_cols, new_cols))

try:
    df = pd.read_csv(RAW_DATA_PATH)
    # Renombrar columnas basado en el diccionario
    df.rename(columns=rename_dict, inplace=True)
    
    # Asegurarse de que solo tenemos las columnas que necesitamos
    df = df[[col for col in new_cols if col in df.columns]]

except Exception as e:
    print(f"Error al cargar o procesar el archivo: {e}")
    exit()

# Verificar si todas las columnas esperadas están presentes
missing_cols = set(new_cols) - set(df.columns)
if missing_cols:
    print(f"Advertencia: Las siguientes columnas no se encontraron y serán ignoradas: {missing_cols}")

# --- Análisis Descriptivo Básico ---

print("--- Análisis Exploratorio Inicial ---")

# 1. Porcentaje de estudiantes que consideraron abandonar
print("\n1. ¿Consideró abandonar sus estudios?")
considero_counts = df['considero_abandonar'].value_counts()
considero_perc = df['considero_abandonar'].value_counts(normalize=True) * 100
print(pd.concat([considero_counts, considero_perc], axis=1, keys=['Frecuencia', 'Porcentaje (%)']))

# 2. Distribución por licenciatura
print("\n2. Distribución por Licenciatura")
licenciatura_counts = df['licenciatura'].value_counts()
licenciatura_perc = df['licenciatura'].value_counts(normalize=True) * 100
print(pd.concat([licenciatura_counts, licenciatura_perc], axis=1, keys=['Frecuencia', 'Porcentaje (%)']))

# 3. Distribución de la frecuencia de pensamientos de abandono
print("\n3. Frecuencia de pensamientos de abandono (1-5)")
print(df['frecuencia_pensamientos'].describe())
print("\nDistribución de Frecuencia:")
print(df['frecuencia_pensamientos'].value_counts().sort_index())

# 4. Top desafíos no académicos
print("\n4. Desafíos no académicos más comunes")
# Limpiar y separar los desafíos
desafios = df['desafios_no_academicos'].str.split(', ').explode().str.strip()
desafios_counts = desafios.value_counts()
desafios_perc = desafios.value_counts(normalize=True) * 100
print(pd.concat([desafios_counts, desafios_perc], axis=1, keys=['Frecuencia', 'Porcentaje (%)']).head())


# --- Guardar Datos Procesados ---
df.to_csv(PROCESSED_DATA_PATH, index=False)

print(f"\nAnálisis completado. Los datos limpios se han guardado en: {PROCESSED_DATA_PATH}")
