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


def plot_container_network(ship, camera, name, display=True):
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
    node_symbol = []

    for node in G.nodes(data=True):
        x, y, z = pos[node[0]]
        degree = len(list(G.neighbors(node[0])))
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        node_text.append(f"{node[0]}<br>Degree: {degree}")

        # Differentiate jamming and normal nodes
        if node[1]['jammer']:
            node_color.append('black')  # Set color for jamming nodes
            node_symbol.append('circle')  # Marker symbol for jamming nodes
        else:
            node_color.append('gray')  # Light gray color for normal nodes
            node_symbol.append('circle')  # Use default marker for normal nodes

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
            opacity=0.8,  # Keep the opacity for all nodes
            symbol=node_symbol,  # Different symbols for different node types
            line=dict(width=2, color='black')  # Outline color
        )
    )

    progress_bar.close()

    fig = go.Figure(data=[edge_trace, node_trace])

    fig.update_layout(scene=dict(
        xaxis=dict(title='Bays', showbackground=False, showticklabels=False),
        yaxis=dict(title='Rows', showbackground=False, showticklabels=False),
        zaxis=dict(title='Layers', showbackground=False, showticklabels=False),
        aspectmode='data',
        camera=camera
    ),
    showlegend=False)

    if display:
        pyo.plot(fig, filename='network_layout.html', auto_open=False)
        fig.write_image(f"{name}.png", width=800, height=600, scale=4)

    return fig, G

def plot_container_network_coloured(ship, camera, name, display=True):
    if ship.G is None:
        ship.generate_container_graph()
    
    G = ship.G

    pos = nx.get_node_attributes(G, 'pos')
    labels = nx.get_node_attributes(G, 'container')

    total_steps = len(G.edges()) + len(G.nodes())
    progress_bar = tqdm(total=total_steps, desc="Rendering graph     ")

    # Step 1: Filter out nodes with no edges (degree 0)
    nodes_with_edges = [n for n in G.nodes() if G.degree(n) > 0]
    filtered_subgraph = G.subgraph(nodes_with_edges)
    
    # Step 2: Find all connected components in the filtered subgraph
    connected_components = list(nx.connected_components(filtered_subgraph))

    # Step 3: Define a color map for the connected components
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta']
    edge_colors = {}
    
    # Assign a unique color to all edges in each connected component
    for i, component in enumerate(connected_components):
        color = colors[i % len(colors)]  # Cycle through colors if more components than colors
        for node in component:
            for neighbor in G.neighbors(node):  # Iterate through all neighbors of the node
                if neighbor in component:  # Ensure we only color edges within the same component
                    edge_colors[(node, neighbor)] = color
                    edge_colors[(neighbor, node)] = color  # Assign color to both directions

    # Create a list to store edge traces for different colors
    edge_traces = []

    # Group edges by color and create separate traces
    for color in set(edge_colors.values()):
        edge_x = []
        edge_y = []
        edge_z = []

        # Collect all edges of the same color
        for (node, neighbor), edge_color in edge_colors.items():
            if edge_color == color:
                x0, y0, z0 = pos[node]
                x1, y1, z1 = pos[neighbor]
                edge_x += [x0, x1, None]
                edge_y += [y0, y1, None]
                edge_z += [z0, z1, None]

        # Create a trace for edges of this color
        edge_trace = go.Scatter3d(
            x=edge_x,
            y=edge_y,
            z=edge_z,
            line=dict(width=2, color=color),  # Set color for this trace
            hoverinfo='none',
            mode='lines'
        )
        edge_traces.append(edge_trace)  # Add trace to the list

    # Combine all traces, including edges and nodes
    fig = go.Figure(data=edge_traces)  # Start with edge traces

    node_x = []
    node_y = []
    node_z = []
    node_text = []
    node_color = []
    node_symbol = []

    for node in G.nodes(data=True):
        x, y, z = pos[node[0]]
        degree = len(list(G.neighbors(node[0])))
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        node_text.append(f"{node[0]}<br>Degree: {degree}")

        # Differentiate jamming and normal nodes
        if node[1]['jammer']:
            node_color.append('black')  # Set color for jamming nodes
            node_symbol.append('circle')  # Marker symbol for jamming nodes
        else:
            node_color.append('lightgray')  # Light gray color for normal nodes
            node_symbol.append('circle')  # Use default marker for normal nodes

        progress_bar.update(1)

    node_trace = go.Scatter3d(
        x=node_x,
        y=node_y,
        z=node_z,
        text=node_text,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            size=5,
            color=node_color,
            opacity=0.8,  # Keep the opacity for all nodes
            symbol=node_symbol,  # Different symbols for different node types
            line=dict(width=2, color='black')  # Outline color
        )
    )

    fig.add_trace(node_trace)  # Add node trace

    progress_bar.close()

    fig.update_layout(scene=dict(
        xaxis=dict(title='Bays', showbackground=False, showticklabels=False),
        yaxis=dict(title='Rows', showbackground=False, showticklabels=False),
        zaxis=dict(title='Layers', showbackground=False, showticklabels=False),
        aspectmode='data',
        camera=camera
    ),
    showlegend=False)

    if display:
        pyo.plot(fig, filename='network_layout.html', auto_open=False)
        fig.write_image(f"{name}.png", width=800, height=600, scale=4)

    return fig, G
