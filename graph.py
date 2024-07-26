import networkx as nx
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output, State
from tqdm import tqdm


def nodal_distance(node1, node2):
    x1, y1, z1 = node1
    x2, y2, z2 = node2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def create_graph(node_positions, malicious_nodes, distance_threshold):
    G = nx.Graph()
    G.add_nodes_from(node_positions)
    nx.set_node_attributes(G, node_positions, 'pos')
    
    malicious_attributes = {node: node in malicious_nodes for node in node_positions}
    nx.set_node_attributes(G, malicious_attributes, 'malicious')

    for node_id_1, pos1 in tqdm(node_positions.items(), disable=True):
        for node_id_2, pos2 in node_positions.items():
            if node_id_1 != node_id_2:
                distance = nodal_distance(pos1, pos2)
                if distance < distance_threshold:
                    G.add_edge(node_id_1, node_id_2)

    return G


def draw_node_with_colors(ax, pos, node, colors, node_size, label, malicious):
    x, y = pos[node]
    radius = node_size / 500
    edge_color = 'red' if malicious else 'black'
    
    if len(colors) == 2:
        circle = patches.Circle((x, y), radius=radius, edgecolor=edge_color, facecolor=colors[0])
        wedge = patches.Wedge((x, y), radius*0.95, theta1=45, theta2=225, edgecolor=None, facecolor=colors[1])
        ax.add_patch(circle)
        ax.add_patch(wedge)
    else:
        circle = patches.Circle((x, y), radius=radius, edgecolor=edge_color, facecolor=colors[0])
        ax.add_patch(circle)

    text_color = 'red' if malicious else 'black'
    ax.text(x, y, str(label), fontsize=12, ha='center', va='center', color=text_color)


def visualize_graph(G, C1, C2):
    pos = nx.spring_layout(G)
    pos = nx.get_node_attributes(G, 'pos')
    node_size = 500
    
    z_layers = set([pos[node][2] for node in pos])
    if len(z_layers) > 1:
        print("Simulation is 3D, exiting visualization.")
        return

    pos = {node: (pos[node][0], pos[node][1]) for node in pos}
    fig, ax = plt.subplots(figsize=(10, 8))

    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='black', width=1.5)

    for node in G.nodes():
        malicious = G.nodes[node].get('malicious', False)
        if node in C1 and node in C2:  # Overlap = two colors
            draw_node_with_colors(ax, pos, node, ['green', 'blue'], node_size, node, malicious)
        elif node in C1:               # C1 = green
            draw_node_with_colors(ax, pos, node, ['green'], node_size, node, malicious)
        elif node in C2:               # C2 = blue
            draw_node_with_colors(ax, pos, node, ['blue'], node_size, node, malicious)
        else:                          # Default = gray
            draw_node_with_colors(ax, pos, node, ['lightgray'], node_size, node, malicious)
    
    ax.set_aspect('equal')

    all_x, all_y = zip(*pos.values())
    x_margin = (max(all_x) - min(all_x)) * 1
    y_margin = (max(all_y) - min(all_y)) * 0.1
    ax.set_xlim(min(all_x) - x_margin, max(all_x) + x_margin)
    ax.set_ylim(min(all_y) - y_margin, max(all_y) + y_margin)

    plt.show()


def visualize_graph_3D(G, C1, C2, port=45145):
    pos = nx.spring_layout(G, dim=3)
    pos = nx.get_node_attributes(G, 'pos')
    x_nodes = [pos[i][0] for i in pos]
    y_nodes = [pos[i][1] for i in pos]
    z_nodes = [pos[i][2] for i in pos]

    node_colors = []
    node_lines = []
    for node in G.nodes():
        if node in C1 and node in C2:
            node_colors.append('purple')
        elif node in C1:
            node_colors.append('green')
        elif node in C2:
            node_colors.append('blue')
        else:
            node_colors.append('lightgray')
        
        if G.nodes[node].get('malicious', False):
            node_lines.append('red')
        else:
            node_lines.append('black')

    edge_trace = []
    for edge in G.edges():
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]
        edge_trace.append(go.Scatter3d(
            x=[x0, x1, None], y=[y0, y1, None], z=[z0, z1, None],
            mode='lines',
            line=dict(color='black', width=2),
            hoverinfo='none'
        ))

    node_trace = go.Scatter3d(
        x=x_nodes, y=y_nodes, z=z_nodes,
        mode='markers',
        marker=dict(symbol='circle',
                    size=12,
                    color=node_colors,
                    line=dict(color=node_lines, width=2)),
        hoverinfo='text'
    )

    fig = go.Figure(data=edge_trace + [node_trace],
                    layout=go.Layout(
                        title='3D Network Graph',
                        showlegend=False,
                        scene=dict(
                            xaxis=dict(showbackground=False),
                            yaxis=dict(showbackground=False),
                            zaxis=dict(showbackground=False),
                            aspectmode='data'
                        )
                    ))

    fig.show()


def visualize_graph_3D_with_click(G, C1, C2, port=45145):
    pos = nx.spring_layout(G, dim=3)
    pos = nx.get_node_attributes(G, 'pos')
    x_nodes = [pos[i][0] for i in pos]
    y_nodes = [pos[i][1] for i in pos]
    z_nodes = [pos[i][2] for i in pos]

    node_colors = []
    node_lines = []
    for node in G.nodes():
        if node in C1 and node in C2:
            node_colors.append('purple')
        elif node in C1:
            node_colors.append('green')
        elif node in C2:
            node_colors.append('blue')
        else:
            node_colors.append('lightgray')
        
        if G.nodes[node].get('malicious', False):
            node_lines.append('red')
        else:
            node_lines.append('black')

    app = Dash(__name__)
    
    edge_trace = []
    for edge in G.edges():
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]
        edge_trace.append(go.Scatter3d(
            x=[x0, x1, None], y=[y0, y1, None], z=[z0, z1, None],
            mode='lines',
            line=dict(color='grey', width=1),
            hoverinfo='none',
            customdata=[edge]
        ))

    node_trace = go.Scatter3d(
        x=x_nodes, y=y_nodes, z=z_nodes,
        mode='markers',
        marker=dict(symbol='circle',
                    size=6,
                    color=node_colors,
                    line=dict(color=node_lines, width=2)),
        hoverinfo='text',
        customdata=list(G.nodes())
    )

    fig = go.Figure(data=edge_trace + [node_trace],
                    layout=go.Layout(
                        title='3D Network Graph',
                        showlegend=False,
                        scene=dict(
                            xaxis=dict(showbackground=False),
                            yaxis=dict(showbackground=False),
                            zaxis=dict(showbackground=False),
                            aspectmode='data'
                        ),
                        hovermode='closest'
                    ))

    app.layout = html.Div([
        dcc.Checklist(
            id='toggle-edges',
            options=[{'label': 'Show Grey Edges', 'value': 'show'}],
            value=['show']
        ),
        dcc.Graph(id='3d-network-graph', figure=fig, style={'height': '80vh'}),
        dcc.Store(id='camera-store', data=dict(up=dict(), center=dict(), eye=dict())),
        dcc.Store(id='clicked-node', data=None)
    ])

    @app.callback(
        Output('3d-network-graph', 'figure'),
        Output('camera-store', 'data'),
        Input('3d-network-graph', 'clickData'),
        Input('toggle-edges', 'value'),
        State('3d-network-graph', 'relayoutData'),
        State('camera-store', 'data')
    )
    def display_click_data(clickData, toggle_edges, relayoutData, camera_data):
        new_fig = fig
        if relayoutData and 'scene.camera' in relayoutData:
            camera_data['up'] = relayoutData['scene.camera']['up']
            camera_data['center'] = relayoutData['scene.camera']['center']
            camera_data['eye'] = relayoutData['scene.camera']['eye']
        
        show_edges = 'show' in toggle_edges

        clicked_node = None
        if clickData and 'points' in clickData and clickData['points']:
            try:
                clicked_node = clickData['points'][0]['customdata']
            except KeyError:
                pass
        
        if clicked_node is not None:
            for i, edge in enumerate(G.edges()):
                if clicked_node in edge:
                    new_fig.data[i].line.width = 4
                    new_fig.data[i].line.color = 'black'
                else:
                    new_fig.data[i].line.width = 1
                    new_fig.data[i].line.color = 'grey' if show_edges else 'rgba(0,0,0,0)'
        else:
            for trace in new_fig.data[:-1]:  # Keep nodes always visible
                trace.line.width = 1
                trace.line.color = 'grey' if show_edges else 'rgba(0,0,0,0)'

        new_fig.update_layout(
            scene_camera=dict(
                up=camera_data.get('up', {}),
                center=camera_data.get('center', {}),
                eye=camera_data.get('eye', {})
            )
        )
        
        return new_fig, camera_data

    app.run_server(port=port, debug=True)


def find_node_with_honest_neighbors(G, malicious_nodes):
    valid_nodes = {}
    node_found = 0
    tqdm_disable = False

    for node in tqdm(G, disable=True):
        if any(neighbor in malicious_nodes for neighbor in G.neighbors(node)):
            continue
        else:
            node_found += 1

    return node_found
