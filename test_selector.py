
import pandas as pd
from scipy.stats import shapiro, levene, chi2_contingency, mannwhitneyu, kruskal

def get_variable_type(series):
    """Determina si una variable es categórica o numérica."""
    if pd.api.types.is_numeric_dtype(series) and series.nunique() > 10:
        return 'numerica'
    else:
        # Trata variables con pocos valores únicos como categóricas/ordinales
        return 'categorica_ordinal'

def choose_statistical_test(df, var1_name, var2_name, force_type={}):
    """
    Analiza dos variables de un DataFrame y recomienda el test estadístico más apropiado.

    Args:
        df (pd.DataFrame): El DataFrame que contiene los datos.
        var1_name (str): El nombre de la primera variable.
        var2_name (str): El nombre de la segunda variable.
        force_type (dict): Un diccionario para forzar el tipo de una variable. 
                           Ej: {'frecuencia_abandono': 'numerica'}
    """
    print(f"Analizando '{var1_name}' y '{var2_name}'...")
    
    var1 = df[var1_name].dropna()
    var2 = df[var2_name].dropna()

    type1 = force_type.get(var1_name, get_variable_type(var1))
    type2 = force_type.get(var2_name, get_variable_type(var2))

    # --- Caso 1: Ambas variables son categóricas/ordinales ---
    if type1 == 'categorica_ordinal' and type2 == 'categorica_ordinal':
        print(f"  - '{var1_name}' es tratada como Categórica/Ordinal.")
        print(f"  - '{var2_name}' es tratada como Categórica/Ordinal.")
        print("\nRecomendación: Usar el Test de Chi-cuadrado.")
        print("  - Razón: Este test es ideal para evaluar si existe una asociación entre dos variables categóricas.")
        
        # Realizar el test para dar un ejemplo
        try:
            contingency_table = pd.crosstab(df[var1_name], df[var2_name])
            chi2, p, _, _ = chi2_contingency(contingency_table)
            print(f"\n  - Ejemplo de resultado (Chi2={chi2:.2f}, p-value={p:.3f}):")
            if p < 0.05:
                print("    El p-value es < 0.05, lo que sugiere una asociación estadísticamente significativa.")
            else:
                print("    El p-value es >= 0.05, no hay evidencia de una asociación estadísticamente significativa.")
        except ValueError:
            print("\n  - No se pudo calcular el Chi-cuadrado (posiblemente por datos insuficientes).")
        return

    # --- Caso 2: Una variable es categórica y la otra es numérica ---
    if type1 == 'categorica_ordinal' and type2 == 'numerica':
        cat_var_name, num_var_name = var1_name, var2_name
    elif type1 == 'numerica' and type2 == 'categorica_ordinal':
        cat_var_name, num_var_name = var2_name, var1_name
    else:
        print("Combinación de tipos de variable no soportada para T-test o Kruskal-Wallis.")
        return

    print(f"  - Variable de Agrupación (Categórica): '{cat_var_name}'")
    print(f"  - Variable de Medición (Numérica): '{num_var_name}'")

    groups = df[cat_var_name].dropna().unique()
    
    is_normal = True
    variances_data = []
    
    print("\n1. Verificando supuestos para T-test/ANOVA:")
    
    for group in groups:
        group_data = df[df[cat_var_name] == group][num_var_name].dropna()
        if len(group_data) > 2:
            _, p_shapiro = shapiro(group_data)
            if p_shapiro < 0.05:
                is_normal = False
            variances_data.append(group_data)

    if is_normal:
        print("  - Supuesto de Normalidad (Test de Shapiro-Wilk): Cumplido. Los datos parecen normales en cada grupo.")
    else:
        print("  - Supuesto de Normalidad (Test de Shapiro-Wilk): No Cumplido. Al menos un grupo no sigue una distribución normal.")

    levene_p = -1
    homogeneidad = False
    if len(variances_data) > 1:
        _, levene_p = levene(*variances_data)
        if levene_p > 0.05:
            homogeneidad = True

    if homogeneidad:
        print("  - Supuesto de Homogeneidad de Varianzas (Test de Levene): Cumplido. Las varianzas son homogéneas.")
    else:
        print("  - Supuesto de Homogeneidad de Varianzas (Test de Levene): No Cumplido. Las varianzas no son homogéneas.")

    print("\n--- Recomendación Final ---")
    if len(groups) == 2:
        if is_normal and homogeneidad:
            print("=> Usar T-test para muestras independientes.")
            print("   Razón: Estás comparando las medias de una variable numérica que cumple los supuestos de normalidad y homogeneidad de varianzas entre dos grupos.")
        else:
            print("=> Usar Test U de Mann-Whitney (alternativa no paramétrica al T-test).")
            print("   Razón: La variable numérica no cumple el supuesto de normalidad y/o homogeneidad de varianzas.")
    elif len(groups) > 2:
        if is_normal and homogeneidad:
            print("=> Usar ANOVA de una vía.")
            print("   Razón: Estás comparando las medias de una variable numérica que cumple los supuestos entre más de dos grupos.")
        else:
            print("=> Usar Test de Kruskal-Wallis (alternativa no paramétrica a ANOVA).")
            print("   Razón: La variable numérica no cumple el supuesto de normalidad y/o homogeneidad de varianzas.")
    else:
        print("Se necesita al menos dos grupos para comparar.")


if __name__ == '__main__':
    try:
        df = pd.read_csv('analisis_chi_cuadrado/data/processed/datos_limpios.csv')
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'analisis_chi_cuadrado/data/processed/datos_limpios.csv'")
        exit()

    print("--- Ejemplo 1: Dos variables categóricas ---")
    choose_statistical_test(df, 'abandono_considerado', 'beca_actual')
    
    print("\n" + "="*60 + "\n")

    print("--- Ejemplo 2: Categórica (2 grupos) vs Numérica/Ordinal ---")
    print("Forzando a 'frecuencia_abandono' a ser tratada como numérica para el análisis.")
    choose_statistical_test(df, 'beca_actual', 'frecuencia_abandono', force_type={'frecuencia_abandono': 'numerica'})

    print("\n" + "="*60 + "\n")

    print("--- Ejemplo 3: Categórica (>2 grupos) vs Numérica/Ordinal ---")
    print("Forzando a 'frecuencia_abandono' a ser tratada como numérica para el análisis.")
    choose_statistical_test(df, 'rendimiento_semestre_pasado', 'frecuencia_abandono', force_type={'frecuencia_abandono': 'numerica'})
