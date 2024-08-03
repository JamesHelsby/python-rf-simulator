import plotly.graph_objects as go
import plotly.offline as pyo
import networkx as nx


def generate_container_network(ship):
    G = nx.Graph()

    for x in range(ship.bays):
        for y in range(ship.rows):
            for z in range(ship.layers):
                cell = ship.cells[x][y][z]
                if cell.container:
                    node_id = f"C({x},{y},{z})"
                    G.add_node(node_id, pos=(cell.x, cell.y, cell.z), container='standard', rf_radius=cell.container.rf_radius)
                if cell.front_half:
                    node_id = f"F({x},{y},{z})"
                    G.add_node(node_id, pos=(cell.front_half.x, cell.front_half.y, cell.front_half.z), container='small_front', rf_radius=cell.front_half.rf_radius)
                if cell.back_half:
                    node_id = f"B({x},{y},{z})"
                    G.add_node(node_id, pos=(cell.back_half.x, cell.back_half.y, cell.back_half.z), container='small_back', rf_radius=cell.back_half.rf_radius)

    nodes = list(G.nodes(data=True))
    for i, (node1, data1) in enumerate(nodes):
        for j, (node2, data2) in enumerate(nodes):
            if i < j:
                dist = ((data1['pos'][0] - data2['pos'][0]) ** 2 + 
                        ((data1['pos'][1] - data2['pos'][1]) ** 2) +
                        ((data1['pos'][2] - data2['pos'][2]) ** 2)) ** 0.5
                rf_radius = min(data1['rf_radius'], data2['rf_radius'])
                if dist <= rf_radius:
                    G.add_edge(node1, node2)
    
    return G


def plot_container_network(ship, display=True):
    G = generate_container_network(ship)
    pos = nx.get_node_attributes(G, 'pos')
    labels = nx.get_node_attributes(G, 'container')

    edge_trace = go.Scatter3d(
        x=[],
        y=[],
        z=[],
        line=dict(width=2, color='red'),
        hoverinfo='none',
        mode='lines'
    )

    for edge in G.edges():
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]
        edge_trace['x'] += (x0, x1, None)
        edge_trace['y'] += (y0, y1, None)
        edge_trace['z'] += (z0, z1, None)

    node_trace = go.Scatter3d(
        x=[],
        y=[],
        z=[],
        text=[],
        mode='markers+text',
        textposition='top center',
        hoverinfo='text',
        marker=dict(
            size=8,
            color='blue',
            opacity=0.8
        )
    )

    for node in G.nodes():
        x, y, z = pos[node]
        node_trace['x'] += (x,)
        node_trace['y'] += (y,)
        node_trace['z'] += (z,)
        node_trace['text'] += (node,)

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

    return fig
