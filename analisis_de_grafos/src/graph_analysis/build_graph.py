import pandas as pd
import networkx as nx
from typing import Tuple
from src.data_processing.load_and_clean import load_data, clean_data

CSV_FILENAME = "_Pulso de la Trayectoria Estudiantil UNRC_ (Respuestas) - Respuestas de formulario 1.csv"

def create_graph_structure(df: pd.DataFrame) -> nx.Graph:
    """
    Crea un grafo de co-ocurrencia basado en las respuestas de la encuesta.
    Los nodos son las respuestas/atributos únicos, y las aristas indican co-ocurrencia en la misma fila.
    """
    if df.empty:
        print("DataFrame vacío, devolviendo grafo vacío.")
        return nx.Graph()

    G = nx.Graph()
    
    # Columnas clave para el análisis de co-ocurrencia (excluyendo el ID implícito de fila)
    key_columns = [
        'Considera_Abandono', 
        'Frecuencia_Abandono', 
        'Rendimiento_Semestre', 
        'Expectativas_Cumplidas', 
        'Tiene_Beca', 
        'Conoce_Apoyo', 
        'Licenciatura'
    ]
    
    # 1. Añadir nodos de atributos categóricos (no desafíos)
    for col in key_columns:
        if col in df.columns:
            nodes = df[col].dropna().unique()
            G.add_nodes_from(nodes, type='attribute')

    # 2. Añadir nodos de desafíos y crear aristas de co-ocurrencia
    # Iterar sobre cada fila (encuestado)
    for index, row in df.iterrows():
        
        # Nodos de atributos categóricos (para asegurar que cada fila se conecte a sus atributos)
        current_nodes = set()
        for col in key_columns:
            if col in df.columns and pd.notna(row[col]):
                current_nodes.add(str(row[col]))
        
        # Nodos de desafíos (si existen)
        if 'Desafios_List' in df.columns and row['Desafios_List']:
            for challenge in row['Desafios_List']:
                challenge_node = f"Desafio: {challenge}"
                current_nodes.add(challenge_node)
                G.add_node(challenge_node, type='challenge')
        
        # Crear aristas entre todos los nodos presentes en esta fila (co-ocurrencia)
        node_list = list(current_nodes)
        if len(node_list) > 1:
            # Usar combinaciones para crear aristas entre todos los conceptos de esta fila
            for i in range(len(node_list)):
                for j in range(i + 1, len(node_list)):
                    u, v = node_list[i], node_list[j]
                    if G.has_edge(u, v):
                        G[u][v]['weight'] += 1
                    else:
                        G.add_edge(u, v, weight=1)

    print(f"Grafo de co-ocurrencia construido. Nodos: {G.number_of_nodes()}, Aristas: {G.number_of_edges()}")
    return G

def main():
    """Función principal para cargar datos y construir el grafo."""
    print("Iniciando construcción del grafo...")
    
    # 1. Cargar y limpiar datos
    raw_df = load_data(CSV_FILENAME)
    if raw_df.empty:
        print("No se pudo construir el grafo debido a datos vacíos.")
        return
        
    cleaned_df = clean_data(raw_df)
    
    # 2. Construir el grafo
    G = create_graph_structure(cleaned_df)
    
    print(f"Grafo construido. Número de nodos: {G.number_of_nodes()}, Número de aristas: {G.number_of_edges()}")
    
    # 3. Guardar el grafo
    output_path = "results/initial_cooccurrence_graph.gexf"
    nx.write_gexf(G, output_path)
    print(f"Grafo guardado en {output_path}")

if __name__ == '__main__':
    main()