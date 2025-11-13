#!/usr/bin/env python3
"""
Script para visualizar métricas de DVC de forma organizada y clara
"""

import json
import os
from pathlib import Path
import pandas as pd

def load_metrics(metrics_dir="metrics"):
    """Cargar todos los archivos de métricas"""
    metrics = {}
    metrics_path = Path(metrics_dir)
    
    if not metrics_path.exists():
        print(f"Error: Directorio {metrics_dir} no encontrado")
        return metrics
    
    for json_file in sorted(metrics_path.glob("*.json")):
        try:
            with open(json_file, 'r') as f:
                metrics[json_file.stem] = json.load(f)
        except Exception as e:
            print(f"Error al cargar {json_file}: {e}")
    
    return metrics

def print_header(title):
    """Imprimir encabezado de sección"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_section(title):
    """Imprimir encabezado de subsección"""
    print(f"\n>>> {title}")
    print("-" * 60)

def format_value(value):
    """Formatear valor para visualización"""
    if isinstance(value, bool):
        return "✓ Sí" if value else "✗ No"
    elif isinstance(value, float):
        return f"{value:.4f}"
    elif isinstance(value, list):
        return f"[{len(value)} elementos]"
    else:
        return str(value)

def show_preprocess_metrics(metrics):
    """Mostrar métricas de preprocesamiento"""
    if 'preprocess' not in metrics:
        return
    
    print_header("ETAPA 1: PREPROCESAMIENTO")
    data = metrics['preprocess']
    
    print(f"Filas de entrada:        {data.get('input_rows', 'N/A')}")
    print(f"Filas de salida:         {data.get('output_rows', 'N/A')}")
    print(f"Filas eliminadas:        {data.get('removed_rows', 'N/A')}")
    print(f"Columnas finales:        {data.get('final_columns', 'N/A')}")
    print(f"Carreras únicas:         {data.get('unique_licenciaturas', 'N/A')}")
    
    if 'licenciaturas' in data:
        print(f"\nCarreras identificadas ({len(data['licenciaturas'])}):")
        for carrera in data['licenciaturas']:
            print(f"  • {carrera}")

def show_exploratory_metrics(metrics):
    """Mostrar métricas de análisis exploratorio"""
    if 'exploratory' not in metrics:
        return
    
    print_header("ETAPA 2: ANÁLISIS EXPLORATORIO")
    data = metrics['exploratory']
    
    print(f"Total de estudiantes:           {data.get('total_estudiantes', 'N/A')}")
    print(f"Consideraron abandonar (Sí):    {data.get('consideraron_abandonar', 'N/A')}")
    print(f"Porcentaje de abandono:         {data.get('porcentaje_abandono', 'N/A'):.2f}%")
    print(f"\nFrecuencia de pensamientos (1-5):")
    print(f"  Promedio:                     {data.get('frecuencia_abandono_promedio', 'N/A'):.2f}")
    print(f"  Mediana:                      {data.get('frecuencia_abandono_mediana', 'N/A'):.2f}")
    print(f"\nDesafíos más común:             {data.get('desafio_mas_comun', 'N/A')}")
    print(f"Total desafíos únicos:          {data.get('desafios_unicos', 'N/A')}")

def show_hypothesis_metrics(metrics):
    """Mostrar métricas de hipótesis"""
    print_header("ETAPAS 3-5: PRUEBAS DE HIPÓTESIS")
    
    # Hipótesis 1
    if 'hipotesis1' in metrics:
        print_section("HIPÓTESIS 1: Rendimiento vs. Abandono")
        data = metrics['hipotesis1']
        print(f"Chi-Cuadrado (χ²):       {data.get('chi2_statistic', 'N/A'):.4f}")
        print(f"P-valor:                 {data.get('p_value', 'N/A'):.4f}")
        print(f"Significancia (α=0.05):  {format_value(data.get('significance', False))}")
        print(f"Tasa máx abandono:       {data.get('max_abandono_rate', 'N/A'):.2f}%")
        print(f"Tasa mín abandono:       {data.get('min_abandono_rate', 'N/A'):.2f}%")
    
    # Hipótesis 2
    if 'hipotesis2' in metrics:
        print_section("HIPÓTESIS 2A: Beca vs. Abandono")
        data = metrics['hipotesis2']
        beca = data.get('beca_actual', {})
        print(f"Chi-Cuadrado (χ²):       {beca.get('chi2_statistic', 'N/A'):.4f}")
        print(f"P-valor:                 {beca.get('p_value', 'N/A'):.4f}")
        print(f"Significancia (α=0.05):  {format_value(beca.get('significance', False))}")
        print(f"Con beca:                {data.get('con_beca', 'N/A')} estudiantes")
        print(f"Sin beca:                {data.get('sin_beca', 'N/A')} estudiantes")
        
        print_section("HIPÓTESIS 2B: Desafío Económico vs. Abandono")
        econ = data.get('desafio_economico', {})
        print(f"Chi-Cuadrado (χ²):       {econ.get('chi2_statistic', 'N/A'):.4f}")
        print(f"P-valor:                 {econ.get('p_value', 'N/A'):.4f}")
        print(f"Significancia (α=0.05):  {format_value(econ.get('significance', False))}")
        print(f"Con desafío económico:   {data.get('con_desafio_economico', 'N/A')} estudiantes")
    
    # Hipótesis 3
    if 'hipotesis3' in metrics:
        print_section("HIPÓTESIS 3: Expectativas vs. Abandono")
        data = metrics['hipotesis3']
        print(f"Chi-Cuadrado (χ²):       {data.get('chi2_statistic', 'N/A'):.4f}")
        print(f"P-valor:                 {data.get('p_value', 'N/A'):.4f}")
        print(f"Significancia (α=0.05):  {format_value(data.get('significance', False))}")
        print(f"Tasa máx abandono:       {data.get('max_abandono_rate', 'N/A'):.2f}%")
        print(f"Tasa mín abandono:       {data.get('min_abandono_rate', 'N/A'):.2f}%")

def show_ordinal_metrics(metrics):
    """Mostrar métricas de análisis ordinal"""
    if 'ordinal' not in metrics:
        return
    
    print_header("ETAPA 6: ANÁLISIS ORDINAL (Kruskal-Wallis / Mann-Whitney)")
    data = metrics['ordinal']
    
    # Rendimiento
    if 'rendimiento' in data:
        print_section("Frecuencia vs. Rendimiento Académico")
        rend = data['rendimiento']
        print(f"Prueba:                  {rend.get('prueba_nombre', 'N/A')}")
        print(f"Estadístico:             {rend.get('estadistico', 'N/A'):.4f}")
        print(f"P-valor:                 {rend.get('p_value', 'N/A'):.4f}")
        print(f"Significancia (α=0.05):  {format_value(rend.get('significance', False))}")
    
    # Beca
    if 'beca' in data:
        print_section("Frecuencia vs. Tenencia de Beca")
        beca = data['beca']
        print(f"Prueba:                  {beca.get('prueba_nombre', 'N/A')}")
        print(f"Estadístico:             {beca.get('estadistico', 'N/A'):.4f}")
        print(f"P-valor:                 {beca.get('p_value', 'N/A'):.4f}")
        print(f"Significancia (α=0.05):  {format_value(beca.get('significance', False))}")
    
    # Expectativas
    if 'expectativas' in data:
        print_section("Frecuencia vs. Expectativas de Carrera")
        exp = data['expectativas']
        print(f"Prueba:                  {exp.get('prueba_nombre', 'N/A')}")
        print(f"Estadístico:             {exp.get('estadistico', 'N/A'):.4f}")
        print(f"P-valor:                 {exp.get('p_value', 'N/A'):.4f}")
        print(f"Significancia (α=0.05):  {format_value(exp.get('significance', False))}")
    
    print(f"\nEstudiantes analizados:  {data.get('sample_size', 'N/A')}")
    print(f"Frecuencia promedio (1-5): {data.get('frecuencia_promedio', 'N/A'):.2f}")
    print(f"Frecuencia mediana (1-5):  {data.get('frecuencia_mediana', 'N/A'):.2f}")

def show_summary(metrics):
    """Mostrar resumen de resultados significativos"""
    print_header("RESUMEN DE RESULTADOS SIGNIFICATIVOS (p < 0.05)")
    
    significativas = []
    
    if 'hipotesis1' in metrics:
        data = metrics['hipotesis1']
        if data.get('significance', False):
            significativas.append("✓ Hipótesis 1: Rendimiento vs. Abandono")
    
    if 'hipotesis3' in metrics:
        data = metrics['hipotesis3']
        if data.get('significance', False):
            significativas.append("✓ Hipótesis 3: Expectativas vs. Abandono")
    
    if 'ordinal' in metrics:
        data = metrics['ordinal']
        if data.get('rendimiento', {}).get('significance', False):
            significativas.append("✓ Análisis Ordinal: Rendimiento → Frecuencia")
        if data.get('expectativas', {}).get('significance', False):
            significativas.append("✓ Análisis Ordinal: Expectativas → Frecuencia")
    
    if significativas:
        print("\nPruebas estadísticamente significativas:")
        for item in significativas:
            print(f"  {item}")
    else:
        print("\nNo hay pruebas estadísticamente significativas con α=0.05")

def main():
    """Función principal"""
    print("\n" + "█"*80)
    print("█  REPORTE DE MÉTRICAS DEL PIPELINE DVC")
    print("█"*80)
    
    metrics = load_metrics()
    
    if not metrics:
        print("No se encontraron métricas")
        return
    
    show_preprocess_metrics(metrics)
    show_exploratory_metrics(metrics)
    show_hypothesis_metrics(metrics)
    show_ordinal_metrics(metrics)
    show_summary(metrics)
    
    print("\n" + "█"*80)
    print("█  FIN DEL REPORTE")
    print("█"*80 + "\n")

if __name__ == "__main__":
    main()