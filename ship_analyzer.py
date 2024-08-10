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

    status = "Pass" if health > 0 and connected_components == 1 else "Fail"

    print(f"\nTotal nodes   : {total_nodes}")
    print(f"  Connected   : {num_connected_nodes}")
    print(f"  Unconnected : {num_unconnected_nodes}")
    print(f"  Affected    : {(num_unconnected_nodes / total_nodes):.2%}\n")
    print(f"Components    : {connected_components}\n")
    print(f"Health        : {health:.2%}\n")
    print(f"Status        : {status}\n")
    
    return {
        'total_nodes': total_nodes,
        'num_connected': num_connected,
        'num_unconnected': num_unconnected_nodes,
        'components': connected_components,
        'health': health,
        'status': status
    }


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

    for node in G.nodes():
        x, y, z = pos[node]
        degree = len(list(G.neighbors(node)))  # Get the degree of the node
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        node_text.append(f"{node}<br>Degree: {degree}")
        node_color.append(degree)  # Color based on degree
        progress_bar.update(1)

    node_trace = go.Scatter3d(
        x=node_x,
        y=node_y,
        z=node_z,
        text=node_text,
        mode='markers',
        # textposition='top center',
        hoverinfo='text',
        marker=dict(
            size=8,
            color=node_color,
            colorscale='Viridis',  # Color scale for degree
            opacity=0.8
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

