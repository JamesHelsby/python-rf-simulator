import plotly.graph_objects as go
import plotly.offline as pyo
import networkx as nx
from tqdm import tqdm


def analyse_graph(G):
    total_nodes = len(G.nodes())
    unconnected_nodes = [node for node in G.nodes() if len(list(G.neighbors(node))) == 0]
    num_unconnected_nodes = len(unconnected_nodes)
    num_connected_nodes = total_nodes - num_unconnected_nodes
    connected_components = nx.number_connected_components(G.subgraph([n for n in G.nodes() if len(list(G.neighbors(n))) > 0]))

    num_connected = total_nodes - num_unconnected_nodes
    threshold = -(-total_nodes // 3)  # Equivalent to math.ceil(total_nodes / 3)
    if num_unconnected_nodes == 0:
        health = 1.0
    elif num_connected <= threshold:
        health = 0.0
    else:
        health = (num_connected - threshold) / (total_nodes - threshold)

    honest_nodes = [node for node, data in G.nodes(data=True) if not data['malicious']]
    malicious_nodes = [node for node, data in G.nodes(data=True) if data['malicious']]
    jamming_nodes = [node for node in malicious_nodes if G.nodes[node]['jammer']]
    non_jamming_malicious_nodes = [node for node in malicious_nodes if not G.nodes[node]['jammer']]

    num_honest = len(honest_nodes)
    num_malicious = len(malicious_nodes)
    num_jamming = len(jamming_nodes)
    num_non_jamming_malicious = len(non_jamming_malicious_nodes)

    status = "Pass" if health > 0 and connected_components == 1 else "Fail"

    print(f"\nTotal nodes             : {total_nodes}")
    print(f"  Connected             : {num_connected_nodes}")
    print(f"  Unconnected           : {num_unconnected_nodes}")
    print(f"  Affected              : {(num_unconnected_nodes / total_nodes):.2%}\n")
    print(f"Total Honest Nodes      : {num_honest}")
    print(f"Total Malicious Nodes   : {num_malicious}")
    print(f"  Non-Jamming Malicious : {num_non_jamming_malicious}")
    print(f"  Jamming Malicious     : {num_jamming}\n")
    # print(f"Health                  : {health:.2%}\n")
    print(f"Components              : {connected_components}\n")
    print(f"Status                  : {status}\n")




def plot_container_network(ship, display=True):
    if ship.G is None:
        ship.generate_container_graph()
    
    G = ship.G

    pos = nx.get_node_attributes(G, 'pos')
    labels = nx.get_node_attributes(G, 'container')

    total_steps = len(G.edges()) + len(G.nodes())
    progress_bar = tqdm(total=total_steps, desc="Rendering graph     ")

    edge_x = []
    edge_y = []
    edge_z = []

    for edge in G.edges():
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        edge_z += [z0, z1, None]
        progress_bar.update(1)

    edge_trace = go.Scatter3d(
        x=edge_x,
        y=edge_y,
        z=edge_z,
        line=dict(width=2, color='red'),
        hoverinfo='none',
        mode='lines'
    )

    node_x = []
    node_y = []
    node_z = []
    node_text = []
    node_color = []

    for node in G.nodes(data=True):
        x, y, z = pos[node[0]]
        degree = len(list(G.neighbors(node[0])))
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        node_text.append(f"{node[0]}<br>Degree: {degree}")
        
        if node[1]['malicious']:
            node_color.append('black')
        else:
            node_color.append(degree)
        
        progress_bar.update(1)

    node_trace = go.Scatter3d(
        x=node_x,
        y=node_y,
        z=node_z,
        text=node_text,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            size=8,
            color=node_color,
            colorscale='Viridis',
            opacity=0.8,
            line=dict(width=2, color='black')
        )
    )

    progress_bar.close()

    fig = go.Figure(data=[edge_trace, node_trace])

    fig.update_layout(scene=dict(
        xaxis=dict(title='Bays', showbackground=False, showticklabels=False),
        yaxis=dict(title='Rows', showbackground=False, showticklabels=False),
        zaxis=dict(title='Layers', showbackground=False, showticklabels=False),
        aspectmode='data'
    ),
    showlegend=False)

    if display:
        pyo.plot(fig, filename='network_layout.html', auto_open=True)

    return fig, G

