import plotly.graph_objects as go
import plotly.offline as pyo
from tqdm import tqdm


def add_box(fig, cell, x, y, z, color, opacity=0.5):
  vertices = [
    [x, y, z],
    [x + cell.length, y, z],
    [x + cell.length, y + cell.width, z],
    [x, y + cell.width, z],
    [x, y, z + cell.height],
    [x + cell.length, y, z + cell.height],
    [x + cell.length, y + cell.width, z + cell.height],
    [x, y + cell.width, z + cell.height]
  ]

  faces = [
    [0, 1, 2, 3],  # Bottom face
    [4, 5, 6, 7],  # Top face
    [0, 1, 5, 4],  # Front face
    [2, 3, 7, 6],  # Back face
    [1, 2, 6, 5],  # Right face
    [0, 3, 7, 4]   # Left face
  ]

  x_coords = [vertices[face[i % 4]][0] for face in faces for i in range(5)]
  y_coords = [vertices[face[i % 4]][1] for face in faces for i in range(5)]
  z_coords = [vertices[face[i % 4]][2] for face in faces for i in range(5)]

  fig.add_trace(go.Mesh3d(
    x=x_coords,
    y=y_coords,
    z=z_coords,
    color=color,
    opacity=opacity,
    alphahull=0,
    lighting=dict(ambient=1.0, diffuse=0.0, specular=0.0, roughness=1.0, fresnel=0.0),
    lightposition=dict(x=0, y=0, z=0)
  ))


def add_box_wireframe(fig, cell, x, y, z, opacity=1.0):
  vertices = [
    [x, y, z],
    [x + cell.length, y, z],
    [x + cell.length, y + cell.width, z],
    [x, y + cell.width, z],
    [x, y, z + cell.height],
    [x + cell.length, y, z + cell.height],
    [x + cell.length, y + cell.width, z + cell.height],
    [x, y + cell.width, z + cell.height]
  ]

  edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # Bottom face
    (4, 5), (5, 6), (6, 7), (7, 4),  # Top face
    (0, 4), (1, 5), (2, 6), (3, 7)   # Vertical edges
  ]

  x_coords = []
  y_coords = []
  z_coords = []

  for edge in edges:
    x_coords.extend([vertices[edge[0]][0], vertices[edge[1]][0], None])
    y_coords.extend([vertices[edge[0]][1], vertices[edge[1]][1], None])
    z_coords.extend([vertices[edge[0]][2], vertices[edge[1]][2], None])

  rgba_color = f'rgba(0, 0, 0, {opacity})'

  fig.add_trace(go.Scatter3d(
    x=x_coords,
    y=y_coords,
    z=z_coords,
    mode='lines',
    line=dict(color=rgba_color, width=2)
  ))


def add_container_centers(fig, ship):
    container_x = []
    container_y = []
    container_z = []

    for x in range(ship.bays):
        for y in range(ship.rows):
            for z in range(ship.layers):
                cell = ship.cells[x][y][z]
                if cell.container:
                    container_x.append(cell.container.x)
                    container_y.append(cell.container.y)
                    container_z.append(cell.container.z)
                if cell.front_half:
                    container_x.append(cell.front_half.x)
                    container_y.append(cell.front_half.y)
                    container_z.append(cell.front_half.z)
                if cell.back_half:
                    container_x.append(cell.back_half.x)
                    container_y.append(cell.back_half.y)
                    container_z.append(cell.back_half.z)

    fig.add_trace(go.Scatter3d(
        x=container_x,
        y=container_y,
        z=container_z,
        mode='markers',
        marker=dict(size=4, color='blue', opacity=0.8),
        name='Container Centers'
    ))


def add_cell_centers(fig, ship):
    cell_x = []
    cell_y = []
    cell_z = []

    for x in range(ship.bays):
        for y in range(ship.rows):
            for z in range(ship.layers):
                cell = ship.cells[x][y][z]
                cell_x.append(cell.x)
                cell_y.append(cell.y)
                cell_z.append(cell.z)

    fig.add_trace(go.Scatter3d(
        x=cell_x,
        y=cell_y,
        z=cell_z,
        mode='markers',
        marker=dict(size=2, color='red', opacity=0.5),
        name='Cell Centers'
    ))


def plot_ship_layout(ship, display=True):
    fig = go.Figure()

    for x in tqdm(range(ship.bays), desc="Rendering"):
        for y in range(ship.rows):
            for z in range(ship.layers):
                cell = ship.cells[x][y][z]
                x_pos = x * cell.length
                y_pos = y * cell.width
                z_pos = z * cell.height

                add_box_wireframe(fig, cell, x_pos, y_pos, z_pos, opacity=0.05)

                if cell.container:
                    add_box(fig, cell, x_pos, y_pos, z_pos, 'darkgrey', opacity=0.5)
                    add_box_wireframe(fig, cell, x_pos, y_pos, z_pos, opacity=0.5)
                if cell.front_half:
                    add_box(fig, cell.front_half, x_pos, y_pos, z_pos, 'darkgrey', opacity=0.5)
                    add_box_wireframe(fig, cell.front_half, x_pos, y_pos, z_pos, opacity=0.5)
                if cell.back_half:
                    back_x_pos = x_pos + cell.length / 2  # Offset for the back half
                    add_box(fig, cell.back_half, back_x_pos, y_pos, z_pos, 'darkgrey', opacity=0.5)
                    add_box_wireframe(fig, cell.back_half, back_x_pos, y_pos, z_pos, opacity=0.5)

    # add_container_centers(fig, ship)
    # add_cell_centers(fig, ship)

    fig.update_layout(scene=dict(
        xaxis=dict(title='Bays', showbackground=False, showticklabels=False),
        yaxis=dict(title='Rows', showbackground=False, showticklabels=False),
        zaxis=dict(title='Layers', showbackground=False, showticklabels=False),
        aspectmode='data'
    ),
    scene_camera=dict(
        eye=dict(x=1.25, y=1.25, z=1.25)
    ),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    showlegend=False)

    if display:
        pyo.plot(fig, filename='ship_layout.html', auto_open=True)

    return fig
