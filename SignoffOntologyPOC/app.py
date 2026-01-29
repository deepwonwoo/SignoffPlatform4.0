"""
Signoff Ontology POC - Dash App (v2.1 Refactored)
Updates:
- Builder: Modified for InputConfig/Workspace separation
- Ontology: 13 Objects (Phase 1+2+3) with correct relationships
"""
import dash
from dash import dcc, html, Input, Output, State, callback, ALL, ctx
import dash_mantine_components as dmc
import dash_cytoscape as cyto
import json
from datetime import datetime

from utils.ontology_store import store

app = dash.Dash(
    __name__, 
    external_stylesheets=dmc.styles.ALL, 
    suppress_callback_exceptions=True
)
app.title = "Signoff Ontology POC"

# --- Styles ---
graph_stylesheet = [
    {'selector': 'node', 'style': {'content': 'data(label)', 'color': 'white', 'background-color': 'data(color)', 'text-valign': 'center', 'text-halign': 'center', 'font-size': '10px', 'width': '60px', 'height': '30px', 'shape': 'round-rectangle', 'border-width': 2, 'border-color': '#343a40'}},
    {'selector': 'edge', 'style': {'width': 1.5, 'line-color': '#adb5bd', 'target-arrow-color': '#adb5bd', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', 'arrow-scale': 0.8}},
    {'selector': ':selected', 'style': {'border-width': 4, 'border-color': '#ff6b6b'}}
]

# --- Sidebar ---
def create_sidebar():
    return dmc.Stack([
        dmc.Title("Signoff Ontology", order=3, c="blue"),
        dmc.Text("POC v2.1 (Ontology Updated)", size="sm", c="dimmed"),
        dmc.Divider(my="md"),
        
        dmc.Text("Pages", size="xs", fw=600, c="dimmed", mb="xs"),
        dmc.NavLink(label="📚 Schema", href="/schema", id="nav-schema", variant="filled", color="indigo"),
        dmc.NavLink(label="🏗️ Builder", href="/", id="nav-builder", variant="filled", color="blue"),
        dmc.NavLink(label="🗺️ Graph", href="/graph", id="nav-graph", variant="filled", color="cyan"),
        dmc.NavLink(label="📊 Dashboard", href="/dashboard", id="nav-dashboard", variant="filled", color="green"),
        
        dmc.Divider(my="md"),
        dmc.Text("Mock Scenarios", size="xs", fw=600, c="dimmed", mb="xs"),
        dmc.Button("Full Lifecycle (R30/R40)", id="btn-scenario-a", variant="light", color="indigo", fullWidth=True, mb="xs", size="xs"),
        dmc.Button("Compare Case", id="btn-scenario-c", variant="light", color="grape", fullWidth=True, mb="xs", size="xs"),
        dmc.Button("Clear All", id="btn-clear", variant="outline", color="red", fullWidth=True, mt="md", size="xs"),
        
        dmc.Divider(my="md"),
        html.Div(id="sidebar-stats"),
    ], p="md", style={"height": "100vh", "backgroundColor": "#e9ecef", "overflowY": "auto", "borderRight": "1px solid #ced4da"})

# --- Page: Schema ---
def create_schema_page():
    schemas = store.get_object_schema()
    return dmc.Container([
        dmc.Title("📚 Ontology Schema (13 Objects)", order=2, mb="md"),
        dmc.SimpleGrid([
            dmc.Card([
                dmc.Group([dmc.Text(info["icon"], size="xl"), dmc.Text(obj, fw=700)], gap="sm"),
                dmc.Text(info["description"], size="xs", c="dimmed", mb="sm"),
                dmc.Group([dmc.Badge(p, size="xs", variant="light", color="gray") for p in info.get("properties", [])], gap=4)
            ], withBorder=True, style={"borderLeft": f"4px solid {info['color']}"})
            for obj, info in schemas.items()
        ], cols=3, spacing="sm")
    ], fluid=True, p="lg")

# --- Page: Builder ---
def create_builder_page():
    return dmc.Container([
        dmc.Title("🏗️ Ontology Builder", order=2, mb="md"),
        dmc.Text("Semantic (Define) → Kinetic (Setup & Execute) → Dynamic (Analyze)", c="dimmed", mb="xl"),
        
        dmc.Grid([
            # 1. Semantic
            dmc.GridCol([
                dmc.Title("1. Semantic", order=5, c="blue", mb="sm"),
                dmc.Card([
                    dmc.Text("Product", fw=600), dmc.TextInput(id="in-prod", placeholder="ID", mb="xs"), 
                    dmc.Button("Add", id="btn-prod", size="xs", fullWidth=True)
                ], withBorder=True, mb="sm", p="sm"),
                dmc.Card([
                    dmc.Text("Revision", fw=600), dmc.Select(id="sel-rev-prod", placeholder="Product", data=[], mb="xs"), 
                    dmc.TextInput(id="in-rev", placeholder="Code (e.g. R30)", mb="xs"),
                    dmc.Button("Add", id="btn-rev", size="xs", fullWidth=True)
                ], withBorder=True, mb="sm", p="sm"),
                dmc.Card([
                    dmc.Text("Block", fw=600), dmc.Select(id="sel-blk-rev", placeholder="Revision", data=[], mb="xs"),
                    dmc.TextInput(id="in-blk", placeholder="Name", mb="xs"),
                    dmc.Button("Add", id="btn-blk", size="xs", fullWidth=True)
                ], withBorder=True, p="sm"),
            ], span=4),

            # 2. Kinetic Setup
            dmc.GridCol([
                dmc.Title("2. Kinetic Setup", order=5, c="green", mb="sm"),
                dmc.Card([
                    dmc.Text("Application", fw=600), dmc.TextInput(id="in-app", placeholder="App ID", mb="xs"),
                    dmc.Button("Add", id="btn-app", size="xs", fullWidth=True)
                ], withBorder=True, mb="sm", p="sm"),
                
                dmc.Card([
                    dmc.Text("InputConfig (New!)", fw=600, c="teal"), 
                    dmc.Select(id="sel-conf-app", placeholder="App", data=[], mb="xs"),
                    dmc.Select(id="sel-conf-rev", placeholder="Revision", data=[], mb="xs"),
                    dmc.TextInput(id="in-conf-name", placeholder="Config Name", mb="xs"),
                    dmc.Button("Create Config", id="btn-conf", color="teal", size="xs", fullWidth=True)
                ], withBorder=True, mb="sm", p="sm", style={"borderColor": "teal"}),

                dmc.Card([
                    dmc.Text("Workspace", fw=600), dmc.TextInput(id="in-ws", placeholder="Path", mb="xs"),
                    dmc.Button("Create WS", id="btn-ws", size="xs", fullWidth=True)
                ], withBorder=True, p="sm"),
            ], span=4),

            # 3. Kinetic Exec & Dynamic
            dmc.GridCol([
                dmc.Title("3. Execution & Result", order=5, c="orange", mb="sm"),
                dmc.Card([
                    dmc.Text("SignoffJob", fw=600),
                    dmc.Select(id="sel-job-blk", placeholder="Target Block", data=[], mb="xs"),
                    dmc.Select(id="sel-job-conf", placeholder="Input Config", data=[], mb="xs"),
                    dmc.Select(id="sel-job-ws", placeholder="Workspace", data=[], mb="xs"),
                    dmc.Button("Run Job", id="btn-job", color="orange", size="xs", fullWidth=True)
                ], withBorder=True, mb="sm", p="sm"),
                
                dmc.Card([
                    dmc.Text("Result", fw=600),
                    dmc.Select(id="sel-res-job", placeholder="Select Job", data=[], mb="xs"),
                    dmc.NumberInput(id="in-res-total", placeholder="Total", value=1000, mb="xs"),
                    dmc.NumberInput(id="in-res-fail", placeholder="Fail", value=10, mb="xs"),
                    dmc.Button("Publish Result", id="btn-res", color="pink", size="xs", fullWidth=True)
                ], withBorder=True, p="sm"),
            ], span=4),
        ])
    ], fluid=True, p="lg")

# --- Page: Graph ---
def create_graph_page():
    return dmc.Container([
        dmc.Title("🗺️ Ontology Knowledge Graph", order=2, mb="md"),
        dmc.Button("Refresh", id="btn-refresh", variant="outline", size="xs", mb="md"),
        cyto.Cytoscape(
            id="ontology-graph", elements=[], stylesheet=graph_stylesheet,
            style={"width": "100%", "height": "600px", "border": "1px solid #dee2e6"},
            layout={"name": "breadthfirst", "rankDir": "TB"}
        )
    ], fluid=True, p="lg")

# --- Page: Dashboard ---
def create_dashboard_page():
    stats = store.get_statistics()
    return dmc.Container([
        dmc.Title("📊 Dashboard", order=2, mb="md"),
        dmc.SimpleGrid([
            dmc.Card([dmc.Text("Jobs", c="dimmed"), dmc.Title(stats['jobs'], order=3)], withBorder=True, p="sm"),
            dmc.Card([dmc.Text("Results", c="dimmed"), dmc.Title(stats['results'], order=3)], withBorder=True, p="sm"),
            dmc.Card([dmc.Text("Fail Rows", c="dimmed"), dmc.Title(f"{stats['pending_count']:,}", order=3, c="red")], withBorder=True, p="sm"),
        ], cols=3)
    ], fluid=True, p="lg")

# --- Layout ---
app.layout = dmc.MantineProvider(
    children=[
        dcc.Location(id="url"),
        dcc.Store(id="trigger", data=0),
        dmc.Grid([
            dmc.GridCol(create_sidebar(), span=2),
            dmc.GridCol(html.Div(id="page-content"), span=10)
        ], gutter=0)
    ]
)

# --- Callbacks ---

@callback(Output("page-content", "children"), Input("url", "pathname"))
def render(p):
    if p=="/schema": return create_schema_page()
    if p=="/graph": return create_graph_page()
    if p=="/dashboard": return create_dashboard_page()
    return create_builder_page()

@callback(Output("trigger", "data"), Input("btn-scenario-a", "n_clicks"), Input("btn-clear", "n_clicks"))
def scenario(n_a, n_cl):
    if ctx.triggered_id == "btn-scenario-a": store.load_template("full_lifecycle")
    if ctx.triggered_id == "btn-clear": store.clear_all()
    return (n_a or 0) + (n_cl or 0)

@callback(Output("sidebar-stats", "children"), Input("trigger", "data"))
def stats(_):
    s = store.get_statistics()
    return dmc.Stack([dmc.Text(f"{k}: {v}", size="xs") for k,v in s.items() if isinstance(v, int)], gap=2)

@callback(Output("ontology-graph", "elements"), Input("url", "pathname"), Input("trigger", "data"), Input("btn-refresh", "n_clicks"))
def graph(p, _, __):
    if p!="/graph": return []
    return store.to_graph_elements()

# Builder Callbacks
@callback(Output("trigger", "data", allow_duplicate=True), Input("btn-prod", "n_clicks"), State("in-prod", "value"), prevent_initial_call=True)
def add_prod(n, v):
    if n and v: store.add_product(v)
    return n

@callback(Output("trigger", "data", allow_duplicate=True), Input("btn-rev", "n_clicks"), State("sel-rev-prod", "value"), State("in-rev", "value"), prevent_initial_call=True)
def add_rev(n, p, v):
    if n and p and v: store.add_revision(f"{p}_{v}", p, v)
    return n

@callback(Output("trigger", "data", allow_duplicate=True), Input("btn-blk", "n_clicks"), State("sel-blk-rev", "value"), State("in-blk", "value"), prevent_initial_call=True)
def add_blk(n, r, v):
    if n and r and v: store.add_block(f"{r}_{v}", r, v)
    return n

@callback(Output("trigger", "data", allow_duplicate=True), Input("btn-app", "n_clicks"), State("in-app", "value"), prevent_initial_call=True)
def add_app(n, v):
    if n and v: store.add_signoff_application(v, v, "STATIC")
    return n

@callback(Output("trigger", "data", allow_duplicate=True), Input("btn-conf", "n_clicks"), State("sel-conf-app", "value"), State("sel-conf-rev", "value"), State("in-conf-name", "value"), prevent_initial_call=True)
def add_conf(n, a, r, name):
    if n and a and r: store.add_input_config(f"CFG-{a}-{name}", a, r, name)
    return n

@callback(Output("trigger", "data", allow_duplicate=True), Input("btn-ws", "n_clicks"), State("in-ws", "value"), prevent_initial_call=True)
def add_ws(n, v):
    if n and v: store.add_workspace(f"WS-{len(store.workspaces)}", "LOCAL", v)
    return n

@callback(Output("trigger", "data", allow_duplicate=True), Input("btn-job", "n_clicks"), State("sel-job-blk", "value"), State("sel-job-conf", "value"), State("sel-job-ws", "value"), prevent_initial_call=True)
def add_job(n, b, c, w):
    if n and b and c: store.add_signoff_job(f"JOB-{n}", c, b, w, "kim_cs")
    return n

@callback(Output("trigger", "data", allow_duplicate=True), Input("btn-res", "n_clicks"), State("sel-res-job", "value"), State("in-res-total", "value"), State("in-res-fail", "value"), prevent_initial_call=True)
def add_res(n, j, t, f):
    if n and j: store.add_result(f"RES-{n}", j, t, fail_count=f)
    return n

# Dropdowns update
@callback(
    Output("sel-rev-prod", "data"), Output("sel-blk-rev", "data"), 
    Output("sel-conf-app", "data"), Output("sel-conf-rev", "data"),
    Output("sel-job-blk", "data"), Output("sel-job-conf", "data"), Output("sel-job-ws", "data"),
    Output("sel-res-job", "data"),
    Input("trigger", "data")
)
def update_drops(_):
    prods = [p['product_id'] for p in store.products]
    revs = [r['revision_id'] for r in store.revisions]
    apps = [a['app_id'] for a in store.signoff_applications]
    blks = [b['block_id'] for b in store.blocks]
    confs = [c['config_id'] for c in store.input_configs]
    wss = [w['workspace_id'] for w in store.workspaces]
    jobs = [j['job_id'] for j in store.signoff_jobs]
    return prods, revs, apps, revs, blks, confs, wss, jobs

if __name__ == "__main__":
    store.load_template("full_lifecycle")
    app.run(debug=True)
