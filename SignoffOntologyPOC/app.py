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
        dmc.NavLink(label="분석 대시보드", leftSection="📈", href="/analysis", id="nav-analysis"),
        dmc.NavLink(label="데이터 탐색기", leftSection="📊", href="/explorer", id="nav-explorer"),
        
        dmc.Divider(my=15),
        dmc.Text("샘플 데이터", size="sm", c="dimmed", mb=5),
        dmc.SegmentedControl(
            id="template-level",
            value="medium",
            data=[
                {"value": "simple", "label": "Simple"},
                {"value": "medium", "label": "Medium"},
                {"value": "complex", "label": "Complex"},
                {"value": "full", "label": "Full"},
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
            dmc.Group([
                dmc.Title("온톨로지 맵", order=2),
                dmc.Badge("전체 구조 시각화", color="blue", variant="light")
            ]),
            dmc.Group([
                dmc.Button("CSV", id="btn-export-csv", variant="light", size="xs", leftSection="📄"),
                dmc.Button("JSON", id="btn-export-json", variant="light", size="xs", color="teal", leftSection="🔗"),
                dmc.Button("Parquet", id="btn-export-parquet", variant="light", size="xs", color="violet", leftSection="📊"),
            ], gap="xs")
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
            dmc.TextInput(
                id="explorer-search",
                placeholder="검색어 입력...",
                size="xs",
                w=200
            )
        ], justify="space-between", mb="md"),
        
        # Stats Cards
        html.Div(id="explorer-stats"),
        
        dmc.Divider(my="md"),
        
        html.Div(id="explorer-content")
    ])

# --- Analysis Page ---
def create_analysis_page():
    """분석 대시보드 페이지"""
    return dmc.Stack([
        dmc.Group([
            dmc.Title("분석 대시보드", order=2),
            dmc.Badge("Signoff 현황 분석", color="violet", variant="light")
        ], justify="space-between", mb="md"),
        
        dmc.Tabs([
            dmc.TabsList([
                dmc.TabsTab("📊 Progress Dashboard", value="progress"),
                dmc.TabsTab("⚠️ Critical Path", value="critical"),
                dmc.TabsTab("⏱️ Timeline", value="timeline"),
                dmc.TabsTab("🔍 Advanced Query", value="query"),
            ]),
            
            # Progress Dashboard Tab
            dmc.TabsPanel([
                html.Div(id="analysis-progress-content")
            ], value="progress"),
            
            # Critical Path Tab
            dmc.TabsPanel([
                html.Div(id="analysis-critical-content")
            ], value="critical"),
            
            # Timeline Tab
            dmc.TabsPanel([
                html.Div(id="analysis-timeline-content")
            ], value="timeline"),
            
            # Advanced Query Tab
            dmc.TabsPanel([
                dmc.Grid([
                    dmc.GridCol([
                        dmc.Paper([
                            dmc.Title("조건부 검색", order=4, mb="md"),
                            dmc.Select(
                                label="Revision 선택",
                                id="query-revision-select",
                                data=store.get_revision_options(),
                                placeholder="선택...",
                                clearable=True,
                                mb="sm"
                            ),
                            dmc.Select(
                                label="상태 필터",
                                id="query-status-filter",
                                data=[
                                    {"value": "대기중", "label": "대기중"},
                                    {"value": "실행중", "label": "실행중"},
                                    {"value": "완료", "label": "완료"},
                                    {"value": "진행중", "label": "진행중"},
                                ],
                                placeholder="전체",
                                clearable=True,
                                mb="sm"
                            ),
                            dmc.TextInput(
                                label="키워드 검색",
                                id="query-keyword",
                                placeholder="예: FULLCHIP, DSC...",
                                mb="md"
                            ),
                            dmc.Button("검색", id="btn-advanced-query", color="violet", fullWidth=True)
                        ], p="md", withBorder=True)
                    ], span=3),
                    dmc.GridCol([
                        dmc.Paper([
                            dmc.Title("검색 결과", order=4, mb="md"),
                            html.Div(id="analysis-query-results")
                        ], p="md", withBorder=True, mih=400)
                    ], span=9)
                ])
            ], value="query"),
        ], value="progress")
    ])

# --- App Layout ---
app.layout = dmc.MantineProvider(
    forceColorScheme="light",
    theme={"primaryColor": "blue", "fontFamily": "'Pretendard', 'Inter', sans-serif"},
    children=[
        dcc.Location(id="url"),
        dcc.Store(id="store-trigger", data=0),
        dcc.Download(id="download-csv"),
        dcc.Download(id="download-json"),
        dcc.Download(id="download-parquet"),
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
     Output("nav-analysis", "active"), Output("nav-explorer", "active")],
    Input("url", "pathname")
)
def render_page(pathname):
    if pathname == "/map":
        return create_map_page(), False, True, False, False
    elif pathname == "/analysis":
        return create_analysis_page(), False, False, True, False
    elif pathname == "/explorer":
        return create_explorer_page(), False, False, False, True
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
    # total_rows defaults to 100 for manual creation
    total_rows = max(100, (violations or 0) + (waivers or 0) + 10)
    result = store.add_result(job_id, total_rows, violations or 0, waivers or 0)
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
    
    node_id = node_data.get("id", "")
    node_type = node_data.get("type", "")
    
    # Find the full object from store
    obj = None
    if node_type == "Job":
        obj = next((j for j in store.jobs if j["id"] == node_id), None)
    elif node_type == "Result":
        obj = next((r for r in store.results if r["id"] == node_id), None)
    elif node_type == "Task":
        obj = next((t for t in store.tasks if t["id"] == node_id), None)
    elif node_type == "Block":
        obj = next((b for b in store.blocks if b["id"] == node_id), None)
    elif node_type == "Product":
        obj = next((p for p in store.products if p["id"] == node_id), None)
    elif node_type == "Revision":
        obj = next((r for r in store.revisions if r["id"] == node_id), None)
    elif node_type == "SignoffApp":
        obj = next((a for a in store.signoff_apps if a["id"] == node_id), None)
    elif node_type == "Designer":
        obj = next((d for d in store.designers if d["id"] == node_id), None)
    
    # Build details list
    details = [
        dmc.Group([
            html.Div(style={"width": "16px", "height": "16px", "borderRadius": "50%", "backgroundColor": node_data.get("color", "#868e96")}),
            dmc.Text(node_data.get("label", ""), fw=600)
        ]),
        dmc.Badge(node_type, variant="outline", size="sm"),
        dmc.Divider(my="xs"),
        dmc.Code(node_id, block=True, style={"fontSize": "10px"})
    ]
    
    # Add object-specific attributes
    if obj:
        if node_type == "Job":
            details.extend([
                dmc.Divider(my="xs", label="Job 상세", labelPosition="center"),
                dmc.Text(f"상태: {obj.get('status', 'N/A')}", size="xs"),
                dmc.Text(f"시작: {obj.get('start_time', 'N/A')[:19] if obj.get('start_time') else 'N/A'}", size="xs"),
                dmc.Text(f"종료: {obj.get('end_time', 'N/A')[:19] if obj.get('end_time') else '실행중'}", size="xs"),
                dmc.Text(f"경로: {obj.get('workspace_dir', 'N/A')}", size="xs", style={"wordBreak": "break-all"})
            ])
        elif node_type == "Result":
            progress = obj.get("progress_pct", 0)
            details.extend([
                dmc.Divider(my="xs", label="Result 상세", labelPosition="center"),
                dmc.Group([
                    dmc.Text("진행률:", size="xs"),
                    dmc.Badge(f"{progress}%", color="green" if progress >= 90 else "yellow", size="sm")
                ]),
                dmc.Text(f"Total: {obj.get('total_rows', 0)}", size="xs"),
                dmc.Text(f"Violations: {obj.get('violation_count', 0)}", size="xs", c="red"),
                dmc.Text(f"Waivers: {obj.get('waiver_count', 0)}", size="xs", c="blue"),
                dmc.Text(f"Remaining: {obj.get('remaining', 0)}", size="xs"),
                dmc.Text(f"파일: {obj.get('file_path', 'N/A')}", size="xs", style={"wordBreak": "break-all"})
            ])
        elif node_type == "Task":
            details.extend([
                dmc.Divider(my="xs", label="Task 상세", labelPosition="center"),
                dmc.Text(f"상태: {obj.get('status', 'N/A')}", size="xs"),
                dmc.Text(f"Block: {obj.get('block_id', 'N/A')}", size="xs"),
                dmc.Text(f"App: {obj.get('app_id', 'N/A')}", size="xs"),
                dmc.Text(f"담당: {obj.get('designer_id', 'N/A')}", size="xs")
            ])
    
    return dmc.Stack(details, gap="xs")

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

@app.callback(
    Output("download-json", "data"),
    Input("btn-export-json", "n_clicks"),
    prevent_initial_call=True
)
def export_json(n_clicks):
    if not n_clicks:
        return None
    
    json_str = store.to_json()
    if not json_str:
        return None 
    
    return dict(content=json_str, filename="signoff_ontology_graph.json")

@app.callback(
    Output("download-parquet", "data"),
    Input("btn-export-parquet", "n_clicks"),
    prevent_initial_call=True
)
def export_parquet(n_clicks):
    if not n_clicks:
        return None
    
    try:
        import io
        import zipfile
        
        parquet_files = store.to_parquet_bytes()
        if not parquet_files:
            return None
        
        # Create ZIP containing both files
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename, data in parquet_files.items():
                zf.writestr(filename, data)
        
        zip_buffer.seek(0)
        return dcc.send_bytes(zip_buffer.getvalue(), "signoff_ontology_parquet.zip")
        
    except ImportError as e:
        print(f"Parquet export failed (pyarrow not installed): {e}")
        return None
    except Exception as e:
        print(f"Parquet export error: {e}")
        return None

# === Analysis Callbacks ===

@app.callback(
    Output("analysis-progress-content", "children"),
    Input("store-trigger", "data")
)
def update_progress_dashboard(trigger):
    """Revision별 검증 진행률 대시보드"""
    revisions = store.revisions
    if not revisions:
        return dmc.Alert("데이터가 없습니다. 샘플을 로드하세요.", color="blue")
    
    cards = []
    for rev in revisions:
        rev_id = rev["id"]
        # Get all results for this revision
        rev_results = []
        for task in store.tasks:
            block = next((b for b in store.blocks if b["id"] == task["block_id"]), None)
            if block and block["revision_id"] == rev_id:
                for job in store.jobs:
                    if job["task_id"] == task["id"]:
                        for res in store.results:
                            if res["job_id"] == job["id"]:
                                rev_results.append(res)
        
        # Calculate overall progress
        if rev_results:
            total_rows = sum(r.get("total_rows", 100) for r in rev_results)
            processed = sum(r.get("waiver_count", 0) + r.get("violation_count", 0) for r in rev_results)
            progress = (processed / total_rows * 100) if total_rows > 0 else 0
            avg_violations = sum(r.get("violation_count", 0) for r in rev_results) / len(rev_results)
        else:
            progress = 0
            avg_violations = 0
        
        color = "green" if progress >= 90 else "yellow" if progress >= 50 else "red"
        
        cards.append(
            dmc.Paper([
                dmc.Group([
                    dmc.Text(rev["name"], fw=700, size="lg"),
                    dmc.Badge(f"{progress:.1f}%", color=color, size="lg")
                ], justify="space-between"),
                dmc.Progress(value=progress, color=color, size="lg", mt="sm"),
                dmc.Group([
                    dmc.Text(f"Results: {len(rev_results)}", size="xs", c="dimmed"),
                    dmc.Text(f"Avg Violations: {avg_violations:.0f}", size="xs", c="dimmed")
                ], mt="sm", justify="space-between")
            ], p="md", withBorder=True, mb="sm")
        )
    
    return dmc.Stack(cards)

@app.callback(
    Output("analysis-critical-content", "children"),
    Input("store-trigger", "data")
)
def update_critical_path(trigger):
    """Violation이 많은 Block/Task 표시"""
    if not store.results:
        return dmc.Alert("결과 데이터가 없습니다.", color="blue")
    
    # Sort results by violation count
    sorted_results = sorted(store.results, key=lambda r: r.get("violation_count", 0), reverse=True)
    
    items = []
    for res in sorted_results[:10]:
        job = next((j for j in store.jobs if j["id"] == res["job_id"]), None)
        task = next((t for t in store.tasks if job and t["id"] == job["task_id"]), None)
        block = next((b for b in store.blocks if task and b["id"] == task["block_id"]), None)
        app = next((a for a in store.signoff_apps if task and a["id"] == task["app_id"]), None)
        
        violations = res.get("violation_count", 0)
        total = res.get("total_rows", 100)
        
        items.append(
            dmc.Paper([
                dmc.Group([
                    dmc.Badge(block["name"] if block else "?", color="blue"),
                    dmc.Badge(app["name"] if app else "?", color="teal"),
                    dmc.Text(f"{violations} violations", c="red", fw=500)
                ]),
                dmc.Progress(
                    value=(violations / total * 100) if total > 0 else 0,
                    color="red",
                    size="sm",
                    mt="xs"
                )
            ], p="sm", withBorder=True, mb="xs")
        )
    
    return dmc.Stack([
        dmc.Title("Top 10 High-Violation Results", order=4, mb="sm"),
        *items
    ])

@app.callback(
    Output("analysis-timeline-content", "children"),
    Input("store-trigger", "data")
)
def update_timeline(trigger):
    """Job 실행 시간 타임라인"""
    if not store.jobs:
        return dmc.Alert("Job 데이터가 없습니다.", color="blue")
    
    # Sort jobs by start time
    sorted_jobs = sorted(store.jobs, key=lambda j: j.get("start_time", ""), reverse=True)
    
    items = []
    for job in sorted_jobs[:15]:
        task = next((t for t in store.tasks if t["id"] == job["task_id"]), None)
        
        start = job.get("start_time", "")[:19] if job.get("start_time") else "N/A"
        end = job.get("end_time", "")[:19] if job.get("end_time") else "실행중"
        status_color = "green" if job["status"] == "완료" else "blue"
        
        items.append(
            dmc.Paper([
                dmc.Group([
                    dmc.Badge(job["status"], color=status_color, size="sm"),
                    dmc.Text(job["id"], size="sm", fw=500)
                ]),
                dmc.Text(f"시작: {start}", size="xs", c="dimmed"),
                dmc.Text(f"종료: {end}", size="xs", c="dimmed"),
                dmc.Text(f"경로: {job.get('workspace_dir', 'N/A')}", size="xs", c="dimmed", style={"wordBreak": "break-all"})
            ], p="sm", withBorder=True, mb="xs")
        )
    
    return dmc.Stack([dmc.Title("최근 Job 실행 이력", order=4, mb="sm"), *items])

@app.callback(
    Output("analysis-query-results", "children"),
    Input("btn-advanced-query", "n_clicks"),
    [State("query-revision-select", "value"), State("query-status-filter", "value"), State("query-keyword", "value")],
    prevent_initial_call=True
)
def do_advanced_query(n_clicks, revision_id, status_filter, keyword):
    """조건부 검색"""
    results = []
    
    for task in store.tasks:
        # Filter by revision
        if revision_id:
            block = next((b for b in store.blocks if b["id"] == task["block_id"]), None)
            if not block or block["revision_id"] != revision_id:
                continue
        
        # Filter by status
        if status_filter and task["status"] != status_filter:
            continue
        
        # Filter by keyword
        if keyword and keyword.lower() not in task["id"].lower():
            continue
        
        results.append(task)
    
    if not results:
        return dmc.Alert("검색 결과가 없습니다.", color="gray")
    
    items = []
    for task in results[:20]:
        items.append(
            dmc.Paper([
                dmc.Group([
                    dmc.Badge(task["status"], 
                             color="green" if task["status"] == "완료" else "yellow" if task["status"] == "실행중" else "gray",
                             size="sm"),
                    dmc.Text(task["id"], size="sm", fw=500)
                ]),
                dmc.Text(f"Block: {task['block_id']}", size="xs", c="dimmed"),
                dmc.Text(f"App: {task['app_id']}", size="xs", c="dimmed")
            ], p="sm", withBorder=True, mb="xs")
        )
    
    return dmc.Stack([dmc.Text(f"{len(results)}개 결과", size="sm", c="dimmed", mb="sm"), *items])


if __name__ == "__main__":
    app.run(debug=True)
