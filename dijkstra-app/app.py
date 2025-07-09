import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_cytoscape as cyto
from dash import dash_table
import networkx as nx
import pandas as pd
import heapq
import copy
import dash_bootstrap_components as dbc

# Tạo đồ thị cố định
G = nx.Graph()
nodes = [chr(i) for i in range(ord('A'), ord('L') + 1)]
G.add_nodes_from(nodes)
edges = [
    ('A', 'B', 14), ('A', 'D', 9), ('A', 'E', 12),
    ('B', 'E', 2), ('B', 'F', 7), ('B', 'C', 13),
    ('C', 'F', 14), ('C', 'G', 19),
    ('D', 'E', 7), ('D', 'H', 3), ('D', 'J', 16),
    ('E', 'F', 11), ('E', 'H', 6),
    ('F', 'I', 15),
    ('G', 'F', 6), ('G', 'I', 12), ('G', 'L', 15),
    ('H', 'I', 12), ('H', 'K', 4), ('H', 'J', 11),
    ('I', 'K', 11), ('I', 'L', 3),
    ('J', 'K', 8),
    ('K', 'L', 7)
]
G.add_weighted_edges_from(edges)

# stylesheet Cytoscape
stylesheet = [
    {'selector': 'node', 'style': {
        'content': 'data(label)', 'text-valign': 'center',
        'background-color': '#0074D9', 'color': 'white'
    }},
    {'selector': 'edge', 'style': {
        'label': 'data(weight)', 'line-color': '#ccc', 'font-size': 12
    }},
    {'selector': '.current', 'style': {
        'background-color': '#FFA500',
        'border-width': 3,
        'border-color': '#FF4136',
        'color': '#fff',
        'font-weight': 'bold'
    }},
    {'selector': '.visited', 'style': {'background-color': '#2ECC40'}},
    {'selector': '.path-edge', 'style': {'line-color': '#FF4136', 'width': 4}},
    {'selector': '.shortest-path', 'style': {'line-color': '#FFD700', 'width': 6}},
    {'selector': '.trace-path', 'style': {'line-color': '#B10DC9', 'line-style': 'dashed', 'width': 3}},
    {'selector': '.finished', 'style': {'background-color': '#0074D9'}},
    {'selector': '.finished-edge', 'style': {'line-color': '#0074D9', 'width': 4}},
    {'selector': '.highlight-path', 'style': {'line-color': '#FF851B', 'width': 6}},
]


# layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.layout = dbc.Container([

    dbc.Row([
        dbc.Col(html.H2("Dijkstra Visualizer", className="text-white bg-primary p-3 mb-3"), width=12)
    ]),

    dbc.Row([

        dbc.Col([
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H5("Bắt đầu", style={"fontSize": "13px"}),
                            dcc.Dropdown(
                                id='source-node',
                                options=[{'label': n, 'value': n} for n in nodes],
                                value='A',
                                clearable=False,
                                style={'marginBottom': '10px', 'fontSize': '12px'}
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            html.H5("Kết thúc", style={"fontSize": "13px"}),
                            dcc.Dropdown(
                                id='target-node',
                                options=[{'label': n, 'value': n} for n in nodes],
                                value='L',
                                clearable=False,
                                style={'marginBottom': '15px', 'fontSize': '12px'}
                            ),
                        ]
                    ),
                ]
            ),             

            dbc.ButtonGroup([
                dbc.Button("Reset", id='reset-button', color="primary", className="me-2 mb-2"),
                dbc.Button("Next", id='next-button', color="info", className="me-2 mb-2"),
                dbc.Button("Play", id='play-button', color="success", className="me-2 mb-2"),
                dbc.Button("Path", id='highlight-path-btn', color="danger", className="me-2 mb-2")
            ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center'}),

            html.Label("Tốc độ chạy (ms)", className="fw-bold", style={"fontSize": "13px"}),
            dcc.Slider(
                id='play-speed',
                min=200, max=2000, step=100,
                marks={
                    200: 'Tia chớp',
                    500: '0.5',
                    1000: '1',
                    1500: '1.5',
                    2000: 'Rùa'
                },
                value=1000,
                tooltip={"placement": "bottom", "always_visible": True},
                updatemode='drag',
                included=False
            ),

            html.Hr(),

            html.H5("Priority Queue", className="mb-2 mt-3"),
            dash_table.DataTable(
                id='priority-table',
                columns=[
                    {'name': 'Node', 'id': 'node'},
                    {'name': 'Distance', 'id': 'distance'}
                ],
                style_table={'width': '100%'},
                style_cell={'textAlign': 'center', 'fontSize': 13},
                style_header={'fontWeight': 'bold'}
            ),

        ], width=3),

        dbc.Col([
            cyto.Cytoscape(
                id='graph',
                layout={'name': 'cose'},
                style={'width': '100%', 'height': '90vh'},
                stylesheet=stylesheet
            )
        ], width=6),

        dbc.Col([
            html.H5("Diễn giải bước chạy", style={"fontSize": "13px"}),
            dcc.Markdown(
                id='step-description',
                style={
                    'padding': '10px',
                    'border': '1px solid #ccc',
                    'borderRadius': '5px',
                    'backgroundColor': '#f8f8f8',
                    'minHeight': '120px',
                    'fontSize': '12px'
                }
            ),

            html.H5("Predecessor Map", className="mb-2 mt-4"),
            dash_table.DataTable(
                id='predecessor-table',
                columns=[
                    {'name': 'Node', 'id': 'node'},
                    {'name': 'Predecessor', 'id': 'predecessor'}
                ],
                style_table={'width': '100%'},
                style_cell={'textAlign': 'center', 'fontSize': 13},
                style_header={'fontWeight': 'bold'}
            ),
        ], width=3)
    ]),

    dcc.Store(id='predecessor-store'),
    dcc.Store(id='steps-store'),
    dcc.Store(id='step-index'),
    dcc.Store(id='target-node-store'),
    dcc.Interval(id='interval', interval=1000, n_intervals=0, disabled=True)

], fluid=False)

# Dijkstra
def run_dijkstra_steps(G, source):
    steps = []
    dist = {node: float('inf') for node in G.nodes}
    dist[source] = 0
    visited = set()
    pq = [(0, source)]
    prev = {}

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        trace = []
        temp = u
        while temp in prev:
            trace.append((prev[temp], temp))
            temp = prev[temp]

        explanation = [f"Đang xét node {u} với khoảng cách hiện tại = {dist[u]}."]
        updated_neighbors = []

        step = {
            'current': u,
            'visited': list(visited),
            'dist': copy.deepcopy(dist),
            'edges': [],
            'prev': copy.deepcopy(prev),
            'trace': trace[::-1]
        }

        for v in G.neighbors(u):
            if v in visited:
                continue
            weight = G[u][v]['weight']
            new_dist = dist[u] + weight
            if dist[v] > new_dist:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(pq, (new_dist, v))
                step['edges'].append((u, v))
                updated_neighbors.append(f"Cập nhật khoảng cách từ {source} đến {v} = {new_dist} qua {u}.")
            else:
                updated_neighbors.append(f"Bỏ qua cạnh ({u}, {v}) vì khoảng cách hiện tại nhỏ hơn.")

        step['explanation'] = " ".join(explanation + updated_neighbors)
        steps.append(step)
    return steps

@app.callback(
    Output('graph', 'elements'),
    Output('step-index', 'data'),
    Output('priority-table', 'data'),
    Output('steps-store', 'data'),
    Output('interval', 'disabled'),
    Output('step-description', 'children'),
    Output('predecessor-store', 'data'), 
    Input('reset-button', 'n_clicks'),
    Input('play-button', 'n_clicks'),
    Input('next-button', 'n_clicks'),
    Input('interval', 'n_intervals'),
    State('source-node', 'value'),
    State('step-index', 'data'),
    State('steps-store', 'data'),
    State('interval', 'disabled'),
    prevent_initial_call=True
)
def update_all(reset_clicks, play_clicks, next_clicks, n_intervals, source, index, steps, interval_disabled):
    triggered = ctx.triggered_id

    if triggered == 'reset-button':
        steps = run_dijkstra_steps(G, source)
        index = 0
        interval_disabled = True
    elif triggered == 'play-button':
        interval_disabled = not interval_disabled
    elif triggered in ['next-button', 'interval']:
        if not steps or index >= len(steps):
            return dash.no_update, index, dash.no_update, dash.no_update, True, dash.no_update, dash.no_update
        index += 1

    if not steps or index > len(steps):
        return dash.no_update, index, dash.no_update, steps, interval_disabled, dash.no_update, dash.no_update

    step = steps[0] if index == 0 else steps[index - 1]

    current = step['current']
    visited = set(step['visited'])
    dist = step['dist']
    prev = step['prev']
    trace = step['trace']

    predecessor_table_data = [
        {'node': node, 'predecessor': prev.get(node, '-')}
        for node in sorted(G.nodes())
    ]

    # Lưu đường đi tạm
    path_edges = {(prev[v], v) for v in prev if prev[v]}

    # Nếu kết thúc, tô finished edges
    shortest_path_edges = []
    if index == len(steps):
        shortest_path_edges = path_edges

    # Cập nhật graph elements
    elements = []
    for node in G.nodes():
        classes = []
        if node in visited:
            classes.append('visited')
        if node == current:
            classes.append('current')
        elements.append({'data': {'id': node, 'label': node}, 'classes': ' '.join(classes)})

    for u, v, d in G.edges(data=True):
        if (u, v) in shortest_path_edges or (v, u) in shortest_path_edges:
            edge_class = 'finished-edge'
        elif (u, v) in path_edges or (v, u) in path_edges:
            edge_class = 'path-edge'
        elif (u, v) in trace or (v, u) in trace:
            edge_class = 'trace-path'
        else:
            edge_class = ''

        elements.append({
            'data': {'id': f"{u}-{v}", 'source': u, 'target': v, 'weight': d['weight']},
            'classes': edge_class
        })

    # Bảng priority queue
    table_data = [
        {'node': k, 'distance': ("∞" if v == float('inf') else v)}
        for k, v in sorted(dist.items())
    ]

    return elements, index, table_data, steps, interval_disabled, step.get('explanation', ''), predecessor_table_data

@app.callback(
    Output('predecessor-table', 'data'),
    Input('predecessor-store', 'data')
)
def update_predecessor_table(predecessor_data):
    if not predecessor_data:
        return []
    return predecessor_data

@app.callback(
    [Output('graph', 'elements', allow_duplicate=True),
     Output('step-description', 'children', allow_duplicate=True)],
    Input('highlight-path-btn', 'n_clicks'),
    State('graph', 'elements'),
    State('source-node', 'value'),
    State('target-node', 'value'),
    prevent_initial_call='initial_duplicate'
)
def highlight_shortest_path(n_clicks, elements, source, target):
    if not n_clicks or source == target:
        raise dash.exceptions.PreventUpdate

    try:
        path = nx.dijkstra_path(G, source, target)
        edge_path = set(zip(path, path[1:])) | set(zip(path[1:], path))
    except nx.NetworkXNoPath:
        return elements, f"**Không tồn tại đường đi từ {source} đến {target}.**"

    # Cập nhật các phần tử graph
    updated_elements = []
    for el in elements:
        if 'classes' in el and 'highlight-path' in el['classes']:
            el['classes'] = ' '.join(c for c in el['classes'].split() if c != 'highlight-path')

        if 'source' in el['data'] and 'target' in el['data']:
            u, v = el['data']['source'], el['data']['target']
            if (u, v) in edge_path or (v, u) in edge_path:
                existing_classes = el.get('classes', '')
                el['classes'] = (existing_classes + ' highlight-path').strip()

        updated_elements.append(el)

    # Diễn giải bằng markdown
    explanation = f"""\
##### Đường đi ngắn nhất từ {source} đến {target}

**{' → '.join(path)}**

---

##### Diễn giải:
"""
    # Viết lại logic diễn giải đi ngược từ đích về nguồn dựa trên predecessor
    total_weight = 0
    for i in range(len(path) - 1, 0, -1):  # từ target về source
        v, u = path[i], path[i - 1]
        w = G[u][v]['weight']
        total_weight += w
        explanation += f"- Từ đỉnh **{v}**, quay ngược về **{u}** qua cạnh trọng số `{w}` → khoảng cách tích lũy `{total_weight}`.\n"

    explanation += f"""\n---

**Tổng trọng số đường đi: `{total_weight}`**
"""
    return updated_elements, explanation

@app.callback(
    Output('interval', 'interval'),
    Input('play-speed', 'value')
)
def update_interval_speed(speed_value):
    return speed_value

if __name__ == '__main__':
    app.run(debug=True)
