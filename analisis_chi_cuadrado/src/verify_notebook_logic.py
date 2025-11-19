import pandas as pd
import os
from scipy.stats import chi2_contingency

# Simulate running from src directory
os.chdir('/Users/arianstoned/Desktop/dropout_MLE_model/analisis_chi_cuadrado/src')

print("Current working directory:", os.getcwd())

try:
    df = pd.read_csv("../data/processed/datos_limpios.csv")
    print("Data loaded successfully.")
    print(f"Shape: {df.shape}")
    
    # Test Chi2 logic
    tabla = pd.crosstab(df['rendimiento_semestre_pasado'], df['abandono_considerado'])
    chi2, p, dof, expected = chi2_contingency(tabla)
    print("Chi2 test ran successfully.")
    print(f"P-value: {p}")
    
except Exception as e:
    print(f"Error: {e}")
