"""
Signoff Ontology POC - Dash App (v2.0)
6개 페이지: Schema, Builder, Graph, Explorer, Dashboard, Compare

Based on: updated_Signoff Platform Ontology.md (13 Object Types, 3 Layers)
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
        dmc.Title("Signoff Ontology", order=3, c="blue"),
        dmc.Text("POC Demo v2.0", size="sm", c="dimmed"),
        dmc.Divider(my="md"),
        
        # Navigation
        dmc.Text("Pages", size="xs", fw=600, c="dimmed", mb="xs"),
        dmc.NavLink(label="📚 Schema", href="/schema", id="nav-schema",
                    variant="filled", color="indigo"),
        dmc.NavLink(label="🏗️ Builder", href="/", id="nav-builder",
                    variant="filled", color="blue"),
        dmc.NavLink(label="🗺️ Graph", href="/graph", id="nav-graph",
                    variant="filled", color="cyan"),
        dmc.NavLink(label="📊 Dashboard", href="/dashboard", id="nav-dashboard",
                    variant="filled", color="green"),
        dmc.NavLink(label="🔄 Compare", href="/compare", id="nav-compare",
                    variant="filled", color="orange"),
        
        dmc.Divider(my="md"),
        
        # Scenario Buttons
        dmc.Text("Mock 데이터 시나리오", size="xs", fw=600, c="dimmed", mb="xs"),
        dmc.Button("A. Full Lifecycle (R00→R60)", id="btn-scenario-a", variant="light", color="indigo", fullWidth=True, mb="xs", size="xs"),
        dmc.Button("B. R40 상세 (Post-Layout)", id="btn-scenario-b", variant="light", color="violet", fullWidth=True, mb="xs", size="xs"),
        dmc.Button("C. R30↔R40 Compare", id="btn-scenario-c", variant="light", color="grape", fullWidth=True, mb="xs", size="xs"),
        dmc.Button("Clear All", id="btn-clear", variant="outline", color="red", fullWidth=True, mt="md", size="xs"),
        
        dmc.Divider(my="md"),
        
        # Statistics
        html.Div(id="sidebar-stats"),
        
        dmc.Divider(my="md"),
        
        # Export
        dmc.Text("Export", size="xs", fw=600, c="dimmed", mb="xs"),
        dmc.Button("📥 JSON (GraphRAG)", id="btn-export-json", variant="light", color="blue", fullWidth=True, size="xs"),
        dcc.Download(id="download-json"),
        
    ], gap="xs", p="md", style={
        "height": "100vh", 
        "backgroundColor": "#e9ecef",
        "overflowY": "auto",
        "borderRight": "1px solid #ced4da"
    })


# --- Page: Schema Viewer ---
def create_schema_page():
    """3-Layer 구조와 13개 Object Type 시각화"""
    schemas = store.get_object_schema()
    
    def create_object_card(obj_type, info):
        return dmc.Card([
            dmc.Group([
                dmc.Text(info["icon"], size="xl"),
                dmc.Stack([
                    dmc.Text(obj_type, fw=700, size="sm"),
                    dmc.Text(info["description"], size="xs", c="dimmed", lineClamp=2),
                ], gap=2)
            ], gap="sm"),
            dmc.Divider(my="xs"),
            dmc.Text("Properties:", size="xs", fw=600, c="dimmed"),
            dmc.Group([
                dmc.Badge(prop, size="xs", variant="light") for prop in info["properties"][:5]
            ], gap=4),
        ], withBorder=True, shadow="sm", p="sm", radius="md", 
           style={"backgroundColor": info["color"] + "15", "borderLeft": f"4px solid {info['color']}"})
    
    semantic_objects = [k for k, v in schemas.items() if v["layer"] == "Semantic"]
    kinetic_objects = [k for k, v in schemas.items() if v["layer"] == "Kinetic"]
    dynamic_objects = [k for k, v in schemas.items() if v["layer"] == "Dynamic"]
    
    return dmc.Container([
        dmc.Title("📚 Signoff Ontology Schema", order=2, mb="md"),
        dmc.Text("3-Layer Architecture & 13 Object Types", c="dimmed", mb="xl"),
        
        # 3-Layer Diagram
        dmc.Card([
            dmc.Title("3-Layer Architecture", order=4, mb="md"),
            dmc.Stack([
                # Dynamic Layer
                dmc.Alert(
                    title="🎯 Dynamic Layer (동적 계층) - \"The Brains\"",
                    color="pink",
                    children=[
                        dmc.Text("결과에 대한 판단과 의사결정. AI 학습 대상 데이터", size="sm"),
                        dmc.Group([
                            dmc.Badge("CategorizePart", color="pink"),
                            dmc.Badge("CompareResult", color="pink"),
                            dmc.Badge("WaiverDecision", color="grape"),
                            dmc.Badge("SignoffIssue", color="grape"),
                        ], gap="xs", mt="sm")
                    ]
                ),
                # Kinetic Layer
                dmc.Alert(
                    title="⚡ Kinetic Layer (운동 계층) - \"The Verbs\"",
                    color="green",
                    children=[
                        dmc.Text("실행 이벤트와 결과. 상태가 변화하는 프로세스 데이터", size="sm"),
                        dmc.Group([
                            dmc.Badge("SignoffJob", color="green"),
                            dmc.Badge("Result", color="lime"),
                        ], gap="xs", mt="sm")
                    ]
                ),
                # Semantic Layer
                dmc.Alert(
                    title="📚 Semantic Layer (의미 계층) - \"The Nouns\"",
                    color="blue",
                    children=[
                        dmc.Text("정적 마스터 데이터. 거의 변하지 않는 기준 정보", size="sm"),
                        dmc.Group([
                            dmc.Badge("Product", color="blue"),
                            dmc.Badge("Revision", color="blue"),
                            dmc.Badge("Block", color="blue"),
                            dmc.Badge("Designer", color="yellow"),
                            dmc.Badge("SignoffApplication", color="orange"),
                            dmc.Badge("CriteriaSet", color="orange"),
                            dmc.Badge("Workspace", color="yellow"),
                        ], gap="xs", mt="sm")
                    ]
                ),
            ], gap="md"),
        ], withBorder=True, shadow="sm", p="lg", mb="xl"),
        
        # Object Type Cards
        dmc.Title("📦 Object Types (13개)", order=4, mb="md"),
        
        dmc.Text("Semantic Layer (7개)", fw=600, c="blue", mb="sm"),
        dmc.SimpleGrid([
            create_object_card(obj, schemas[obj]) for obj in semantic_objects
        ], cols=3, spacing="md", mb="xl"),
        
        dmc.Text("Kinetic Layer (2개)", fw=600, c="green", mb="sm"),
        dmc.SimpleGrid([
            create_object_card(obj, schemas[obj]) for obj in kinetic_objects
        ], cols=2, spacing="md", mb="xl"),
        
        dmc.Text("Dynamic Layer (4개)", fw=600, c="pink", mb="sm"),
        dmc.SimpleGrid([
            create_object_card(obj, schemas[obj]) for obj in dynamic_objects
        ], cols=2, spacing="md"),
        
    ], fluid=True, p="lg")


# --- Page: Builder ---
def create_builder_page():
    return dmc.Container([
        dmc.Title("🏗️ Ontology Builder", order=2, mb="md"),
        dmc.Text("13개 Object Type을 인터랙티브하게 생성합니다.", c="dimmed", mb="xl"),
        
        # Quick actions
        dmc.Alert(
            title="💡 빠른 시작",
            color="blue",
            children="왼쪽 사이드바에서 Mock 데이터 시나리오를 선택하면 자동으로 데이터가 생성됩니다.",
            mb="xl"
        ),
        
        dmc.Grid([
            # Column 1: Product, Revision, Block
            dmc.GridCol([
                dmc.Card([
                    dmc.Text("Product", fw=600),
                    dmc.TextInput(id="input-product-id", placeholder="Product ID (예: HBM4E)", mb="xs"),
                    dmc.TextInput(id="input-product-name", placeholder="Product Name", mb="xs"),
                    dmc.Button("➕ Add Product", id="btn-add-product", color="blue", fullWidth=True),
                ], withBorder=True, p="sm", mb="md"),
                
                dmc.Card([
                    dmc.Text("Revision", fw=600),
                    dmc.Select(id="select-revision-product", placeholder="Select Product", data=[], mb="xs"),
                    dmc.Select(id="select-revision-phase", placeholder="Phase", 
                               data=["R00", "R10", "R20", "R30", "R40", "R50", "R60"], mb="xs"),
                    dmc.Button("➕ Add Revision", id="btn-add-revision", color="blue", fullWidth=True),
                ], withBorder=True, p="sm", mb="md"),
                
                dmc.Card([
                    dmc.Text("Block", fw=600),
                    dmc.Select(id="select-block-revision", placeholder="Select Revision", data=[], mb="xs"),
                    dmc.TextInput(id="input-block-name", placeholder="Block Name", mb="xs"),
                    dmc.Button("➕ Add Block", id="btn-add-block", color="blue", fullWidth=True),
                ], withBorder=True, p="sm"),
            ], span=4),
            
            # Column 2: Application, Designer, CriteriaSet
            dmc.GridCol([
                dmc.Card([
                    dmc.Text("SignoffApplication", fw=600),
                    dmc.Select(id="select-app-preset", placeholder="Preset Application",
                               data=[a["app_id"] for a in store.APPLICATIONS], mb="xs"),
                    dmc.Button("➕ Add Application", id="btn-add-app", color="teal", fullWidth=True),
                ], withBorder=True, p="sm", mb="md"),
                
                dmc.Card([
                    dmc.Text("Designer", fw=600),
                    dmc.TextInput(id="input-designer-id", placeholder="Designer ID", mb="xs"),
                    dmc.TextInput(id="input-designer-name", placeholder="Name", mb="xs"),
                    dmc.Select(id="select-designer-role", placeholder="Role",
                               data=["DESIGNER", "LEAD", "DEVELOPER", "MANAGER"], mb="xs"),
                    dmc.Button("➕ Add Designer", id="btn-add-designer", color="yellow", fullWidth=True),
                ], withBorder=True, p="sm", mb="md"),
                
                dmc.Card([
                    dmc.Text("CriteriaSet", fw=600),
                    dmc.Select(id="select-criteria-app", placeholder="Select Application", data=[], mb="xs"),
                    dmc.TextInput(id="input-criteria-name", placeholder="Criteria Name", mb="xs"),
                    dmc.Button("➕ Add Criteria", id="btn-add-criteria", color="orange", fullWidth=True),
                ], withBorder=True, p="sm"),
            ], span=4),
            
            # Column 3: SignoffJob, Result
            dmc.GridCol([
                dmc.Card([
                    dmc.Text("SignoffJob", fw=600),
                    dmc.Select(id="select-job-block", placeholder="Select Block", data=[], mb="xs"),
                    dmc.Select(id="select-job-app", placeholder="Select Application", data=[], mb="xs"),
                    dmc.Select(id="select-job-pvt", placeholder="PVT Corner",
                               data=[p["name"] for p in store.PVT_CORNERS], mb="xs"),
                    dmc.Button("⚡ Execute Job", id="btn-add-job", color="green", fullWidth=True),
                ], withBorder=True, p="sm", mb="md"),
                
                dmc.Card([
                    dmc.Text("Result", fw=600),
                    dmc.Select(id="select-result-job", placeholder="Select Job", data=[], mb="xs"),
                    dmc.NumberInput(id="input-result-rows", placeholder="Total Rows", value=100000, mb="xs"),
                    dmc.NumberInput(id="input-result-waiver", placeholder="Waiver Count", value=0, mb="xs"),
                    dmc.NumberInput(id="input-result-fixed", placeholder="Fixed Count", value=0, mb="xs"),
                    dmc.Button("📊 Add Result", id="btn-add-result", color="red", fullWidth=True),
                ], withBorder=True, p="sm"),
            ], span=4),
        ]),
        
    ], fluid=True, p="lg")


# --- Page: Graph ---
def create_graph_page():
    return dmc.Container([
        dmc.Title("🗺️ Ontology Knowledge Graph", order=2, mb="md"),
        dmc.Text("13개 Object Type과 관계를 시각화합니다.", c="dimmed", mb="lg"),
        
        dmc.Grid([
            dmc.GridCol([
                dmc.Group([
                    dmc.Text("Layout", size="sm", fw=500),
                    dmc.Select(id="graph-layout", value="breadthfirst",
                               data=[
                                   {"value": "breadthfirst", "label": "Hierarchical"},
                                   {"value": "cose", "label": "Force-directed"},
                                   {"value": "circle", "label": "Circle"},
                                   {"value": "grid", "label": "Grid"},
                               ], w=150),
                ], gap="sm"),
            ], span=3),
            dmc.GridCol([
                dmc.Text("Object Types", size="sm", fw=500),
                dmc.MultiSelect(
                    id="graph-type-filter",
                    data=[
                        {"value": "Product", "label": "📦 Product"},
                        {"value": "Revision", "label": "📋 Revision"},
                        {"value": "Block", "label": "🔲 Block"},
                        {"value": "Designer", "label": "👤 Designer"},
                        {"value": "SignoffApplication", "label": "🔧 Application"},
                        {"value": "CriteriaSet", "label": "📏 Criteria"},
                        {"value": "SignoffJob", "label": "⚡ Job"},
                        {"value": "Result", "label": "📊 Result"},
                        {"value": "CompareResult", "label": "🔄 Compare"},
                    ],
                    value=["Product", "Revision", "Block", "SignoffApplication", "SignoffJob", "Result"],
                    clearable=True,
                ),
            ], span=9),
        ], mb="md"),
        
        dmc.Grid([
            dmc.GridCol([
                cyto.Cytoscape(
                    id="ontology-graph",
                    elements=[],
                    stylesheet=graph_stylesheet,
                    style={"width": "100%", "height": "550px", "border": "1px solid #dee2e6", "borderRadius": "8px"},
                    layout={"name": "breadthfirst", "rankDir": "TB"},
                ),
            ], span=8),
            dmc.GridCol([
                dmc.Card([
                    dmc.Title("Node Details", order=4, mb="md"),
                    html.Div(id="node-detail", children=[
                        dmc.Text("Click a node to see details", c="dimmed")
                    ])
                ], withBorder=True, p="md", h="100%"),
            ], span=4),
        ]),
        
    ], fluid=True, p="lg")


# --- Page: Dashboard ---
def create_dashboard_page():
    return dmc.Container([
        dmc.Title("📊 Signoff Dashboard", order=2, mb="md"),
        dmc.Text("Revision별 Signoff 진행률 및 WAIVER/FIXED/PENDING 현황", c="dimmed", mb="lg"),
        
        # KPI Cards
        html.Div(id="dashboard-kpi"),
        
        dmc.Divider(my="xl"),
        
        # Revision Progress Table
        dmc.Title("Revision별 진행률", order=4, mb="md"),
        html.Div(id="dashboard-revision-table"),
        
        dmc.Divider(my="xl"),
        
        # Application Stats
        dmc.Title("Application별 현황", order=4, mb="md"),
        html.Div(id="dashboard-app-stats"),
        
    ], fluid=True, p="lg")


# --- Page: Compare ---
def create_compare_page():
    return dmc.Container([
        dmc.Title("🔄 Revision Compare & Waiver Migration", order=2, mb="md"),
        dmc.Text("Revision 간 비교 결과 및 Waiver 자동 이관 시뮬레이션", c="dimmed", mb="lg"),
        
        # Compare Results
        html.Div(id="compare-results"),
        
    ], fluid=True, p="lg")


# --- App Layout ---
app.layout = dmc.MantineProvider(
    forceColorScheme="light",
    theme={"primaryColor": "blue", "fontFamily": "'Pretendard', 'Inter', sans-serif"},
    children=[
        dcc.Location(id="url"),
        dcc.Store(id="builder-trigger", data=0),
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
    if pathname == "/schema":
        return create_schema_page()
    elif pathname == "/graph":
        return create_graph_page()
    elif pathname == "/dashboard":
        return create_dashboard_page()
    elif pathname == "/compare":
        return create_compare_page()
    else:
        return create_builder_page()


# --- NavLink Active State ---
@callback(
    Output("nav-schema", "active"),
    Output("nav-builder", "active"),
    Output("nav-graph", "active"),
    Output("nav-dashboard", "active"),
    Output("nav-compare", "active"),
    Input("url", "pathname")
)
def update_nav_active(pathname):
    return (
        pathname == "/schema",
        pathname == "/" or pathname == "",
        pathname == "/graph",
        pathname == "/dashboard",
        pathname == "/compare"
    )


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
        store.load_template("r40_detail")
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
        dmc.Text(f"📦 Products: {stats['products']}", size="xs"),
        dmc.Text(f"📋 Revisions: {stats['revisions']}", size="xs"),
        dmc.Text(f"🔲 Blocks: {stats['blocks']}", size="xs"),
        dmc.Text(f"⚡ Jobs: {stats['jobs']}", size="xs"),
        dmc.Text(f"📊 Results: {stats['results']}", size="xs"),
        dmc.Divider(my="xs"),
        dmc.Text(f"🟢 WAIVER: {stats['waiver_count']:,}", size="xs", c="green"),
        dmc.Text(f"🔵 FIXED: {stats['fixed_count']:,}", size="xs", c="blue"),
        dmc.Text(f"🟠 PENDING: {stats['pending_count']:,}", size="xs", c="orange"),
        dmc.Progress(value=stats['progress_pct'], color="green", size="sm", mt="xs"),
        dmc.Text(f"{stats['progress_pct']}% Complete", size="xs", ta="center"),
    ], gap=2)


# --- Builder Dropdowns ---
@callback(
    Output("select-revision-product", "data"),
    Output("select-block-revision", "data"),
    Output("select-criteria-app", "data"),
    Output("select-job-block", "data"),
    Output("select-job-app", "data"),
    Output("select-result-job", "data"),
    Input("builder-trigger", "data"),
    Input("url", "pathname")
)
def update_builder_dropdowns(trigger, pathname):
    products = [p["product_id"] for p in store.products]
    revisions = [r["revision_id"] for r in store.revisions]
    blocks = [b["block_id"] for b in store.blocks]
    apps = [a["app_id"] for a in store.signoff_applications]
    jobs = [j["job_id"] for j in store.signoff_jobs if j["status"] == "DONE"]
    return products, revisions, apps, blocks, apps, jobs


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
        store.add_product(pid, pname)
    return (trigger or 0) + 1


# --- Builder: Add Revision ---
@callback(
    Output("builder-trigger", "data", allow_duplicate=True),
    Input("btn-add-revision", "n_clicks"),
    State("select-revision-product", "value"),
    State("select-revision-phase", "value"),
    State("builder-trigger", "data"),
    prevent_initial_call=True
)
def add_revision(n, product_id, phase, trigger):
    if n and product_id and phase:
        rev_id = f"{product_id}_{phase}"
        store.add_revision(rev_id, product_id, phase)
    return (trigger or 0) + 1


# --- Builder: Add Block ---
@callback(
    Output("builder-trigger", "data", allow_duplicate=True),
    Input("btn-add-block", "n_clicks"),
    State("select-block-revision", "value"),
    State("input-block-name", "value"),
    State("builder-trigger", "data"),
    prevent_initial_call=True
)
def add_block(n, rev_id, block_name, trigger):
    if n and rev_id and block_name:
        block_id = f"{rev_id}_{block_name}"
        store.add_block(block_id, rev_id, block_name)
    return (trigger or 0) + 1


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
        app_info = next((a for a in store.APPLICATIONS if a["app_id"] == app_id), None)
        if app_info:
            store.add_signoff_application(app_info["app_id"], app_info["app_name"], 
                                          app_info["app_group"], app_info["engine_type"])
    return (trigger or 0) + 1


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
        store.add_designer(did, dname, role=drole or "DESIGNER")
    return (trigger or 0) + 1


# --- Builder: Add Job ---
@callback(
    Output("builder-trigger", "data", allow_duplicate=True),
    Input("btn-add-job", "n_clicks"),
    State("select-job-block", "value"),
    State("select-job-app", "value"),
    State("select-job-pvt", "value"),
    State("builder-trigger", "data"),
    prevent_initial_call=True
)
def add_job(n, block_id, app_id, pvt, trigger):
    if n and block_id and app_id:
        job_id = f"JOB-{block_id}-{app_id}"
        block = next((b for b in store.blocks if b["block_id"] == block_id), None)
        if block:
            store.add_signoff_job(job_id, block["revision_id"], block_id, app_id, 
                                  pvt_corner=pvt or "SSPLVCT", status="DONE")
    return (trigger or 0) + 1


# --- Builder: Add Result ---
@callback(
    Output("builder-trigger", "data", allow_duplicate=True),
    Input("btn-add-result", "n_clicks"),
    State("select-result-job", "value"),
    State("input-result-rows", "value"),
    State("input-result-waiver", "value"),
    State("input-result-fixed", "value"),
    State("builder-trigger", "data"),
    prevent_initial_call=True
)
def add_result(n, job_id, total, waiver, fixed, trigger):
    if n and job_id:
        result_id = f"RESULT-{job_id}"
        store.add_result(result_id, job_id, total or 1000, 
                         waiver_count=waiver or 0, fixed_count=fixed or 0)
    return (trigger or 0) + 1


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
    if pathname != "/graph":
        return [], {"name": layout or "breadthfirst"}
    
    elements = store.to_graph_elements()
    
    if type_filter:
        filtered = []
        node_ids = set()
        for el in elements:
            if "source" not in el.get("data", {}):
                if el.get("data", {}).get("type") in type_filter:
                    filtered.append(el)
                    node_ids.add(el["data"]["id"])
        for el in elements:
            if "source" in el.get("data", {}):
                if el["data"]["source"] in node_ids and el["data"]["target"] in node_ids:
                    filtered.append(el)
        elements = filtered
    
    return elements, {"name": layout or "breadthfirst", "rankDir": "TB", "spacingFactor": 1.2}


# --- Graph Node Click ---
@callback(
    Output("node-detail", "children"),
    Input("ontology-graph", "tapNodeData"),
)
def show_node_detail(node_data):
    if not node_data:
        return dmc.Text("Click a node to see details", c="dimmed")
    
    obj_type = node_data.get("type", "Unknown")
    obj_id = node_data.get("id", "")
    
    all_objects = store.get_all_objects()
    obj_list = all_objects.get(obj_type, [])
    
    obj = None
    for o in obj_list:
        id_field = list(o.keys())[0] if o else None
        if o.get(id_field) == obj_id or o.get("product_id") == obj_id or o.get("revision_id") == obj_id or o.get("block_id") == obj_id or o.get("job_id") == obj_id or o.get("result_id") == obj_id or o.get("designer_id") == obj_id or o.get("app_id") == obj_id:
            obj = o
            break
    
    if not obj:
        return dmc.Stack([
            dmc.Badge(obj_type, color=store.COLORS.get(obj_type, "gray"), size="lg"),
            dmc.Text(f"ID: {obj_id}", fw=600),
        ])
    
    return dmc.Stack([
        dmc.Badge(obj_type, color=store.COLORS.get(obj_type, "gray"), size="lg"),
        dmc.Text(f"ID: {obj_id}", fw=600),
        dmc.Divider(my="sm"),
        dmc.Stack([
            dmc.Group([
                dmc.Text(f"{k}:", size="xs", fw=500, c="dimmed"),
                dmc.Text(str(v)[:50], size="xs")
            ]) for k, v in list(obj.items())[:10]
        ], gap=4)
    ])


# --- Dashboard KPI ---
@callback(
    Output("dashboard-kpi", "children"),
    Input("builder-trigger", "data"),
    Input("url", "pathname")
)
def update_dashboard_kpi(trigger, pathname):
    if pathname != "/dashboard":
        return []
    
    stats = store.get_statistics()
    
    return dmc.SimpleGrid([
        dmc.Card([
            dmc.Text("Total Rows", size="sm", c="dimmed"),
            dmc.Title(f"{stats['total_rows']:,}", order=2, c="blue"),
        ], withBorder=True, p="md"),
        dmc.Card([
            dmc.Text("WAIVER", size="sm", c="dimmed"),
            dmc.Title(f"{stats['waiver_count']:,}", order=2, c="green"),
        ], withBorder=True, p="md"),
        dmc.Card([
            dmc.Text("FIXED", size="sm", c="dimmed"),
            dmc.Title(f"{stats['fixed_count']:,}", order=2, c="blue"),
        ], withBorder=True, p="md"),
        dmc.Card([
            dmc.Text("PENDING", size="sm", c="dimmed"),
            dmc.Title(f"{stats['pending_count']:,}", order=2, c="orange"),
        ], withBorder=True, p="md"),
        dmc.Card([
            dmc.Text("Progress", size="sm", c="dimmed"),
            dmc.Title(f"{stats['progress_pct']}%", order=2, c="green"),
            dmc.Progress(value=stats['progress_pct'], color="green", size="lg", mt="sm"),
        ], withBorder=True, p="md"),
    ], cols=5, spacing="md")


# --- Dashboard Revision Table ---
@callback(
    Output("dashboard-revision-table", "children"),
    Input("builder-trigger", "data"),
    Input("url", "pathname")
)
def update_revision_table(trigger, pathname):
    if pathname != "/dashboard":
        return []
    
    progress_data = store.get_revision_progress()
    
    if not progress_data:
        return dmc.Text("No revision data available", c="dimmed")
    
    def get_status_badge(status):
        color_map = {"COMPLETED": "green", "IN_PROGRESS": "blue", "NOT_STARTED": "gray"}
        return dmc.Badge(status, color=color_map.get(status, "gray"), size="sm")
    
    rows = []
    for p in progress_data:
        rows.append(html.Tr([
            html.Td(p["revision_code"]),
            html.Td(get_status_badge(p["status"])),
            html.Td(f"{p['total_jobs']}"),
            html.Td(f"{p['done_jobs']}"),
            html.Td(f"{p['total_rows']:,}"),
            html.Td(f"{p['waiver_count']:,}"),
            html.Td(f"{p['fixed_count']:,}"),
            html.Td(f"{p['pending_count']:,}"),
            html.Td([
                dmc.Progress(value=p['progress_pct'], color="green", size="md", w=100)
            ]),
        ]))
    
    return dmc.Table([
        html.Thead(html.Tr([
            html.Th("Revision"),
            html.Th("Status"),
            html.Th("Tasks"),
            html.Th("Jobs"),
            html.Th("Total"),
            html.Th("WAIVER"),
            html.Th("FIXED"),
            html.Th("PENDING"),
            html.Th("Progress"),
        ])),
        html.Tbody(rows)
    ], striped=True, highlightOnHover=True)


# --- Dashboard App Stats ---
@callback(
    Output("dashboard-app-stats", "children"),
    Input("builder-trigger", "data"),
    Input("url", "pathname")
)
def update_app_stats(trigger, pathname):
    if pathname != "/dashboard":
        return []
    
    app_stats = store.get_application_stats()
    
    if not app_stats:
        return dmc.Text("No application data available", c="dimmed")
    
    return dmc.SimpleGrid([
        dmc.Card([
            dmc.Text(stat["app_id"], fw=600),
            dmc.Text(stat["app_name"], size="xs", c="dimmed"),
            dmc.Divider(my="xs"),
            dmc.Text(f"Jobs: {stat['job_count']}", size="sm"),
            dmc.Text(f"Total: {stat['total_rows']:,}", size="sm"),
        ], withBorder=True, p="sm")
        for stat in app_stats[:6]
    ], cols=6, spacing="md")


# --- Compare Page ---
@callback(
    Output("compare-results", "children"),
    Input("builder-trigger", "data"),
    Input("url", "pathname")
)
def update_compare(trigger, pathname):
    if pathname != "/compare":
        return []
    
    compares = store.compare_results
    
    if not compares:
        return dmc.Alert(
            title="비교 데이터 없음",
            color="yellow",
            children="'C. R30↔R40 Compare' 시나리오를 선택하면 비교 결과가 표시됩니다."
        )
    
    cards = []
    for cmp in compares:
        cards.append(dmc.Card([
            dmc.Text(cmp["compare_id"], fw=600),
            dmc.Text(f"{cmp['source_result_id']} → {cmp['target_result_id']}", size="xs", c="dimmed"),
            dmc.Divider(my="sm"),
            dmc.SimpleGrid([
                dmc.Stack([
                    dmc.Text("New Fail", size="xs", c="dimmed"),
                    dmc.Text(f"{cmp['new_fail_count']:,}", fw=600, c="red"),
                ], gap=0),
                dmc.Stack([
                    dmc.Text("Fixed", size="xs", c="dimmed"),
                    dmc.Text(f"{cmp['fixed_count']:,}", fw=600, c="green"),
                ], gap=0),
                dmc.Stack([
                    dmc.Text("Regressed", size="xs", c="dimmed"),
                    dmc.Text(f"{cmp['regressed_count']:,}", fw=600, c="orange"),
                ], gap=0),
                dmc.Stack([
                    dmc.Text("Unchanged", size="xs", c="dimmed"),
                    dmc.Text(f"{cmp['unchanged_fail_count']:,}", fw=600, c="blue"),
                ], gap=0),
            ], cols=4, spacing="md"),
            dmc.Divider(my="sm"),
            dmc.Group([
                dmc.Badge(f"Waiver Migrated: {cmp['waiver_migrated_count']:,}", color="green", size="lg"),
            ]),
        ], withBorder=True, p="md", mb="md"))
    
    return dmc.Stack(cards)


# --- Export JSON ---
@callback(
    Output("download-json", "data"),
    Input("btn-export-json", "n_clicks"),
    prevent_initial_call=True
)
def export_json(n):
    if n:
        data = store.to_json_graphrag()
        return dict(content=json.dumps(data, indent=2, ensure_ascii=False), 
                    filename=f"signoff_ontology_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    return None


# --- Run ---
if __name__ == "__main__":
    # 기본 데이터 로드
    store.load_template("full_lifecycle")
    app.run(debug=True)
