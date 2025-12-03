import dash
from dash import dcc, html, Input, Output, State, callback, _dash_renderer
import dash_mantine_components as dmc
import dash_cytoscape as cyto
import pandas as pd
from mock_data import generate_mock_data, get_ontology_schema
from data.object_schemas import OBJECT_SCHEMAS, LAYERS
from utils.ontology_generator import OntologyGenerator
from utils.file_utils import save_ontology_to_json
from data.templates import DEFAULT_SIGNOFF_MATRIX
import json

# --- App Setup ---
app = dash.Dash(__name__, external_stylesheets=dmc.styles.ALL, suppress_callback_exceptions=True)
app.title = "Signoff Ontology POC"

# 2. Ontology Builder View
builder_layout = dmc.Stack([
    dmc.Title("Ontology Builder", order=2),
    dmc.Text("Generate mock Signoff Ontology data based on SRS requirements.", c="dimmed"),
    
    dmc.Grid([
        dmc.GridCol([
            dmc.Paper([
                dmc.Title("Configuration", order=4, mb="md"),
                dmc.TextInput(label="Product ID", id="builder-product-id", value="HBM4E", mb="sm"),
                dmc.Select(
                    label="Product Type", 
                    id="builder-product-type", 
                    data=["HBM", "DRAM", "LPDDR", "FLASH"], 
                    value="HBM", 
                    mb="sm"
                ),
                dmc.MultiSelect(
                    label="Active Revisions", 
                    id="builder-revisions", 
                    data=["R00", "R10", "R20", "R30", "R40", "R50", "R60"], 
                    value=["R30"], 
                    mb="md"
                ),
                dmc.Button("Generate Mock Data", id="builder-generate-btn", fullWidth=True, color="blue"),
            ], p="md", withBorder=True, shadow="sm")
        ], span=4),
        
        dmc.GridCol([
            dmc.Paper([
                dmc.Group([
                    dmc.Title("Generated Data (Editable)", order=4),
                    dmc.Button("Save to JSON", id="builder-save-btn", color="green", size="xs")
                ], justify="space-between", mb="md"),
                
                dmc.Textarea(
                    id="builder-json-output",
                    placeholder="Generated JSON will appear here...",
                    minRows=20,
                    autosize=True,
                    style={"fontFamily": "monospace", "fontSize": "12px"}
                ),
                html.Div(id="builder-notification-area", style={"marginTop": "10px"})
            ], p="md", withBorder=True, shadow="sm")
        ], span=8)
    ], gutter="xl")
])

# --- Components ---

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
                label="Ontology Builder",
                leftSection="🛠️",
                href="/builder",
                id="nav-builder"
            ),
            dmc.NavLink(
                label="Digital Twin Explorer",
                leftSection="📊",
                href="/explorer",
                id="nav-explorer"
            ),
            dmc.NavLink(
                label="AI Agent Demo",
                leftSection="🤖",
                href="/agent",
                id="nav-agent"
            ),
        ],
        h="100%",
        p="md",
        bg="dark",
    )

# --- Enhanced Graph Data Preparation ---
def get_enhanced_schema_elements():
    elements = []
    
    # 1. Add Layer Nodes (Compound Parents)
    for layer_name, layer_info in LAYERS.items():
        elements.append({
            'data': {'id': layer_name, 'label': layer_info['name'], 'color': layer_info['color']},
            'classes': 'layer-node'
        })
    
    # 2. Add Object Nodes with Parent and Color
    base_elements = get_ontology_schema()
    for el in base_elements:
        if 'source' in el['data']: # Edge
            elements.append(el)
        else: # Node
            node_id = el['data']['id']
            schema = OBJECT_SCHEMAS.get(node_id)
            if schema:
                el['data']['parent'] = schema['layer']
                el['data']['color'] = schema['color']
                elements.append(el)
            else:
                # Fallback for nodes not in schema (e.g. SignoffJob if not added yet)
                elements.append(el)
                
    return elements

schema_elements = get_enhanced_schema_elements()

# --- Data Initialization ---
data = generate_mock_data()

# Convert lists to DataFrames for easier handling
df_products = pd.DataFrame([p.to_dict() for p in data['products']])
df_revisions = pd.DataFrame([r.to_dict() for p in data['revisions'] for r in [p]])
df_blocks = pd.DataFrame([b.to_dict() for b in data['blocks']])
df_tasks = pd.DataFrame([t.to_dict() for t in data['tasks']])
df_jobs = pd.DataFrame([j.to_dict() for j in data['jobs']])
df_results = pd.DataFrame([r.to_dict() for r in data['results']])

# Merge for the Explorer View
df_full = df_tasks.merge(df_blocks, left_on='block_id', right_on='id', suffixes=('_task', '_block'))
df_full = df_full.merge(df_jobs.rename(columns={'id': 'id_job'}), left_on='id_task', right_on='task_id', how='left', suffixes=('', '_job'))
df_full = df_full.merge(df_results.rename(columns={'id': 'id_result'}), left_on='id_job', right_on='job_id', how='left', suffixes=('', '_result'))

# 1. Ontology Map View
ontology_layout = dmc.Stack([
    dmc.Title("Signoff Ontology Schema", order=2),
    dmc.Text("Visualizing the relationships between Signoff Objects. Click a node to view details.", c="dimmed"),
    
    dmc.Grid([
        dmc.GridCol([
            dmc.Select(
                label="Select Layout",
                placeholder="Choose a layout",
                id="ontology-layout-dropdown",
                data=[
                    {'label': 'Cose (Compound)', 'value': 'cose'},
                    {'label': 'Breadthfirst', 'value': 'breadthfirst'},
                    {'label': 'Circle', 'value': 'circle'},
                    {'label': 'Grid', 'value': 'grid'},
                    {'label': 'Concentric', 'value': 'concentric'},
                ],
                value='cose',
                style={'width': 200, 'marginBottom': 10},
                allowDeselect=False
            ),
            dmc.Paper(
                cyto.Cytoscape(
                    id='ontology-graph',
                    layout={
                        'name': 'cose',
                        'animate': True,
                        'componentSpacing': 100,
                        'nodeRepulsion': 400000,
                        'nodeOverlap': 20,
                        'padding': 30,
                    },
                    style={'width': '100%', 'height': '600px'},
                    elements=schema_elements,
                    stylesheet=[
                        # Layer Nodes (Parents)
                        {
                            'selector': '.layer-node',
                            'style': {
                                'content': 'data(label)',
                                'text-valign': 'top',
                                'text-halign': 'center',
                                'background-color': 'data(color)',
                                'background-opacity': 0.2,
                                'border-width': 1,
                                'border-color': '#adb5bd',
                                'font-size': '16px',
                                'font-weight': 'bold',
                                'color': '#495057',
                                'padding': '20px'
                            }
                        },
                        # Object Nodes
                        {
                            'selector': 'node[!parent]',
                            'style': {
                                'content': 'data(label)',
                                'color': 'white',
                                'background-color': '#228be6',
                                'text-valign': 'center',
                                'text-halign': 'center',
                                'width': '140px',
                                'height': '60px',
                                'shape': 'round-rectangle',
                                'font-family': 'Inter, sans-serif'
                            }
                        },
                        {
                            'selector': 'node[parent]',
                            'style': {
                                'content': 'data(label)',
                                'color': 'white',
                                'background-color': 'data(color)',
                                'text-valign': 'center',
                                'text-halign': 'center',
                                'width': '140px',
                                'height': '60px',
                                'shape': 'round-rectangle',
                                'font-family': 'Inter, sans-serif',
                                'border-width': 2,
                                'border-color': '#fff'
                            }
                        },
                        # Edges
                        {
                            'selector': 'edge',
                            'style': {
                                'label': 'data(label)',
                                'color': '#868e96',
                                'line-color': '#868e96',
                                'target-arrow-color': '#868e96',
                                'target-arrow-shape': 'triangle',
                                'curve-style': 'bezier',
                                'font-size': '11px',
                                'text-background-color': '#ffffff',
                                'text-background-opacity': 0.8,
                                'text-background-padding': '2px',
                                'width': 1.5
                            }
                        }
                    ]
                ),
                shadow="sm",
                p="md",
                withBorder=True,
                radius="md"
            )
        ], span=8),
        
        dmc.GridCol([
            dmc.Paper(
                children=[
                    dmc.Title("Object Details", order=4, mb="md"),
                    html.Div(id="ontology-details-panel", children=dmc.Text("Select a node to view details.", c="dimmed"))
                ],
                shadow="sm",
                p="md",
                withBorder=True,
                radius="md",
                h="600px"
            )
        ], span=4)
    ], gutter="md")
])

# 3. Explorer View
explorer_layout = dmc.Stack([
    dmc.Title("Digital Twin Explorer", order=2),
    dmc.Grid([
        dmc.GridCol([
            dmc.Select(
                label="Select Product",
                placeholder="Choose a product",
                id='product-dropdown',
                data=[{'label': p.name, 'value': p.id} for p in data['products']],
                value='HBM4E',
                allowDeselect=False
            )
        ], span=4),
        dmc.GridCol([
            dmc.Select(
                label="Select Revision",
                placeholder="Choose a revision",
                id='revision-dropdown',
                data=[], # Populated by callback
                value='HBM4E_R30',
                allowDeselect=False
            )
        ], span=4),
    ], gutter="xl"),
    
    dmc.Space(h=20),
    dmc.Title("Signoff Status Overview", order=4),
    html.Div(id='status-table-container')
])

# 4. AI Agent Demo View
agent_layout = dmc.Stack([
    dmc.Title("Signoff AI Agent Demo", order=2),
    dmc.Text("Simulating AI interactions based on Ontology data.", c="dimmed"),
    
    dmc.Grid([
        dmc.GridCol([
            dmc.Card([
                dmc.CardSection(
                    dmc.Group(
                        [
                            dmc.Text("User Query", fw=500),
                            dmc.Text("👤")
                        ],
                        justify="space-between"
                    ),
                    withBorder=True,
                    inheritPadding=True,
                    py="xs"
                ),
                dmc.Stack([
                    dmc.Textarea(
                        id="user-query-input",
                        placeholder="Ask something...",
                        minRows=3,
                        autosize=True
                    ),
                    dmc.Group([
                        dmc.Button("Scenario 1: Status Check", id="btn-sc1", variant="outline", size="xs", color="blue"),
                        dmc.Button("Scenario 2: Power Error", id="btn-sc2", variant="outline", size="xs", color="red"),
                        dmc.Button("Scenario 3: Waiver Analysis", id="btn-sc3", variant="outline", size="xs", color="green"),
                    ], gap="xs"),
                    dmc.Button("Send Query", id="btn-send", fullWidth=True, leftSection="🚀"),
                ], p="md")
            ], withBorder=True, shadow="sm", radius="md")
        ], span=5),
        
        dmc.GridCol([
            dmc.Card([
                dmc.CardSection(
                    dmc.Group(
                        [
                            dmc.Text("AI Agent Response (Ontology-Aware)", fw=500),
                            dmc.Text("💡")
                        ],
                        justify="space-between"
                    ),
                    withBorder=True,
                    inheritPadding=True,
                    py="xs",
                    bg="gray.1"
                ),
                dmc.CardSection(
                    dcc.Markdown(id="agent-response-output", style={"white-space": "pre-wrap", "padding": "15px"}),
                )
            ], withBorder=True, shadow="sm", radius="md", h="100%")
        ], span=7)
    ], gutter="xl")
])

# --- Main Layout ---

app.layout = dmc.MantineProvider(
    forceColorScheme="dark",
    theme={
        "primaryColor": "blue",
        "fontFamily": "'Inter', sans-serif",
        "components": {
            "Button": {"defaultProps": {"fw": 400}},
            "Container": {"defaultProps": {"fluid": True}},
        },
    },
    children=[
        dcc.Location(id="url"),
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

# ... (Existing callbacks)

@app.callback(
    Output("builder-json-output", "value"),
    Input("builder-generate-btn", "n_clicks"),
    [State("builder-product-id", "value"),
     State("builder-product-type", "value"),
     State("builder-revisions", "value")]
)
def generate_mock_data_callback(n_clicks, product_id, product_type, revisions):
    if not n_clicks:
        return ""
    
    # Build Config
    config = {
        "product_id": product_id,
        "product_type": product_type,
        "active_revisions": revisions,
        "blocks": [
            {"block_name": "FULLCHIP", "block_type": "TOP"},
            {"block_name": "IO", "block_type": "PHY"},
            {"block_name": "SRAM_A", "block_type": "MEMORY"},
            {"block_name": "CORE", "block_type": "DIGITAL"},
        ],
        "signoff_matrix": {} # Will be populated by generator based on revisions
    }
    
    # Populate Matrix based on DEFAULT_SIGNOFF_MATRIX
    for group, apps in DEFAULT_SIGNOFF_MATRIX.items():
        for app_name, app_info in apps.items():
            # If any of the selected revisions are in the app's supported revisions, add it
            if any(rev in app_info['revisions'] for rev in revisions):
                if app_name not in config["signoff_matrix"]:
                    config["signoff_matrix"][app_name] = []
                # Add only the relevant revisions
                config["signoff_matrix"][app_name] = [r for r in revisions if r in app_info['revisions']]

    generator = OntologyGenerator(config)
    data = generator.generate()
    
    return json.dumps(data, indent=2, ensure_ascii=False)

@app.callback(
    Output("builder-notification-area", "children"),
    Input("builder-save-btn", "n_clicks"),
    State("builder-json-output", "value")
)
def save_mock_data_callback(n_clicks, json_data):
    if not n_clicks or not json_data:
        return ""
    
    try:
        data = json.loads(json_data)
        filename = f"{data['config']['product_id']}_ontology.json"
        filepath = save_ontology_to_json(data, filename)
        return dmc.Alert(f"Successfully saved to {filepath}", title="Success", color="green")
    except Exception as e:
        return dmc.Alert(f"Failed to save: {str(e)}", title="Error", color="red")




# 1. Ontology Map View



@app.callback(
    [Output("nav-ontology", "active"), Output("nav-builder", "active"), Output("nav-explorer", "active"), Output("nav-agent", "active")],
    [Input("url", "pathname")]
)
def update_active_nav(pathname):
    if pathname == "/":
        return True, False, False, False
    elif pathname == "/builder":
        return False, True, False, False
    elif pathname == "/explorer":
        return False, False, True, False
    elif pathname == "/agent":
        return False, False, False, True
    return True, False, False, False

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return ontology_layout
    elif pathname == "/builder":
        return builder_layout
    elif pathname == "/explorer":
        return explorer_layout
    elif pathname == "/agent":
        return agent_layout
    return ontology_layout

# Ontology Map Callbacks
@app.callback(
    Output("ontology-details-panel", "children"),
    Input("ontology-graph", "tapNodeData")
)
def display_node_data(data):
    if not data:
        return dmc.Text("Select a node to view details.", c="dimmed")
    
    node_id = data['id']
    print(f"DEBUG: Displaying node data for {node_id}")
    schema = OBJECT_SCHEMAS.get(node_id)
    
    if not schema:
        return dmc.Alert(f"No schema definition found for {node_id}", color="yellow")
    
    # Create Property Table
    rows = []
    for prop in schema['properties']:
        required_badge = dmc.Badge("REQ", color="red", size="xs") if prop['required'] else dmc.Badge("OPT", color="gray", size="xs")
        rows.append(
            html.Tr([
                html.Td(dmc.Code(prop['name'])),
                html.Td(dmc.Text(prop['type'], size="sm")),
                html.Td(required_badge),
                html.Td(dmc.Text(prop['description'], size="sm", c="dimmed"))
            ])
        )
    
    table = dmc.Table(
        children=[
            html.Thead(
                html.Tr([
                    html.Th("Property"),
                    html.Th("Type"),
                    html.Th("Req"),
                    html.Th("Description")
                ])
            ),
            html.Tbody(rows)
        ],
        striped=True,
        highlightOnHover=True,
        withTableBorder=True
    )
    
    return dmc.Stack([
        dmc.Group([
            html.Div(style={'backgroundColor': schema['color'], 'width': '20px', 'height': '20px', 'borderRadius': '50%'}),
            dmc.Title(node_id, order=3),
            dmc.Badge(schema['layer'], color="gray", variant="outline")
        ]),
        dmc.Text(schema['description'], size="sm", mb="md"),
        dmc.Text("Properties", fw=500, mb="xs"),
        table
    ])

# Explorer Callbacks
@app.callback(
    Output('revision-dropdown', 'data'),
    Input('product-dropdown', 'value')
)
def set_revisions(product_id):
    revs = [r for r in data['revisions'] if r.product_id == product_id]
    return [{'label': r.phase, 'value': r.id} for r in revs]

@app.callback(
    Output('status-table-container', 'children'),
    [Input('revision-dropdown', 'value')]
)
def update_table(revision_id):
    if not revision_id:
        return dmc.Alert("Select a revision.", color="yellow")
    
    filtered = df_full[df_full['revision_id_task'] == revision_id]
    
    if filtered.empty:
        return dmc.Alert("No data found for this revision.", color="blue")
    
    display_df = filtered[['name', 'app_id', 'status', 'status_job', 'waiver_rate', 'error_msg']]
    display_df.columns = ['Block', 'App', 'Task Status', 'Job Status', 'Waiver %', 'Error Message']
    
    # Create DMC Table
    header = [
        html.Tr([html.Th(col) for col in display_df.columns])
    ]
    
    rows = []
    for _, row in display_df.iterrows():
        # Status Badge Logic
        status_color = "gray"
        if row['Task Status'] == "COMPLETED": status_color = "green"
        elif row['Task Status'] == "BLOCKED": status_color = "red"
        elif row['Task Status'] == "IN_PROGRESS": status_color = "blue"
        
        status_badge = dmc.Badge(row['Task Status'], color=status_color, variant="light")
        
        job_color = "gray"
        if row['Job Status'] == "DONE": job_color = "green"
        elif row['Job Status'] == "FAILED": job_color = "red"
        elif row['Job Status'] == "RUNNING": job_color = "blue"
        
        job_badge = dmc.Badge(row['Job Status'], color=job_color, variant="dot") if row['Job Status'] else "-"

        rows.append(
            html.Tr([
                html.Td(row['Block']),
                html.Td(dmc.Code(row['App'])),
                html.Td(status_badge),
                html.Td(job_badge),
                html.Td(f"{row['Waiver %']}%" if pd.notna(row['Waiver %']) else "-"),
                html.Td(dmc.Text(row['Error Message'], size="sm", c="red") if pd.notna(row['Error Message']) else "-"),
            ])
        )

    table = dmc.Table(
        children=[html.Thead(header), html.Tbody(rows)],
        striped=True,
        highlightOnHover=True,
        withTableBorder=True,
        withColumnBorders=True
    )
    
    return table

# Agent Callbacks
@app.callback(
    [Output("user-query-input", "value"), Output("agent-response-output", "children")],
    [Input("btn-send", "n_clicks"), Input("btn-sc1", "n_clicks"), Input("btn-sc2", "n_clicks"), Input("btn-sc3", "n_clicks")],
    [State("user-query-input", "value")]
)
def update_agent_interaction(n_send, n_sc1, n_sc2, n_sc3, current_query):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "", "Ready to help."
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == "btn-sc1":
        query = "HBM4E R30 전체 Signoff 현황 알려줘"
        response = """
**AI Agent (Ontology Search):**
`Product("HBM4E")` → `Revision("R30")` → `SignoffTask` Aggregation

**Response:**
HBM4E R30 Signoff Status:

| Block | App | Status | Note |
|---|---|---|---|
| **FULLCHIP** | DSC | ✅ PASS | Waiver 96.7% |
| **IO** | DSC | ❌ FAILED | Power Error (VDD_PERI) |
| **SRAM_A** | LSC | 🔄 RUNNING | Started 13:00 |

⚠️ **Bottleneck:** IO Block DSC Failed.
        """
        return query, response
    
    elif button_id == "btn-sc2":
        query = "IO Block DSC 왜 에러났어?"
        response = """
**AI Agent (Ontology Search):**
1. `SignoffJob` (Failed) → `error_msg` analysis.
2. `SignoffIssue` DB search for "Power Net not defined".

**Response:**
The Job `JOB_DSC_IO_R30_001` failed due to:
> **Error:** Power Net 'VDD_PERI' not defined in power list.

**Context:**
- This is a common issue in `IO` blocks.
- In R29, a similar issue was resolved by adding `VDD_PERI` to `power_list.pp`.

**Action:**
Shall I add `VDD_PERI` to the power list and re-run the job?
        """
        return query, response

    elif button_id == "btn-sc3":
        query = "FULLCHIP DSC 결과 분석해줘. Waiver 할거 있어?"
        response = """
**AI Agent (Ontology Search):**
1. `Result` comparison (R30 vs R29).
2. `Waiver` pattern matching.

**Response:**
Total Violations: 1,500
- **Same as R29:** 1,450 (Auto-migrated ✅)
- **Fixed:** 50
- **New:** 0

**Waiver Status:**
96.7% of violations are already waived based on R29 history.
The remaining violations are marked as 'Fixed' in the design.

No manual waiver action is required at this moment.
        """
        return query, response
        
    elif button_id == "btn-send":
        return current_query, f"I received your query: '{current_query}'.\n(This is a mock agent. Please use the Scenario buttons for demonstrated responses.)"
    
    return "", ""

@app.callback(
    Output('ontology-graph', 'layout'),
    Input('ontology-layout-dropdown', 'value')
)
def update_ontology_layout(layout_name):
    if layout_name == 'cose':
        return {
            'name': 'cose',
            'animate': True,
            'componentSpacing': 100,
            'nodeRepulsion': 400000,
            'nodeOverlap': 20,
            'padding': 30,
        }
    else:
        return {'name': layout_name, 'animate': True}

if __name__ == "__main__":
    app.run(debug=True)
