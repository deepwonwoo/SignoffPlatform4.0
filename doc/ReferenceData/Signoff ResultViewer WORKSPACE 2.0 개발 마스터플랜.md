
## 📋 문서 정보

- **대상**: AI 기반 자동 개발 시스템 (Claude Code, Codex, Gemini CLI 등)
- **목적**: 완전한 구현 가능 수준의 개발 명세서

---

## 1. 프로젝트 개요

### 1.1 목적과 비전

**WORKSPACE 2.0**는 기존 ResultViewer의 WORKSPACE 1.0을 완전히 대체하는 차세대 협업 데이터 관리 시스템입니다.

**핵심 목표:**

- 대용량 Parquet 데이터(10M-100M rows)의 효율적 처리
- 다중 사용자 동시 편집을 통한 팀 협업 강화
- Selective Loading을 통한 메모리 최적화
- 버전 관리를 통한 데이터 무결성 보장

### 1.2 개발 범위

**Phase 1 (현재 코드):**
- Read/Edit Mode & Full Lock

**신규 계획 (개발 계획):**

- **통합 Phase**: Selective Loading + Partial Lock + Merge Update + Version Management를 하나의 Phase로 완성
- Phase 1의 file_mode.py (SegmentedControl 방식) 대체
- workspace_explorer.py (WORKSPACE 1.0) 완전 제거

### 1.3 주요 개선사항

#### 🎯 기존 Phase 1 대비 주요 변경점

| 항목      | Phase 1 (기존)     | WORKSPACE 2.0 (신규)           |
| ------- | ---------------- | ---------------------------- |
| 데이터 로딩  | 전체 파일 로드         | Selective Loading (필터링된 부분만) |
| Lock 방식 | Full Lock만 지원    | Full Lock + Partial Lock     |
| 동시 편집   | 1명만 편집 가능        | 여러 명 동시 편집 (영역 분리)           |
| 저장 방식   | 전체 덮어쓰기          | Merge Update (수정 부분만 병합)     |
| 버전 관리   | 간단한 백업           | .version 파일 기반 체계적 관리        |
| Mode 전환 | SegmentedControl | Selective Loading Dialog     |

### 1.4 사용자 환경

- **대상 사용자**: 메모리 설계 엔지니어 약 300명
- **실행 환경**: LSF 기반 HPC Linux 시스템
- **애플리케이션 구조**: FlaskWebGUI를 통한 개별 사용자별 Dash App 인스턴스
- **데이터 저장소**: NFS 마운트된 중앙 WORKSPACE (권한 777)
    - 개발 중: `/home/deepwonwoo/resultviewer/WORKSPACE`
    - 배포 시: NFS 스토리지 경로로 변경 (CONFIG.WORKSPACE)
- **데이터 규모**: 10만 ~ 1억 행의 Parquet DataFrame

각 엔지니어마다 Linux HPC System에서 login node에서 lsf로 resultviewer job을 제출하여 각각의 ResultViewer Dash App을 실행. 그런데 Workspace의 중앙저장소에서 parquet형식의 dataframe 데이터를 열고 편집할텐데, 여러명이 같은파일을 작업할때 실시간 동시편집은 아니더라도 충돌없이 협업을 지원하기위해 WORKSPACE 2.0을 개발.
### 1.5 기술 스택

**프레임워크 & 라이브러리:**

- **Dash**: Plotly Dash 기반 웹 애플리케이션
- **dash_ag_grid**: 데이터 그리드 (SSRM - Server-Side Row Model)
- **dash_mantine_components (dmc)**: 주요 UI 컴포넌트
- **dash_blueprint_components (dbpc)**: 보조 UI (Icon, Toast)
- **polars**: 대용량 데이터 처리 (pandas보다 10-100배 빠름)
- **dash-flexlayout**: 레이아웃 관리

**개발 & 테스트:**

- **Playwright MCP**: E2E 테스트 자동화 (필수 사용)
- **pytest**: 단위 테스트
- **다중 Python 인스턴스**: 동시 접속 시뮬레이션
(그밖의 다양한 방법)
---

## 2. 시스템 아키텍처

### 2.1 전체 구조

```
┌─────────────────────────────────────────────────────────────┐
│                        사용자 레이어                          │
├─────────────────────────────────────────────────────────────┤
│  User 1 Dash App  │  User 2 Dash App  │  User N Dash App   │
│  (FlaskWebGUI)    │  (FlaskWebGUI)    │  (FlaskWebGUI)      │
└────────┬──────────┴────────┬──────────┴────────┬───────────┘
         │                   │                    │
         └───────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   NFS WORKSPACE  │
                    │  (중앙 저장소)    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼─────┐      ┌───────▼────────┐   ┌──────▼──────┐
   │ Parquet  │      │  Lock 시스템    │   │   Version   │
   │  Files   │      │ Full + Partial │   │  Management │
   └──────────┘      └────────────────┘   └─────────────┘
```

### 2.2 컴포넌트 구조

가능하다면 resultviewer/components/menu/home/item/workspace에서 workspace2.0관련 코드 개발. 
```
resultviewer/
├── app.py                          # Dash 앱 진입점
├── components/
│   ├── RV.py                       # ResultViewer 메인
│   ├── grid/
│   │   ├── data_grid.py            # Dash AG Grid 메인
│   │   └── dag/
│   │       ├── server_side_operations.py
│   │       └── column_definitions.py
│   └── menu/
│       └── home/
│           └── item/
│               ├── open.py         # 로컬 파일 열기
│               ├── save.py         # 저장
│               └── workspace/      # ✨ WORKSPACE 2.0
│                   ├── layout.py              # 메인 레이아웃
│                   ├── file_explorer.py       # 파일 탐색기
│                   ├── file_uploader.py       # 파일 업로더
│                   ├── folder_manager.py      # 폴더 관리
│                   ├── metadata_editor.py     # 메타데이터 편집
│                   ├── selective_loader.py    # ⭐ Selective Loading UI
│                   ├── version_viewer.py      # ⭐ 버전 관리 UI
│                   └── core/
│                       ├── metadata_utils.py       # 메타데이터 생성
│                       ├── file_utils.py           # 파일 시스템
│                       ├── lock_manager.py         # ⭐ Lock 관리 (Full + Partial)
│                       ├── storage_utils.py        # 파일/폴더 CRUD
│                       ├── merge_updater.py        # ⭐ Merge Update
│                       └── version_manager.py      # ⭐ 버전 관리
├── utils/
│   ├── config.py                   # CONFIG.WORKSPACE
│   ├── logging_utils.py            # logger, Toast
│   ├── data_processing.py          # file2df, validate_df
│   └── db_management.py            # SSDF (Singleton DataFrame)
└── tests/                          # E2E 테스트 (Playwright)
```

**범례:**

- ✨ 신규 또는 대폭 수정
- ⭐ 핵심 신규 기능



### 2.3 WORKSPACE 파일 시스템 구조

#### 표준 디렉토리 구조

```
WORKSPACE/
├── {PRODUCT}/                    # 예: D1b
│   └── {REVISION}/               # 예: R00
│       └── {BLOCK}/              # 예: FULLCHIP
│           └── {TOOL}/           # 예: DRIVER_KEEPER
│               ├── result.parquet           # 실제 데이터
│               ├── result.meta              # 메타데이터
│               ├── result.lock              # Full Lock
│               ├── result.{user1}_{timestamp}.lock  # Partial Lock
│               ├── result.merge.lock        # Merge 작업 중 임시 Lock
│               ├── result.version           # 버전 정보
│               └── backup/                 # 버전 백업 폴더
│                   ├── result_v1_20250105_090000.parquet
│                   ├── result_v2_20250105_100000.parquet
│                   └── result_v3_20250105_110000.parquet
└── USERS/                        # Personal Space
    └── {username}/
        └── temp_analysis.parquet
```

#### 파일명 규칙

- **데이터 파일**: `{basename}.parquet`
- **메타데이터**: `{basename}.meta`
- **Full Lock**: `{basename}.lock`
- **Partial Lock**: `{basename}.{user}_{timestamp}.lock`
- **Merge Lock**: `{basename}.merge.lock` (저장 중 임시)
- **버전 정보**: `{basename}.version`
- **버전 백업**: `backup/{basename}_v{N}_{timestamp}.parquet`

### 2.4 Lock 파일 구조

#### Full Lock

```json
{
  "user": "deepwonwoo",
  "type": "full",
  "locked_at": "2025-01-08T12:30:00"
}
```

#### Partial Lock

```json
{
  "user": "deepwonwoo",
  "type": "partial",
  "locked_at": "2025-01-08T12:30:00",
  "filter_expr": "col('Part').eq('CPU') & col('waiver').eq('Result')",
  "selected_columns": ["uniqid", "waiver", "Part", "Net", "user", "waiver_comment"],
  "locked_uniqids": [1, 2, 3, ..., 100]  # 전체 uniqid 리스트 포함
}
```

**중요 설계 결정:**

- ❌ 별도 `.lock_uniqids_{hash}.json` 파일 불필요
- ✅ Lock 파일 안에 모든 정보 포함 (단일 파일 관리)
- ✅ uniqid 리스트 전체 저장 (hash 방식 X)

### 2.5 메타데이터 스키마

`.meta` 파일 (JSON):

```json
{
  "start_date": "2025-01-05",
  "end_date": "2025-06-30",
  "assignee": "",
  "visible": "False",
  "sol_dir": "/path/to/signoff/launcher",
  "waive": {
    "result": 1000,
    "waiver": 50,
    "fixed": 30,
    "task_progress": 0.074,
    "details": [
      {
        "Block": "FULLCHIP",
        "Part": "CPU",
        "Result": 500,
        "Waiver": 30,
        "Fixed": 20,
        "Progress": 0.09
      }
    ],
    "warn_users": "user1,user2"
  },
  "last_modified": "2025-01-08T04:33:38.123456",
  "modified_by": "deepwonwoo",
  "uploaded_at": "2025-01-05T09:00:00.000000",
  "uploaded_by": "deepwonwoo",
  "filterModel": {}
}
```

### 2.6 버전 정보 스키마

`.version` 파일 (JSON):

```json
{
  "current_version": 5,
  "history": [
    {
      "version": 1,
      "backup_file": "result_v1_20250105_090000.parquet",
      "created_by": "user1",
      "created_at": "2025-01-05T09:00:00",
      "action": "full_save",
      "filter_expr": null,
    },
    {
      "version": 2,
      "backup_file": "result_v2_20250105_100000.parquet",
      "created_by": "user2",
      "created_at": "2025-01-05T10:00:00",
      "action": "partial_save",
      "filter_expr": "col('Part').eq('CPU')",
    }
  ]
}
```

---

## 3. Selective Loading 상세 명세

### 3.1 사용자 워크플로우

```
1. ResultViewer 실행 → Home 메뉴 → Open from Workspace
2. WORKSPACE Explorer 열림 → 파일 탐색
3. 파일 클릭 → Selective Loading Dialog 자동 표시
4. [Dialog Stage 1] 파일 정보, Lock 상태, 샘플 데이터 자동 로딩
5. 사용자 설정:
   - 컬럼 선택 (기본: 전체 선택, 시스템 컬럼은 필수)
   - 필터 조건 입력 (optional, Polars expression)
   - Lock 모드 선택 (Read-Only / Partial Lock / Full Lock)
6. 실시간 예상 정보 표시:
   - 예상 행 수
   - 예상 메모리 사용량
   - Lock 충돌 여부
7. "Load Data" 버튼 클릭
8. 충돌 검사 수행
9. Lock 획득 (Edit Mode인 경우)
10. ResultViewer Grid에 데이터 로딩
11. 편집 작업 수행
12. 저장 시 Merge Update 실행
```

### 3.2 UI 구조 (dmc 기반)

#### Selective Loading Dialog

**컴포넌트 계층:**

```python
dmc.Modal(
    id="selective-load-modal",
    size="xl",
    title="Selective Data Loading",
    children=[
        dmc.Stack([
            # ━━━ Section 1: File Information ━━━
            dmc.Paper([
                dmc.Title("File Information", order=5),
                dmc.Grid([
                    dmc.Col(dmc.Text(f"Path: {display_path}"), span=12),
                    dmc.Col(dmc.Text(f"Size: {file_size}"), span=4),
                    dmc.Col(dmc.Text(f"Rows: {total_rows:,}"), span=4),
                    dmc.Col(dmc.Text(f"Columns: {total_cols}"), span=4),
                ]),
                dmc.Group([
                    # Lock 상태 Badge
                    dmc.Badge(
                        "🔒 2 users editing (user1, user2)",
                        color="orange"
                    ) if has_locks else dmc.Badge(
                        "✅ Available",
                        color="green"
                    ),
                ]),
            ], withBorder=True, p="md", mb="md"),
            
            # ━━━ Section 2: Sample Data (Optional, Accordion) ━━━
            dmc.Accordion([
                dmc.AccordionItem(
                    value="preview",
                    children=[
                        dmc.AccordionControl("📊 Preview Data (10 rows)"),
                        dmc.AccordionPanel(
                            dmc.Table(...)  # 샘플 10행
                        ),
                    ],
                ),
            ], mb="md"),
            
            # ━━━ Section 3: Column Selection ━━━
            dmc.Stack([
                dmc.Title("Select Columns", order=5),
                dmc.Text("System columns (uniqid, waiver, user, waiver_comment) are always included.", size="sm", color="dimmed"),
                dmc.Group([
                    dmc.Button("Select All", id="select-all-cols", size="xs"),
                    dmc.Button("Deselect All", id="deselect-all-cols", size="xs"),
                ]),
                dmc.CheckboxGroup(
                    id="column-selection",
                    value=all_columns,  # 기본: 전체 선택
                    children=[
                        dmc.Checkbox(
                            label=f"{col} ({dtype})",
                            value=col,
                            disabled=(col in system_cols)
                        )
                        for col, dtype in columns
                    ],
                ),
            ], mb="md"),
            
            # ━━━ Section 4: Row Filter ━━━
            dmc.Stack([
                dmc.Title("Filter Rows (Optional)", order=5),
                dmc.Textarea(
                    id="filter-expression",
                    placeholder='예: col("Part").eq("CPU") & col("waiver").eq("Result")',
                    minRows=3,
                    description="Polars expression syntax",
                ),
                dmc.Group([
                    dmc.Text("Suggested filters:", size="sm", color="dimmed"),
                    dmc.Button(
                        "My rows",
                        id="filter-my-rows",
                        size="xs",
                        variant="light",
                    ),
                    dmc.Button(
                        "Result rows",
                        id="filter-result-rows",
                        size="xs",
                        variant="light",
                    ),
                ]),
                # 실시간 예상 정보
                dmc.Alert(
                    id="filter-preview-alert",
                    title="Preview",
                    color="blue",
                    children="",  # 동적으로 업데이트
                ),
            ], mb="md"),
            
            # ━━━ Section 5: Lock Mode Selection ━━━
            dmc.Stack([
                dmc.Title("Loading Mode", order=5),
                dmc.RadioGroup(
                    id="lock-mode-selection",
                    value="read",
                    children=[
                        dmc.Radio(
                            label="📖 Read-Only (View Only, No Lock)",
                            value="read",
                            description="열람 전용, WORKSPACE 저장 불가",
                        ),
                        dmc.Radio(
                            label="🔓 Partial Lock (Edit Selected Rows)",
                            value="partial",
                            description="필터링된 영역만 편집 가능, 다른 사용자와 동시 작업 가능",
                        ),
                        dmc.Radio(
                            label="🔒 Full Lock (Edit Entire File)",
                            value="full",
                            description="전체 파일 독점 편집, 다른 사용자는 Read-Only",
                        ),
                    ],
                ),
            ], mb="md"),
            
            # ━━━ Section 6: Action Buttons ━━━
            dmc.Group([
                dmc.Button(
                    "Load Data",
                    id="load-data-button",
                    color="blue",
                    size="md",
                    leftIcon=DashIconify(icon="mdi:check"),
                ),
                dmc.Button(
                    "Cancel",
                    id="cancel-load-button",
                    variant="outline",
                    size="md",
                ),
            ], position="right"),
            
        ], spacing="md"),
    ],
)
```

### 3.3 Callbacks 명세

#### 3.3.1 Dialog 열기

```python
@app.callback(
    Output("selective-load-modal", "opened"),
    Output("file-info-section", "children"),
    Output("column-selection", "children"),
    Output("filter-expression", "value"),
    Input("file-explorer-table", "cellClicked"),
    State("current-directory", "data"),
    prevent_initial_call=True,
)
def open_selective_loader(cell_clicked, current_dir):
    """
    File Explorer에서 파일 클릭 시 Dialog 열기
    
    로직:
    1. 파일 경로 추출
    2. pl.scan_parquet()로 메타정보 읽기 (총 행 수, 컬럼 목록)
    3. Lock 상태 스캔 (scan_all_locks())
    4. 샘플 데이터 10행 읽기 (head(10))
    5. UI 렌더링
    """
    if not cell_clicked:
        return no_update, no_update, no_update, no_update
    
    file_path = get_clicked_file_path(cell_clicked, current_dir)
    
    # Polars lazy evaluation
    lazy_df = pl.scan_parquet(file_path)
    schema = lazy_df.schema
    total_rows = lazy_df.select(pl.count()).collect().item()
    
    # Lock 상태
    locks = scan_all_locks(file_path)
    lock_badge = generate_lock_badge(locks)
    
    # 샘플 데이터
    sample_df = lazy_df.head(10).collect()
    
    # UI 생성
    file_info = create_file_info_section(file_path, total_rows, schema, lock_badge)
    column_checkboxes = create_column_checkboxes(schema)
    
    return True, file_info, column_checkboxes, ""
```

#### 3.3.2 실시간 필터 미리보기

```python
@app.callback(
    Output("filter-preview-alert", "children"),
    Output("load-data-button", "disabled"),
    Input("filter-expression", "value"),
    Input("column-selection", "value"),
    Input("lock-mode-selection", "value"),
    State("current-file-path", "data"),
    prevent_initial_call=True,
)
def update_filter_preview(filter_expr, selected_cols, lock_mode, file_path):
    """
    필터 조건 변경 시 예상 정보 실시간 업데이트
    
    로직:
    1. 필터 조건 파싱 및 검증
    2. pl.scan_parquet().filter(expr).select(pl.count())로 행 수 계산
    3. 메모리 예측: (row_count × col_count × 8) / (1024^3) GB
    4. Lock 충돌 검사 (lock_mode가 "partial" 또는 "full"인 경우)
    5. 결과 텍스트 생성
    """
    if not filter_expr:
        # 필터 없음
        lazy_df = pl.scan_parquet(file_path)
        filtered_rows = lazy_df.select(pl.count()).collect().item()
    else:
        try:
            # 필터 적용
            lazy_df = pl.scan_parquet(file_path).filter(eval(filter_expr))
            filtered_rows = lazy_df.select(pl.count()).collect().item()
        except Exception as e:
            return f"❌ 필터 문법 오류: {str(e)}", True
    
    # 메모리 예측
    estimated_memory = (filtered_rows * len(selected_cols) * 8) / (1024**3)
    
    # Lock 충돌 검사
    if lock_mode in ["partial", "full"]:
        can_acquire, conflict_msg = check_lock_availability(
            file_path, lock_mode, filter_expr, filtered_rows
        )
        if not can_acquire:
            return f"⚠️ {conflict_msg}", True
    
    preview_text = f"✅ 예상: {filtered_rows:,} rows × {len(selected_cols)} cols ≈ {estimated_memory:.2f} GB"
    
    return preview_text, False
```

#### 3.3.3 Suggested Filters

```python
@app.callback(
    Output("filter-expression", "value", allow_duplicate=True),
    Input("filter-my-rows", "n_clicks"),
    Input("filter-result-rows", "n_clicks"),
    prevent_initial_call=True,
)
def apply_suggested_filter(my_clicks, result_clicks):
    """
    Suggested filter 버튼 클릭 시 자동 입력
    """
    ctx_id = ctx.triggered_id
    
    if ctx_id == "filter-my-rows":
        return f'col("user").eq("{CONFIG.USERNAME}")'
    elif ctx_id == "filter-result-rows":
        return 'col("waiver").eq("Result")'
    
    return no_update
```

#### 3.3.4 Load Data

```python
@app.callback(
    Output("selective-load-modal", "opened", allow_duplicate=True),
    Output("aggrid-overlay", "visible"),  # 로딩 표시
    Output("data-grid", "rowData"),
    Output("toaster", "children", allow_duplicate=True),
    Input("load-data-button", "n_clicks"),
    State("filter-expression", "value"),
    State("column-selection", "value"),
    State("lock-mode-selection", "value"),
    State("current-file-path", "data"),
    prevent_initial_call=True,
)
def load_data_with_selective_loading(n_clicks, filter_expr, selected_cols, lock_mode, file_path):
    """
    Load Data 버튼 클릭 시 데이터 로딩
    
    로직:
    1. 현재 ResultViewer가 Edit Mode인지 확인
       → Edit Mode라면 "먼저 저장하거나 Read Mode로 전환하세요" 경고
    2. 동일 사용자의 기존 Lock 확인
       → 있다면 자동 해제 (A안)
    3. Lock 충돌 검사 (최종 확인)
    4. Lock 획득 (lock_mode가 "partial" 또는 "full"인 경우)
    5. 데이터 로딩:
       - pl.scan_parquet().filter(expr).select(cols).collect()
    6. SSDF에 저장:
       - SSDF.dataframe = df
       - SSDF.file_path = file_path
       - SSDF.readonly = (lock_mode == "read")
    7. AG Grid에 렌더링
    8. Dialog 닫기
    """
    if not n_clicks:
        return no_update, no_update, no_update, no_update
    
    # Step 1: 현재 Edit Mode 체크
    if SSDF.get_current_mode() == "edit":
        toast = dbpc.Toast(
            message="현재 다른 파일을 편집 중입니다. 먼저 저장하거나 Read Mode로 전환하세요.",
            intent="warning",
            icon="warning-sign",
        )
        return no_update, no_update, no_update, [toast]
    
    # Step 2: 동일 사용자 기존 Lock 자동 해제
    release_existing_user_locks(file_path, CONFIG.USERNAME)
    
    # Step 3: Lock 충돌 검사 (최종)
    if lock_mode in ["partial", "full"]:
        can_acquire, conflict_msg = perform_lock_conflict_check(
            file_path, lock_mode, filter_expr
        )
        if not can_acquire:
            toast = dbpc.Toast(
                message=conflict_msg,
                intent="danger",
                icon="error",
            )
            return no_update, False, no_update, [toast]
    
    # Step 4: 로딩 표시 시작
    # (aggrid-overlay visible)
    
    try:
        # Step 5: Lock 획득
        if lock_mode == "full":
            success = acquire_full_lock(file_path, CONFIG.USERNAME)
        elif lock_mode == "partial":
            success = acquire_partial_lock(
                file_path, CONFIG.USERNAME, filter_expr, selected_cols
            )
        else:
            success = True  # Read-Only는 Lock 불필요
        
        if not success:
            raise Exception("Lock 획득 실패")
        
        # Step 6: 데이터 로딩
        lazy_df = pl.scan_parquet(file_path)
        
        if filter_expr:
            lazy_df = lazy_df.filter(eval(filter_expr))
        
        df = lazy_df.select(selected_cols).collect()
        
        # Step 7: SSDF 저장
        SSDF.dataframe = df
        SSDF.file_path = file_path
        SSDF.readonly = (lock_mode == "read")
        
        # Step 8: AG Grid 렌더링
        row_data = df.to_dicts()
        
        toast = dbpc.Toast(
            message=f"데이터 로딩 완료: {len(df):,} rows",
            intent="success",
            icon="tick",
        )
        
        return False, False, row_data, [toast]
        
    except Exception as e:
        logger.error(f"Data loading failed: {e}")
        toast = dbpc.Toast(
            message=f"데이터 로딩 실패: {str(e)}",
            intent="danger",
            icon="error",
        )
        return no_update, False, no_update, [toast]
```

---

## 4. Lock 시스템 상세 명세

### 4.1 Lock 충돌 검사 알고리즘

```python
def check_lock_conflict(file_path: str, mode: str, filter_expr: str = None) -> Tuple[bool, str]:
    """
    Lock 충돌 검사 통합 알고리즘
    
    Args:
        file_path: 대상 파일 경로
        mode: "read" | "partial" | "full"
        filter_expr: Partial Lock인 경우 필터 조건
    
    Returns:
        (can_proceed: bool, message: str)
    
    알고리즘:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    1. 모든 Lock 파일 스캔
       - result.lock (Full Lock)
       - result.*.lock (Partial Locks)
    
    2. Full Lock 존재 확인
       - 있고, 소유자가 나 → OK (재획득)
       - 있고, 소유자가 다른 사람 → FAIL
    
    3. 요청 모드가 Full Lock인 경우
       - 다른 Lock(Full or Partial) 존재 → FAIL
       - 없음 → OK
    
    4. 요청 모드가 Partial Lock인 경우
       - Full Lock 존재 → FAIL
       - Partial Lock들과 uniqid 교집합 확인
         - 교집합 있음 → FAIL
         - 교집합 없음 → OK
    
    5. 요청 모드가 Read-Only인 경우
       - 항상 OK (Lock 불필요)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    # Step 1: Lock 파일 스캔
    lock_files = scan_all_locks(file_path)
    # 반환 예: [
    #   {"type": "full", "user": "user1", "file": "result.lock"},
    #   {"type": "partial", "user": "user2", "file": "result.user2_20250108.lock", "uniqids": [...]}
    # ]
    
    # Step 2: Full Lock 확인
    full_lock = next((lock for lock in lock_files if lock["type"] == "full"), None)
    
    if full_lock:
        if full_lock["user"] == CONFIG.USERNAME:
            return True, ""  # 내가 이미 Full Lock 보유
        else:
            return False, f"파일이 {full_lock['user']}에 의해 완전히 잠겨있습니다."
    
    # Step 3: 요청 모드가 Full Lock
    if mode == "full":
        if len(lock_files) > 0:
            users = [lock["user"] for lock in lock_files]
            return False, f"다른 사용자가 편집 중입니다: {', '.join(users)}"
        else:
            return True, ""
    
    # Step 4: 요청 모드가 Partial Lock
    if mode == "partial":
        # uniqid 계산 (필터 조건 기반)
        my_uniqids = calculate_uniqids_from_filter(file_path, filter_expr)
        my_uniqids_set = set(my_uniqids)
        
        # 기존 Partial Lock들과 교집합 확인
        for lock in lock_files:
            if lock["type"] == "partial":
                if lock["user"] == CONFIG.USERNAME:
                    continue  # 내 Lock은 스킵
                
                locked_uniqids_set = set(lock["uniqids"])
                overlap = my_uniqids_set & locked_uniqids_set
                
                if len(overlap) > 0:
                    return False, f"충돌: {lock['user']}가 {len(overlap)}개 행을 편집 중입니다."
        
        return True, ""
    
    # Step 5: Read-Only
    if mode == "read":
        return True, ""
    
    return False, "알 수 없는 모드"
```

### 4.2 Lock 파일 스캔

```python
def scan_all_locks(file_path: str) -> List[dict]:
    """
    파일에 대한 모든 Lock 스캔
    
    Returns:
        List[dict]: Lock 정보 리스트
        [
            {
                "type": "full",
                "user": "user1",
                "file": "result.lock",
                "locked_at": "2025-01-08T12:30:00"
            },
            {
                "type": "partial",
                "user": "user2",
                "file": "result.user2_20250108123000.lock",
                "locked_at": "2025-01-08T12:30:00",
                "filter_expr": "col('Part').eq('CPU')",
                "uniqids": [1, 2, 3, ...]
            }
        ]
    """
    actual_path = convert_to_actual_path(file_path)
    basename = os.path.splitext(os.path.basename(actual_path))[0]
    directory = os.path.dirname(actual_path)
    
    locks = []
    
    # Full Lock 확인
    full_lock_path = os.path.join(directory, f"{basename}.lock")
    if os.path.exists(full_lock_path):
        try:
            with open(full_lock_path, 'r') as f:
                lock_data = json.load(f)
            lock_data["file"] = full_lock_path
            locks.append(lock_data)
        except Exception as e:
            logger.warning(f"손상된 Lock 파일: {full_lock_path}, {e}")
    
    # Partial Lock들 스캔
    for file in os.listdir(directory):
        if file.startswith(f"{basename}.") and file.endswith(".lock") and file != f"{basename}.lock":
            lock_path = os.path.join(directory, file)
            try:
                with open(lock_path, 'r') as f:
                    lock_data = json.load(f)
                lock_data["file"] = lock_path
                locks.append(lock_data)
            except Exception as e:
                logger.warning(f"손상된 Lock 파일: {lock_path}, {e}")
    
    return locks
```

### 4.3 uniqid 계산

```python
def calculate_uniqids_from_filter(file_path: str, filter_expr: str) -> List[int]:
    """
    필터 조건에 해당하는 uniqid 리스트 계산
    
    주의: 대용량 파일의 경우 시간이 걸릴 수 있음
          → 호출하는 곳에서 aggrid-overlay 표시 필수
    
    Args:
        file_path: Parquet 파일 경로
        filter_expr: Polars 필터 표현식 (문자열)
    
    Returns:
        List[int]: uniqid 리스트
    """
    actual_path = convert_to_actual_path(file_path)
    
    if not filter_expr:
        # 필터 없음 → 전체 uniqid
        df = pl.read_parquet(actual_path, columns=["uniqid"])
        return df["uniqid"].to_list()
    
    try:
        # Polars lazy evaluation
        uniqids = pl.scan_parquet(actual_path) \
                    .filter(eval(filter_expr)) \
                    .select("uniqid") \
                    .collect()["uniqid"].to_list()
        
        return uniqids
    except Exception as e:
        logger.error(f"uniqid 계산 실패: {e}")
        raise
```

### 4.4 Lock 획득

#### Full Lock

```python
def acquire_full_lock(file_path: str, user: str) -> bool:
    """
    Full Lock 획득
    
    Returns:
        bool: 성공 여부
    """
    actual_path = convert_to_actual_path(file_path)
    basename = os.path.splitext(os.path.basename(actual_path))[0]
    directory = os.path.dirname(actual_path)
    lock_path = os.path.join(directory, f"{basename}.lock")
    
    # Lock 파일 생성
    lock_data = {
        "user": user,
        "type": "full",
        "locked_at": datetime.now().isoformat(),
    }
    
    try:
        with open(lock_path, 'w') as f:
            json.dump(lock_data, f, indent=2)
        
        os.chmod(lock_path, 0o777)
        
        # NFS sync
        time.sleep(1)
        
        # 생성 확인
        if os.path.exists(lock_path):
            logger.info(f"Full Lock 획득: {lock_path}")
            return True
        else:
            logger.error(f"Full Lock 생성 실패: {lock_path}")
            return False
    
    except Exception as e:
        logger.error(f"Full Lock 생성 오류: {e}")
        return False
```

#### Partial Lock

```python
def acquire_partial_lock(file_path: str, user: str, filter_expr: str, selected_columns: List[str]) -> bool:
    """
    Partial Lock 획득
    
    Returns:
        bool: 성공 여부
    """
    actual_path = convert_to_actual_path(file_path)
    basename = os.path.splitext(os.path.basename(actual_path))[0]
    directory = os.path.dirname(actual_path)
    
    # uniqid 계산 (시간 소요 가능)
    locked_uniqids = calculate_uniqids_from_filter(file_path, filter_expr)
    
    # Lock 파일명 생성: result.{user}_{timestamp}.lock
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    lock_filename = f"{basename}.{user}_{timestamp}.lock"
    lock_path = os.path.join(directory, lock_filename)
    
    # Lock 데이터
    lock_data = {
        "user": user,
        "type": "partial",
        "locked_at": datetime.now().isoformat(),
        "filter_expr": filter_expr,
        "selected_columns": selected_columns,
        "locked_uniqids": locked_uniqids,  # 전체 리스트 포함
    }
    
    try:
        with open(lock_path, 'w') as f:
            json.dump(lock_data, f, indent=2)
        
        os.chmod(lock_path, 0o777)
        
        # NFS sync
        time.sleep(1)
        
        # 생성 확인
        if os.path.exists(lock_path):
            logger.info(f"Partial Lock 획득: {lock_path}, {len(locked_uniqids)} uniqids")
            return True
        else:
            logger.error(f"Partial Lock 생성 실패: {lock_path}")
            return False
    
    except Exception as e:
        logger.error(f"Partial Lock 생성 오류: {e}")
        return False
```

### 4.5 Lock 해제

```python
def release_lock(file_path: str, user: str) -> bool:
    """
    사용자의 Lock 해제 (Full 또는 Partial)
    
    Returns:
        bool: 성공 여부
    """
    actual_path = convert_to_actual_path(file_path)
    basename = os.path.splitext(os.path.basename(actual_path))[0]
    directory = os.path.dirname(actual_path)
    
    released = False
    
    # Full Lock 확인 및 해제
    full_lock_path = os.path.join(directory, f"{basename}.lock")
    if os.path.exists(full_lock_path):
        try:
            with open(full_lock_path, 'r') as f:
                lock_data = json.load(f)
            
            if lock_data.get("user") == user:
                os.remove(full_lock_path)
                logger.info(f"Full Lock 해제: {full_lock_path}")
                released = True
        except Exception as e:
            logger.error(f"Full Lock 해제 실패: {e}")
    
    # Partial Lock 확인 및 해제
    for file in os.listdir(directory):
        if file.startswith(f"{basename}.{user}_") and file.endswith(".lock"):
            lock_path = os.path.join(directory, file)
            try:
                os.remove(lock_path)
                logger.info(f"Partial Lock 해제: {lock_path}")
                released = True
            except Exception as e:
                logger.error(f"Partial Lock 해제 실패: {e}")
    
    # NFS sync
    if released:
        time.sleep(1)
    
    return released
```

### 4.6 동일 사용자 기존 Lock 자동 해제

```python
def release_existing_user_locks(file_path: str, user: str):
    """
    같은 파일에 대한 동일 사용자의 기존 Lock 자동 해제
    
    사용 시나리오:
    - User A가 Partial Lock A를 보유
    - User A가 같은 파일을 다시 Selective Load
    → 기존 Lock A를 자동 해제하고 새 Lock 생성
    """
    release_lock(file_path, user)
```

---

## 5. Merge Update 상세 명세

### 5.1 Merge Update 개요

**목적:** Partial Lock으로 작업한 영역만 원본 Parquet에 병합하여 저장

**핵심 원칙:**

1. 수정된 uniqid만 업데이트
2. 다른 사용자가 작업한 영역은 보존
3. Atomic 교체로 데이터 무결성 보장
4. 동시 저장 방지 (.merge.lock)

### 5.2 Merge Update 알고리즘

```python
def merge_update_safe(file_path: str, modified_df: pl.DataFrame, locked_uniqids: List[int], user: str) -> Tuple[bool, str]:
    """
    안전한 Merge Update (동시성 제어 포함)
    
    Args:
        file_path: 대상 파일 경로
        modified_df: 수정된 DataFrame (SSDF.dataframe)
        locked_uniqids: 내가 Lock한 uniqid 리스트
        user: 저장하는 사용자
    
    Returns:
        (success: bool, message: str)
    
    알고리즘:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    1. Merge Lock 획득 (.merge.lock 파일 생성, 최대 10초 대기)
    2. 백업 생성 (backup/result_v{N}_{timestamp}.parquet)
    3. 원본 Parquet 읽기
    4. Merge 수행:
       - 방법 A: Polars update() 사용
       - 방법 B: filter + concat + sort
    5. 임시 파일에 저장 (result.parquet.tmp)
    6. Atomic rename (os.replace)
    7. .version 파일 업데이트
    8. .meta 파일 업데이트 (gen_waive_metadata)
    9. Merge Lock 해제
    10. NFS sync
    
    실패 시:
    - Rollback: 백업에서 복원
    - Merge Lock 해제
    - 에러 로그 + 관리자 알림
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    actual_path = convert_to_actual_path(file_path)
    basename = os.path.splitext(os.path.basename(actual_path))[0]
    directory = os.path.dirname(actual_path)
    merge_lock_path = os.path.join(directory, f"{basename}.merge.lock")
    
    # Step 1: Merge Lock 획득
    acquired = try_acquire_merge_lock(merge_lock_path, timeout=10)
    if not acquired:
        return False, "다른 사용자가 저장 중입니다. 잠시 후 다시 시도하세요."
    
    backup_path = None
    
    try:
        # Step 2: 백업 생성
        backup_path = create_version_backup(actual_path)
        
        # Step 3: 원본 읽기
        original_df = pl.read_parquet(actual_path)
        
        # Step 4: Merge 수행
        merged_df = perform_merge(original_df, modified_df, locked_uniqids)
        
        # Step 5: 임시 파일 저장
        temp_path = f"{actual_path}.tmp"
        merged_df.write_parquet(temp_path)
        
        # Step 6: Atomic rename
        os.replace(temp_path, actual_path)
        os.chmod(actual_path, 0o777)
        
        # Step 7: .version 업데이트
        update_version_file(actual_path, backup_path, user, "partial_save", filter_expr=None)
        
        # Step 8: .meta 업데이트
        update_metadata_with_waive(actual_path, merged_df)
        
        # Step 9: Merge Lock 해제
        release_merge_lock(merge_lock_path)
        
        # Step 10: NFS sync
        time.sleep(1)
        
        logger.info(f"Merge Update 성공: {actual_path}")
        return True, "저장 완료"
    
    except Exception as e:
        logger.error(f"Merge Update 실패: {e}")
        
        # Rollback
        if backup_path and os.path.exists(backup_path):
            try:
                shutil.copy(backup_path, actual_path)
                logger.info(f"Rollback 완료: {backup_path} → {actual_path}")
            except Exception as rollback_error:
                logger.critical(f"Rollback 실패: {rollback_error}")
                # 관리자 알림 (구현 방법은 시스템에 맞게)
                notify_admin(f"CRITICAL: Rollback 실패 {actual_path}")
        
        # Merge Lock 해제
        release_merge_lock(merge_lock_path)
        
        return False, f"저장 실패: {str(e)}"
```

### 5.3 Merge 방법 구현

```python
def perform_merge(original_df: pl.DataFrame, modified_df: pl.DataFrame, locked_uniqids: List[int]) -> pl.DataFrame:
    """
    DataFrame Merge 수행
    
    두 가지 방법 비교:
    - 방법 A: Polars update() (추천)
    - 방법 B: filter + concat + sort
    
    성능 테스트 후 빠른 방법 채택
    """
    # 방법 A: Polars update() (Polars 0.20.0+)
    try:
        merged_df = original_df.update(
            modified_df.filter(pl.col("uniqid").is_in(locked_uniqids)),
            on="uniqid"
        )
        return merged_df
    except Exception as e:
        logger.warning(f"update() 실패, concat 방식 사용: {e}")
    
    # 방법 B: filter + concat + sort
    # 1. 수정된 행만 추출
    modified_rows = modified_df.filter(pl.col("uniqid").is_in(locked_uniqids))
    
    # 2. 원본에서 수정되지 않은 행 추출
    unchanged_rows = original_df.filter(~pl.col("uniqid").is_in(locked_uniqids))
    
    # 3. Concat
    merged_df = pl.concat([modified_rows, unchanged_rows])
    
    # 4. Sort
    merged_df = merged_df.sort("uniqid")
    
    return merged_df
```

### 5.4 Merge Lock 관리

```python
def try_acquire_merge_lock(lock_path: str, timeout: int = 10) -> bool:
    """
    Merge Lock 획득 시도 (최대 timeout초 대기)
    
    Returns:
        bool: 획득 성공 여부
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if not os.path.exists(lock_path):
            try:
                # Lock 파일 생성
                with open(lock_path, 'w') as f:
                    json.dump({
                        "user": CONFIG.USERNAME,
                        "acquired_at": datetime.now().isoformat(),
                    }, f)
                
                os.chmod(lock_path, 0o777)
                
                # NFS sync
                time.sleep(0.5)
                
                # 생성 확인
                if os.path.exists(lock_path):
                    logger.info(f"Merge Lock 획득: {lock_path}")
                    return True
            except Exception as e:
                logger.warning(f"Merge Lock 획득 시도 실패: {e}")
        
        # 0.5초 대기 후 재시도
        time.sleep(0.5)
    
    logger.error(f"Merge Lock 획득 타임아웃: {lock_path}")
    return False


def release_merge_lock(lock_path: str):
    """
    Merge Lock 해제
    """
    if os.path.exists(lock_path):
        try:
            os.remove(lock_path)
            logger.info(f"Merge Lock 해제: {lock_path}")
        except Exception as e:
            logger.error(f"Merge Lock 해제 실패: {e}")
```

### 5.5 저장 시 호출 지점

```python
# components/menu/home/item/save.py

@app.callback(
    Output("toaster", "children", allow_duplicate=True),
    Input("save-to-workspace-button", "n_clicks"),
    prevent_initial_call=True,
)
def save_to_workspace(n_clicks):
    """
    WORKSPACE 저장 (Merge Update 사용)
    """
    if not n_clicks:
        return no_update
    
    # Read Mode 체크
    if SSDF.readonly:
        toast = dbpc.Toast(
            message="Read Mode에서는 WORKSPACE에 저장할 수 없습니다.",
            intent="warning",
            icon="warning-sign",
        )
        return [toast]
    
    file_path = SSDF.file_path
    modified_df = SSDF.dataframe
    
    # Lock 정보 가져오기
    locks = scan_all_locks(file_path)
    my_lock = next((lock for lock in locks if lock["user"] == CONFIG.USERNAME), None)
    
    if not my_lock:
        toast = dbpc.Toast(
            message="Lock이 없습니다. 저장할 수 없습니다.",
            intent="danger",
            icon="error",
        )
        return [toast]
    
    # Full Lock vs Partial Lock
    if my_lock["type"] == "full":
        # 전체 덮어쓰기
        success = save_full(file_path, modified_df, CONFIG.USERNAME)
    else:
        # Merge Update
        success, message = merge_update_safe(
            file_path,
            modified_df,
            my_lock["locked_uniqids"],
            CONFIG.USERNAME
        )
    
    if success:
        toast = dbpc.Toast(
            message="저장 완료",
            intent="success",
            icon="tick",
        )
    else:
        toast = dbpc.Toast(
            message=f"저장 실패: {message}",
            intent="danger",
            icon="error",
        )
    
    return [toast]
```

---

## 6. Version Management 상세 명세

### 6.1 버전 백업 생성

```python
def create_version_backup(file_path: str) -> str:
    """
    버전 백업 생성
    
    Args:
        file_path: 원본 Parquet 파일 경로
    
    Returns:
        str: 백업 파일 경로
    
    로직:
    1. backup/ 폴더 생성 (없으면)
    2. .version 파일 읽기 → 다음 버전 번호 계산
    3. {basename}_v{N}_{timestamp}.parquet로 복사
    4. chmod 0o777
    """
    actual_path = convert_to_actual_path(file_path)
    basename = os.path.splitext(os.path.basename(actual_path))[0]
    directory = os.path.dirname(actual_path)
    backup_dir = os.path.join(directory, "backup")
    
    # backup/ 폴더 생성
    os.makedirs(backup_dir, exist_ok=True)
    
    # 다음 버전 번호
    version_file_path = os.path.join(directory, f"{basename}.version")
    next_version = get_next_version_number(version_file_path)
    
    # 백업 파일명
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{basename}_v{next_version}_{timestamp}.parquet"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # 복사
    shutil.copy(actual_path, backup_path)
    os.chmod(backup_path, 0o777)
    
    logger.info(f"버전 백업 생성: {backup_path}")
    return backup_path


def get_next_version_number(version_file_path: str) -> int:
    """
    다음 버전 번호 계산
    """
    if not os.path.exists(version_file_path):
        return 1
    
    try:
        with open(version_file_path, 'r') as f:
            version_data = json.load(f)
        return version_data.get("current_version", 0) + 1
    except Exception as e:
        logger.warning(f".version 파일 읽기 실패: {e}")
        return 1
```

### 6.2 .version 파일 업데이트

```python
def update_version_file(
    file_path: str,
    backup_path: str,
    user: str,
    action: str,
    filter_expr: str = None
):
    """
    .version 파일 업데이트
    
    Args:
        file_path: 원본 파일 경로
        backup_path: 백업 파일 경로
        user: 저장한 사용자
        action: "full_save" | "partial_save"
        filter_expr: Partial Save인 경우 필터 조건
    """
    actual_path = convert_to_actual_path(file_path)
    basename = os.path.splitext(os.path.basename(actual_path))[0]
    directory = os.path.dirname(actual_path)
    version_file_path = os.path.join(directory, f"{basename}.version")
    
    # 기존 버전 정보 읽기
    if os.path.exists(version_file_path):
        with open(version_file_path, 'r') as f:
            version_data = json.load(f)
    else:
        version_data = {
            "current_version": 0,
            "history": []
        }
    
    # 새 버전 추가
    new_version = version_data["current_version"] + 1
    backup_filename = os.path.basename(backup_path)
    
    history_entry = {
        "version": new_version,
        "backup_file": backup_filename,
        "created_by": user,
        "created_at": datetime.now().isoformat(),
        "action": action,
        "filter_expr": filter_expr,
        "description": f"{action} by {user}",
    }
    
    version_data["current_version"] = new_version
    version_data["history"].append(history_entry)
    
    # 저장
    with open(version_file_path, 'w') as f:
        json.dump(version_data, f, indent=2)
    
    os.chmod(version_file_path, 0o777)
    
    logger.info(f".version 업데이트: v{new_version}")
```

### 6.3 Version Viewer UI

```python
# components/menu/home/item/workspace/version_viewer.py

def create_version_viewer_layout():
    """
    버전 뷰어 UI
    """
    return dmc.Modal(
        id="version-viewer-modal",
        title="Version History",
        size="xl",
        children=[
            dmc.Stack([
                # 버전 테이블
                html.Div(id="version-table-container"),
                
                # 액션 버튼
                dmc.Group([
                    dmc.Button(
                        "Close",
                        id="version-viewer-close",
                        variant="outline",
                    ),
                ], position="right"),
            ]),
        ],
    )


@app.callback(
    Output("version-viewer-modal", "opened"),
    Output("version-table-container", "children"),
    Input("view-versions-button", "n_clicks"),
    State("current-file-path", "data"),
    prevent_initial_call=True,
)
def open_version_viewer(n_clicks, file_path):
    """
    버전 뷰어 열기
    """
    if not n_clicks:
        return no_update, no_update
    
    # .version 파일 읽기
    versions = load_version_history(file_path)
    
    # 테이블 생성
    table = create_version_table(versions, file_path)
    
    return True, table


def create_version_table(versions: List[dict], file_path: str):
    """
    버전 테이블 생성
    """
    rows = []
    
    for v in reversed(versions):  # 최신 버전부터
        is_current = (v["version"] == versions[-1]["version"])
        
        row = html.Tr([
            html.Td(f"v{v['version']}" + (" (Current)" if is_current else "")),
            html.Td(v["created_by"]),
            html.Td(v["created_at"][:19]),  # 초까지만
            html.Td(v["action"]),
            html.Td(v.get("filter_expr", "-")),
            html.Td([
                dmc.Button(
                    "Restore",
                    id={"type": "restore-version", "version": v["version"]},
                    size="xs",
                    color="orange",
                    disabled=is_current,
                ),
                dmc.Button(
                    "Download",
                    id={"type": "download-version", "version": v["version"]},
                    size="xs",
                    variant="light",
                    style={"marginLeft": "5px"},
                ),
            ]),
        ])
        rows.append(row)
    
    table = dmc.Table([
        html.Thead([
            html.Tr([
                html.Th("Version"),
                html.Th("Saved By"),
                html.Th("Saved At"),
                html.Th("Action"),
                html.Th("Filter"),
                html.Th("Actions"),
            ]),
        ]),
        html.Tbody(rows),
    ], striped=True, highlightOnHover=True)
    
    return table
```

### 6.4 버전 복원

```python
@app.callback(
    Output("toaster", "children", allow_duplicate=True),
    Output("version-viewer-modal", "opened", allow_duplicate=True),
    Input({"type": "restore-version", "version": ALL}, "n_clicks"),
    State("current-file-path", "data"),
    prevent_initial_call=True,
)
def restore_version(n_clicks, file_path):
    """
    버전 복원
    
    로직:
    1. Lock 확인 → 있으면 복원 불가
    2. 백업 파일 복사
    3. .meta 업데이트
    4. Toast 알림
    """
    if not any(n_clicks):
        return no_update, no_update
    
    version = ctx.triggered_id["version"]
    
    # Lock 확인
    locks = scan_all_locks(file_path)
    if len(locks) > 0:
        toast = dbpc.Toast(
            message="파일이 Lock되어 있습니다. 먼저 Lock을 해제하세요.",
            intent="warning",
            icon="warning-sign",
        )
        return [toast], no_update
    
    # 복원 수행
    try:
        success = perform_version_restore(file_path, version)
        
        if success:
            toast = dbpc.Toast(
                message=f"v{version}으로 복원되었습니다.",
                intent="success",
                icon="tick",
            )
            return [toast], False  # Modal 닫기
        else:
            toast = dbpc.Toast(
                message="복원 실패",
                intent="danger",
                icon="error",
            )
            return [toast], no_update
    
    except Exception as e:
        logger.error(f"버전 복원 실패: {e}")
        toast = dbpc.Toast(
            message=f"복원 실패: {str(e)}",
            intent="danger",
            icon="error",
        )
        return [toast], no_update


def perform_version_restore(file_path: str, version: int) -> bool:
    """
    버전 복원 수행
    """
    actual_path = convert_to_actual_path(file_path)
    basename = os.path.splitext(os.path.basename(actual_path))[0]
    directory = os.path.dirname(actual_path)
    
    # .version 파일에서 백업 파일명 찾기
    version_file_path = os.path.join(directory, f"{basename}.version")
    
    with open(version_file_path, 'r') as f:
        version_data = json.load(f)
    
    target_version = next(
        (v for v in version_data["history"] if v["version"] == version),
        None
    )
    
    if not target_version:
        raise Exception(f"버전 {version}을 찾을 수 없습니다.")
    
    backup_filename = target_version["backup_file"]
    backup_path = os.path.join(directory, "backup", backup_filename)
    
    if not os.path.exists(backup_path):
        raise Exception(f"백업 파일이 없습니다: {backup_path}")
    
    # 현재 버전 백업 (복원 전)
    current_backup = create_version_backup(actual_path)
    
    # 복원
    shutil.copy(backup_path, actual_path)
    os.chmod(actual_path, 0o777)
    
    # .meta 업데이트
    df = pl.read_parquet(actual_path)
    update_metadata_with_waive(actual_path, df)
    
    # NFS sync
    time.sleep(1)
    
    logger.info(f"버전 복원 완료: v{version}")
    return True
```

---

## 7. 에러 처리 및 예외 상황

### 7.1 에러 분류

```python
# 에러 유형별 처리 방식

ERROR_TYPES = {
    # 치명적 에러 (Modal Dialog)
    "CRITICAL": {
        "LOCK_CONFLICT": "다른 사용자가 이미 이 영역을 편집 중입니다.",
        "FULL_LOCK_EXISTS": "파일이 {user}에 의해 완전히 잠겨있습니다.",
        "FILTER_SYNTAX_ERROR": "필터 조건 문법이 올바르지 않습니다.",
        "NFS_SYNC_FAILED": "네트워크 동기화 실패. 다시 시도해주세요.",
        "MERGE_CONFLICT": "저장 중 충돌이 발생했습니다. 백업을 확인하세요.",
        "EDITING_ANOTHER_FILE": "현재 다른 파일을 편집 중입니다. 먼저 저장하거나 Read Mode로 전환하세요.",
    },
    
    # 경고 (Toast, 자동 사라짐)
    "WARNING": {
        "READ_MODE_SAVE": "Read Mode에서는 WORKSPACE에 저장할 수 없습니다.",
        "NO_LOCK": "Lock이 없습니다. 저장할 수 없습니다.",
        "LOCK_RELEASE_FAILED": "Lock 해제 실패. 수동으로 해제하세요.",
    },
    
    # 정보 (Toast)
    "INFO": {
        "LOCK_ACQUIRED": "Lock 획득 완료",
        "DATA_LOADED": "데이터 로딩 완료: {rows} rows",
        "SAVED": "저장 완료",
    },
}
```

### 7.2 에러 핸들러

```python
def handle_error(error_code: str, **kwargs) -> dbpc.Toast:
    """
    에러 코드에 따른 Toast 생성
    
    Args:
        error_code: 에러 코드 ("LOCK_CONFLICT" 등)
        **kwargs: 메시지 포맷용 변수
    
    Returns:
        dbpc.Toast
    """
    # 에러 타입 찾기
    error_type = None
    message = None
    
    for etype, errors in ERROR_TYPES.items():
        if error_code in errors:
            error_type = etype
            message = errors[error_code].format(**kwargs)
            break
    
    if not message:
        message = f"알 수 없는 에러: {error_code}"
        error_type = "CRITICAL"
    
    # Toast 생성
    if error_type == "CRITICAL":
        intent = "danger"
        icon = "error"
    elif error_type == "WARNING":
        intent = "warning"
        icon = "warning-sign"
    else:
        intent = "primary"
        icon = "info-sign"
    
    return dbpc.Toast(
        message=message,
        intent=intent,
        icon=icon,
        timeout=5000 if error_type != "CRITICAL" else 0,  # 치명적 에러는 자동 닫기 X
    )


# 사용 예시
toast = handle_error("LOCK_CONFLICT")
toast = handle_error("FULL_LOCK_EXISTS", user="deepwonwoo")
toast = handle_error("DATA_LOADED", rows=45000)
```

### 7.3 예외 상황 처리

#### 1. 현재 다른 파일 편집 중

```python
def check_current_edit_mode() -> Tuple[bool, str]:
    """
    현재 ResultViewer가 Edit Mode인지 확인
    
    Returns:
        (is_editing: bool, message: str)
    """
    if SSDF.get_current_mode() == "edit":
        return True, "현재 다른 파일을 편집 중입니다."
    return False, ""


# Selective Loading Dialog 열기 전 체크
is_editing, msg = check_current_edit_mode()
if is_editing:
    return handle_error("EDITING_ANOTHER_FILE")
```

#### 2. 네트워크 지연 (NFS)

```python
def safe_nfs_operation(operation_func, *args, **kwargs):
    """
    NFS 작업 래퍼 (재시도 로직 포함)
    
    Args:
        operation_func: 실행할 함수
        *args, **kwargs: 함수 인자
    
    Returns:
        함수 실행 결과
    """
    max_retries = 3
    retry_delay = 1  # 초
    
    for attempt in range(max_retries):
        try:
            result = operation_func(*args, **kwargs)
            
            # NFS sync
            time.sleep(1)
            
            return result
        
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"NFS 작업 재시도 ({attempt + 1}/{max_retries}): {e}")
                time.sleep(retry_delay)
            else:
                logger.error(f"NFS 작업 실패: {e}")
                raise


# 사용 예시
safe_nfs_operation(os.remove, lock_path)
```

#### 3. Lock 파일 손상

```python
def validate_lock_file(lock_path: str) -> Tuple[bool, dict]:
    """
    Lock 파일 검증
    
    Returns:
        (is_valid: bool, lock_data: dict)
    """
    try:
        with open(lock_path, 'r') as f:
            lock_data = json.load(f)
        
        # 필수 필드 확인
        required_fields = ["user", "type", "locked_at"]
        for field in required_fields:
            if field not in lock_data:
                logger.warning(f"Lock 파일 손상: {lock_path}, 필드 누락 {field}")
                return False, {}
        
        return True, lock_data
    
    except Exception as e:
        logger.warning(f"Lock 파일 읽기 실패: {lock_path}, {e}")
        return False, {}


# scan_all_locks에서 사용
is_valid, lock_data = validate_lock_file(lock_path)
if is_valid:
    locks.append(lock_data)
else:
    # 손상된 Lock 무시
    pass
```

#### 4. Rollback 실패

```python
def notify_admin(message: str):
    """
    관리자에게 알림 전송
    
    구현 방법:
    - devworks_api.py를 통한 메시지 전송
    - 또는 에러 로그 파일에 CRITICAL 레벨 기록
    """
    logger.critical(f"[ADMIN ALERT] {message}")
    
    # DevWorks 메시지 전송 (구현되어 있다면)
    try:
        from utils.devworks_api import send_message
        send_message(
            recipient="admin@company.com",
            subject="ResultViewer CRITICAL ERROR",
            body=message,
        )
    except Exception as e:
        logger.error(f"관리자 알림 전송 실패: {e}")
```

---

## 8. 성능 최적화 및 테스트 전략

### 8.1 성능 최적화

#### 1. Polars Lazy Evaluation

```python
# ❌ 비효율적
df = pl.read_parquet(file_path)
filtered_df = df.filter(col("Part").eq("CPU"))
row_count = len(filtered_df)

# ✅ 효율적 (Lazy Evaluation)
row_count = pl.scan_parquet(file_path) \
              .filter(col("Part").eq("CPU")) \
              .select(pl.count()) \
              .collect().item()
```

#### 2. 컬럼 선택 최적화

```python
# 필요한 컬럼만 읽기
df = pl.scan_parquet(file_path, columns=["uniqid", "waiver", "Part"]) \
       .collect()
```

#### 3. Merge Update 최적화

```python
# update() vs concat() 성능 비교 테스트
import time

def benchmark_merge_methods(original_df, modified_df, uniqids):
    # 방법 A: update()
    start = time.time()
    result_a = original_df.update(
        modified_df.filter(pl.col("uniqid").is_in(uniqids)),
        on="uniqid"
    )
    time_a = time.time() - start
    
    # 방법 B: concat()
    start = time.time()
    modified_rows = modified_df.filter(pl.col("uniqid").is_in(uniqids))
    unchanged_rows = original_df.filter(~pl.col("uniqid").is_in(uniqids))
    result_b = pl.concat([modified_rows, unchanged_rows]).sort("uniqid")
    time_b = time.time() - start
    
    logger.info(f"update(): {time_a:.3f}s, concat(): {time_b:.3f}s")
    
    # 빠른 방법 반환
    return result_a if time_a < time_b else result_b
```

### 8.2 테스트 전략

#### 1. E2E 테스트 (Playwright MCP)

**필수 테스트 시나리오:**

```python
# tests/test_selective_loading.py

def test_selective_loading_basic():
    """
    기본 Selective Loading 테스트
    
    시나리오:
    1. ResultViewer 실행
    2. WORKSPACE Explorer 열기
    3. 파일 클릭 → Dialog 표시 확인
    4. Lock 모드 선택 (Read-Only)
    5. Load Data 클릭
    6. Grid에 데이터 표시 확인
    """
    pass


def test_partial_lock_acquisition():
    """
    Partial Lock 획득 테스트
    
    시나리오:
    1. User A: CPU 데이터 Partial Lock 획득
    2. Lock 파일 생성 확인
    3. User B (다른 Python 인스턴스): GPU 데이터 Partial Lock 획득 (성공)
    4. User C: CPU 데이터 Partial Lock 시도 (실패)
    """
    pass


def test_merge_update():
    """
    Merge Update 테스트
    
    시나리오:
    1. User A: CPU 데이터 편집 후 저장
    2. User B: GPU 데이터 편집 후 저장
    3. 원본 파일에 두 사용자 변경사항 모두 반영 확인
    4. 백업 파일 생성 확인
    5. .version 파일 업데이트 확인
    """
    pass


def test_lock_conflict():
    """
    Lock 충돌 테스트
    
    시나리오:
    1. User A: Full Lock 획득
    2. User B: Partial Lock 시도 → 실패 메시지 확인
    3. User A: Lock 해제
    4. User B: Partial Lock 재시도 → 성공
    """
    pass


def test_version_restore():
    """
    버전 복원 테스트
    
    시나리오:
    1. 데이터 수정 및 저장 (v1, v2, v3 생성)
    2. Version Viewer 열기
    3. v1으로 복원
    4. 데이터 확인
    """
    pass
```

#### 2. 다중 사용자 시뮬레이션

```python
# tests/test_concurrent_access.py

import subprocess
import time

def test_concurrent_partial_locks():
    """
    다중 Python 인스턴스로 동시 접속 테스트
    """
    # User A 인스턴스 시작
    process_a = subprocess.Popen([
        "python", "app.py",
        "--username", "user_a",
        "--port", "8050"
    ])
    
    time.sleep(5)  # 초기화 대기
    
    # User B 인스턴스 시작
    process_b = subprocess.Popen([
        "python", "app.py",
        "--username", "user_b",
        "--port", "8051"
    ])
    
    time.sleep(5)
    
    # Playwright로 두 브라우저 제어
    # ...
    
    # 테스트 후 정리
    process_a.terminate()
    process_b.terminate()
```

#### 3. 성능 벤치마크

```python
# tests/test_performance.py

def test_large_file_loading():
    """
    대용량 파일 로딩 성능 테스트
    
    목표:
    - 1GB Parquet → 5초 이내 메타정보 표시
    - 필터링 (10만 행 → 1만 행) → 10초 이내
    """
    pass


def test_merge_update_performance():
    """
    Merge Update 성능 테스트
    
    목표:
    - 1억 행 DataFrame에서 1만 행 병합 → 30초 이내
    """
    pass
```

### 8.3 로딩 표시 (UX)

**필수:** 시간이 걸리는 모든 작업에 로딩 표시

```python
# 로딩 표시 패턴

# 1. aggrid-overlay 사용 (전체 화면)
@app.callback(
    Output("aggrid-overlay", "visible"),
    Input("some-button", "n_clicks"),
)
def show_loading(n_clicks):
    # 작업 시작
    return True
    
    # 작업 완료 후
    return False


# 2. dmc.Loader 사용 (부분 영역)
dmc.LoadingOverlay(
    visible=True,
    loaderProps={"variant": "dots", "color": "blue"},
    children=[
        html.Div(id="content-area")
    ],
)


# 3. Progress Bar
dmc.Progress(
    value=progress_percent,
    label=f"{progress_percent}%",
    size="xl",
    radius="xl",
    striped=True,
    animate=True,
)
```







# WORKSPACE 2.0 상세 테스트 시나리오

## 1. 기능별 단위 테스트

### 1.1 File Lock 관리 테스트

```python
def test_file_lock_lifecycle():
    """
    Lock 파일 생명주기 테스트
    
    시나리오:
    1. Read Mode로 파일 열기 → .lock 파일 미생성 확인
    2. Edit Mode 전환 → .lock 파일 생성 확인
    3. Lock 파일 내용 검증 (username, timestamp, pid)
    4. Read Mode 전환 → .lock 파일 삭제 확인
    5. 비정상 종료 시뮬레이션 → orphaned lock 확인
    6. 앱 재시작 → orphaned lock 자동 정리 확인
    """
    
def test_lock_conflict_resolution():
    """
    Lock 충돌 해결 테스트
    
    시나리오:
    1. User A: 파일을 Edit Mode로 열기
    2. User B: 같은 파일 Edit Mode 시도
    3. 에러 메시지 확인: "파일이 {username}에 의해 편집 중입니다"
    4. User B: Read Mode로는 열기 가능 확인
    5. User A: 작업 완료 및 모드 전환
    6. User B: Edit Mode 재시도 → 성공
    """

def test_stale_lock_detection():
    """
    Stale Lock 감지 및 처리
    
    시나리오:
    1. Lock 파일 생성 (프로세스 종료 상태)
    2. 30분 이상 경과 시뮬레이션
    3. 새 사용자 접근 시 stale lock 감지
    4. 관리자 알림 또는 자동 해제 옵션 제공
    """
```

### 1.2 데이터 저장 및 동기화 테스트

```python
def test_save_to_workspace():
    """
    Workspace 저장 기능 테스트
    
    시나리오:
    1. 데이터 수정 (10개 셀)
    2. Save to Workspace 실행
    3. 백업 파일 생성 확인 (backup/*)
    4. 원본 파일 업데이트 확인
    5. .version 파일 업데이트 확인
    6. .meta 파일 통계 업데이트 확인
    7. 다른 사용자가 즉시 변경사항 확인 가능
    """

def test_concurrent_save_handling():
    """
    동시 저장 처리 테스트
    
    시나리오:
    1. User A: 대용량 데이터(1M rows) 저장 시작
    2. User B: 같은 파일 저장 시도 (1초 후)
    3. Merge lock 대기 메시지 확인
    4. User A 저장 완료
    5. User B 자동 재시도 및 성공
    6. 두 사용자 변경사항 모두 반영 확인
    """

def test_save_failure_recovery():
    """
    저장 실패 복구 테스트
    
    시나리오:
    1. 저장 중 네트워크 오류 시뮬레이션
    2. 임시 파일(.tmp) 존재 확인
    3. 롤백 프로세스 실행
    4. 백업에서 복원 확인
    5. 사용자에게 재시도 옵션 제공
    """
```

### 1.3 모드 전환 테스트

```python
def test_mode_transition_data_integrity():
    """
    모드 전환 시 데이터 무결성 테스트
    
    시나리오:
    1. Read Mode에서 데이터 수정 (메모리만)
    2. Edit Mode 전환 시도
    3. 경고 메시지: "Read Mode의 변경사항이 사라집니다"
    4. 확인 → 원본 데이터 다시 로드
    5. 취소 → Read Mode 유지, 수정사항 보존
    """

def test_edit_to_read_transition():
    """
    Edit → Read 모드 전환 테스트
    
    시나리오:
    1. Edit Mode에서 데이터 수정
    2. 저장하지 않고 Read Mode 전환 시도
    3. 경고: "저장되지 않은 변경사항이 있습니다"
    4. 저장 후 전환 / 저장 안함 / 취소 옵션
    5. 각 옵션별 동작 확인
    """
```

## 2. 통합 테스트 시나리오

### 2.1 다중 사용자 협업 시나리오

```python
def test_team_collaboration_workflow():
    """
    실제 팀 협업 워크플로우 테스트
    
    시나리오:
    1. Manager: 새 프로젝트 폴더 생성 (/D1b/R01/FULLCHIP/DRIVER_KEEPER/)
    2. Engineer A: result.parquet 업로드 (10M rows)
    3. Engineer B: 파일 열기 (Read Mode) → 데이터 분석
    4. Engineer A: Edit Mode로 waiver 컬럼 수정 시작
    5. Engineer B: Edit Mode 시도 → 실패 (Already locked)
    6. Engineer A: 수정 완료 및 저장
    7. Engineer B: 자동 새로고침 알림 → 데이터 재로드
    8. Engineer B: Edit Mode로 전환 성공
    9. Manager: Version history 확인
    10. 모든 변경사항 추적 가능 확인
    """
```

### 2.2 대용량 데이터 처리 시나리오

```python
def test_large_data_performance():
    """
    대용량 데이터 성능 테스트
    
    데이터셋:
    - 100M rows × 15 columns Parquet file
    - 파일 크기: ~5GB
    
    시나리오:
    1. 파일 메타데이터 로딩 시간 측정 (목표: <2초)
    2. 샘플 데이터 프리뷰 로딩 (목표: <5초)
    3. Full 데이터 로딩 시간 측정
    4. 필터링 적용 (10M → 100K rows)
    5. Grid 렌더링 시간 측정 (목표: <3초)
    6. 스크롤 성능 확인 (lag 없음)
    7. 편집 모드 전환 시간
    8. 1000개 셀 동시 수정
    9. 저장 시간 측정 (목표: <30초)
    10. 메모리 사용량 모니터링 (목표: <2GB)
    """
```

### 2.3 오류 복구 시나리오

```python
def test_disaster_recovery():
    """
    재해 복구 시나리오 테스트
    
    시나리오:
    1. 3명의 사용자가 동시 작업 중
    2. NFS 연결 일시 중단 (10초)
    3. 자동 재연결 시도 확인
    4. 작업 중단 없이 계속 진행
    5. 연결 복구 후 자동 동기화
    6. 데이터 무결성 확인
    """

def test_corrupt_file_handling():
    """
    손상된 파일 처리 테스트
    
    시나리오:
    1. Parquet 파일 일부 손상 시뮬레이션
    2. 파일 열기 시도
    3. 에러 감지 및 사용자 알림
    4. 백업에서 복원 옵션 제공
    5. 복원 프로세스 실행
    6. 정상 동작 확인
    """
```

## 3. 성능 벤치마크 테스트

### 3.1 부하 테스트

```python
def test_concurrent_user_load():
    """
    동시 사용자 부하 테스트
    
    시나리오:
    - 50명 동시 접속
    - 각 사용자별 다른 파일 작업
    - 5명은 동일 파일 Read Mode
    - 10명은 데이터 편집 중
    - 나머지는 파일 브라우징
    
    측정 항목:
    - 응답 시간
    - CPU/Memory 사용량
    - Lock 경합 발생 빈도
    - 에러 발생률
    """
```

### 3.2 메모리 최적화 테스트

```python
def test_memory_optimization():
    """
    메모리 최적화 효과 측정
    
    비교 시나리오:
    1. 전체 데이터 로드 vs Selective Loading
       - 100M rows 전체 vs 1M rows 필터링
       - 메모리 사용량 90% 감소 확인
    
    2. 컬럼 선택 효과
       - 50 columns 전체 vs 10 columns 선택
       - 메모리 사용량 80% 감소 확인
    """
```

## 4. 사용자 수용성 테스트 (UAT)

### 4.1 실제 업무 시나리오

```
1. Signoff 결과 분석 워크플로우
   - STAR 툴 결과 파일 업로드
   - Violation 데이터 필터링
   - Waiver 상태 업데이트
   - 팀원들과 리뷰
   - 최종 승인 및 보고서 생성

2. Cross-team 협업 시나리오
   - Design 팀: 초기 데이터 업로드
   - Verification 팀: 검증 결과 추가
   - Physical 팀: Layout 정보 병합
   - Manager: 전체 진행상황 모니터링

3. 긴급 수정 시나리오
   - Production 이슈 발생
   - 여러 엔지니어 동시 분석
   - 실시간 데이터 공유 및 수정
   - 빠른 의사결정 지원
```

## 5. 자동화 테스트 전략

### 5.1 CI/CD 파이프라인 통합

```yaml
test_pipeline:
  - unit_tests:
      - test_data_validation
      - test_lock_manager
      - test_file_operations
  
  - integration_tests:
      - test_mode_transitions
      - test_save_operations
      - test_concurrent_access
  
  - e2e_tests:
      - test_user_workflows
      - test_collaboration
  
  - performance_tests:
      - test_load_times
      - test_memory_usage
  
  - regression_tests:
      - test_backward_compatibility
      - test_existing_features
```

### 5.2 테스트 커버리지 목표

- Unit Test: 80% 이상
- Integration Test: Core 기능 100%
- E2E Test: 주요 시나리오 100%
- Performance: 모든 KPI 달성

## 6. 테스트 데이터 준비

### 6.1 테스트 데이터셋

```python
test_datasets = {
    "small": "1K rows × 10 cols",      # 빠른 기능 테스트
    "medium": "100K rows × 20 cols",   # 일반 테스트
    "large": "10M rows × 30 cols",     # 성능 테스트
    "xlarge": "100M rows × 50 cols",   # 스트레스 테스트
}
```

### 6.2 테스트 시나리오별 데이터

- 정상 데이터: 표준 Parquet 형식
- 엣지 케이스: 특수 문자, NULL 값, 극단값
- 손상 데이터: 파일 손상 시뮬레이션
- 레거시 데이터: 이전 버전 호환성

## 7. 테스트 실행 계획

### Phase 1: 개발 중 테스트 (현재)

- 개발과 동시에 unit test 작성
- 기능 구현 직후 integration test
- 매일 자동화 테스트 실행

### Phase 2: 통합 테스트 (개발 완료 후)

- 전체 기능 통합 테스트
- 다중 사용자 시뮬레이션
- 성능 벤치마크

### Phase 3: UAT (배포 전)

- 베타 사용자 10-20명 선정
- 2주간 실제 업무 적용
- 피드백 수집 및 반영

