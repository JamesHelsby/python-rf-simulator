import plotly.graph_objects as go
import plotly.offline as pyo
import networkx as nx
from tqdm import tqdm


def analyse_graph(G):
    total_nodes = len(G.nodes())
    unconnected = [node for node in G.nodes() if len(list(G.neighbors(node))) == 0]
    num_unconnected = len(unconnected)
    num_connected = total_nodes - num_unconnected
    
    connected_subgraph = G.subgraph([n for n in G.nodes() if len(list(G.neighbors(n))) > 0])
    connected_components = list(nx.connected_components(connected_subgraph))
    num_connected_components = len(connected_components)

    honest_nodes = [node for node, data in G.nodes(data=True) if not data['malicious']]
    malicious_nodes = [node for node, data in G.nodes(data=True) if data['malicious']]
    jamming_nodes = [node for node in malicious_nodes if G.nodes[node]['jammer']]
    non_jamming_malicious_nodes = [node for node in malicious_nodes if not G.nodes[node]['jammer']]

    num_honest = len(honest_nodes)
    num_malicious = len(malicious_nodes)
    num_jamming = len(jamming_nodes)
    num_non_jammings = len(non_jamming_malicious_nodes)

    B = total_nodes - 1 - 3 * num_malicious
    trustset_configuration = B >= (num_unconnected - num_jamming)

    status = "Pass" if trustset_configuration and num_connected_components == 1 else "Fail"

    print(f"\nTotal nodes             : {total_nodes}")
    print(f"  Honest Nodes          : {num_honest}")
    print(f"  Jamming Nodes         : {num_jamming}\n")

    print(f"Total disconnected      : {num_unconnected}")
    print(f"  Potential Honest      : {num_unconnected - num_jamming}")
    print(f"  Buffer Margin         : {B}\n")

    print(f"Trustset Configuration  : {trustset_configuration}\n")

    print(f"Components              : {num_connected_components}")
    if num_connected_components > 1:
        for i, component in enumerate(connected_components):
            print(f"  Component {i + 1:<12}: {len(component)} nodes")
        print()
    else:
        print()

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
        pyo.plot(fig, filename='network_layout.html', auto_open=False)

    return fig, G

