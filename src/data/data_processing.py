import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer

def load_data(file_path):
    """Carga el dataset desde un archivo CSV."""
    try:
        df = pd.read_csv(file_path, sep=";")
        print(f"✅ Datos cargados: {df.shape}")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

def clean_data(df):
    """Limpia el dataset: maneja valores nulos y verifica duplicados."""
    # Verificar duplicados
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        print(f"⚠️ Encontrados {duplicates} duplicados. Eliminando...")
        df = df.drop_duplicates()

    # Imputar valores nulos con estrategias apropiadas
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns

    # Para numéricas: usar mediana
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            df[col].fillna(df[col].median(), inplace=True)

    # Para categóricas: usar moda o 'Desconocido'
    for col in categorical_cols:
        if df[col].isnull().sum() > 0:
            mode_val = df[col].mode().iloc[0] if not df[col].mode().empty else 'Desconocido'
            df[col].fillna(mode_val, inplace=True)

    print(f"✅ Limpieza completada. Valores nulos restantes: {df.isnull().sum().sum()}")
    return df

def create_features(df):
    """Crea nuevas características basadas en análisis del EDA."""
    df = df.copy()

    # 1. Ratios de aprobación por semestre (core features del plan)
    df['Ratio_Aprobacion_S1'] = df['Curricular units 1st sem (approved)'] / df['Curricular units 1st sem (enrolled)'].replace(0, 1)
    df['Ratio_Aprobacion_S2'] = df['Curricular units 2nd sem (approved)'] / df['Curricular units 2nd sem (enrolled)'].replace(0, 1)
    df['Delta_Ratio_Aprobacion'] = df['Ratio_Aprobacion_S2'] - df['Ratio_Aprobacion_S1']

    # 2. Indicadores de rendimiento temprano (basado en EDA: dropout alto si bajo rendimiento inicial)
    df['Bajo_Rendimiento_S1'] = (df['Ratio_Aprobacion_S1'] < 0.5).astype(int)
    df['Mejora_Semestral'] = (df['Delta_Ratio_Aprobacion'] > 0.1).astype(int)

    # 3. Categorías de edad (EDA mostró grupos de riesgo: adultos jóvenes más propensos)
    df['Grupo_Edad_Riesgo'] = pd.cut(df['Age at enrollment'],
                                     bins=[0, 20, 25, 50],
                                     labels=['Joven_Adulto', 'Adulto_Joven_Riesgo', 'Adulto_Mayor']).astype(str)

    # 4. Indicadores socioeconómicos combinados (EDA: deudores y becarios tienen patrones)
    df['Socioeconomico_Riesgo'] = ((df['Debtor'] == 1) & (df['Scholarship holder'] == 0)).astype(int)
    df['Educacion_Padres_Alta'] = ((df["Mother's qualification"] > 30) | (df["Father's qualification"] > 30)).astype(int)

    # 5. Rendimiento académico promedio y variabilidad
    df['Nota_Promedio'] = (df['Curricular units 1st sem (grade)'] + df['Curricular units 2nd sem (grade)']) / 2
    df['Diferencia_Notas'] = df['Curricular units 2nd sem (grade)'] - df['Curricular units 1st sem (grade)']

    # 6. Efectividad de evaluaciones (EDA: menos evaluaciones podría indicar menor engagement)
    df['Eficiencia_S1'] = df['Curricular units 1st sem (approved)'] / df['Curricular units 1st sem (evaluations)'].replace(0, 1)
    df['Eficiencia_S2'] = df['Curricular units 2nd sem (approved)'] / df['Curricular units 2nd sem (evaluations)'].replace(0, 1)

    # 7. Características adicionales de riesgo (basado en correlaciones del EDA)
    df['Unidades_Sin_Evaluar_Total'] = df['Curricular units 1st sem (without evaluations)'] + df['Curricular units 2nd sem (without evaluations)']
    df['Tasa_Inflacion_Ajustada'] = df['Inflation rate'] * (1 + df['GDP'] / 100)  # Ajuste económico

    # Manejar valores infinitos o NaN generados por divisiones
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(0)

    print(f"✅ Nuevas características creadas: {len([col for col in df.columns if col not in ['Marital status', 'Application mode', 'Course', 'Target']])} adicionales, total columnas: {df.shape[1]}")
    return df

def preprocess_data(df, target_col='Target'):
    """Aplica todo el pipeline de preprocesamiento."""
    # Separar features y target
    feature_cols = [col for col in df.columns if col != target_col]
    X = df[feature_cols]
    y = df[target_col] if target_col in df.columns else None

    # Identificar tipos de columnas
    numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = X.select_dtypes(exclude=[np.number]).columns.tolist()

    # Crear preprocesador
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(drop='first', sparse_output=False), categorical_features)
        ],
        remainder='passthrough'
    )

    # Aplicar preprocesamiento
    X_processed = preprocessor.fit_transform(X)

    # Obtener nombres de características
    feature_names = (numeric_features +
                     preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_features).tolist())

    print(f"✅ Preprocesamiento completado. Features originales: {X.shape[1]}, procesadas: {X_processed.shape[1]}")

    return X_processed, y, feature_names, preprocessor

def save_processed_data(df, output_path):
    """Guarda el DataFrame procesado en formato Parquet."""
    try:
        df.to_parquet(output_path, index=False)
        print(f"✅ Datos guardados en: {output_path}")
    except Exception as e:
        print(f"❌ Error al guardar: {e}")
        raise