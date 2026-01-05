"""
Signoff Ontology POC - Dash App
5개 페이지: Builder, Graph, Explorer, Dashboard, Compare

Based on: updated_Signoff Platform Ontology.md
"""
import dash
from dash import dcc, html, Input, Output, State, callback, ALL, ctx
import dash_mantine_components as dmc
import dash_cytoscape as cyto
import pandas as pd
import json
from datetime import datetime

from utils.ontology_store import store

# --- App Setup ---
app = dash.Dash(
    __name__, 
    external_stylesheets=dmc.styles.ALL, 
    suppress_callback_exceptions=True
)
app.title = "Signoff Ontology POC"

# --- Graph Stylesheet ---
graph_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)',
            'color': 'white',
            'background-color': 'data(color)',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '10px',
            'width': '60px',
            'height': '30px',
            'shape': 'round-rectangle',
            'border-width': 2,
            'border-color': '#343a40',
        }
    },
    {
        'selector': 'edge',
        'style': {
            'width': 1.5,
            'line-color': '#adb5bd',
            'target-arrow-color': '#adb5bd',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 0.8
        }
    },
    {
        'selector': ':selected',
        'style': {
            'border-width': 4,
            'border-color': '#ff6b6b',
        }
    }
]

# --- Sidebar ---
def create_sidebar():
    return dmc.Stack([
        dmc.Title("Signoff Ontology", order=3, c="white"),
        dmc.Text("POC Demo", size="sm", c="dimmed"),
        dmc.Divider(my="md"),
        
        # Navigation
        dmc.NavLink(label="🏗️ Builder", href="/", active=True, id="nav-builder"),
        dmc.NavLink(label="🗺️ Graph", href="/graph", id="nav-graph"),
        dmc.NavLink(label="📊 Explorer", href="/explorer", id="nav-explorer"),
        dmc.NavLink(label="📈 Dashboard", href="/dashboard", id="nav-dashboard"),
        dmc.NavLink(label="🔄 Compare", href="/compare", id="nav-compare"),
        
        dmc.Divider(my="md"),
        
        # Scenario Buttons
        dmc.Text("Mock 데이터 시나리오", size="sm", fw=600, c="dimmed"),
        dmc.Button("A. Full Lifecycle (R00→R60)", id="btn-scenario-a", variant="light", fullWidth=True, mb="xs"),
        dmc.Button("B. R40 상세 (5 Apps)", id="btn-scenario-b", variant="light", fullWidth=True, mb="xs"),
        dmc.Button("C. R30→R40 Compare", id="btn-scenario-c", variant="light", fullWidth=True, mb="xs"),
        dmc.Button("Clear All", id="btn-clear", variant="outline", color="red", fullWidth=True, mt="md"),
        
        dmc.Divider(my="md"),
        
        # Statistics
        html.Div(id="sidebar-stats"),
        
        dmc.Divider(my="md"),
        
        # Export Buttons
        dmc.Text("Export", size="sm", fw=600, c="dimmed"),
        dmc.Button("📥 JSON (GraphRAG)", id="btn-export-json", variant="subtle", fullWidth=True, size="xs"),
        dcc.Download(id="download-json"),
        
    ], gap="xs", p="md", style={"height": "100vh", "backgroundColor": "#1a1b1e"})


# --- Page: Builder ---
def create_builder_page():
    return dmc.Container([
        dmc.Title("🏗️ Ontology Builder", order=2, mb="lg"),
        dmc.Text("10개 핵심 Object Type을 인터랙티브하게 생성합니다.", c="dimmed", mb="xl"),
        
        dmc.Grid([
            # Column 1: Product, Revision, Block
            dmc.GridCol([
                dmc.Card([
                    dmc.Text("Product", fw=600),
                    dmc.TextInput(id="input-product-id", placeholder="Product ID (예: HBM4E)", mb="xs"),
                    dmc.TextInput(id="input-product-name", placeholder="Product Name", mb="xs"),
                    dmc.Button("➕ Add Product", id="btn-add-product", size="xs", fullWidth=True),
                ], withBorder=True, p="md", mb="md"),
                
                dmc.Card([
                    dmc.Text("Revision", fw=600),
                    dmc.Select(id="select-product-for-rev", placeholder="Select Product", data=[], mb="xs"),
                    dmc.Select(id="select-rev-phase", placeholder="Phase", data=[
                        {"value": p, "label": p} for p in ["R00", "R10", "R20", "R30", "R40", "R50", "R60"]
                    ], mb="xs"),
                    dmc.Button("➕ Add Revision", id="btn-add-revision", size="xs", fullWidth=True),
                ], withBorder=True, p="md", mb="md"),
                
                dmc.Card([
                    dmc.Text("Block", fw=600),
                    dmc.Select(id="select-rev-for-block", placeholder="Select Revision", data=[], mb="xs"),
                    dmc.Select(id="select-block-name", placeholder="Block Name", data=[
                        {"value": b, "label": b} for b in ["FULLCHIP", "FULLCHIP_NO_CORE", "CORE", "PAD", "IO", "PHY"]
                    ], mb="xs"),
                    dmc.Button("➕ Add Block", id="btn-add-block", size="xs", fullWidth=True),
                ], withBorder=True, p="md"),
            ], span=4),
            
            # Column 2: Application, Designer
            dmc.GridCol([
                dmc.Card([
                    dmc.Text("SignoffApplication", fw=600),
                    dmc.Select(id="select-app-preset", placeholder="Preset Application", data=[
                        {"value": "DSC", "label": "DSC - Driver Size Check"},
                        {"value": "LSC", "label": "LSC - Latch Strength Check"},
                        {"value": "LS", "label": "LS - Level Shifter Check"},
                        {"value": "PEC", "label": "PEC - Power Error Check"},
                        {"value": "CANATR", "label": "CANATR - Coupling Noise"},
                        {"value": "CDA", "label": "CDA - Coupling Delay"},
                    ], mb="xs"),
                    dmc.Button("➕ Add Application", id="btn-add-app", size="xs", fullWidth=True),
                ], withBorder=True, p="md", mb="md"),
                
                dmc.Card([
                    dmc.Text("Designer", fw=600),
                    dmc.TextInput(id="input-designer-id", placeholder="Designer ID", mb="xs"),
                    dmc.TextInput(id="input-designer-name", placeholder="Name", mb="xs"),
                    dmc.Select(id="select-designer-role", placeholder="Role", data=[
                        {"value": "ENGINEER", "label": "Engineer"},
                        {"value": "LEAD", "label": "Lead"},
                        {"value": "MANAGER", "label": "Manager"},
                        {"value": "DEVELOPER", "label": "Developer"},
                    ], mb="xs"),
                    dmc.Button("➕ Add Designer", id="btn-add-designer", size="xs", fullWidth=True),
                ], withBorder=True, p="md", mb="md"),
                
                dmc.Card([
                    dmc.Text("SignoffTask", fw=600),
                    dmc.Select(id="select-block-for-task", placeholder="Select Block", data=[], mb="xs"),
                    dmc.Select(id="select-app-for-task", placeholder="Select Application", data=[], mb="xs"),
                    dmc.Select(id="select-designer-for-task", placeholder="Select Owner", data=[], mb="xs"),
                    dmc.Button("➕ Add Task", id="btn-add-task", size="xs", fullWidth=True),
                ], withBorder=True, p="md"),
            ], span=4),
            
            # Column 3: Job, Result
            dmc.GridCol([
                dmc.Card([
                    dmc.Text("SignoffJob", fw=600),
                    dmc.Select(id="select-task-for-job", placeholder="Select Task", data=[], mb="xs"),
                    dmc.Button("▶️ Execute Job", id="btn-add-job", size="xs", fullWidth=True, color="green"),
                ], withBorder=True, p="md", mb="md"),
                
                dmc.Card([
                    dmc.Text("Result", fw=600),
                    dmc.Select(id="select-job-for-result", placeholder="Select Job", data=[], mb="xs"),
                    dmc.NumberInput(id="input-total-rows", placeholder="Total Rows", value=1000, min=1, mb="xs"),
                    dmc.NumberInput(id="input-waiver-count", placeholder="Waiver Count", value=700, min=0, mb="xs"),
                    dmc.NumberInput(id="input-fixed-count", placeholder="Fixed Count", value=200, min=0, mb="xs"),
                    dmc.Button("📊 Add Result", id="btn-add-result", size="xs", fullWidth=True, color="orange"),
                ], withBorder=True, p="md"),
            ], span=4),
        ]),
        
    ], fluid=True, p="xl")


# --- Page: Graph ---
def create_graph_page():
    return dmc.Container([
        dmc.Title("🗺️ Ontology Graph", order=2, mb="lg"),
        dmc.Text("10개 Object Type과 관계를 시각화합니다.", c="dimmed", mb="md"),
        
        dmc.Grid([
            dmc.GridCol([
                dmc.Group([
                    dmc.Select(
                        id="graph-layout",
                        label="Layout",
                        data=[
                            {"value": "cose", "label": "Force-directed"},
                            {"value": "breadthfirst", "label": "Hierarchical"},
                            {"value": "grid", "label": "Grid"},
                            {"value": "circle", "label": "Circle"},
                            {"value": "concentric", "label": "Concentric"},
                        ],
                        value="breadthfirst",
                        w=150
                    ),
                    dmc.MultiSelect(
                        id="graph-type-filter",
                        label="Object Types",
                        data=[{"value": t, "label": t} for t in store.COLORS.keys()],
                        value=list(store.COLORS.keys()),
                        w=300
                    ),
                ]),
            ], span=12),
        ], mb="md"),
        
        dmc.Grid([
            dmc.GridCol([
                dmc.Paper([
                    cyto.Cytoscape(
                        id='ontology-graph',
                        layout={'name': 'breadthfirst', 'directed': True},
                        style={'width': '100%', 'height': '600px'},
                        stylesheet=graph_stylesheet,
                        elements=[]
                    )
                ], withBorder=True, p="xs", radius="md")
            ], span=8),
            
            dmc.GridCol([
                dmc.Paper([
                    dmc.Title("Node Details", order=4, mb="md"),
                    html.Div(id="node-detail-content", children=[
                        dmc.Text("Click a node to see details", c="dimmed")
                    ])
                ], withBorder=True, p="md", radius="md", h="100%")
            ], span=4),
        ]),
        
        # Legend
        dmc.Paper([
            dmc.Group([
                dmc.Group([
                    html.Div(style={"width": 16, "height": 16, "backgroundColor": color, "borderRadius": 4}),
                    dmc.Text(obj_type, size="xs")
                ], gap="xs") for obj_type, color in store.COLORS.items()
            ], gap="lg")
        ], withBorder=True, p="sm", mt="md"),
        
    ], fluid=True, p="xl")


# --- Page: Explorer ---
def create_explorer_page():
    return dmc.Container([
        dmc.Title("📊 Data Explorer", order=2, mb="lg"),
        dmc.Text("모든 Ontology 객체를 테이블로 탐색합니다.", c="dimmed", mb="md"),
        
        dmc.Select(
            id="explorer-type-select",
            label="Object Type",
            data=[{"value": t, "label": t} for t in store.COLORS.keys()],
            value="Result",
            w=200,
            mb="md"
        ),
        
        dmc.TextInput(id="explorer-search", placeholder="Search...", w=300, mb="md"),
        
        html.Div(id="explorer-table-container"),
        
    ], fluid=True, p="xl")


# --- Page: Dashboard ---
def create_dashboard_page():
    return dmc.Container([
        dmc.Title("📈 Signoff Dashboard", order=2, mb="lg"),
        dmc.Text("Revision별 Signoff 진행률 및 WAIVER/FIXED/PENDING 현황", c="dimmed", mb="xl"),
        
        # KPI Cards
        html.Div(id="dashboard-kpi-cards", className="mb-4"),
        
        dmc.Divider(my="lg"),
        
        # Progress by Revision
        dmc.Title("Revision별 진행률", order=4, mb="md"),
        html.Div(id="dashboard-revision-progress"),
        
        dmc.Divider(my="lg"),
        
        # Application별 현황
        dmc.Title("Application별 현황", order=4, mb="md"),
        html.Div(id="dashboard-app-stats"),
        
    ], fluid=True, p="xl")


# --- Page: Compare ---
def create_compare_page():
    return dmc.Container([
        dmc.Title("🔄 Compare & Migration", order=2, mb="lg"),
        dmc.Text("Revision 간 결과 비교 및 Waiver Migration 시뮬레이션", c="dimmed", mb="xl"),
        
        dmc.Grid([
            dmc.GridCol([
                dmc.Select(id="compare-rev1", label="Base Revision (Previous)", placeholder="Select", data=[]),
            ], span=4),
            dmc.GridCol([
                dmc.Select(id="compare-rev2", label="Target Revision (Current)", placeholder="Select", data=[]),
            ], span=4),
            dmc.GridCol([
                dmc.Button("🔍 Compare", id="btn-compare", mt="xl"),
            ], span=4),
        ], mb="xl"),
        
        html.Div(id="compare-results"),
        
    ], fluid=True, p="xl")


# --- App Layout ---
app.layout = dmc.MantineProvider(
    forceColorScheme="light",
    theme={"primaryColor": "blue", "fontFamily": "'Pretendard', 'Inter', sans-serif"},
    children=[
        dcc.Location(id="url"),
        dcc.Store(id="builder-trigger", data=0),  # Global trigger for updates across pages
        dmc.Grid([
            dmc.GridCol(create_sidebar(), span=2),
            dmc.GridCol(html.Div(id="page-content"), span=10)
        ], gutter=0)
    ]
)


# ========== CALLBACKS ==========

# --- Page Routing ---
@callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname):
    if pathname == "/graph":
        return create_graph_page()
    elif pathname == "/explorer":
        return create_explorer_page()
    elif pathname == "/dashboard":
        return create_dashboard_page()
    elif pathname == "/compare":
        return create_compare_page()
    else:
        return create_builder_page()


# --- Scenario Loading ---
@callback(
    Output("builder-trigger", "data"),
    Input("btn-scenario-a", "n_clicks"),
    Input("btn-scenario-b", "n_clicks"),
    Input("btn-scenario-c", "n_clicks"),
    Input("btn-clear", "n_clicks"),
    State("builder-trigger", "data"),
    prevent_initial_call=True
)
def load_scenario(na, nb, nc, nclear, trigger):
    triggered = ctx.triggered_id
    if triggered == "btn-scenario-a":
        store.load_template("full_lifecycle")
    elif triggered == "btn-scenario-b":
        store.load_template("r30_detail")
    elif triggered == "btn-scenario-c":
        store.load_template("compare")
    elif triggered == "btn-clear":
        store.clear_all()
    return (trigger or 0) + 1


# --- Sidebar Stats ---
@callback(Output("sidebar-stats", "children"), Input("builder-trigger", "data"), Input("url", "pathname"))
def update_stats(trigger, pathname):
    stats = store.get_statistics()
    return dmc.Stack([
        dmc.Text(f"📦 Products: {stats['products']}", size="xs", c="dimmed"),
        dmc.Text(f"📋 Revisions: {stats['revisions']}", size="xs", c="dimmed"),
        dmc.Text(f"🧱 Blocks: {stats['blocks']}", size="xs", c="dimmed"),
        dmc.Text(f"📝 Tasks: {stats['tasks']}", size="xs", c="dimmed"),
        dmc.Text(f"⚙️ Jobs: {stats['jobs']}", size="xs", c="dimmed"),
        dmc.Text(f"📊 Results: {stats['results']}", size="xs", c="dimmed"),
        dmc.Divider(my="xs"),
        dmc.Text(f"✅ WAIVER: {stats['total_waiver']:,}", size="xs", c="green"),
        dmc.Text(f"🔧 FIXED: {stats['total_fixed']:,}", size="xs", c="blue"),
        dmc.Text(f"⏳ PENDING: {stats['total_pending']:,}", size="xs", c="orange"),
        dmc.Progress(value=stats['overall_progress'], color="green", size="sm", mt="xs"),
        dmc.Text(f"{stats['overall_progress']}% Complete", size="xs", c="dimmed", ta="center"),
    ], gap=2)


# --- Builder Dropdowns ---
@callback(
    Output("select-product-for-rev", "data"),
    Output("select-rev-for-block", "data"),
    Output("select-block-for-task", "data"),
    Output("select-app-for-task", "data"),
    Output("select-designer-for-task", "data"),
    Output("select-task-for-job", "data"),
    Output("select-job-for-result", "data"),
    Input("builder-trigger", "data"),
    Input("url", "pathname")
)
def update_builder_dropdowns(trigger, pathname):
    return (
        store.get_product_options(),
        store.get_revision_options(),
        store.get_block_options(),
        store.get_app_options(),
        store.get_designer_options(),
        store.get_task_options(),
        [{"value": j["job_id"], "label": j["job_id"]} for j in store.signoff_jobs if j["status"] != "DONE"],
    )


# --- Builder: Add Product ---
@callback(
    Output("builder-trigger", "data", allow_duplicate=True),
    Input("btn-add-product", "n_clicks"),
    State("input-product-id", "value"),
    State("input-product-name", "value"),
    State("builder-trigger", "data"),
    prevent_initial_call=True
)
def add_product(n, pid, pname, trigger):
    if n and pid:
        store.add_product(pid, pname or pid)
        return (trigger or 0) + 1
    return trigger


# --- Builder: Add Revision ---
@callback(
    Output("builder-trigger", "data", allow_duplicate=True),
    Input("btn-add-revision", "n_clicks"),
    State("select-product-for-rev", "value"),
    State("select-rev-phase", "value"),
    State("builder-trigger", "data"),
    prevent_initial_call=True
)
def add_revision(n, product_id, phase, trigger):
    if n and product_id and phase:
        rev_id = f"{product_id}_{phase}"
        store.add_revision(rev_id, product_id, phase)
        return (trigger or 0) + 1
    return trigger


# --- Builder: Add Block ---
@callback(
    Output("builder-trigger", "data", allow_duplicate=True),
    Input("btn-add-block", "n_clicks"),
    State("select-rev-for-block", "value"),
    State("select-block-name", "value"),
    State("builder-trigger", "data"),
    prevent_initial_call=True
)
def add_block(n, rev_id, block_name, trigger):
    if n and rev_id and block_name:
        block_id = f"{rev_id}_{block_name}"
        store.add_block(block_id, rev_id, block_name)
        return (trigger or 0) + 1
    return trigger


# --- Builder: Add Application ---
@callback(
    Output("builder-trigger", "data", allow_duplicate=True),
    Input("btn-add-app", "n_clicks"),
    State("select-app-preset", "value"),
    State("builder-trigger", "data"),
    prevent_initial_call=True
)
def add_app(n, app_id, trigger):
    if n and app_id:
        store.add_signoff_application(app_id)
        return (trigger or 0) + 1
    return trigger


# --- Builder: Add Designer ---
@callback(
    Output("builder-trigger", "data", allow_duplicate=True),
    Input("btn-add-designer", "n_clicks"),
    State("input-designer-id", "value"),
    State("input-designer-name", "value"),
    State("select-designer-role", "value"),
    State("builder-trigger", "data"),
    prevent_initial_call=True
)
def add_designer(n, did, dname, drole, trigger):
    if n and did:
        store.add_designer(did, dname, role=drole or "ENGINEER")
        return (trigger or 0) + 1
    return trigger


# --- Builder: Add Task ---
@callback(
    Output("builder-trigger", "data", allow_duplicate=True),
    Input("btn-add-task", "n_clicks"),
    State("select-block-for-task", "value"),
    State("select-app-for-task", "value"),
    State("select-designer-for-task", "value"),
    State("builder-trigger", "data"),
    prevent_initial_call=True
)
def add_task(n, block_id, app_id, owner_id, trigger):
    if n and block_id and app_id:
        # Get revision_id from block
        block = next((b for b in store.blocks if b["block_id"] == block_id), None)
        if block:
            task_id = f"{block_id}_{app_id}"
            store.add_signoff_task(task_id, block["revision_id"], block_id, app_id, owner_id)
            return (trigger or 0) + 1
    return trigger


# --- Builder: Add Job ---
@callback(
    Output("builder-trigger", "data", allow_duplicate=True),
    Input("btn-add-job", "n_clicks"),
    State("select-task-for-job", "value"),
    State("builder-trigger", "data"),
    prevent_initial_call=True
)
def add_job(n, task_id, trigger):
    if n and task_id:
        job_id = f"JOB_{task_id}"
        store.add_signoff_job(job_id, task_id, status="RUNNING")
        return (trigger or 0) + 1
    return trigger


# --- Builder: Add Result ---
@callback(
    Output("builder-trigger", "data", allow_duplicate=True),
    Input("btn-add-result", "n_clicks"),
    State("select-job-for-result", "value"),
    State("input-total-rows", "value"),
    State("input-waiver-count", "value"),
    State("input-fixed-count", "value"),
    State("builder-trigger", "data"),
    prevent_initial_call=True
)
def add_result(n, job_id, total, waiver, fixed, trigger):
    if n and job_id:
        result_id = f"RESULT_{job_id}"
        store.add_result(result_id, job_id, total or 1000, waiver or 0, fixed or 0)
        return (trigger or 0) + 1
    return trigger


# --- Graph Update ---
@callback(
    Output("ontology-graph", "elements"),
    Output("ontology-graph", "layout"),
    Input("builder-trigger", "data"),
    Input("graph-layout", "value"),
    Input("graph-type-filter", "value"),
    Input("url", "pathname")
)
def update_graph(trigger, layout, type_filter, pathname):
    elements = store.to_graph_elements()
    
    # Filter by type
    if type_filter:
        filtered_elements = []
        node_ids = set()
        for el in elements:
            if "source" not in el.get("data", {}):  # Node
                if el["data"].get("type") in type_filter:
                    filtered_elements.append(el)
                    node_ids.add(el["data"]["id"])
        # Add edges only if both nodes are present
        for el in elements:
            if "source" in el.get("data", {}):  # Edge
                if el["data"]["source"] in node_ids and el["data"]["target"] in node_ids:
                    filtered_elements.append(el)
        elements = filtered_elements
    
    layout_config = {'name': layout or 'breadthfirst', 'directed': True}
    
    return elements, layout_config


# --- Graph Node Click ---
@callback(
    Output("node-detail-content", "children"),
    Input("ontology-graph", "tapNodeData"),
)
def show_node_detail(node_data):
    if not node_data:
        return dmc.Text("Click a node to see details", c="dimmed")
    
    node_id = node_data.get("id", "")
    node_type = node_data.get("type", "")
    
    # Find the object
    all_objects = store.get_all_objects()
    obj = None
    for obj_type, obj_list in all_objects.items():
        for o in obj_list:
            obj_id_key = list(o.keys())[0]  # First key is usually the ID
            if o.get(obj_id_key) == node_id or o.get("product_id") == node_id or \
               o.get("revision_id") == node_id or o.get("block_id") == node_id or \
               o.get("app_id") == node_id or o.get("designer_id") == node_id or \
               o.get("task_id") == node_id or o.get("job_id") == node_id or \
               o.get("result_id") == node_id:
                obj = o
                break
        if obj:
            break
    
    if not obj:
        return dmc.Text(f"Node: {node_id}", c="dimmed")
    
    # Display object properties
    items = []
    for k, v in obj.items():
        if not k.startswith("_"):
            if isinstance(v, dict):
                v = json.dumps(v, ensure_ascii=False)
            items.append(dmc.Group([
                dmc.Text(f"{k}:", size="xs", fw=600, c="dimmed", w=120),
                dmc.Text(str(v)[:50], size="xs")
            ], gap="xs"))
    
    return dmc.Stack([
        dmc.Badge(node_type, color="blue", mb="sm"),
        *items
    ], gap="xs")


# --- Explorer Table ---
@callback(
    Output("explorer-table-container", "children"),
    Input("explorer-type-select", "value"),
    Input("explorer-search", "value"),
    Input("builder-trigger", "data"),
    Input("url", "pathname")
)
def update_explorer(obj_type, search, trigger, pathname):
    all_objects = store.get_all_objects()
    objects = all_objects.get(obj_type, [])
    
    if not objects:
        return dmc.Text("No data available", c="dimmed")
    
    # Filter by search
    if search:
        search_lower = search.lower()
        objects = [o for o in objects if search_lower in str(o).lower()]
    
    # Create table
    if not objects:
        return dmc.Text("No matching results", c="dimmed")
    
    # Get columns from first object
    columns = [k for k in objects[0].keys() if not k.startswith("_")]
    
    header = dmc.TableThead(
        dmc.TableTr([dmc.TableTh(col) for col in columns])
    )
    
    rows = []
    for obj in objects[:50]:  # Limit to 50 rows
        cells = []
        for col in columns:
            val = obj.get(col, "")
            if isinstance(val, dict):
                val = json.dumps(val, ensure_ascii=False)[:30] + "..."
            elif isinstance(val, list):
                val = ", ".join(str(v) for v in val[:3])
            cells.append(dmc.TableTd(str(val)[:40]))
        rows.append(dmc.TableTr(cells))
    
    body = dmc.TableTbody(rows)
    
    return dmc.Table([header, body], striped=True, highlightOnHover=True, withTableBorder=True)


# --- Dashboard ---
@callback(
    Output("dashboard-kpi-cards", "children"),
    Output("dashboard-revision-progress", "children"),
    Output("dashboard-app-stats", "children"),
    Input("builder-trigger", "data"),
    Input("url", "pathname")
)
def update_dashboard(trigger, pathname):
    stats = store.get_statistics()
    
    # KPI Cards
    kpi_cards = dmc.Grid([
        dmc.GridCol([
            dmc.Card([
                dmc.Text("Total Rows", size="xs", c="dimmed"),
                dmc.Title(f"{stats['total_rows']:,}", order=3),
            ], withBorder=True, p="md")
        ], span=2),
        dmc.GridCol([
            dmc.Card([
                dmc.Text("WAIVER", size="xs", c="dimmed"),
                dmc.Title(f"{stats['total_waiver']:,}", order=3, c="green"),
            ], withBorder=True, p="md")
        ], span=2),
        dmc.GridCol([
            dmc.Card([
                dmc.Text("FIXED", size="xs", c="dimmed"),
                dmc.Title(f"{stats['total_fixed']:,}", order=3, c="blue"),
            ], withBorder=True, p="md")
        ], span=2),
        dmc.GridCol([
            dmc.Card([
                dmc.Text("PENDING", size="xs", c="dimmed"),
                dmc.Title(f"{stats['total_pending']:,}", order=3, c="orange"),
            ], withBorder=True, p="md")
        ], span=2),
        dmc.GridCol([
            dmc.Card([
                dmc.Text("Progress", size="xs", c="dimmed"),
                dmc.Title(f"{stats['overall_progress']}%", order=3),
                dmc.Progress(value=stats['overall_progress'], color="green", size="md", mt="xs"),
            ], withBorder=True, p="md")
        ], span=4),
    ])
    
    # Revision Progress
    rev_progress = store.get_revision_progress()
    if not rev_progress:
        rev_table = dmc.Text("No revision data", c="dimmed")
    else:
        header = dmc.TableThead(
            dmc.TableTr([
                dmc.TableTh("Revision"),
                dmc.TableTh("Status"),
                dmc.TableTh("Tasks"),
                dmc.TableTh("Jobs"),
                dmc.TableTh("Total"),
                dmc.TableTh("WAIVER"),
                dmc.TableTh("FIXED"),
                dmc.TableTh("PENDING"),
                dmc.TableTh("Progress"),
            ])
        )
        rows = []
        for r in rev_progress:
            color = "green" if r["progress_pct"] >= 95 else ("yellow" if r["progress_pct"] >= 50 else "red")
            rows.append(dmc.TableTr([
                dmc.TableTd(r["revision_phase"]),
                dmc.TableTd(dmc.Badge(r["status"], size="xs")),
                dmc.TableTd(str(r["total_tasks"])),
                dmc.TableTd(str(r["completed_jobs"])),
                dmc.TableTd(f"{r['total_rows']:,}"),
                dmc.TableTd(f"{r['waiver_count']:,}"),
                dmc.TableTd(f"{r['fixed_count']:,}"),
                dmc.TableTd(f"{r['pending_count']:,}"),
                dmc.TableTd(dmc.Progress(value=r["progress_pct"], color=color, size="md", style={"width": 100})),
            ]))
        body = dmc.TableTbody(rows)
        rev_table = dmc.Table([header, body], striped=True, withTableBorder=True)
    
    # App Stats (placeholder)
    app_stats = dmc.Text(f"{len(store.signoff_applications)} Applications registered", c="dimmed")
    
    return kpi_cards, rev_table, app_stats


# --- Compare Page ---
@callback(
    Output("compare-rev1", "data"),
    Output("compare-rev2", "data"),
    Input("builder-trigger", "data"),
    Input("url", "pathname")
)
def update_compare_dropdowns(trigger, pathname):
    options = store.get_revision_options()
    return options, options


@callback(
    Output("compare-results", "children"),
    Input("btn-compare", "n_clicks"),
    State("compare-rev1", "value"),
    State("compare-rev2", "value"),
    prevent_initial_call=True
)
def do_compare(n, rev1, rev2):
    if not rev1 or not rev2:
        return dmc.Text("Select two revisions to compare", c="dimmed")
    
    # Find results for each revision
    rev1_tasks = [t for t in store.signoff_tasks if t["revision_id"] == rev1]
    rev2_tasks = [t for t in store.signoff_tasks if t["revision_id"] == rev2]
    
    rev1_jobs = [j for j in store.signoff_jobs if j["task_id"] in [t["task_id"] for t in rev1_tasks]]
    rev2_jobs = [j for j in store.signoff_jobs if j["task_id"] in [t["task_id"] for t in rev2_tasks]]
    
    rev1_results = [r for r in store.results if r["job_id"] in [j["job_id"] for j in rev1_jobs]]
    rev2_results = [r for r in store.results if r["job_id"] in [j["job_id"] for j in rev2_jobs]]
    
    # Summary
    rev1_total = sum(r["row_count"] for r in rev1_results)
    rev2_total = sum(r["row_count"] for r in rev2_results)
    
    rev1_waiver = sum(r["waiver_count"] for r in rev1_results)
    rev2_waiver = sum(r["waiver_count"] for r in rev2_results)
    
    # Comparison summary from rev2 results
    total_same = sum(r["comparison_summary"].get("same_count", 0) for r in rev2_results)
    total_diff = sum(r["comparison_summary"].get("diff_count", 0) for r in rev2_results)
    total_new = sum(r["comparison_summary"].get("new_count", 0) for r in rev2_results)
    total_removed = sum(r["comparison_summary"].get("removed_count", 0) for r in rev2_results)
    
    return dmc.Stack([
        dmc.Title(f"{rev1} vs {rev2}", order=4),
        
        dmc.Grid([
            dmc.GridCol([
                dmc.Card([
                    dmc.Text(rev1.split("_")[-1], fw=600),
                    dmc.Text(f"Total: {rev1_total:,}", size="sm"),
                    dmc.Text(f"WAIVER: {rev1_waiver:,}", size="sm", c="green"),
                ], withBorder=True, p="md")
            ], span=4),
            
            dmc.GridCol([
                dmc.Stack([
                    dmc.Text("→", size="xl", ta="center"),
                    dmc.Text("Migration", size="xs", c="dimmed", ta="center"),
                ], align="center", justify="center", h="100%")
            ], span=2),
            
            dmc.GridCol([
                dmc.Card([
                    dmc.Text(rev2.split("_")[-1], fw=600),
                    dmc.Text(f"Total: {rev2_total:,}", size="sm"),
                    dmc.Text(f"WAIVER: {rev2_waiver:,}", size="sm", c="green"),
                ], withBorder=True, p="md")
            ], span=4),
        ], mb="lg"),
        
        dmc.Title("Comparison Summary", order=5, mb="md"),
        dmc.Grid([
            dmc.GridCol([
                dmc.Card([
                    dmc.Text("Same", size="xs", c="dimmed"),
                    dmc.Title(f"{total_same:,}", order=4, c="green"),
                    dmc.Text("→ WAIVER 자동 이관", size="xs", c="dimmed"),
                ], withBorder=True, p="md", bg="green.0")
            ], span=3),
            dmc.GridCol([
                dmc.Card([
                    dmc.Text("Diff", size="xs", c="dimmed"),
                    dmc.Title(f"{total_diff:,}", order=4, c="orange"),
                    dmc.Text("→ 재검토 필요", size="xs", c="dimmed"),
                ], withBorder=True, p="md", bg="orange.0")
            ], span=3),
            dmc.GridCol([
                dmc.Card([
                    dmc.Text("New", size="xs", c="dimmed"),
                    dmc.Title(f"{total_new:,}", order=4, c="red"),
                    dmc.Text("→ 신규 검토", size="xs", c="dimmed"),
                ], withBorder=True, p="md", bg="red.0")
            ], span=3),
            dmc.GridCol([
                dmc.Card([
                    dmc.Text("Removed", size="xs", c="dimmed"),
                    dmc.Title(f"{total_removed:,}", order=4, c="gray"),
                    dmc.Text("→ 해결됨", size="xs", c="dimmed"),
                ], withBorder=True, p="md", bg="gray.0")
            ], span=3),
        ]),
    ])


# --- Export JSON ---
@callback(
    Output("download-json", "data"),
    Input("btn-export-json", "n_clicks"),
    prevent_initial_call=True
)
def export_json(n):
    if n:
        content = store.to_json_graphrag()
        return dict(content=content, filename="signoff_ontology.json")
    return None


# --- Run Server ---
if __name__ == "__main__":
    # Load default scenario
    store.load_template("full_lifecycle")
    app.run(debug=True, port=8050)
