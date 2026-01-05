# 📊 ResultViewer 완전 분석 문서

## 목차
1. [프로젝트 개요](#1-프로젝트-개요)
2. [Codebase Architecture Analysis](#2-codebase-architecture-analysis)
3. [프로젝트 구조 상세 분석](#3-프로젝트-구조-상세-분석)
4. [핵심 기능 시스템 분석](#4-핵심-기능-시스템-분석)
5. [데이터 플로우 및 상태 관리](#5-데이터-플로우-및-상태-관리)
6. [보안 및 동시성 처리](#6-보안-및-동시성-처리)
7. [성능 최적화 전략](#7-성능-최적화-전략)
8. [확장성과 유지보수성](#8-확장성과-유지보수성)
9. [개발자 가이드라인](#9-개발자-가이드라인)
10. [알려진 제한사항 및 향후 계획](#10-알려진-제한사항-및-향후-계획)

---

## 1. 프로젝트 개요

**ResultViewer**는 반도체 설계 검증(Signoff) 프로세스에서 생성되는 대용량 결과 데이터를 효율적으로 관리하고 편집할 수 있는 웹 기반 협업 도구입니다. Dash 프레임워크를 기반으로 하며, AG-Grid의 서버사이드 모델을 활용하여 대용량 데이터 처리와 실시간 편집을 지원합니다.

### 🎯 주요 목적
- **대용량 데이터 처리**: 수백만 행의 검증 결과 데이터 실시간 처리
- **실시간 협업**: 다중 사용자 환경에서 동시 편집 충돌 방지
- **데이터 무결성**: 자동 백업과 메타데이터 관리를 통한 데이터 보호
- **사용자 경험**: 직관적인 웹 인터페이스로 복잡한 데이터 작업 단순화

### 🔧 핵심 기술 스택
- **Backend**: Python, Polars, Flask
- **Frontend**: Dash, AG-Grid Enterprise, React Components
- **Data Storage**: Parquet + JSON 메타데이터
- **Concurrency**: File-based locking system

---

## 2. 📊 Codebase Architecture Analysis

### 🏗️ 전체 아키텍처 개요

ResultViewer는 **개별 사용자별 Dash App + 중앙화된 WORKSPACE 파일시스템**의 하이브리드 구조입니다.

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-User Architecture                  │
├─────────────────┬─────────────────┬─────────────────────────┤
│   User A        │   User B        │   User C                │
│ (Dash App #1)   │ (Dash App #2)   │ (Dash App #3)          │
│                 │                 │                         │
│ ┌─────────────┐ │ ┌─────────────┐ │ ┌─────────────────────┐ │
│ │ DataGrid    │ │ │ DataGrid    │ │ │ DataGrid            │ │
│ │ (AG Grid)   │ │ │ (AG Grid)   │ │ │ (AG Grid)           │ │
│ └─────────────┘ │ └─────────────┘ │ └─────────────────────┘ │
│ ┌─────────────┐ │ ┌─────────────┐ │ ┌─────────────────────┐ │
│ │ SSDF        │ │ │ SSDF        │ │ │ SSDF                │ │
│ │ (Singleton) │ │ │ (Singleton) │ │ │ (Singleton)         │ │
│ └─────────────┘ │ └─────────────┘ │ └─────────────────────┘ │
└─────────────────┴─────────────────┴─────────────────────────┘
                │              │              │
                └──────────────┼──────────────┘
                               │
                ┌───────────────▼───────────────┐
                │     WORKSPACE (Filesystem)    │
                │  - Centralized Storage        │
                │  - .parquet + .meta files     │
                │  - .lock files for conflicts  │
                │  - chmod 0o777 permissions    │
                └───────────────────────────────┘
```

### 🔧 Core Components Deep Dive

#### 1. Data Grid System
- **AG Grid with Server-Side Row Model (SSRM)**
- **Backend**: Polars 기반 대용량 데이터 처리
- **실시간 데이터 조작** 및 waiver 처리
- **Memory-efficient lazy loading**

#### 2. Centralized File Management

**WORKSPACE Structure:**
```
/WORKSPACE/{Product}/{Revision}/{BLOCK}/{TOOL}/
├── result.parquet      # 실제 데이터
├── result.parquet.meta # 메타데이터
├── result.parquet.lock # 편집 잠금 (임시)
└── backup/            # 버전 백업
    └── result_20250726_user1.parquet
```

#### 3. Workspace Explorer Components

```
WorkspaceExplorer/
├── layout.py           # 메인 탭 레이아웃
├── file_explorer.py    # 파일 탐색, CRUD 작업
├── folder_manager.py   # 계층적 폴더 관리
└── file_uploader.py    # CSV/Parquet 업로드
```

#### 4. Metadata Structure

```json
{
  "visible": false,                    // Dashboard 표시 여부
  "start_date": null,                  // 작업 시작일
  "end_date": null,                    // 작업 완료일
  "sol_dir": "",                       // 솔루션 디렉토리 경로
  "details": [{                        // Waiver 통계
    "name": "All",
    "result": 8616,
    "waiver": 2,
    "fixed": 0
  }],
  "last_modified": "2025-06-22T14:53:39.290522",
  "modified_by": "wonwo",
  "filterModel": {},                   // AG Grid 필터 상태
  "locks": [],                         // 향후 Partial Lock용
  "uploaded_at": "2025-06-22T14:25:16.434062",
  "uploaded_by": "wonwo"
}
```

#### 5. Lock Management System

```
Lock States:
┌─────────────┐    file-mode-control    ┌─────────────┐
│ Read Mode   │ ──────────────────────▶ │ Edit Mode   │
│ (Default)   │                         │ (.lock 생성) │
│ No .lock    │ ◀────────────────────── │ Exclusive   │
└─────────────┘    앱 종료/모드 변경      └─────────────┘
```

### 🗃️ Data Management Layer

**SSDF (Server-Side DataFrame) - Global Singleton**

```python
SSDF = DataFrameManager()  # 각 사용자 Dash App당 하나

# 주요 역할:
- DataFrame Storage (Polars)
- Lock Status Management  
- Cache Management
- Request Processing
- Metadata Tracking
```

---

## 3. 프로젝트 구조 상세 분석

### 📁 전체 디렉토리 구조

```
C:\Users\wonwo\OneDrive\문서\PYTHON\resultviewer\
├── app.py                                 # 메인 애플리케이션 엔트리포인트
├── CLAUDE.md                             # 개발 히스토리 문서
├── RESULTVIEWER_COMPLETE_DOCUMENTATION.md # 이 문서
├── assets\                               # 정적 자원
│   ├── custom.css                        # 커스텀 스타일시트
│   └── dashAgGridFunctions.js           # AG-Grid 커스텀 JavaScript 함수
├── components\                           # UI 컴포넌트
│   ├── RV.py                            # 메인 ResultViewer 클래스
│   ├── grid\                            # 데이터 그리드 관련
│   │   ├── data_grid.py                 # 메인 데이터 그리드 컴포넌트
│   │   └── dag\                         # Dash AG-Grid 관련
│   │       ├── column_definitions.py     # 컬럼 정의 및 생성
│   │       ├── server_side_operations.py # 서버 사이드 작업
│   │       └── SSRM\                    # Server Side Row Model
│   │           ├── apply_filter.py      # 필터 적용
│   │           ├── apply_group.py       # 그룹화 적용
│   │           └── apply_sort.py        # 정렬 적용
│   └── menu\                            # 메뉴 시스템
│       └── home\                        # 홈 메뉴
│           ├── home.py                  # 홈 메뉴 메인
│           └── item\                    # 메뉴 아이템들
│               ├── file_mode.py         # 파일 모드 (읽기/편집)
│               ├── open.py              # 파일 열기
│               ├── save.py              # 파일 저장
│               └── workspace\           # 워크스페이스 관련
│                   ├── layout.py        # 워크스페이스 레이아웃
│                   ├── file_explorer.py # 파일 탐색기
│                   ├── file_uploader.py # 파일 업로더
│                   ├── folder_manager.py# 폴더 관리
│                   └── metadata_editor.py# 메타데이터 편집기
└── utils\                               # 유틸리티 모듈
    ├── config.py                        # 설정 관리
    ├── data_processing.py               # 데이터 처리
    ├── db_management.py                 # 데이터베이스 관리 (SSDF)
    ├── devworks_api.py                  # DevWorks API
    ├── file_operations.py               # 파일 작업
    ├── lock_manager.py                  # 잠금 관리 (레거시)
    ├── lock_operations.py               # 잠금 작업
    ├── logging_utils.py                 # 로깅 유틸리티
    └── metadata_manager.py              # 메타데이터 관리
```

### 🔑 핵심 파일별 상세 분석

#### 📋 app.py - 애플리케이션 엔트리포인트
```python
# Flask + Dash 서버 생성
# ResultViewer 인스턴스 초기화
# 콜백 등록 및 서버 시작
```

#### 🎯 components/RV.py - 메인 애플리케이션 클래스
- **레이아웃 관리**: 전체 애플리케이션의 UI 구조 정의
- **컴포넌트 통합**: 모든 하위 컴포넌트들의 통합 관리
- **콜백 등록**: 중앙화된 콜백 관리 시스템

#### 📊 components/grid/data_grid.py - 데이터 그리드 시스템
```python
class DataGrid:
    DASH_GRID_OPTIONS = {
        "rowModelType": "serverSide",
        "cacheBlockSize": 1000,
        "maxBlocksInCache": 3,
        "enableCharts": True,
        "undoRedoCellEditing": True,
        # ... 대용량 데이터 최적화 옵션들
    }
```

**주요 기능:**
- **Server-Side Row Model**: 대용량 데이터 가상화
- **실시간 편집**: 셀 값 변경과 전파 규칙 적용
- **Editable Column Reset**: 모드 변경 시 컬럼 상태 초기화

#### 🗂️ utils/db_management.py - SSDF 데이터 관리자
```python
class DataFrameManager:
    def __init__(self):
        self.dataframe = None        # 메인 데이터프레임
        self.lock = None            # 잠금 상태
        self.is_readonly = True     # 읽기 전용 모드
        self.file_path = None       # 현재 파일 경로
        # ... 캐시 및 상태 관리 변수들
```

#### 🔧 utils/config.py - 설정 관리
```python
class Config:
    def __init__(self):
        self.USERNAME = getpass.getuser()
        self.WORKSPACE = self._get_workspace_path()
        self.USER_RV_DIR = Path.home() / ".resultviewer"
        # ... 환경별 설정 관리
```

---

## 4. 핵심 기능 시스템 분석

### 🌐 Workspace Explorer 시스템

#### 🔍 File Explorer (file_explorer.py)
**실시간 파일 탐색 및 관리 시스템**

```python
class FileExplorer:
    def create_file_table(self, directory_path):
        # 파일 목록 생성 및 메타데이터 통합
        # 실시간 파일 상태 업데이트
        # 필터링 및 검색 기능
```

**핵심 기능:**
- **실시간 파일 스캔**: 디렉토리 변경사항 자동 감지
- **메타데이터 통합**: .meta 파일 정보와 파일 시스템 정보 결합
- **액션 버튼**: 열기, 편집, 복사, 이동, 삭제, 메타데이터 편집
- **필터링**: 파일 타입, 수정 날짜, 사용자별 필터링

#### 📤 File Uploader (file_uploader.py)
**드래그 앤 드롭 파일 업로드 시스템**

```python
class FileUploader:
    def validate_and_process_upload(self, contents, filename):
        # CSV/Parquet 파일 검증
        # 데이터 구조 검사
        # WORKSPACE 경로로 저장
        # 메타데이터 자동 생성
```

**핵심 기능:**
- **다중 파일 업로드**: 드래그 앤 드롭으로 여러 파일 동시 업로드
- **형식 검증**: CSV/Parquet 파일 구조 자동 검증
- **경로 관리**: WORKSPACE 구조에 맞는 자동 경로 생성
- **중복 처리**: 기존 파일 백업 후 덮어쓰기

#### 📁 Folder Manager (folder_manager.py)
**계층적 폴더 구조 관리**

```python
class FolderManager:
    def create_folder_tree(self, base_path):
        # 트리 구조 생성
        # 권한 검사
        # 폴더 생성/삭제 관리
```

**핵심 기능:**
- **트리 구조 표시**: 계층적 폴더 구조 시각화
- **폴더 생성**: 새 폴더 생성 및 권한 설정
- **폴더 관리**: 이름 변경, 삭제, 이동 기능
- **권한 제어**: 사용자별 폴더 접근 권한 관리

### 🔄 File Mode 시스템 (file_mode.py)

#### 📖 Read Mode vs ✏️ Edit Mode 전환
```python
class FileMode:
    def handle_mode_change(self, new_mode, model_layout):
        if new_mode == "edit":
            # 1. 파일 잠금 획득 시도
            # 2. 데이터 재로딩 (원본 데이터)
            # 3. 편집 가능 상태로 전환
        elif new_mode == "read":
            # 1. 자동 저장 옵션 확인
            # 2. 잠금 해제
            # 3. 읽기 전용 모드로 전환
```

**핵심 특징:**
- **스마트 잠금**: 다른 사용자 편집 중일 때 대기열 등록
- **자동 저장**: Edit → Read 전환 시 변경사항 자동 저장 옵션
- **데이터 무결성**: 모드 전환 시 원본 데이터 재로딩
- **사용자 확인**: 모드 변경 시 사용자 확인 및 취소 가능

### 💾 Save/Auto-save 시스템 (save.py)

#### 🏠 Local Save vs ☁️ Workspace Save
```python
class Saver:
    def save_local(self, save_path, filtered_save_as):
        # 로컬 파일 시스템에 저장
        # CSV/Parquet 형식 지원
        # 필터링된 데이터만 저장 옵션
        
    def save_csv_workspace(self, save_path):
        # WORKSPACE에 저장
        # 자동 백업 생성
        # 메타데이터 업데이트
```

**핵심 기능:**
- **이중 저장 방식**: 로컬 저장과 워크스페이스 저장 분리
- **자동 백업**: 기존 파일 자동 백업 후 새 버전 저장
- **메타데이터 동기화**: 저장 시 메타데이터 자동 업데이트
- **경로 검증**: 저장 경로 유효성 및 권한 검사

#### 🔄 Auto-save 메커니즘
```python
def workspace_save(save_path):
    # 1. 경로 정규화 및 검증
    # 2. 기존 파일 백업
    # 3. 새 데이터 저장
    # 4. 메타데이터 업데이트
    # 5. 권한 설정 (chmod 0o777)
```

### 📊 Server-side AG-Grid 구현

#### 🔧 Server Side Row Model (SSRM)
```python
# server_side_operations.py
def extract_rows_from_data(request):
    # 1. 요청 파싱 (필터, 정렬, 그룹화)
    # 2. Polars 데이터프레임 처리
    # 3. 페이징 처리
    # 4. 결과 반환
```

**SSRM 디렉토리 구조:**
```
SSRM/
├── apply_filter.py    # 고급 필터링 로직
├── apply_group.py     # 그룹화 및 집계
└── apply_sort.py      # 다중 컬럼 정렬
```

**성능 최적화:**
- **Lazy Evaluation**: Polars의 지연 평가 활용
- **블록 캐싱**: 1000행 단위 블록 캐싱
- **메모리 효율성**: 필요한 데이터만 메모리에 로드

#### ✏️ Editable Column Reset 기능
```javascript
// dashAgGridFunctions.js
window.editableResetListeners = [];
window.triggerEditableReset = function() {
    window.editableResetListeners.forEach(listener => {
        try { 
            listener(); 
        } catch (error) { 
            console.error(error); 
        }
    });
};
```

**React 컴포넌트 통합:**
```javascript
const EditableHeaderComponent = (props) => {
    const [isEditable, setIsEditable] = useState(false);
    
    useEffect(() => {
        const resetListener = () => setIsEditable(false);
        window.editableResetListeners.push(resetListener);
        return () => {
            // cleanup
        };
    }, []);
};
```

### 🗃️ 메타데이터 관리 시스템

#### 📋 Metadata Manager (metadata_manager.py)
```python
def create_default_metadata(sol_dir=None, uploaded_by=None):
    return {
        "visible": False,
        "start_date": None,
        "end_date": None,
        "sol_dir": sol_dir or "",
        "details": [{"name": "All", "result": 0, "waiver": 0, "fixed": 0}],
        "last_modified": datetime.now().isoformat(),
        "modified_by": CONFIG.USERNAME,
        "filterModel": {},
        "locks": [],
        "uploaded_at": datetime.now().isoformat(),
        "uploaded_by": uploaded_by or CONFIG.USERNAME
    }
```

#### ✏️ Metadata Editor (metadata_editor.py)
**메타데이터 편집 UI 시스템**

```python
class MetadataEditor:
    def create_editor(self):
        # 1. 가시성 토글 스위치
        # 2. 솔루션 디렉토리 입력
        # 3. 날짜 범위 선택기
        # 4. 현재 파일 정보 표시
        # 5. 저장/취소 버튼
```

**검증 시스템:**
- **날짜 검증**: 시작일 ≤ 종료일 검사
- **경로 검증**: 솔루션 디렉토리 유효성 검사
- **권한 검증**: 편집 권한 확인

### 🔄 백업 시스템

#### 📚 자동 백업 메커니즘
```python
def backup_file(base_dir, file_path):
    backup_dir = os.path.join(base_dir, "backup")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    username = CONFIG.USERNAME
    backup_filename = f"{filename}_{timestamp}_{username}.parquet"
    # 백업 디렉토리 생성 및 파일 복사
```

**백업 전략:**
- **타임스탬프 기반**: 저장 시점별 버전 관리
- **사용자별 추적**: 누가 언제 변경했는지 추적
- **자동 정리**: 오래된 백업 파일 자동 정리 (향후 구현 예정)

### 🔒 Lock 관리 시스템

#### 🚪 File-based Locking
```python
# lock_operations.py
def create_lock_file(file_path, lock_user):
    lock_path = f"{file_path}.lock"
    lock_data = {
        "locked_by": lock_user,
        "locked_at": datetime.now().isoformat(),
        "viewers": []  # 대기 중인 사용자들
    }
    # .lock 파일 생성
```

**동시성 제어:**
- **배타적 잠금**: 한 번에 한 사용자만 편집 가능
- **대기열 시스템**: 편집 요청자들의 순차적 처리
- **자동 해제**: 비정상 종료 시 잠금 자동 해제
- **타임아웃**: 장시간 미사용 시 잠금 해제

---

## 5. 데이터 플로우 및 상태 관리

### 🔄 전체 데이터 플로우

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ File System │───▶│    SSDF     │───▶│  AG-Grid    │───▶│ User Edit   │
│ (.parquet)  │    │ (Polars DF) │    │   (SSRM)    │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       ▲                   ▲                   │                   │
       │                   │                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Metadata   │    │    Cache    │    │   Filter    │    │ Propagation │
│   (.meta)   │    │   System    │    │   Apply     │    │    Rules    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### 🎯 SSDF (Server-Side DataFrame) 상태 관리

#### 📊 핵심 상태 변수들
```python
class DataFrameManager:
    # 데이터 상태
    self.dataframe = None           # 메인 데이터프레임 (Polars)
    self.original_dataframe = None  # 원본 데이터 백업
    
    # 잠금 및 모드 상태
    self.lock = None               # 현재 잠금 상태
    self.is_readonly = True        # 읽기 전용 모드
    self.file_path = None         # 현재 열린 파일 경로
    
    # 캐시 및 성능 최적화
    self.request = {}             # 마지막 AG-Grid 요청
    self.hide_waiver = False      # Waiver 숨김 상태
    self.tree_mode = False        # 트리 모드 활성화
    self.tree_col = None         # 트리 컬럼명
    self.propa_rule = None       # 전파 규칙
    
    # 통계 및 메타데이터
    self.row_counts = {}         # 행 수 캐시
    self.column_stats = {}       # 컬럼 통계 캐시
```

#### 🔄 상태 전환 시나리오

**1. 파일 로딩**
```python
def file2df(file_path, auto_release_lock=True):
    # 1. 파일 존재성 확인
    # 2. Parquet 파일 로딩 (Polars)
    # 3. 데이터 검증 (validate_df)
    # 4. SSDF에 저장
    # 5. 메타데이터 로딩
    # 6. 잠금 상태 확인
```

**2. 편집 모드 진입**
```python
def acquire_lock(file_path):
    # 1. 기존 잠금 확인
    # 2. 새 잠금 생성
    # 3. SSDF 상태 업데이트
    # 4. 원본 데이터 백업
```

**3. 데이터 편집**
```python
def apply_edit(cell_changed):
    # 1. 변경된 셀 정보 파싱
    # 2. 전파 규칙 적용
    # 3. Polars 데이터프레임 업데이트
    # 4. 캐시 무효화
    # 5. UI 새로고침 트리거
```

### 📈 캐싱 전략

#### 🗄️ 다중 레벨 캐싱
```python
# 1. SSDF 레벨 캐싱
self.row_counts = {
    "filtered": 8000,
    "groupby": 1200,
    "total": 10000
}

# 2. AG-Grid 블록 캐싱
DASH_GRID_OPTIONS = {
    "cacheBlockSize": 1000,
    "maxBlocksInCache": 3,
    "blockLoadDebounceMillis": 100
}

# 3. 메타데이터 캐싱
metadata_cache = {
    file_path: metadata_dict
}
```

#### ♻️ 캐시 무효화 전략
- **데이터 변경 시**: 전체 캐시 클리어
- **필터 변경 시**: 필터 관련 캐시만 클리어
- **모드 변경 시**: 상태 관련 캐시 클리어

---

## 6. 보안 및 동시성 처리

### 🔐 보안 체계

#### 🛡️ 입력 검증
```python
def validate_df(df):
    # 1. 필수 컬럼 존재 확인 ('uniqid')
    # 2. 데이터 타입 검증
    # 3. 중복 레코드 검사
    # 4. 악성 데이터 패턴 검사
```

#### 🔑 접근 제어
```python
def check_file_permissions(file_path, user):
    # 1. 파일 존재성 확인
    # 2. 읽기 권한 확인
    # 3. 쓰기 권한 확인 (편집 모드 시)
    # 4. 디렉토리 접근 권한 확인
```

#### 🚨 입력 살균화
```python
def sanitize_input(user_input):
    # 1. SQL Injection 방지
    # 2. Path Traversal 방지
    # 3. XSS 방지
    # 4. 파일명 정규화
```

### 🔄 동시성 제어

#### 🚪 파일 레벨 잠금
```python
class FileLock:
    def __init__(self, file_path, user):
        self.file_path = file_path
        self.lock_path = f"{file_path}.lock"
        self.locked_by = user
        self.locked_at = datetime.now()
        self.viewers = []  # 대기 중인 사용자들
```

**잠금 상태 전환:**
```
[Unlocked] → [Edit Request] → [Lock Check] → [Lock Acquired] → [Editing]
     ↑                                             ↓
[Lock Released] ← [Mode Change/Exit] ← [Edit Complete]
```

#### 👥 다중 사용자 협업
```python
def add_viewer_to_lock_file(file_path, viewer):
    # 1. 기존 잠금 파일 읽기
    # 2. 대기열에 사용자 추가
    # 3. 잠금 파일 업데이트
    # 4. 알림 시스템 트리거
```

**대기열 관리:**
- **FIFO 순서**: 먼저 요청한 사용자가 우선
- **자동 알림**: 잠금 해제 시 대기 중인 사용자에게 알림
- **타임아웃**: 응답 없는 사용자 자동 제거

#### ⚡ 경쟁 상태 방지
```python
def atomic_file_operation(operation, file_path):
    # 1. 임시 파일 생성
    # 2. 원자적 연산 수행
    # 3. 원본 파일과 교체
    # 4. 임시 파일 정리
```

---

## 7. 성능 최적화 전략

### 🚀 대용량 데이터 처리

#### ⚡ Polars 활용 최적화
```python
# 지연 평가 (Lazy Evaluation)
lazy_df = pl.scan_parquet(file_path)
result = (
    lazy_df
    .filter(pl.col("status") == "failed")
    .group_by("category")
    .agg(pl.count())
    .collect()  # 실제 실행은 여기서
)
```

**성능 이점:**
- **Zero-Copy**: 메모리 복사 최소화
- **SIMD 최적화**: CPU 벡터 연산 활용
- **병렬 처리**: 다중 코어 자동 활용
- **메모리 효율성**: 필요한 컬럼만 로드

#### 🔄 AG-Grid SSRM 최적화
```python
DASH_GRID_OPTIONS = {
    "cacheBlockSize": 1000,      # 블록 크기 최적화
    "maxBlocksInCache": 3,       # 메모리 사용량 제한
    "blockLoadDebounceMillis": 100,  # 요청 디바운싱
    "purgeClosedRowNodes": True, # 메모리 정리
}
```

**최적화 전략:**
- **블록 단위 로딩**: 화면에 보이는 데이터만 로드
- **지능형 캐싱**: LRU 기반 블록 캐시 관리
- **요청 배칭**: 연속된 요청들을 배치로 처리
- **메모리 정리**: 사용하지 않는 노드 자동 정리

### 📊 프론트엔드 최적화

#### ⚡ JavaScript 성능 최적화
```javascript
// 디바운싱으로 과도한 API 호출 방지
const debouncedSearch = debounce((searchTerm) => {
    performSearch(searchTerm);
}, 300);

// 가상화로 대량 DOM 엘리먼트 처리
const VirtualizedTable = ({ items }) => {
    return (
        <FixedSizeList
            height={600}
            itemCount={items.length}
            itemSize={35}
        >
            {Row}
        </FixedSizeList>
    );
};
```

#### 🎨 CSS 최적화
```css
/* GPU 가속 활용 */
.data-grid {
    transform: translate3d(0,0,0);
    will-change: transform;
}

/* 불필요한 리플로우 방지 */
.grid-cell {
    contain: layout style paint;
}
```

### 🗄️ 메모리 관리

#### 📈 메모리 사용량 모니터링
```python
def monitor_memory_usage():
    import psutil
    process = psutil.Process()
    memory_info = process.memory_info()
    
    logger.info(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
    logger.info(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
```

#### 🧹 가비지 컬렉션 최적화
```python
import gc

def cleanup_dataframes():
    # 사용하지 않는 데이터프레임 정리
    if hasattr(SSDF, 'old_dataframes'):
        del SSDF.old_dataframes
    
    # 명시적 가비지 컬렉션
    gc.collect()
```

---

## 8. 확장성과 유지보수성

### 🧩 플러그인 시스템 설계

#### 🔌 컴포넌트 플러그인 아키텍처
```python
class PluginManager:
    def __init__(self):
        self.plugins = {}
        self.hooks = defaultdict(list)
    
    def register_plugin(self, name, plugin_class):
        self.plugins[name] = plugin_class()
        
    def execute_hook(self, hook_name, *args, **kwargs):
        for callback in self.hooks[hook_name]:
            callback(*args, **kwargs)
```

**확장 포인트:**
- **데이터 처리 파이프라인**: 커스텀 데이터 변환 로직
- **UI 컴포넌트**: 새로운 메뉴 아이템 추가
- **내보내기 형식**: 새로운 파일 형식 지원
- **인증 시스템**: 외부 인증 시스템 통합

#### 📦 모듈화 설계 원칙
```python
# 단일 책임 원칙
class DataValidator:
    def validate_data_structure(self, df): pass
    def validate_data_types(self, df): pass
    def validate_business_rules(self, df): pass

# 개방-폐쇄 원칙
class FileProcessor:
    def process(self, file_path):
        processor = self.get_processor(file_path)
        return processor.process(file_path)
    
    def get_processor(self, file_path):
        # 팩토리 패턴으로 확장 가능
        pass
```

### 📝 로깅 및 모니터링

#### 📊 구조화된 로깅
```python
# logging_utils.py
class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        
    def log_user_action(self, action, user, file_path, **kwargs):
        self.logger.info({
            "action": action,
            "user": user,
            "file_path": file_path,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        })
```

**로깅 카테고리:**
- **사용자 액션**: 파일 열기, 편집, 저장 등
- **시스템 이벤트**: 잠금 생성/해제, 오류 발생
- **성능 메트릭**: 응답 시간, 메모리 사용량
- **보안 이벤트**: 권한 위반, 비정상 접근

#### 📈 성능 모니터링
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = defaultdict(list)
    
    @contextmanager
    def measure_time(self, operation_name):
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            self.metrics[operation_name].append(duration)
```

### 🧪 테스트 전략

#### 🎯 단위 테스트
```python
# tests/test_data_processing.py
class TestDataProcessing(unittest.TestCase):
    def setUp(self):
        self.sample_df = pl.DataFrame({
            "uniqid": [1, 2, 3],
            "status": ["pass", "fail", "waiver"]
        })
    
    def test_validate_df_with_valid_data(self):
        result = validate_df(self.sample_df)
        self.assertTrue(result)
    
    def test_validate_df_missing_uniqid(self):
        invalid_df = self.sample_df.drop("uniqid")
        with self.assertRaises(ValidationError):
            validate_df(invalid_df)
```

#### 🔄 통합 테스트
```python
# tests/test_file_operations.py
class TestFileOperations(unittest.TestCase):
    def test_file_upload_and_metadata_creation(self):
        # 1. 파일 업로드
        # 2. 메타데이터 자동 생성 확인
        # 3. 파일 접근 권한 확인
        # 4. 정리 작업
```

#### 🌐 E2E 테스트
```python
# tests/test_end_to_end.py
from selenium import webdriver

class TestUserWorkflow(unittest.TestCase):
    def test_complete_edit_workflow(self):
        # 1. 파일 탐색기에서 파일 선택
        # 2. Edit 모드로 전환
        # 3. 데이터 편집
        # 4. 저장 및 모드 전환
        # 5. 결과 검증
```

---

## 9. 개발자 가이드라인

### 📋 코딩 표준

#### 🐍 Python 코딩 스타일
```python
# PEP 8 준수
class ComponentName:  # PascalCase for classes
    def method_name(self):  # snake_case for methods
        variable_name = "value"  # snake_case for variables
        CONSTANT_NAME = "VALUE"  # UPPER_CASE for constants

# 타입 힌트 사용
def process_data(df: pl.DataFrame, options: Dict[str, Any]) -> pl.DataFrame:
    """
    데이터 처리 함수
    
    Args:
        df: 처리할 데이터프레임
        options: 처리 옵션
        
    Returns:
        처리된 데이터프레임
        
    Raises:
        ValidationError: 데이터 검증 실패 시
    """
    pass
```

#### 🎨 JavaScript/React 스타일
```javascript
// camelCase 사용
const editableHeaderComponent = (props) => {
    const [isEditable, setIsEditable] = useState(false);
    
    // JSX에서 명확한 이벤트 핸들러명
    const handleToggleEditable = useCallback(() => {
        setIsEditable(prev => !prev);
    }, []);
    
    return (
        <div className="header-component">
            <button onClick={handleToggleEditable}>
                {isEditable ? 'Disable' : 'Enable'}
            </button>
        </div>
    );
};
```

### 🏗️ 컴포넌트 개발 가이드

#### 📋 새 컴포넌트 개발 템플릿
```python
class NewComponent:
    """새 컴포넌트 클래스 템플릿"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        초기화 메서드
        
        Args:
            config: 컴포넌트 설정
        """
        self.config = config or {}
        
    def layout(self) -> html.Div:
        """
        컴포넌트 레이아웃 정의
        
        Returns:
            Dash HTML 컴포넌트
        """
        return html.Div([
            # 컴포넌트 구조 정의
        ])
    
    def register_callbacks(self, app) -> None:
        """
        콜백 등록
        
        Args:
            app: Dash 애플리케이션 인스턴스
        """
        @app.callback(
            Output("component-output", "children"),
            Input("component-input", "value"),
            prevent_initial_call=True
        )
        def handle_interaction(value):
            # 콜백 로직 구현
            return value
```

#### 🔄 콜백 개발 모범 사례
```python
@app.callback(
    [
        Output("output-1", "children"),
        Output("output-2", "value"),
    ],
    [
        Input("input-1", "n_clicks"),
        Input("input-2", "value"),
    ],
    [
        State("state-1", "data"),
    ],
    prevent_initial_call=True
)
def callback_function(n_clicks, input_value, state_data):
    """
    콜백 함수 예제
    
    Returns:
        Tuple of outputs matching Output declarations
    """
    # 1. 입력 검증
    if not n_clicks:
        raise PreventUpdate
    
    # 2. 비즈니스 로직
    try:
        result = process_logic(input_value, state_data)
    except Exception as e:
        logger.error(f"Callback error: {e}")
        return "Error occurred", no_update
    
    # 3. 결과 반환
    return result, "Success"
```

### 🔧 유틸리티 함수 개발

#### 📊 데이터 처리 유틸리티
```python
# utils/data_helpers.py
def safe_dataframe_operation(operation: str, df: pl.DataFrame, **kwargs) -> pl.DataFrame:
    """
    안전한 데이터프레임 연산 래퍼
    
    Args:
        operation: 수행할 연산명
        df: 대상 데이터프레임
        **kwargs: 연산별 파라미터
        
    Returns:
        연산 결과 데이터프레임
        
    Raises:
        DataProcessingError: 연산 실패 시
    """
    try:
        if operation == "filter":
            return df.filter(kwargs["condition"])
        elif operation == "group_by":
            return df.group_by(kwargs["columns"]).agg(kwargs["aggregations"])
        # ... 다른 연산들
    except Exception as e:
        raise DataProcessingError(f"Operation {operation} failed: {e}")
```

#### 🗂️ 파일 시스템 유틸리티
```python
# utils/file_helpers.py
def safe_file_operation(operation: Callable, file_path: str, **kwargs):
    """
    안전한 파일 연산 래퍼
    
    Args:
        operation: 수행할 파일 연산 함수
        file_path: 대상 파일 경로
        **kwargs: 연산별 파라미터
        
    Returns:
        연산 결과
    """
    # 1. 경로 검증
    normalized_path = os.path.normpath(file_path)
    if not is_safe_path(normalized_path):
        raise SecurityError("Unsafe file path")
    
    # 2. 권한 검사
    if not has_permission(normalized_path, kwargs.get("permission", "read")):
        raise PermissionError("Insufficient permissions")
    
    # 3. 연산 수행
    try:
        return operation(normalized_path, **kwargs)
    except Exception as e:
        logger.error(f"File operation failed: {e}")
        raise
```

### 📈 성능 최적화 가이드

#### ⏱️ 성능 측정 데코레이터
```python
def measure_performance(func):
    """성능 측정 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        memory_before = get_memory_usage()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            memory_after = get_memory_usage()
            
            logger.info(f"{func.__name__} - Duration: {duration:.3f}s, "
                       f"Memory: {memory_after - memory_before:.2f}MB")
    
    return wrapper
```

#### 🗄️ 캐싱 가이드라인
```python
from functools import lru_cache
from typing import Optional

@lru_cache(maxsize=128)
def expensive_computation(param1: str, param2: int) -> str:
    """비용이 큰 계산 함수의 결과 캐싱"""
    # 복잡한 계산 로직
    return result

# 캐시 무효화
def invalidate_cache():
    expensive_computation.cache_clear()
```

---

## 10. 알려진 제한사항 및 향후 계획

### ⚠️ 현재 제한사항

#### 🔒 동시성 제한
- **파일 레벨 잠금**: 현재는 전체 파일 단위로만 잠금 지원
- **세션 관리**: 브라우저 종료 시 잠금 자동 해제 미구현
- **네트워크 단절**: 네트워크 문제 시 잠금 상태 불일치 가능

#### 📊 데이터 처리 제한
- **메모리 사용량**: 매우 큰 파일(10GB+)에서 메모리 부족 가능
- **동시 사용자**: 현재 테스트는 소수 사용자 기준
- **실시간 동기화**: 사용자 간 실시간 변경사항 동기화 미지원

#### 🎨 UI/UX 제한
- **모바일 지원**: 데스크탑 환경에만 최적화
- **접근성**: 스크린 리더 등 접근성 도구 지원 미흡
- **다국어**: 현재 한국어/영어만 지원

### 🚀 향후 개발 계획

#### Phase 1: 안정성 개선 (1-2개월)
```
✅ 예외 처리 강화
✅ 로깅 시스템 개선  
✅ 자동 테스트 커버리지 확대
✅ 메모리 사용량 최적화
```

#### Phase 2: 고급 기능 (2-3개월)
```
🔄 실시간 협업 기능
   - WebSocket 기반 실시간 동기화
   - 사용자별 커서 표시
   - 변경사항 실시간 브로드캐스트

📊 고급 분석 기능
   - 데이터 시각화 차트
   - 통계 분석 도구
   - 트렌드 분석 대시보드

🔍 검색 및 필터링 개선
   - 전문 검색 엔진 통합
   - 고급 쿼리 빌더
   - 저장된 필터 템플릿
```

#### Phase 3: 엔터프라이즈 기능 (3-6개월)
```
🔐 보안 강화
   - LDAP/Active Directory 통합
   - 역할 기반 접근 제어 (RBAC)
   - 감사 로그 시스템

📈 확장성 개선
   - 분산 처리 지원
   - 클러스터 환경 지원  
   - 로드 밸런싱

🔄 DevOps 통합
   - CI/CD 파이프라인
   - 자동 배포 시스템
   - 모니터링 및 알림
```

### 🎯 기술적 개선 사항

#### 🏗️ 아키텍처 개선
```python
# 마이크로 서비스 아키텍처 전환 계획
services = {
    "auth_service": "사용자 인증 및 권한 관리",
    "data_service": "데이터 처리 및 저장",
    "notification_service": "실시간 알림 시스템",
    "file_service": "파일 관리 및 백업",
}
```

#### 📊 데이터베이스 통합
```sql
-- PostgreSQL 스키마 설계 (향후)
CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    path VARCHAR(500) UNIQUE NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE file_locks (
    id SERIAL PRIMARY KEY,
    file_id INTEGER REFERENCES files(id),
    locked_by VARCHAR(100) NOT NULL,
    locked_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);
```

#### 🔄 실시간 기능 로드맵
```javascript
// WebSocket 통합 계획
const socketManager = {
    connect: () => {
        // WebSocket 연결 관리
    },
    
    broadcastChange: (fileId, change) => {
        // 변경사항 실시간 브로드캐스트
    },
    
    handleIncomingChange: (change) => {
        // 다른 사용자 변경사항 처리
    }
};
```

---

## 📚 참고 자료 및 문서

### 📖 핵심 라이브러리 문서
- **[Dash Documentation](https://dash.plotly.com/)**: 기본 Dash 프레임워크
- **[AG-Grid Documentation](https://www.ag-grid.com/)**: 데이터 그리드 컴포넌트
- **[Polars Documentation](https://pola-rs.github.io/polars/)**: 데이터 처리 엔진
- **[Dash AG-Grid](https://dash.plotly.com/dash-ag-grid)**: Dash AG-Grid 통합

### 🔧 개발 도구
- **IDE 설정**: VSCode + Python extension + Dash snippets
- **디버깅**: Dash Dev Tools, Chrome DevTools
- **프로파일링**: py-spy, memory_profiler
- **테스트**: pytest, selenium

### 📋 프로젝트 관련 파일
- **`CLAUDE.md`**: 개발 과정 및 변경 이력
- **`requirements.txt`**: Python 의존성 목록
- **`assets/`**: 정적 자원 (CSS, JS)
- **`tests/`**: 테스트 파일들 (향후 생성)

---

## 🎯 결론

**ResultViewer**는 대용량 데이터 처리와 실시간 협업을 위한 강력하고 확장 가능한 웹 애플리케이션입니다. 

**주요 강점:**
- 🚀 **고성능**: Polars + AG-Grid SSRM으로 대용량 데이터 효율 처리
- 👥 **협업 친화적**: 파일 잠금 시스템으로 동시 편집 충돌 방지
- 🔧 **확장성**: 모듈화된 아키텍처로 새 기능 추가 용이
- 🛡️ **안정성**: 자동 백업과 메타데이터 관리로 데이터 무결성 보장

**개발자를 위한 핵심 포인트:**
1. **SSDF 중심 설계**: 모든 데이터 상태는 SSDF를 통해 관리
2. **컴포넌트 기반**: 각 기능은 독립적인 컴포넌트로 구현
3. **서버사이드 처리**: 대용량 데이터는 서버에서 처리
4. **파일 기반 협업**: 단순하지만 효과적인 잠금 시스템

이 문서를 통해 새로운 개발자나 LLM이 프로젝트를 빠르게 이해하고 효과적으로 기여할 수 있기를 바랍니다.

---

**문서 버전**: 1.0  
**최종 업데이트**: 2025-01-27  
**작성자**: ResultViewer Development Team