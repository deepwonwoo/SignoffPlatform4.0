import dash
from dash import dcc, html, Input, Output, State, callback, _dash_renderer
import dash_mantine_components as dmc
import dash_cytoscape as cyto
import pandas as pd
from data.object_schemas import OBJECT_SCHEMAS, LAYERS
from utils.ontology_generator import OntologyGenerator
from utils.file_utils import save_ontology_to_json
from data.templates import DEFAULT_SIGNOFF_MATRIX
import json

# --- App Setup ---
app = dash.Dash(__name__, external_stylesheets=dmc.styles.ALL, suppress_callback_exceptions=True)
app.title = "Signoff Ontology POC"

# --- Data Initialization ---
# Initial Default Config
default_config = {
    "product_id": "HBM4E",
    "product_type": "HBM",
    "active_revisions": ["R30"],
    "blocks": [
        {"block_name": "FULLCHIP", "block_type": "TOP", "instance_count": 50000000},
        {"block_name": "IO", "block_type": "PHY", "instance_count": 2000000},
        {"block_name": "SRAM_A", "block_type": "MEMORY", "instance_count": 500000},
        {"block_name": "CORE", "block_type": "DIGITAL", "instance_count": 10000000},
    ],
    "signoff_matrix": {
        "DSC": ["R30"], 
        "LSC": ["R30"],
        "PEC": ["R30"]
    }
}

generator = OntologyGenerator(default_config)
initial_data = generator.generate()

# --- Helper Functions ---

def get_graph_elements(data):
    """Convert generated ontology data to Cytoscape elements"""
    elements = []
    
    # 1. Add Layer Nodes (Compound Parents)
    for layer_name, layer_info in LAYERS.items():
        elements.append({
            'data': {'id': layer_name, 'label': layer_info['name'], 'color': layer_info['color']},
            'classes': 'layer-node'
        })
    
    # 2. Add Nodes and Edges from Generator
    # The generator already creates nodes with 'parent' (layer) if we map it correctly
    # But currently generator adds 'layer' property, not 'parent' data field for Cytoscape compound nodes.
    # We need to adjust this.
    
    gen_graph = data['graph']
    
    for node in gen_graph['nodes']:
        # Add parent field for compound graph
        node['data']['parent'] = node['data']['layer']
        elements.append(node)
        
    for edge in gen_graph['edges']:
        elements.append(edge)
        
    return elements

def get_dataframes(data):
    """Convert ontology lists to DataFrames"""
    dfs = {}
    ontology = data['ontology']
    for key in ontology.keys():
        if ontology[key]:
            dfs[key] = pd.DataFrame(ontology[key])
        else:
            dfs[key] = pd.DataFrame()
    return dfs

# --- Stylesheets ---

base_stylesheet = [
    # Layer Nodes (Parents)
    {
        'selector': '.layer-node',
        'style': {
            'content': 'data(label)',
            'text-valign': 'top',
            'text-halign': 'center',
            'background-color': 'data(color)',
            'background-opacity': 0.1,
            'border-width': 1,
            'border-color': '#adb5bd',
            'font-size': '20px',
            'font-weight': 'bold',
            'color': '#868e96',
            'padding': '40px'
        }
    },
    # Object Nodes
    {
        'selector': 'node[!parent]',
        'style': {
            'content': 'data(label)',
            'color': 'white',
            'background-color': 'data(color)',
            'text-valign': 'center',
            'text-halign': 'center',
            'width': '120px',
            'height': '50px',
            'shape': 'round-rectangle',
            'font-family': 'Inter, sans-serif',
            'font-size': '12px',
            'border-width': 0
        }
    },
    # Edges
    {
        'selector': 'edge',
        'style': {
            'label': 'data(label)',
            'color': '#ced4da',
            'line-color': '#dee2e6',
            'target-arrow-color': '#dee2e6',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'font-size': '10px',
            'text-background-color': '#ffffff',
            'text-background-opacity': 0.8,
            'width': 1.5
        }
    },
    # Highlighted State
    {
        'selector': '.highlighted',
        'style': {
            'background-color': '#228be6', # Blue
            'line-color': '#228be6',
            'target-arrow-color': '#228be6',
            'border-width': 2,
            'border-color': '#1864ab',
            'width': 3,
            'z-index': 9999
        }
    },
    {
        'selector': '.dimmed',
        'style': {
            'opacity': 0.1,
            'label': ''
        }
    }
]

# --- Layouts ---

def get_sidebar():
    return dmc.Stack(
        children=[
            dmc.Group(
                [
                    dmc.Text("🧠", size="xl"),
                    dmc.Text("Signoff AI", size="xl", fw=700),
                ],
                mb=20,
            ),
            dmc.NavLink(
                label="Ontology Map",
                leftSection="🕸️",
                href="/",
                active=True,
                id="nav-ontology"
            ),
            dmc.NavLink(
                label="Data Explorer",
                leftSection="📊",
                href="/explorer",
                id="nav-explorer"
            ),
            dmc.NavLink(
                label="Ontology Builder",
                leftSection="🛠️",
                href="/builder",
                id="nav-builder"
            ),
        ],
        h="100%",
        p="md",
        bg="dark",
    )

# 1. Ontology Map View
ontology_layout = dmc.Stack([
    dmc.Group([
        dmc.Title("Signoff Ontology Map", order=2),
        dmc.Badge("Visualizing Context & Lineage", color="blue", variant="light", size="lg")
    ], justify="space-between"),
    
    dmc.Text("Click any node to visualize its full context (Lineage). See how Result is connected to Product.", c="dimmed"),
    
    dmc.Grid([
        dmc.GridCol([
            dmc.Paper(
                [
                    dmc.Group([
                        dmc.Select(
                            label="Layout",
                            data=['cose', 'breadthfirst', 'grid', 'circle'],
                            value='cose',
                            id='graph-layout-select',
                            size="xs",
                            style={"width": 150}
                        ),
                        dmc.Button("Reset View", id="btn-reset-graph", variant="subtle", size="xs")
                    ], mb="xs"),
                    cyto.Cytoscape(
                        id='ontology-graph',
                        layout={'name': 'cose', 'animate': True},
                        style={'width': '100%', 'height': '700px'},
                        elements=get_graph_elements(initial_data),
                        stylesheet=base_stylesheet,
                        responsive=True
                    )
                ],
                shadow="sm",
                p="md",
                withBorder=True,
                radius="md"
            )
        ], span=9),
        
        dmc.GridCol([
            dmc.Stack([
                dmc.Paper(
                    children=[
                        dmc.Title("Context Viewer", order=4, mb="md"),
                        html.Div(id="ontology-details-panel", children=dmc.Text("Select a node to view its context.", c="dimmed"))
                    ],
                    shadow="sm",
                    p="md",
                    withBorder=True,
                    radius="md",
                    h="750px",
                    style={"overflowY": "auto"}
                )
            ])
        ], span=3)
    ], gutter="md")
])

# 2. Data Explorer View
explorer_layout = dmc.Stack([
    dmc.Title("Data Explorer", order=2),
    dmc.Text("Raw data view of the generated ontology objects.", c="dimmed"),
    
    dmc.Tabs(
        [
            dmc.TabsList(
                [
                    dmc.TabsTab("Products", value="products"),
                    dmc.TabsTab("Revisions", value="revisions"),
                    dmc.TabsTab("Blocks", value="blocks"),
                    dmc.TabsTab("Tasks", value="tasks"),
                    dmc.TabsTab("Jobs", value="jobs"),
                    dmc.TabsTab("Results", value="results"),
                ]
            ),
            dmc.TabsPanel(html.Div(id="table-products", style={"marginTop": "20px"}), value="products"),
            dmc.TabsPanel(html.Div(id="table-revisions", style={"marginTop": "20px"}), value="revisions"),
            dmc.TabsPanel(html.Div(id="table-blocks", style={"marginTop": "20px"}), value="blocks"),
            dmc.TabsPanel(html.Div(id="table-tasks", style={"marginTop": "20px"}), value="tasks"),
            dmc.TabsPanel(html.Div(id="table-jobs", style={"marginTop": "20px"}), value="jobs"),
            dmc.TabsPanel(html.Div(id="table-results", style={"marginTop": "20px"}), value="results"),
        ],
        value="tasks",
        id="explorer-tabs"
    )
])

# 3. Builder View (Simplified)
builder_layout = dmc.Stack([
    dmc.Title("Ontology Builder", order=2),
    dmc.Text("Regenerate mock data with different configurations.", c="dimmed"),
    dmc.Button("Regenerate Data", id="builder-generate-btn", size="lg"),
    html.Div(id="builder-status")
])

# --- Main Layout ---
app.layout = dmc.MantineProvider(
    forceColorScheme="dark",
    theme={
        "primaryColor": "blue",
        "fontFamily": "'Inter', sans-serif"
    },
    children=[
        dcc.Location(id="url"),
        dcc.Store(id="ontology-data-store", data=initial_data), # Store generated data client-side
        dmc.Grid(
            [
                dmc.GridCol(get_sidebar(), span=2, style={"minHeight": "100vh", "backgroundColor": "#1A1B1E"}),
                dmc.GridCol(
                    dmc.Container(
                        id="page-content",
                        p="xl",
                        fluid=True
                    ),
                    span=10
                ),
            ],
            gutter=0,
        )
    ]
)

# --- Callbacks ---

# Navigation
@app.callback(
    [Output("nav-ontology", "active"), Output("nav-explorer", "active"), Output("nav-builder", "active")],
    [Input("url", "pathname")]
)
def update_active_nav(pathname):
    if pathname == "/": return True, False, False
    elif pathname == "/explorer": return False, True, False
    elif pathname == "/builder": return False, False, True
    return True, False, False

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/": return ontology_layout
    elif pathname == "/explorer": return explorer_layout
    elif pathname == "/builder": return builder_layout
    return ontology_layout

# Graph Interaction (Path Highlighting)
@app.callback(
    [Output('ontology-graph', 'stylesheet'), Output('ontology-details-panel', 'children')],
    [Input('ontology-graph', 'tapNodeData'), Input('btn-reset-graph', 'n_clicks')],
    [State('ontology-graph', 'elements')]
)
def update_graph_interaction(node_data, n_clicks, elements):
    ctx = dash.callback_context
    if not ctx.triggered:
        return base_stylesheet, dmc.Text("Select a node to view its context.", c="dimmed")
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'btn-reset-graph' or not node_data:
        return base_stylesheet, dmc.Text("Select a node to view its context.", c="dimmed")
    
    # --- Path Highlighting Logic ---
    selected_id = node_data['id']
    
    # Build adjacency list for traversal
    adj = {}
    edges = [e for e in elements if 'source' in e['data']]
    
    for edge in edges:
        src = edge['data']['source']
        tgt = edge['data']['target']
        
        if src not in adj: adj[src] = []
        if tgt not in adj: adj[tgt] = []
        
        # Bidirectional traversal for context
        adj[src].append(tgt)
        adj[tgt].append(src)
        
    # BFS to find all connected nodes
    connected_nodes = {selected_id}
    queue = [selected_id]
    
    while queue:
        curr = queue.pop(0)
        if curr in adj:
            for neighbor in adj[curr]:
                if neighbor not in connected_nodes:
                    connected_nodes.add(neighbor)
                    queue.append(neighbor)
                    
    # Create new stylesheet
    new_stylesheet = []
    
    # 1. Dim everything first
    new_stylesheet.append({
        'selector': 'node',
        'style': {'opacity': 0.1}
    })
    new_stylesheet.append({
        'selector': 'edge',
        'style': {'opacity': 0.1}
    })
    
    # 2. Highlight connected nodes and edges
    for node_id in connected_nodes:
        new_stylesheet.append({
            'selector': f'node[id="{node_id}"]',
            'style': {'opacity': 1, 'border-width': 2, 'border-color': '#fff'}
        })
        
    for edge in edges:
        src = edge['data']['source']
        tgt = edge['data']['target']
        if src in connected_nodes and tgt in connected_nodes:
             new_stylesheet.append({
                'selector': f'edge[source="{src}"][target="{tgt}"]',
                'style': {'opacity': 1, 'line-color': '#228be6', 'target-arrow-color': '#228be6', 'width': 3}
            })
             
    # 3. Highlight selected node specifically
    new_stylesheet.append({
        'selector': f'node[id="{selected_id}"]',
        'style': {'background-color': '#fab005', 'border-color': '#fff', 'border-width': 3}
    })
    
    # Keep layer nodes visible but dim
    new_stylesheet.append({
        'selector': '.layer-node',
        'style': {'opacity': 1, 'background-opacity': 0.05}
    })
    
    # --- Details Panel ---
    obj_type = node_data.get('type')
    
    if not obj_type:
        # Check if it is a layer node
        if node_data['id'] in LAYERS:
            layer_info = LAYERS[node_data['id']]
            details = dmc.Stack([
                dmc.Group([
                    html.Div(style={'backgroundColor': node_data.get('color', 'gray'), 'width': '20px', 'height': '20px', 'borderRadius': '50%'}),
                    dmc.Title(layer_info['name'], order=3),
                ]),
                dmc.Badge("Layer", color="gray", variant="outline"),
                dmc.Text(layer_info['description'], size="sm", mb="md"),
                dmc.Divider(label="Context", labelPosition="center"),
                dmc.Text(f"Contains {len(connected_nodes)-1} highlighted objects.", size="sm", fw=500),
            ])
            return new_stylesheet, details
        else:
            return new_stylesheet, dmc.Alert("Unknown node type", color="red")

    schema = OBJECT_SCHEMAS.get(obj_type)
    
    if not schema:
        return new_stylesheet, dmc.Alert(f"No schema found for type: {obj_type}", color="red")
    
    details = dmc.Stack([
        dmc.Group([
            html.Div(style={'backgroundColor': node_data['color'], 'width': '20px', 'height': '20px', 'borderRadius': '50%'}),
            dmc.Title(node_data['label'], order=3),
        ]),
        dmc.Badge(node_data['type'], color="gray", variant="outline"),
        dmc.Text(schema['description'] if schema else "", size="sm", mb="md"),
        
        dmc.Divider(label="Context", labelPosition="center"),
        dmc.Text(f"Connected to {len(connected_nodes)-1} other objects.", size="sm", fw=500),
        
        dmc.Divider(label="Properties", labelPosition="center"),
        # We would need to look up the actual object data here. 
        # For this demo, we just show the schema.
        dmc.Code(json.dumps(node_data, indent=2), block=True)
    ])
    
    return new_stylesheet, details

# Explorer Tables
@app.callback(
    [Output(f"table-{key}", "children") for key in ["products", "revisions", "blocks", "tasks", "jobs", "results"]],
    Input("ontology-data-store", "data")
)
def update_explorer_tables(data):
    if not data: return [""] * 6
    
    dfs = get_dataframes(data)
    outputs = []
    
    for key in ["products", "revisions", "blocks", "tasks", "jobs", "results"]:
        if key in dfs and not dfs[key].empty:
            df = dfs[key]
            # Simple table
            header = [html.Tr([html.Th(col) for col in df.columns])]
            rows = [html.Tr([html.Td(str(row[col])) for col in df.columns]) for _, row in df.iterrows()]
            
            table = dmc.Table(
                children=[html.Thead(header), html.Tbody(rows)],
                striped=True,
                highlightOnHover=True,
                withTableBorder=True,
                style={"fontSize": "12px"}
            )
            outputs.append(dmc.ScrollArea(table, h=600))
        else:
            outputs.append(dmc.Alert("No data available", color="gray"))
            
    return outputs

if __name__ == "__main__":
    app.run(debug=True)
