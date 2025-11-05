import networkx as nx
import matplotlib.pyplot as plt
import os

GRAPH_FILE = "results/initial_cooccurrence_graph.gexf"
OUTPUT_IMAGE = "results/initial_cooccurrence_graph.png"

def visualize_graph(graph_path: str, output_path: str):
    """Carga un grafo GEXF y lo visualiza usando Matplotlib."""
    
    if not os.path.exists(graph_path):
        print(f"Error: Archivo de grafo no encontrado en {graph_path}")
        return

    print(f"Cargando grafo desde: {graph_path}")
    try:
        G = nx.read_gexf(graph_path)
    except Exception as e:
        print(f"Error al leer el archivo GEXF: {e}")
        return

    print(f"Grafo cargado: Nodos={G.number_of_nodes()}, Aristas={G.number_of_edges()}")

    # Configuración de visualización
    plt.figure(figsize=(18, 18))
    
    # --- Mejoras Avanzadas de Visualización ---

    # 1. Algoritmo de Layout Kamada-Kawai para una mejor distribución
    pos = nx.kamada_kawai_layout(G)

    # 2. Filtrar aristas débiles para reducir el desorden
    strong_edges = [(u, v) for u, v, d in G.edges(data=True) if d['weight'] > 1]
    
    # 3. Detección de comunidades para colorear nodos
    communities = nx.community.greedy_modularity_communities(G)
    node_colors = {}
    color_map = plt.get_cmap('viridis', len(communities))
    for i, community in enumerate(communities):
        for node in community:
            node_colors[node] = color_map(i)

    # 4. Tamaño de nodos basado en el grado ponderado (fuerza total de conexión)
    degrees = dict(G.degree(weight='weight'))
    # Crear una lista de tamaños ordenada por el orden de los nodos en G.nodes()
    node_sizes = [degrees.get(n, 0) * 20 for n in G.nodes()] # Multiplicador ajustado

    # 5. Grosor de aristas basado en el peso (solo para aristas fuertes)
    weights = [G[u][v]['weight'] for u, v in strong_edges]
    max_weight = max(weights) if weights else 1.0
    edge_widths = [(w / max_weight) * 4.0 + 0.5 for w in weights]

    # Dibujar la red con las mejoras
    # Dibujar todos los nodos con sus colores de comunidad y tamaños calculados
    nx.draw_networkx_nodes(G, pos, node_color=[node_colors.get(n, 'gray') for n in G.nodes()], node_size=node_sizes, alpha=0.8)
    
    # Dibujar solo las aristas fuertes
    nx.draw_networkx_edges(G, pos, edgelist=strong_edges, width=edge_widths, alpha=0.3, edge_color='gray')

    # 6. Etiquetado y resaltado de nodos críticos (Top 10 por Intermediación)
    betweenness_centrality = nx.betweenness_centrality(G, weight='weight')
    sorted_betweenness = sorted(betweenness_centrality.items(), key=lambda item: item[1], reverse=True)
    top_nodes = [node for node, value in sorted_betweenness[:10]]
    
    # Crear etiquetas solo para los nodos principales
    labels = {node: node.replace("Desafio: ", "") if node.startswith("Desafio: ") else node for node in top_nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=9, font_color='black', font_weight='bold')

    # Resaltar los nodos principales con un borde rojo
    # Se usa una lista de tamaños que corresponde a todos los nodos, pero solo se dibujan los top_nodes
    nx.draw_networkx_nodes(G, pos, nodelist=top_nodes, node_size=[degrees.get(n, 0) * 20 for n in top_nodes], 
                           node_color=[node_colors.get(n, 'gray') for n in top_nodes],
                           edgecolors='red', linewidths=2.0)

    plt.title("Grafo de Co-ocurrencia de Factores de Abandono Estudiantil (Mejorado)")
    plt.axis('off')
    
    # Guardar la figura
    plt.savefig(output_path, format="PNG")
    print(f"Visualización guardada en: {output_path}")

if __name__ == '__main__':
    # Asegurar que el directorio de resultados exista
    os.makedirs(os.path.dirname(OUTPUT_IMAGE), exist_ok=True)
    visualize_graph(GRAPH_FILE, OUTPUT_IMAGE)