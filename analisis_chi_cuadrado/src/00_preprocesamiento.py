import pandas as pd
import os

# Definir las rutas de los archivos de entrada y salida
raw_data_path = os.path.join('..', 'data', 'raw', '_Pulso de la Trayectoria Estudiantil UNRC_ (Respuestas) - Respuestas de formulario 1.csv')
processed_data_path = os.path.join('..', 'data', 'processed', 'datos_limpios.csv')

# Cargar los datos
df = pd.read_csv(raw_data_path)

# Renombrar las columnas para que sean más manejables
column_mapping = {
    'Marca temporal': 'marca_temporal',
    '2. En los últimos 6 meses, ¿has considerado seriamente la posibilidad de abandonar tus estudios o darte de baja temporal?': 'abandono_considerado',
    '3. En una escala del 1 al 5, ¿con qué frecuencia has tenido estos pensamientos?\n(1) Nunca\n(2) Rara vez\n(3) A veces\n(4) Frecuentemente\n(5) Constantemente': 'frecuencia_abandono',
    '4. Pensando en tu rendimiento del semestre pasado, ¿cuál de estas frases te describe mejor?': 'rendimiento_semestre_pasado',
    '5. ¿Sientes que la carrera que elegiste ha cumplido con tus expectativas?': 'expectativas_carrera',
    '1. De la siguiente lista, por favor selecciona los 3 desafíos NO académicos más importantes que has enfrentado en el último año.': 'desafios_no_academicos',
    '2. ¿Cuentas actualmente con alguna beca (académica, de manutención, etc.)?': 'beca_actual',
    '3. ¿Conoces los servicios de tutoría o apoyo psicopedagógico que ofrece la UNRC?': 'conoce_servicios_apoyo',
    '¿Qué recompensa deseas?\nElige una opción ': 'recompensa',
    'Gracias por tus respuestas, ¿Quieres participar en el sorteo?': 'participa_sorteo',
    'Escribe tu correo electrónico': 'email',
    '1. ¿Cual es tu licenciatura?': 'licenciatura',
    'Columna 9': 'columna_9'
}
df.rename(columns=column_mapping, inplace=True)

# Limpiar los datos de la columna 'licenciatura'
# Strip whitespace
df['licenciatura'] = df['licenciatura'].str.strip()

# Unify values
df['licenciatura'] = df['licenciatura'].replace({
    'Humanidades y Narrativa Multimedia': 'Humanidades y Narrativas Multimedia',
    'Humanidades y Narrativas Multímedia': 'Humanidades y Narrativas Multimedia',
    'Humanidades Narrativas y multimedia': 'Humanidades y Narrativas Multimedia'
})

# Remove 'Matemáticas'
df = df[df['licenciatura'] != 'Matemáticas']

# Imprimir los valores únicos de la columna 'licenciatura' para inspección
print("Valores únicos en la columna 'licenciatura' después de la limpieza final:")
print(df['licenciatura'].unique())

# Guardar el DataFrame limpio en un nuevo archivo CSV
df.to_csv(processed_data_path, index=False)

print(f"\nLos datos limpios se han guardado en: {processed_data_path}")