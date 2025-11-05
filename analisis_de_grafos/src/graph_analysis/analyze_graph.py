import networkx as nx
import os

GRAPH_FILE = "results/initial_cooccurrence_graph.gexf"
ANALYSIS_OUTPUT_FILE = "results/centrality_analysis.txt"

def analyze_centrality(graph_path: str, output_path: str):
    """
    Carga un grafo y realiza un análisis de centralidad, guardando los resultados.
    """
    if not os.path.exists(graph_path):
        print(f"Error: Archivo de grafo no encontrado en {graph_path}")
        return

    G = nx.read_gexf(graph_path)
    print(f"Grafo cargado para análisis: Nodos={G.number_of_nodes()}, Aristas={G.number_of_edges()}")

    # --- 1. Centralidad de Grado (Ponderada por el peso de las aristas) ---
    # Mide la fuerza total de las conexiones de un nodo.
    degree_centrality = G.degree(weight='weight')
    sorted_degree = sorted(degree_centrality, key=lambda item: item[1], reverse=True)

    # --- 2. Centralidad de Intermediación ---
    # Mide cuántas veces un nodo actúa como puente.
    betweenness_centrality = nx.betweenness_centrality(G, weight='weight')
    sorted_betweenness = sorted(betweenness_centrality.items(), key=lambda item: item[1], reverse=True)

    # --- 3. Centralidad de Vector Propio ---
    # Mide la influencia de un nodo en la red.
    try:
        eigenvector_centrality = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
        sorted_eigenvector = sorted(eigenvector_centrality.items(), key=lambda item: item[1], reverse=True)
    except nx.PowerIterationFailedConvergence:
        print("La centralidad de vector propio no convergió. Se omitirá este análisis.")
        sorted_eigenvector = []

    # --- Guardar resultados en un archivo ---
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("--- ANÁLISIS DE CENTRALIDAD DEL GRAFO ---\n\n")
        
        f.write("1. Centralidad de Grado (Ponderada) - Factores más conectados\n")
        f.write("   Mide la fuerza total de las conexiones de un nodo.\n")
        f.write("------------------------------------------------------------\n")
        for node, value in sorted_degree[:5]:
            f.write(f"- {node}: {value:.2f}\n")
        
        f.write("\n2. Centralidad de Intermediación - Factores 'puente' más críticos\n")
        f.write("   Mide la frecuencia con la que un nodo conecta diferentes grupos de factores.\n")
        f.write("--------------------------------------------------------------------------\n")
        for node, value in sorted_betweenness[:5]:
            f.write(f"- {node}: {value:.4f}\n")

        if sorted_eigenvector:
            f.write("\n3. Centralidad de Vector Propio - Factores más influyentes\n")
            f.write("   Mide la influencia de un nodo al estar conectado a otros nodos influyentes.\n")
            f.write("---------------------------------------------------------------------------\n")
            for node, value in sorted_eigenvector[:5]:
                f.write(f"- {node}: {value:.4f}\n")

    print(f"Análisis de centralidad completado. Resultados guardados en: {output_path}")
    
    # Imprimir en consola también
    with open(output_path, 'r', encoding='utf-8') as f:
        print(f.read())


if __name__ == '__main__':
    analyze_centrality(GRAPH_FILE, ANALYSIS_OUTPUT_FILE)