#!/usr/bin/env python3
# Script de prueba para ejecutar las funciones de data_processing.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.data.data_processing import load_data, clean_data, create_features, preprocess_data, save_processed_data

# Ejecutar pipeline completo
print("🚀 Ejecutando pipeline de preprocesamiento...")

# 1. Cargar datos
df = load_data("data/raw/data.csv")

# 2. Limpiar datos
df = clean_data(df)

# 3. Crear features
df = create_features(df)

# 4. Aplicar preprocesamiento (opcional, para obtener arrays procesados)
X_processed, y, feature_names, preprocessor = preprocess_data(df)

# 5. Guardar datos procesados
output_path = "data/processed/preprocessed_data.parquet"
save_processed_data(df, output_path)

print("✅ Pipeline ejecutado exitosamente!")
print(f"📊 Datos finales guardados en: {output_path}")
print(f"🔧 Número de características nuevas: {len([col for col in df.columns if col not in ['Marital status', 'Application mode', 'Course', 'Target']])}")
