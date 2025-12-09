"""
Signoff Ontology POC - Enhanced Interactive Builder
"""
import dash
from dash import dcc, html, Input, Output, State, callback, ALL
import dash_mantine_components as dmc
import dash_cytoscape as cyto
import pandas as pd
import json

from utils.ontology_store import store

# --- App Setup ---
app = dash.Dash(__name__, external_stylesheets=dmc.styles.ALL, suppress_callback_exceptions=True)
app.title = "Signoff Ontology POC"

# --- Stylesheet ---
graph_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)',
            'color': 'white',
            'background-color': 'data(color)',
            'text-valign': 'center',
            'text-halign': 'center',
            'width': '100px',
            'height': '40px',
            'shape': 'round-rectangle',
            'font-family': 'Pretendard, sans-serif',
            'font-size': '11px',
            'border-width': 2,
            'border-color': '#fff'
        }
    },
    {
        'selector': 'edge',
        'style': {
            'label': 'data(label)',
            'color': '#adb5bd',
            'line-color': '#ced4da',
            'target-arrow-color': '#ced4da',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'font-size': '9px',
            'width': 1.5
        }
    },
    {
        'selector': ':selected',
        'style': {
            'border-width': 4,
            'border-color': '#fab005'
        }
    },
    {
        'selector': '.highlighted',
        'style': {
            'border-width': 4,
            'border-color': '#ff6b6b',
            'background-color': '#ff8787'
        }
    }
]

# --- Sidebar ---
def create_sidebar():
    return dmc.Stack([
        dmc.Group([
            dmc.Text("🧠", size="xl"),
            dmc.Text("Signoff Ontology", size="lg", fw=700)
        ], mb=10),
        dmc.Text("POC Demo App", size="xs", c="dimmed", mb=15),
        dmc.Divider(mb=10),
        
        dmc.NavLink(label="온톨로지 빌더", leftSection="🔧", href="/", id="nav-builder"),
        dmc.NavLink(label="온톨로지 맵", leftSection="🗺️", href="/map", id="nav-map"),
        dmc.NavLink(label="데이터 탐색기", leftSection="📊", href="/explorer", id="nav-explorer"),
        dmc.NavLink(label="검색", leftSection="🔍", href="/search", id="nav-search"),
        
        dmc.Divider(my=15),
        dmc.Text("샘플 데이터", size="sm", c="dimmed", mb=5),
        dmc.SegmentedControl(
            id="template-level",
            value="medium",
            data=[
                {"value": "simple", "label": "Simple"},
                {"value": "medium", "label": "Medium"},
                {"value": "complex", "label": "Complex"},
            ],
            fullWidth=True,
            size="xs",
            mb=10
        ),
        dmc.Button("샘플 데이터 로드", id="btn-load-template", variant="light", color="blue", fullWidth=True, mb=5),
        dmc.Button("전체 삭제", id="btn-clear-all", variant="outline", color="red", fullWidth=True, size="xs"),
        
        dmc.Divider(my=15),
        html.Div(id="sidebar-stats")
    ], h="100%", p="md")

# --- Builder Page ---
def create_builder_page():
    return dmc.Stack([
        dmc.Title("온톨로지 빌더", order=2, mb="sm"),
        dmc.Text("Signoff 온톨로지 객체를 직접 생성하고 연결합니다.", c="dimmed", mb="md"),
        
        dmc.Grid([
            dmc.GridCol([
                dmc.Accordion([
                    dmc.AccordionItem([
                        dmc.AccordionControl("1️⃣ Product (제품)"),
                        dmc.AccordionPanel([
                            dmc.TextInput(label="제품 이름", placeholder="예: HBM4E", id="input-product-name"),
                            dmc.Button("생성", id="btn-add-product", color="blue", mt="sm", fullWidth=True)
                        ])
                    ], value="product"),
                    
                    dmc.AccordionItem([
                        dmc.AccordionControl("2️⃣ Revision (버전)"),
                        dmc.AccordionPanel([
                            dmc.Select(label="Product 선택", id="select-product-for-rev", data=[]),
                            dmc.TextInput(label="버전 이름", placeholder="예: R30", id="input-revision-name", mt="sm"),
                            dmc.Button("생성", id="btn-add-revision", color="blue", mt="sm", fullWidth=True)
                        ])
                    ], value="revision"),
                    
                    dmc.AccordionItem([
                        dmc.AccordionControl("3️⃣ Block (설계 블록)"),
                        dmc.AccordionPanel([
                            dmc.Select(label="Revision 선택", id="select-revision-for-block", data=[]),
                            dmc.TextInput(label="블록 이름", placeholder="예: FULLCHIP_NO_CORE, PAD", id="input-block-name", mt="sm"),
                            dmc.Button("생성", id="btn-add-block", color="blue", mt="sm", fullWidth=True)
                        ])
                    ], value="block"),
                    
                    dmc.AccordionItem([
                        dmc.AccordionControl("4️⃣ Designer & App"),
                        dmc.AccordionPanel([
                            dmc.Grid([
                                dmc.GridCol([
                                    dmc.TextInput(label="담당자", placeholder="예: 최원우", id="input-designer-name"),
                                    dmc.Button("등록", id="btn-add-designer", color="violet", mt="sm", size="sm", fullWidth=True)
                                ], span=6),
                                dmc.GridCol([
                                    dmc.TextInput(label="검증 도구", placeholder="예: DSC", id="input-app-name"),
                                    dmc.Button("등록", id="btn-add-app", color="teal", mt="sm", size="sm", fullWidth=True)
                                ], span=6),
                            ])
                        ])
                    ], value="designer-app"),
                    
                    dmc.AccordionItem([
                        dmc.AccordionControl("5️⃣ Task (검증 작업)"),
                        dmc.AccordionPanel([
                            dmc.Select(label="Block", id="select-block-for-task", data=[]),
                            dmc.Select(label="App", id="select-app-for-task", data=[], mt="sm"),
                            dmc.Select(label="담당자", id="select-designer-for-task", data=[], mt="sm", placeholder="(선택)"),
                            dmc.Button("Task 생성", id="btn-add-task", color="green", mt="sm", fullWidth=True)
                        ])
                    ], value="task"),
                    
                    dmc.AccordionItem([
                        dmc.AccordionControl("6️⃣ Job & Result"),
                        dmc.AccordionPanel([
                            dmc.Select(label="Task", id="select-task-for-job", data=[]),
                            dmc.Button("Job 실행", id="btn-add-job", color="orange", mt="sm", fullWidth=True),
                            dmc.Divider(my="sm"),
                            dmc.Select(label="완료할 Job", id="select-job-for-result", data=[]),
                            dmc.Group([
                                dmc.NumberInput(label="Violation", id="input-violation-count", value=0, min=0, w=100),
                                dmc.NumberInput(label="Waiver", id="input-waiver-count", value=0, min=0, w=100),
                            ]),
                            dmc.Button("Result 생성", id="btn-add-result", color="orange", mt="sm", fullWidth=True),
                        ])
                    ], value="job-result"),
                ], value="product", chevronPosition="right", variant="separated")
            ], span=5),
            
            dmc.GridCol([
                dmc.Paper([
                    dmc.Title("실시간 미리보기", order=4, mb="sm"),
                    cyto.Cytoscape(
                        id='builder-graph',
                        layout={'name': 'cose', 'animate': True, 'nodeRepulsion': 8000},
                        style={'width': '100%', 'height': '550px'},
                        elements=[],
                        stylesheet=graph_stylesheet
                    )
                ], p="md", withBorder=True, shadow="sm")
            ], span=7),
        ]),
        
        html.Div(id="notification-area")
    ])

# --- Map Page ---
def create_map_page():
    return dmc.Stack([
        dmc.Group([
            dmc.Title("온톨로지 맵", order=2),
            dmc.Badge("전체 구조 시각화", color="blue", variant="light")
        ], justify="space-between", mb="md"),
        
        # Controls
        dmc.Paper([
            dmc.Grid([
                dmc.GridCol([
                    dmc.Select(
                        label="레이아웃",
                        id="map-layout-select",
                        value="layered",
                        data=[
                            {"value": "layered", "label": "📊 계층형 (Layered)"},
                            {"value": "cose", "label": "🔄 자동 배치 (CoSE)"},
                            {"value": "breadthfirst", "label": "🌳 트리형 (Breadthfirst)"},
                            {"value": "circle", "label": "⭕ 원형 (Circle)"},
                            {"value": "grid", "label": "📐 격자형 (Grid)"},
                        ]
                    )
                ], span=2),
                dmc.GridCol([
                    dmc.Select(
                        label="객체 유형 필터",
                        id="map-type-filter",
                        placeholder="전체",
                        data=store.get_type_options(),
                        clearable=True
                    )
                ], span=2),
                dmc.GridCol([
                    dmc.Select(
                        label="Product 필터",
                        id="map-product-filter",
                        placeholder="전체",
                        data=store.get_product_options(),
                        clearable=True
                    )
                ], span=2),
                dmc.GridCol([
                    dmc.Select(
                        label="상태 필터",
                        id="map-status-filter",
                        placeholder="전체",
                        data=[
                            {"value": "대기중", "label": "대기중"},
                            {"value": "실행중", "label": "실행중"},
                            {"value": "완료", "label": "완료"},
                        ],
                        clearable=True
                    )
                ], span=2),
                dmc.GridCol([
                    # Legend
                    dmc.Group([
                        dmc.Badge("Product", color="blue", size="xs"),
                        dmc.Badge("Block", color="indigo", size="xs"),
                        dmc.Badge("Task", color="teal", size="xs"),
                        dmc.Badge("Result", color="orange", size="xs"),
                    ], gap="xs", mt=25)
                ], span=4),
            ])
        ], p="sm", withBorder=True, mb="md"),
        
        dmc.Grid([
            dmc.GridCol([
                dmc.Paper([
                    cyto.Cytoscape(
                        id='map-graph',
                        layout={'name': 'preset'},
                        style={'width': '100%', 'height': '650px'},
                        elements=[],
                        stylesheet=graph_stylesheet
                    )
                ], p="md", withBorder=True, shadow="sm")
            ], span=9),
            
            dmc.GridCol([
                dmc.Paper([
                    dmc.Title("노드 상세", order=4, mb="md"),
                    html.Div(id="map-node-details", children=dmc.Text("노드를 클릭하세요", c="dimmed"))
                ], p="md", withBorder=True),
                
                dmc.Paper([
                    dmc.Title("연결된 객체", order=5, mb="sm"),
                    html.Div(id="map-related-objects")
                ], p="md", withBorder=True, mt="md")
            ], span=3)
        ])
    ])

# --- Explorer Page ---
def create_explorer_page():
    return dmc.Stack([
        dmc.Group([
            dmc.Title("데이터 탐색기", order=2),
            dmc.Button("CSV 내보내기", id="btn-export-csv", variant="light", size="xs")
        ], justify="space-between", mb="md"),
        
        # Stats Cards
        html.Div(id="explorer-stats"),
        
        dmc.Divider(my="md"),
        
        html.Div(id="explorer-content")
    ])

# --- Search Page ---
def create_search_page():
    return dmc.Stack([
        dmc.Title("온톨로지 검색", order=2, mb="md"),
        dmc.Text("키워드로 온톨로지 객체를 검색합니다.", c="dimmed", mb="lg"),
        
        dmc.Grid([
            dmc.GridCol([
                dmc.Paper([
                    dmc.TextInput(
                        label="검색어",
                        placeholder="예: FULLCHIP, 최원우, R30...",
                        id="search-input",
                        size="md"
                    ),
                    dmc.Select(
                        label="객체 유형 필터",
                        id="search-type-filter",
                        placeholder="전체",
                        data=store.get_type_options(),
                        clearable=True,
                        mt="sm"
                    ),
                    dmc.Button("검색", id="btn-search", color="blue", mt="md", fullWidth=True)
                ], p="md", withBorder=True)
            ], span=3),
            
            dmc.GridCol([
                dmc.Paper([
                    dmc.Title("검색 결과", order=4, mb="md"),
                    html.Div(id="search-results")
                ], p="md", withBorder=True, mih=400)
            ], span=9)
        ])
    ])

# --- App Layout ---
app.layout = dmc.MantineProvider(
    forceColorScheme="light",
    theme={"primaryColor": "blue", "fontFamily": "'Pretendard', 'Inter', sans-serif"},
    children=[
        dcc.Location(id="url"),
        dcc.Store(id="store-trigger", data=0),
        dcc.Download(id="download-csv"),
        dmc.Grid([
            dmc.GridCol(create_sidebar(), span=2, style={"minHeight": "100vh", "backgroundColor": "#f8f9fa", "borderRight": "1px solid #dee2e6"}),
            dmc.GridCol(dmc.Container(id="page-content", p="xl", fluid=True), span=10)
        ], gutter=0)
    ]
)

# === CALLBACKS ===

# Page Routing
@app.callback(
    [Output("page-content", "children"),
     Output("nav-builder", "active"), Output("nav-map", "active"), 
     Output("nav-explorer", "active"), Output("nav-search", "active")],
    Input("url", "pathname")
)
def render_page(pathname):
    if pathname == "/map":
        return create_map_page(), False, True, False, False
    elif pathname == "/explorer":
        return create_explorer_page(), False, False, True, False
    elif pathname == "/search":
        return create_search_page(), False, False, False, True
    return create_builder_page(), True, False, False, False

# Template & Clear
@app.callback(
    Output("store-trigger", "data", allow_duplicate=True),
    [Input("btn-load-template", "n_clicks"), Input("btn-clear-all", "n_clicks")],
    State("template-level", "value"),
    State("store-trigger", "data"),
    prevent_initial_call=True
)
def handle_template_buttons(n_load, n_clear, level, trigger):
    ctx = dash.callback_context
    if not ctx.triggered:
        return trigger
    
    btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if btn_id == "btn-load-template":
        store.load_template(level)
    elif btn_id == "btn-clear-all":
        store.clear_all()
    
    return trigger + 1

# Sidebar Stats
@app.callback(
    Output("sidebar-stats", "children"),
    Input("store-trigger", "data")
)
def update_sidebar_stats(trigger):
    stats = store.get_statistics()
    return dmc.Stack([
        dmc.Text("통계", size="sm", fw=500),
        dmc.SimpleGrid([
            dmc.Paper([
                dmc.Text(str(stats.get("Task", 0)), size="lg", fw=700, ta="center"),
                dmc.Text("Task", size="xs", c="dimmed", ta="center")
            ], p="xs", withBorder=True),
            dmc.Paper([
                dmc.Text(str(stats.get("완료", 0)), size="lg", fw=700, ta="center", c="green"),
                dmc.Text("완료", size="xs", c="dimmed", ta="center")
            ], p="xs", withBorder=True),
        ], cols=2, spacing="xs")
    ], gap="xs")

# === Builder Callbacks ===

@app.callback(
    [Output("store-trigger", "data", allow_duplicate=True), Output("notification-area", "children", allow_duplicate=True)],
    Input("btn-add-product", "n_clicks"),
    [State("input-product-name", "value"), State("store-trigger", "data")],
    prevent_initial_call=True
)
def add_product(n_clicks, name, trigger):
    if not name:
        return trigger, dmc.Alert("제품 이름을 입력하세요", color="yellow", withCloseButton=True)
    result = store.add_product(name)
    if result:
        return trigger + 1, dmc.Alert(f"✅ Product '{name}' 생성 완료", color="green", withCloseButton=True)
    return trigger, dmc.Alert(f"⚠️ '{name}'이(가) 이미 존재합니다", color="orange", withCloseButton=True)

@app.callback(
    [Output("store-trigger", "data", allow_duplicate=True), Output("notification-area", "children", allow_duplicate=True)],
    Input("btn-add-revision", "n_clicks"),
    [State("select-product-for-rev", "value"), State("input-revision-name", "value"), State("store-trigger", "data")],
    prevent_initial_call=True
)
def add_revision(n_clicks, product_id, name, trigger):
    if not product_id or not name:
        return trigger, dmc.Alert("Product와 버전 이름을 입력하세요", color="yellow", withCloseButton=True)
    result = store.add_revision(product_id, name)
    if result:
        return trigger + 1, dmc.Alert(f"✅ Revision '{name}' 생성", color="green", withCloseButton=True)
    return trigger, dmc.Alert("⚠️ 이미 존재하거나 오류", color="orange", withCloseButton=True)

@app.callback(
    [Output("store-trigger", "data", allow_duplicate=True), Output("notification-area", "children", allow_duplicate=True)],
    Input("btn-add-block", "n_clicks"),
    [State("select-revision-for-block", "value"), State("input-block-name", "value"), State("store-trigger", "data")],
    prevent_initial_call=True
)
def add_block(n_clicks, revision_id, name, trigger):
    if not revision_id or not name:
        return trigger, dmc.Alert("Revision과 블록 이름을 입력하세요", color="yellow", withCloseButton=True)
    result = store.add_block(revision_id, name)
    if result:
        return trigger + 1, dmc.Alert(f"✅ Block '{name}' 생성", color="green", withCloseButton=True)
    return trigger, dmc.Alert("⚠️ 이미 존재하거나 오류", color="orange", withCloseButton=True)

@app.callback(
    [Output("store-trigger", "data", allow_duplicate=True), Output("notification-area", "children", allow_duplicate=True)],
    Input("btn-add-designer", "n_clicks"),
    [State("input-designer-name", "value"), State("store-trigger", "data")],
    prevent_initial_call=True
)
def add_designer(n_clicks, name, trigger):
    if not name:
        return trigger, dmc.Alert("담당자 이름을 입력하세요", color="yellow", withCloseButton=True)
    result = store.add_designer(name)
    if result:
        return trigger + 1, dmc.Alert(f"✅ Designer '{name}' 등록", color="green", withCloseButton=True)
    return trigger, dmc.Alert("⚠️ 이미 존재", color="orange", withCloseButton=True)

@app.callback(
    [Output("store-trigger", "data", allow_duplicate=True), Output("notification-area", "children", allow_duplicate=True)],
    Input("btn-add-app", "n_clicks"),
    [State("input-app-name", "value"), State("store-trigger", "data")],
    prevent_initial_call=True
)
def add_app(n_clicks, name, trigger):
    if not name:
        return trigger, dmc.Alert("도구 이름을 입력하세요", color="yellow", withCloseButton=True)
    result = store.add_signoff_app(name)
    if result:
        return trigger + 1, dmc.Alert(f"✅ App '{name}' 등록", color="green", withCloseButton=True)
    return trigger, dmc.Alert("⚠️ 이미 존재", color="orange", withCloseButton=True)

@app.callback(
    [Output("store-trigger", "data", allow_duplicate=True), Output("notification-area", "children", allow_duplicate=True)],
    Input("btn-add-task", "n_clicks"),
    [State("select-block-for-task", "value"), State("select-app-for-task", "value"), 
     State("select-designer-for-task", "value"), State("store-trigger", "data")],
    prevent_initial_call=True
)
def add_task(n_clicks, block_id, app_id, designer_id, trigger):
    if not block_id or not app_id:
        return trigger, dmc.Alert("Block과 App을 선택하세요", color="yellow", withCloseButton=True)
    result = store.add_task(block_id, app_id, designer_id)
    if result:
        return trigger + 1, dmc.Alert("✅ Task 생성", color="green", withCloseButton=True)
    return trigger, dmc.Alert("⚠️ 중복 또는 오류", color="orange", withCloseButton=True)

@app.callback(
    [Output("store-trigger", "data", allow_duplicate=True), Output("notification-area", "children", allow_duplicate=True)],
    Input("btn-add-job", "n_clicks"),
    [State("select-task-for-job", "value"), State("store-trigger", "data")],
    prevent_initial_call=True
)
def add_job(n_clicks, task_id, trigger):
    if not task_id:
        return trigger, dmc.Alert("Task를 선택하세요", color="yellow", withCloseButton=True)
    result = store.add_job(task_id)
    if result:
        return trigger + 1, dmc.Alert("✅ Job 실행", color="green", withCloseButton=True)
    return trigger, dmc.Alert("⚠️ 오류", color="red", withCloseButton=True)

@app.callback(
    [Output("store-trigger", "data", allow_duplicate=True), Output("notification-area", "children", allow_duplicate=True)],
    Input("btn-add-result", "n_clicks"),
    [State("select-job-for-result", "value"), State("input-violation-count", "value"), 
     State("input-waiver-count", "value"), State("store-trigger", "data")],
    prevent_initial_call=True
)
def add_result(n_clicks, job_id, violations, waivers, trigger):
    if not job_id:
        return trigger, dmc.Alert("Job을 선택하세요", color="yellow", withCloseButton=True)
    result = store.add_result(job_id, violations or 0, waivers or 0)
    if result:
        return trigger + 1, dmc.Alert("✅ Result 생성", color="green", withCloseButton=True)
    return trigger, dmc.Alert("⚠️ 오류", color="red", withCloseButton=True)

# Update Dropdowns (only builder components that always exist)
@app.callback(
    [Output("select-product-for-rev", "data"),
     Output("select-revision-for-block", "data"),
     Output("select-block-for-task", "data"),
     Output("select-app-for-task", "data"),
     Output("select-designer-for-task", "data"),
     Output("select-task-for-job", "data"),
     Output("select-job-for-result", "data"),
     Output("builder-graph", "elements")],
    Input("store-trigger", "data")
)
def update_dropdowns(trigger):
    elements = store.to_graph_elements()
    
    return (
        store.get_product_options(),
        store.get_revision_options(),
        store.get_block_options(),
        store.get_app_options(),
        store.get_designer_options(),
        store.get_task_options(),
        store.get_job_options(),
        elements
    )

# === Map Callbacks ===

@app.callback(
    [Output("map-graph", "elements"), Output("map-graph", "layout")],
    [Input("store-trigger", "data"), 
     Input("map-layout-select", "value"),
     Input("map-type-filter", "value"),
     Input("map-product-filter", "value"),
     Input("map-status-filter", "value")]
)
def update_map(trigger, layout_type, type_filter, product_filter, status_filter):
    elements = store.to_graph_elements()
    
    # Apply filters
    if type_filter or product_filter or status_filter:
        filtered = []
        valid_ids = set()
        
        for el in elements:
            if "source" not in el["data"]:  # Node
                node = el["data"]
                keep = True
                
                if type_filter and node.get("type") != type_filter:
                    keep = False
                if product_filter and product_filter not in node.get("id", ""):
                    keep = False
                # Status filter only applies to Tasks/Jobs
                if status_filter:
                    obj = None
                    for t in store.tasks:
                        if t["id"] == node.get("id"):
                            obj = t
                            break
                    if not obj:
                        for j in store.jobs:
                            if j["id"] == node.get("id"):
                                obj = j
                                break
                    if obj and obj.get("status") != status_filter:
                        keep = False
                
                if keep:
                    valid_ids.add(node["id"])
                    filtered.append(el)
        
        # Add edges between valid nodes
        for el in elements:
            if "source" in el["data"]:
                if el["data"]["source"] in valid_ids and el["data"]["target"] in valid_ids:
                    filtered.append(el)
        
        elements = filtered
    
    # Layout
    if layout_type == "layered":
        positions = store.get_layered_positions()
        for el in elements:
            if "source" not in el["data"]:
                node_id = el["data"]["id"]
                if node_id in positions:
                    el["position"] = positions[node_id]
        return elements, {"name": "preset"}
    else:
        layout_config = {"name": layout_type, "animate": True}
        if layout_type == "cose":
            layout_config["nodeRepulsion"] = 10000
        return elements, layout_config

@app.callback(
    Output("map-node-details", "children"),
    Input("map-graph", "tapNodeData")
)
def show_node_details(node_data):
    if not node_data:
        return dmc.Text("노드를 클릭하세요", c="dimmed")
    
    return dmc.Stack([
        dmc.Group([
            html.Div(style={"width": "16px", "height": "16px", "borderRadius": "50%", "backgroundColor": node_data.get("color", "#868e96")}),
            dmc.Text(node_data.get("label", ""), fw=600)
        ]),
        dmc.Badge(node_data.get("type", ""), variant="outline", size="sm"),
        dmc.Divider(my="xs"),
        dmc.Code(node_data.get("id", ""), block=True)
    ], gap="xs")

@app.callback(
    Output("map-related-objects", "children"),
    Input("map-graph", "tapNodeData")
)
def show_related(node_data):
    if not node_data:
        return dmc.Text("노드 선택 시 표시", c="dimmed", size="sm")
    
    related = store.get_related_objects(node_data.get("id", ""))
    
    items = []
    if related["upstream"]:
        items.append(dmc.Text("⬆️ 상위", size="xs", fw=500))
        for obj in related["upstream"]:
            items.append(dmc.Badge(obj.get("name", obj.get("id", "")), size="xs", variant="light", color="blue"))
    
    if related["downstream"]:
        items.append(dmc.Text("⬇️ 하위", size="xs", fw=500, mt="xs"))
        for obj in related["downstream"][:5]:  # Limit
            items.append(dmc.Badge(obj.get("name", obj.get("id", "")), size="xs", variant="light", color="green"))
        if len(related["downstream"]) > 5:
            items.append(dmc.Text(f"... +{len(related['downstream'])-5}개", size="xs", c="dimmed"))
    
    if not items:
        return dmc.Text("연결된 객체 없음", c="dimmed", size="sm")
    
    return dmc.Stack(items, gap=3)

# === Explorer Callbacks ===

@app.callback(
    [Output("explorer-stats", "children"), Output("explorer-content", "children")],
    Input("store-trigger", "data")
)
def update_explorer(trigger):
    stats = store.get_statistics()
    all_data = store.get_all_data()
    
    # Stats Cards
    stat_cards = dmc.SimpleGrid([
        dmc.Paper([
            dmc.Text(str(stats.get("Task", 0)), size="xl", fw=700, ta="center"),
            dmc.Text("전체 Task", size="sm", c="dimmed", ta="center")
        ], p="md", withBorder=True),
        dmc.Paper([
            dmc.Text(str(stats.get("완료", 0)), size="xl", fw=700, ta="center", c="green"),
            dmc.Text("완료", size="sm", c="dimmed", ta="center")
        ], p="md", withBorder=True),
        dmc.Paper([
            dmc.Text(str(stats.get("실행중", 0)), size="xl", fw=700, ta="center", c="blue"),
            dmc.Text("실행중", size="sm", c="dimmed", ta="center")
        ], p="md", withBorder=True),
        dmc.Paper([
            dmc.Text(str(stats.get("대기중", 0)), size="xl", fw=700, ta="center", c="gray"),
            dmc.Text("대기중", size="sm", c="dimmed", ta="center")
        ], p="md", withBorder=True),
    ], cols=4, spacing="md")
    
    # Tables
    tabs_list = []
    panels = []
    
    for name, data in all_data.items():
        if not data:
            continue
        
        tabs_list.append(dmc.TabsTab(f"{name} ({len(data)})", value=name))
        df = pd.DataFrame(data)
        
        table = dmc.Table(
            children=[
                html.Thead(html.Tr([html.Th(c) for c in df.columns])),
                html.Tbody([html.Tr([html.Td(str(row[c])) for c in df.columns]) for _, row in df.iterrows()])
            ],
            striped=True, withTableBorder=True, style={"fontSize": "11px"}
        )
        panels.append(dmc.TabsPanel(dmc.ScrollArea(table, h=400), value=name))
    
    if not tabs_list:
        content = dmc.Alert("데이터가 없습니다. 빌더에서 생성하거나 샘플을 로드하세요.", color="blue")
    else:
        content = dmc.Tabs([dmc.TabsList(tabs_list)] + panels, value=tabs_list[0].value)
    
    return stat_cards, content

@app.callback(
    Output("download-csv", "data"),
    Input("btn-export-csv", "n_clicks"),
    prevent_initial_call=True
)
def export_csv(n_clicks):
    if not n_clicks:
        return None
    
    all_data = store.get_all_data()
    # Combine all into one CSV
    rows = []
    for obj_type, data in all_data.items():
        for obj in data:
            obj["_type"] = obj_type
            rows.append(obj)
    
    if not rows:
        return None
    
    df = pd.DataFrame(rows)
    return dcc.send_data_frame(df.to_csv, "ontology_export.csv", index=False)

# === Search Callbacks ===

@app.callback(
    Output("search-results", "children"),
    Input("btn-search", "n_clicks"),
    [State("search-input", "value"), State("search-type-filter", "value")],
    prevent_initial_call=True
)
def do_search(n_clicks, query, type_filter):
    if not query:
        return dmc.Alert("검색어를 입력하세요", color="yellow")
    
    results = store.search(query, type_filter)
    
    if not results:
        return dmc.Alert(f"'{query}'에 대한 검색 결과가 없습니다.", color="gray")
    
    items = []
    for obj in results[:20]:  # Limit
        items.append(
            dmc.Paper([
                dmc.Group([
                    dmc.Badge(obj.get("type", ""), size="sm"),
                    dmc.Text(obj.get("name", obj.get("id", "")), fw=500)
                ]),
                dmc.Code(obj.get("id", ""), block=True, style={"fontSize": "10px"})
            ], p="sm", withBorder=True, mb="xs")
        )
    
    return dmc.Stack([
        dmc.Text(f"{len(results)}개 결과", size="sm", c="dimmed", mb="sm"),
        *items
    ])


if __name__ == "__main__":
    app.run(debug=True)
