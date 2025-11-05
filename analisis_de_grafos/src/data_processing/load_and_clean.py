import pandas as pd
import os

def load_data(filename: str) -> pd.DataFrame:
    """Carga el archivo CSV especificado desde data/raw/."""
    file_path = os.path.join("data", "raw", filename)
    print(f"Intentando cargar datos desde: {file_path}")
    try:
        df = pd.read_csv(file_path)
        print(f"Datos cargados exitosamente. Filas: {len(df)}, Columnas: {len(df.columns)}")
        return df
    except FileNotFoundError:
        print(f"Error: El archivo {file_path} no fue encontrado.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error al leer el CSV: {e}")
        return pd.DataFrame()

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Realiza una limpieza inicial de los datos, incluyendo el manejo de
    múltiples selecciones en la columna de desafíos.
    """
    if df.empty:
        return df
    
    # Renombrar columnas clave para facilitar el acceso
    df.rename(columns={
        '2. En los últimos 6 meses, ¿has considerado seriamente la posibilidad de abandonar tus estudios o darte de baja temporal?': 'Considera_Abandono',
        '3. En una escala del 1 al 5, ¿con qué frecuencia has tenido estos pensamientos?': 'Frecuencia_Abandono',
        '4. Pensando en tu rendimiento del semestre pasado, ¿cuál de estas frases te describe mejor?': 'Rendimiento_Semestre',
        '5. ¿Sientes que la carrera que elegiste ha cumplido con tus expectativas?': 'Expectativas_Cumplidas',
        '1. De la siguiente lista, por favor selecciona los 3 desafíos NO académicos más importantes que has enfrentado en el último año.': 'Desafios_No_Academicos',
        '2. ¿Cuentas actualmente con alguna beca (académica, de manutención, etc.)?': 'Tiene_Beca',
        '3. ¿Conoces los servicios de tutoría o apoyo psicopedagógico que ofrece la UNRC?': 'Conoce_Apoyo',
        '¿Qué recompensa deseas?': 'Email_Sorteo',
        '1. ¿Cual es tu licenciatura?': 'Licenciatura'
    }, inplace=True)
    
    # Manejar la columna de desafíos (múltiples selecciones separadas por comas)
    # Creamos una lista de desafíos únicos a partir de esta columna
    all_challenges = set()
    
    def extract_challenges(challenges_str):
        if pd.isna(challenges_str):
            return []
        # Limpiar y dividir la cadena de desafíos
        # Nota: Hay que tener cuidado con los espacios extra y el final de línea en la última entrada
        challenges = [c.strip() for c in challenges_str.split(',') if c.strip()]
        all_challenges.update(challenges)
        return challenges

    df['Desafios_List'] = df['Desafios_No_Academicos'].apply(extract_challenges)
    
    # Eliminar columnas temporales o no necesarias para el grafo inicial
    df.drop(columns=['Marca temporal', 'Desafios_No_Academicos', 'Email_Sorteo', 'Columna 9'], errors='ignore', inplace=True)
    
    print(f"Limpieza inicial completada. Filas restantes: {len(df)}. Desafíos únicos encontrados: {len(all_challenges)}")
    return df

if __name__ == '__main__':
    # Nombre del archivo CSV movido
    CSV_FILENAME = "_Pulso de la Trayectoria Estudiantil UNRC_ (Respuestas) - Respuestas de formulario 1.csv"
    
    data = load_data(CSV_FILENAME)
    if not data.empty:
        cleaned_data = clean_data(data)
        # Aquí se podría guardar el DataFrame limpio en data/processed/
        # cleaned_data.to_csv(os.path.join("data", "processed", "cleaned_data.csv"), index=False)
        print("Proceso de carga y limpieza simulado.")