"""
Signoff Ontology POC - 인터랙티브 온톨로지 빌더
"""
import dash
from dash import dcc, html, Input, Output, State, callback, ALL, MATCH
import dash_mantine_components as dmc
import dash_cytoscape as cyto
import pandas as pd
import json

from utils.ontology_store import store

# --- App Setup ---
app = dash.Dash(__name__, external_stylesheets=dmc.styles.ALL, suppress_callback_exceptions=True)
app.title = "Signoff Ontology Builder"

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
    }
]

# --- Sidebar ---
def create_sidebar():
    return dmc.Stack([
        dmc.Group([
            dmc.Text("🧠", size="xl"),
            dmc.Text("Signoff Ontology", size="lg", fw=700)
        ], mb=20),
        dmc.Divider(mb=10),
        dmc.NavLink(label="온톨로지 빌더", leftSection="🔧", href="/", id="nav-builder"),
        dmc.NavLink(label="온톨로지 맵", leftSection="🗺️", href="/map", id="nav-map"),
        dmc.NavLink(label="데이터 탐색기", leftSection="📊", href="/explorer", id="nav-explorer"),
        dmc.Divider(my=20),
        dmc.Text("빠른 실행", size="sm", c="dimmed", mb=5),
        dmc.Button("샘플 데이터 로드", id="btn-load-template", variant="light", color="blue", fullWidth=True, mb=5),
        dmc.Button("전체 삭제", id="btn-clear-all", variant="outline", color="red", fullWidth=True),
    ], h="100%", p="md")

# --- Builder Page ---
def create_builder_page():
    return dmc.Stack([
        dmc.Title("온톨로지 빌더", order=2, mb="sm"),
        dmc.Text("Signoff 온톨로지 객체를 직접 생성하고 연결해보세요.", c="dimmed", mb="md"),
        
        dmc.Grid([
            # Left: Forms
            dmc.GridCol([
                dmc.Accordion([
                    # 1. Product
                    dmc.AccordionItem([
                        dmc.AccordionControl("1️⃣ Product (제품) 생성"),
                        dmc.AccordionPanel([
                            dmc.TextInput(label="제품 이름", placeholder="예: HBM4E", id="input-product-name"),
                            dmc.Button("생성", id="btn-add-product", color="blue", mt="sm", fullWidth=True)
                        ])
                    ], value="product"),
                    
                    # 2. Revision
                    dmc.AccordionItem([
                        dmc.AccordionControl("2️⃣ Revision (버전) 생성"),
                        dmc.AccordionPanel([
                            dmc.Select(label="상위 Product 선택", id="select-product-for-rev", data=[], placeholder="Product를 먼저 생성하세요"),
                            dmc.TextInput(label="버전 이름", placeholder="예: R30", id="input-revision-name", mt="sm"),
                            dmc.Button("생성", id="btn-add-revision", color="blue", mt="sm", fullWidth=True)
                        ])
                    ], value="revision"),
                    
                    # 3. Block
                    dmc.AccordionItem([
                        dmc.AccordionControl("3️⃣ Block (설계 블록) 생성"),
                        dmc.AccordionPanel([
                            dmc.Select(label="상위 Revision 선택", id="select-revision-for-block", data=[], placeholder="Revision을 먼저 생성하세요"),
                            dmc.TextInput(label="블록 이름", placeholder="예: PHY, Core", id="input-block-name", mt="sm"),
                            dmc.Button("생성", id="btn-add-block", color="blue", mt="sm", fullWidth=True)
                        ])
                    ], value="block"),
                    
                    # 4. Designer & App
                    dmc.AccordionItem([
                        dmc.AccordionControl("4️⃣ Designer & Signoff App 등록"),
                        dmc.AccordionPanel([
                            dmc.Grid([
                                dmc.GridCol([
                                    dmc.TextInput(label="담당자 이름", placeholder="예: 김철수", id="input-designer-name"),
                                    dmc.Button("등록", id="btn-add-designer", color="violet", mt="sm", size="sm", fullWidth=True)
                                ], span=6),
                                dmc.GridCol([
                                    dmc.TextInput(label="검증 도구 이름", placeholder="예: STA, LVS", id="input-app-name"),
                                    dmc.Button("등록", id="btn-add-app", color="teal", mt="sm", size="sm", fullWidth=True)
                                ], span=6),
                            ])
                        ])
                    ], value="designer-app"),
                    
                    # 5. Task
                    dmc.AccordionItem([
                        dmc.AccordionControl("5️⃣ Task (검증 작업) 정의"),
                        dmc.AccordionPanel([
                            dmc.Select(label="Block 선택", id="select-block-for-task", data=[]),
                            dmc.Select(label="Signoff App 선택", id="select-app-for-task", data=[], mt="sm"),
                            dmc.Select(label="담당자 배정", id="select-designer-for-task", data=[], mt="sm", placeholder="(선택 사항)"),
                            dmc.Button("Task 생성", id="btn-add-task", color="green", mt="sm", fullWidth=True)
                        ])
                    ], value="task"),
                    
                    # 6. Job & Result
                    dmc.AccordionItem([
                        dmc.AccordionControl("6️⃣ Job 실행 & Result 생성"),
                        dmc.AccordionPanel([
                            dmc.Select(label="Task 선택", id="select-task-for-job", data=[]),
                            dmc.Button("Job 실행", id="btn-add-job", color="orange", mt="sm", fullWidth=True),
                            dmc.Divider(my="sm"),
                            dmc.Select(label="완료할 Job 선택", id="select-job-for-result", data=[]),
                            dmc.NumberInput(label="Violation 수", id="input-violation-count", value=0, min=0, mt="sm"),
                            dmc.NumberInput(label="Waiver 수", id="input-waiver-count", value=0, min=0, mt="sm"),
                            dmc.Button("Result 생성", id="btn-add-result", color="orange", mt="sm", fullWidth=True),
                        ])
                    ], value="job-result"),
                ], value="product", chevronPosition="right", variant="separated")
            ], span=5),
            
            # Right: Graph Preview
            dmc.GridCol([
                dmc.Paper([
                    dmc.Group([
                        dmc.Title("실시간 미리보기", order=4),
                        html.Div(id="stats-display")
                    ], justify="space-between", mb="sm"),
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
        
        # Notification Area
        html.Div(id="notification-area")
    ])

# --- Map Page ---
def create_map_page():
    return dmc.Stack([
        dmc.Group([
            dmc.Title("온톨로지 맵", order=2),
            dmc.Badge("전체 보기", color="blue", variant="light")
        ], justify="space-between", mb="md"),
        
        dmc.Grid([
            dmc.GridCol([
                dmc.Paper([
                    cyto.Cytoscape(
                        id='map-graph',
                        layout={'name': 'cose', 'animate': True, 'nodeRepulsion': 10000},
                        style={'width': '100%', 'height': '700px'},
                        elements=[],
                        stylesheet=graph_stylesheet
                    )
                ], p="md", withBorder=True, shadow="sm")
            ], span=9),
            
            dmc.GridCol([
                dmc.Paper([
                    dmc.Title("선택된 노드", order=4, mb="md"),
                    html.Div(id="map-node-details", children=dmc.Text("노드를 클릭하세요", c="dimmed"))
                ], p="md", withBorder=True, h="100%")
            ], span=3)
        ])
    ])

# --- Explorer Page ---
def create_explorer_page():
    return dmc.Stack([
        dmc.Title("데이터 탐색기", order=2, mb="md"),
        html.Div(id="explorer-content")
    ])

# --- App Layout ---
app.layout = dmc.MantineProvider(
    forceColorScheme="light",
    theme={"primaryColor": "blue", "fontFamily": "'Pretendard', 'Inter', sans-serif"},
    children=[
        dcc.Location(id="url"),
        dcc.Store(id="store-trigger", data=0),  # Trigger for updates
        dmc.Grid([
            dmc.GridCol(create_sidebar(), span=2, style={"minHeight": "100vh", "backgroundColor": "#f8f9fa", "borderRight": "1px solid #dee2e6"}),
            dmc.GridCol(dmc.Container(id="page-content", p="xl", fluid=True), span=10)
        ], gutter=0)
    ]
)

# --- Callbacks ---

# Page Routing
@app.callback(
    [Output("page-content", "children"),
     Output("nav-builder", "active"), Output("nav-map", "active"), Output("nav-explorer", "active")],
    Input("url", "pathname")
)
def render_page(pathname):
    if pathname == "/map":
        return create_map_page(), False, True, False
    elif pathname == "/explorer":
        return create_explorer_page(), False, False, True
    return create_builder_page(), True, False, False

# Template & Clear
@app.callback(
    Output("store-trigger", "data", allow_duplicate=True),
    [Input("btn-load-template", "n_clicks"), Input("btn-clear-all", "n_clicks")],
    State("store-trigger", "data"),
    prevent_initial_call=True
)
def handle_template_buttons(n_load, n_clear, trigger):
    ctx = dash.callback_context
    if not ctx.triggered:
        return trigger
    
    btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if btn_id == "btn-load-template":
        store.load_template()
    elif btn_id == "btn-clear-all":
        store.clear_all()
    
    return trigger + 1

# Add Product
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
    return trigger, dmc.Alert(f"⚠️ Product '{name}'이(가) 이미 존재합니다", color="orange", withCloseButton=True)

# Add Revision
@app.callback(
    [Output("store-trigger", "data", allow_duplicate=True), Output("notification-area", "children", allow_duplicate=True)],
    Input("btn-add-revision", "n_clicks"),
    [State("select-product-for-rev", "value"), State("input-revision-name", "value"), State("store-trigger", "data")],
    prevent_initial_call=True
)
def add_revision(n_clicks, product_id, name, trigger):
    if not product_id or not name:
        return trigger, dmc.Alert("Product와 Revision 이름을 모두 입력하세요", color="yellow", withCloseButton=True)
    
    result = store.add_revision(product_id, name)
    if result:
        return trigger + 1, dmc.Alert(f"✅ Revision '{name}' 생성 완료", color="green", withCloseButton=True)
    return trigger, dmc.Alert(f"⚠️ Revision '{name}'이(가) 이미 존재하거나 Product가 없습니다", color="orange", withCloseButton=True)

# Add Block
@app.callback(
    [Output("store-trigger", "data", allow_duplicate=True), Output("notification-area", "children", allow_duplicate=True)],
    Input("btn-add-block", "n_clicks"),
    [State("select-revision-for-block", "value"), State("input-block-name", "value"), State("store-trigger", "data")],
    prevent_initial_call=True
)
def add_block(n_clicks, revision_id, name, trigger):
    if not revision_id or not name:
        return trigger, dmc.Alert("Revision과 Block 이름을 모두 입력하세요", color="yellow", withCloseButton=True)
    
    result = store.add_block(revision_id, name)
    if result:
        return trigger + 1, dmc.Alert(f"✅ Block '{name}' 생성 완료", color="green", withCloseButton=True)
    return trigger, dmc.Alert(f"⚠️ Block '{name}'이(가) 이미 존재하거나 Revision이 없습니다", color="orange", withCloseButton=True)

# Add Designer
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
        return trigger + 1, dmc.Alert(f"✅ Designer '{name}' 등록 완료", color="green", withCloseButton=True)
    return trigger, dmc.Alert(f"⚠️ Designer '{name}'이(가) 이미 존재합니다", color="orange", withCloseButton=True)

# Add App
@app.callback(
    [Output("store-trigger", "data", allow_duplicate=True), Output("notification-area", "children", allow_duplicate=True)],
    Input("btn-add-app", "n_clicks"),
    [State("input-app-name", "value"), State("store-trigger", "data")],
    prevent_initial_call=True
)
def add_app(n_clicks, name, trigger):
    if not name:
        return trigger, dmc.Alert("검증 도구 이름을 입력하세요", color="yellow", withCloseButton=True)
    
    result = store.add_signoff_app(name)
    if result:
        return trigger + 1, dmc.Alert(f"✅ SignoffApp '{name}' 등록 완료", color="green", withCloseButton=True)
    return trigger, dmc.Alert(f"⚠️ SignoffApp '{name}'이(가) 이미 존재합니다", color="orange", withCloseButton=True)

# Add Task
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
        return trigger + 1, dmc.Alert("✅ Task 생성 완료", color="green", withCloseButton=True)
    return trigger, dmc.Alert("⚠️ 동일한 Task가 이미 존재하거나 Block/App이 없습니다", color="orange", withCloseButton=True)

# Add Job
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
        return trigger + 1, dmc.Alert("✅ Job 실행 시작", color="green", withCloseButton=True)
    return trigger, dmc.Alert("Job 생성 실패", color="red", withCloseButton=True)

# Add Result
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
        return trigger + 1, dmc.Alert("✅ Result 생성 완료", color="green", withCloseButton=True)
    return trigger, dmc.Alert("Result 생성 실패", color="red", withCloseButton=True)

# Update Dropdowns & Graph
@app.callback(
    [Output("select-product-for-rev", "data"),
     Output("select-revision-for-block", "data"),
     Output("select-block-for-task", "data"),
     Output("select-app-for-task", "data"),
     Output("select-designer-for-task", "data"),
     Output("select-task-for-job", "data"),
     Output("select-job-for-result", "data"),
     Output("builder-graph", "elements"),
     Output("stats-display", "children")],
    Input("store-trigger", "data")
)
def update_ui(trigger):
    elements = store.to_graph_elements()
    stats = store.get_statistics()
    
    stats_badges = dmc.Group([
        dmc.Badge(f"{v} {k}", color="gray", variant="light", size="sm")
        for k, v in stats.items() if v > 0
    ], gap="xs")
    
    return (
        store.get_product_options(),
        store.get_revision_options(),
        store.get_block_options(),
        store.get_app_options(),
        store.get_designer_options(),
        store.get_task_options(),
        store.get_job_options(),
        elements,
        stats_badges
    )

# Map Graph
@app.callback(
    Output("map-graph", "elements"),
    Input("store-trigger", "data")
)
def update_map_graph(trigger):
    return store.to_graph_elements()

# Map Node Details
@app.callback(
    Output("map-node-details", "children"),
    Input("map-graph", "tapNodeData")
)
def show_node_details(node_data):
    if not node_data:
        return dmc.Text("노드를 클릭하세요", c="dimmed")
    
    return dmc.Stack([
        dmc.Group([
            html.Div(style={"width": "20px", "height": "20px", "borderRadius": "50%", "backgroundColor": node_data.get("color", "#868e96")}),
            dmc.Title(node_data.get("label", ""), order=4)
        ]),
        dmc.Badge(node_data.get("type", ""), variant="outline"),
        dmc.Divider(my="sm"),
        dmc.Code(json.dumps(node_data, indent=2, ensure_ascii=False), block=True)
    ])

# Explorer Content
@app.callback(
    Output("explorer-content", "children"),
    Input("store-trigger", "data")
)
def update_explorer(trigger):
    all_data = store.get_all_data()
    
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
            striped=True, withTableBorder=True, style={"fontSize": "12px"}
        )
        panels.append(dmc.TabsPanel(dmc.ScrollArea(table, h=500), value=name))
    
    if not tabs_list:
        return dmc.Alert("데이터가 없습니다. 빌더에서 객체를 생성하거나 '샘플 데이터 로드'를 클릭하세요.", color="blue")
    
    return dmc.Tabs([dmc.TabsList(tabs_list)] + panels, value=tabs_list[0].value if tabs_list else None)


if __name__ == "__main__":
    app.run(debug=True)
