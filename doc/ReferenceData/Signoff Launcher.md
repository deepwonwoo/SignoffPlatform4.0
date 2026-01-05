
* **Signoff Launcher Dash App** : Signoff Launcher is a web application that aims to simplify setting up Signoff Simulation by providing a user-friendly graphical user interface.  It relies on the Inhouse Signoff Tool Engine for the backend, and Plotly Dash for the frontend.

* Inhouse Signoff Tool은 C++로 만들어진 회로설계 검증 엔진으로, 입력된 회로정보(Netlist, Process/Voltage/Temperature)를 기반으로 SPICE 등의 회로시뮬레이션을 수행하여, Driver Size Check(DSC), PEC(Power Error Check), LSC(Level Shifter Check)등의 회로 Signoff Application을 제공해. 이런 Inhouse Signoff Application을 수행하기 위한 Interface가 Signoff launcher야. Web GUI를 통해 입력된 회로정보를 바탕으로 Signoff Application 을 수행하고 Job Scheduling, Monitoring System, Input/Output 관리 등의 사용자의 작업 효율성을 높이는 Signoff Lancher를 새로 개발하려고해.


* 뉴스레터 소개 자료: Signoff 작업을 수행을 위한 Interface Tool
	- Signoff Application 수행에 필요한 입력 데이터를 받고,  LSF Scheduler(HPC)에 작업 제출
	Signoff Launcher 는 기존 Tool 별로 존재하던 LEGO Flow를 일원화한 Signoff 수행용 GUI 플랫폼입니다.
	1) Revision별 수행해야 하는 Signoff의 수행 항목들을 눈에 볼 수 있습니다.
	2) 한 번의 Input File 입력으로 모든 Tool/Corner에 대해 Signoff 수행 가능하여 재사용성이 높습니다.
	3) 입력된 Input File 들은 BTS/VSE 내 환경에 Template으로 저장되어 Schematic 과 함께 DB로써 관리되며, Revision 이 변경될 때 함께 복사되어 재수행 부담이 적습니다.

# UserGuide

첨부의 Signoff Launcher Dash App Codebase를 실행시켜보면,
크게 두 개의 주요 페이지(Set Page, Run Page)와 하나의 설정 관리 영역(Workspace)으로 구성되어 있어.


## 주요 컴포넌트 및 기능


### 1. 공통 인터페이스 (app.py)
애플리케이션의 진입점으로, Dash 앱을 초기화하고 주요 컴포넌트들을 조합하여 전체 인터페이스를 구성합니다.

**주요 기능:**
- 네비게이션 바: Set Page와 Run Page 간 전환 버튼 및 워크스페이스 관리 버튼 제공
- 페이지 전환: Set Page와 Run Page 간 전환을 처리하는 콜백 로직
- 초기 워크스페이스 설정: 첫 접속 시 워크스페이스 설정 모달 표시


### 2. 워크스페이스 관리 (workspace.py)
작업 디렉토리 설정 및 관리를 담당하는 컴포넌트입니다.

**주요 기능:**
- 워크스페이스 초기 설정: 애플리케이션 첫 접속 시 작업 디렉토리 설정
- 워크스페이스 변경: 기존 작업 디렉토리 변경 및 유효성 검증
- 디렉토리 탐색: 현재 작업 디렉토리 내용 표시

**구현 방식:**
- 워크스페이스 설정은 설정 파일(settings.json)에 저장되며, 앱 시작 시 로드됩니다.
- 워크스페이스 초기 설정은 모달 인터페이스를 통해 이루어지며, 제품명과 리비전 기반의 표준 경로 또는 사용자 정의 경로를 지정할 수 있습니다.
- 워크스페이스 드로어에서는 경로 변경 및 현재 워크스페이스 내용 확인이 가능합니다.


Launcher Dash App이 처음 실행될 때 `workspace_setup_modal`이 자동으로 표시되. 
이 모달에서는 두 가지 방식으로 워크스페이스 디렉토리를 설정할 수 있습니다:

1. **제품 구조 탭**: 회사의 표준 경로 형식(`/user/{Product}/{Revision}/Signoff/`)을 따르도록 유도합니다. 드롭다운 메뉴에서 제품명(예: lgx102, hbmuw, hbm3e)과 리비전(예: R00, V01, V10)을 선택하면 자동으로 경로가 생성됩니다.
2. **사용자 정의 경로 탭**: 사용자가 원하는 임의의 경로를 직접 입력할 수 있습니다. 초기값으로 `/user/signoff_workspace` 같은 권장 경로가 제안됩니다.
모달에서 "Set Workspace" 버튼을 클릭하면 `handle_modal_actions` 콜백이 실행되어 해당 디렉토리가 존재하지 않으면 생성하고, 설정 파일(`utils/settings.py`의 `SETTINGS_FILE`)에 경로를 저장합니다.

**워크스페이스 변경:**
사용자는 네비게이션 바의 워크스페이스 버튼(`workspace-btn`)을 클릭하여 언제든지 워크스페이스 드로어를 열고 작업 디렉토리를 변경할 수 있습니다. 드로어에서는 현재 워크스페이스의 내용을 탐색하고, 새 경로를 입력하여 변경할 수 있습니다.

입력된 경로는 `validate_workspace_path` 메서드에 의해 검증되며, 다음 조건을 확인합니다:
- 경로가 비어있지 않은지
- 경로가 존재하는 경우 디렉토리인지
- 쓰기 권한이 있는지
- 경로가 존재하지 않는 경우 상위 디렉토리에 쓰기 권한이 있는지

유효한 경로가 확인되면 "Apply Changes" 버튼이 활성화되며, 클릭 시 `update_workspace` 콜백이 실행되어 새 워크스페이스를 설정합니다.

**워크스페이스 내용 표시:**
현재 워크스페이스 디렉토리의 내용은 `_get_directory_contents` 메서드에 의해 스캔되고 표시됩니다. 이 메서드는 사용자 소유의 파일과 디렉토리만 표시하며, 너무 많은 항목이 있는 경우 최대 표시 항목 수를 제한합니다.

### 3. 작업 설정 페이지 (job_set/)

작업 설정 페이지는 Signoff Application들을 워크스페이스 디렉토리에서 실행할 수 있도록 하는 인터페이스입니다. 이 페이지는 세 가지 주요 영역으로 구성됩니다:

**1. Job Cards (job_set/jobCards.py):**
Job Cards는 실행할 Signoff Application을 선택하고 구성하는 영역입니다. `signoff_applications.yaml` 파일에 정의된 애플리케이션 목록을 기반으로 생성됩니다.

작동 방식:
- "Create Job" 버튼을 클릭하면 새 Job Card가 생성됩니다.
- 각 카드에서는 애플리케이션 그룹과 특정 애플리케이션을 선택할 수 있습니다.
- 선택된 애플리케이션에 따라 해당 `RUNSCRIPTS/{애플리케이션}/input_config.yaml`에서 필요한 입력 구성이 로드됩니다.
- 애플리케이션이 PVT(Process-Voltage-Temperature) 조건을 지원하는 경우(`input_config.yaml`에 `pvt_inputs` 섹션이 있는 경우), PVT 설정 섹션이 표시됩니다.
- 사용자는 동일한 타입의 카드를 여러 개 생성하여 여러 Signoff Application을 병렬로 구성할 수 있습니다.

Job Card의 상태는 다음 콜백들에 의해 관리됩니다:
- `add_new_job_card`: 새 카드 생성
- `copy_job_card`: 기존 카드 복사
- `delete_job_card`: 카드 삭제
- `update_signoff_applications`: 선택된 카테고리에 따라 애플리케이션 목록 업데이트
- `update_job_card_color`: 선택된 애플리케이션에 따라 카드 색상 및 PVT 섹션 표시 여부 업데이트
- `manage_pvt_corner_splits`: PVT 코너 추가/삭제

**2. Job Inputs (job_set/jobInputs.py):**
Job Inputs 영역은 선택된 애플리케이션들에 필요한 입력 필드를 동적으로 표시합니다. 여러 Job Card에서 공통으로 사용되는 입력 필드는 자동으로 통합되어 표시됩니다.

작동 방식:
- `update_input_fields` 콜백은 선택된 모든 애플리케이션의 입력 요구사항을 분석하고 필드를 생성합니다.
- 입력 필드는 타입별로 그룹화됩니다(파일, 숫자, 텍스트, 선택 항목 등).
- 필수 필드와 선택적 필드가 구분되며, 선택적 필드는 "Optional Inputs" 섹션에 접을 수 있는 형태로 표시됩니다.
- PVT 의존성이 있는 입력 필드(`depends_on` 속성이 있는 필드)는 선택된 PVT 조건에 따라 동적으로 표시됩니다.

각 입력 필드는 해당 애플리케이션 색상으로 표시된 배지와 함께 나타나므로, 어떤 애플리케이션에 필요한 입력인지 쉽게 알 수 있습니다.

**3. Job Queue (job_set/jobQueue.py):**
Job Queue 영역은 설정된 작업들의 최종 확인 및 실행을 위한 테이블을 제공합니다. 상단의 Job Card 및 입력 필드를 통해 구성된 작업들이 테이블에 추가되고, 여기서 일괄 실행할 수 있습니다.

작동 방식:
- "Add Jobs" 버튼이 활성화되려면 모든 필수 입력 필드가 채워져야 합니다(`check_add_job_queue_button_status` 콜백).
- "Add Jobs" 버튼을 클릭하면, 선택된 애플리케이션, PVT 조건, 입력값에 따라 작업 항목이 테이블에 추가됩니다.
- 작업 테이블에서는 항목 복사, 삭제, CSV 내보내기/가져오기 등의 관리 기능을 제공합니다.
- "Run All Jobs" 버튼을 클릭하면, 테이블의 모든 작업이 `JobManager`를 통해 실행됩니다.

실제 작업 실행 과정:
1. `JobManager`가 각 작업에 대해 생성됩니다(`app_name`, `job_name`, `corner`, `inputs` 등 설정).
2. `setup()` 메서드가 호출되어 워크스페이스 내에 작업 디렉토리를 생성하고, 해당 애플리케이션의 RUNSCRIPTS를 복사합니다.
3. `run()` 메서드가 호출되어 환경 변수를 설정하고 `run.sh` 스크립트를 실행합니다.
4. 작업 실행은 별도의 프로세스에서 이루어지며, 작업 상태는 `job_config.yaml` 파일을 통해 관리됩니다.

### 4. 작업 실행 페이지 (job_run/)

실행 중이거나 완료된 작업을 모니터링하고 관리하는 페이지입니다.

**구성 요소:**
- **jobTable**: 작업 목록 표시 및 상세 정보 제공
- **jobFiltering**: 작업 필터링 (상태별, 검색어 기반)
- **jobMonitoring**: 작업 상태 모니터링 및 자동 새로고침
- **actions/**: 작업 관리 기능 (로그 보기, 결과 보기, 재실행, 중지, 삭제 등)

**주요 기능:**
- 작업 상태 모니터링 (pending, running, done, failed)
- 작업 필터링 및 검색
- 작업 상세 정보 조회
- 작업 관리 (로그 보기, 결과 보기, 재실행, 중지, 삭제, 터미널 열기)
- 자동/수동 새로고침

**구현 방식:**
- jobTable은 Dash AG Grid를 사용하여 작업 목록을 표시하고, 작업 상세 정보는 Master-Detail 기능을 통해 제공합니다.
- jobFiltering은 AG Grid의 필터 모델을 활용하여 상태별 필터링 및 텍스트 기반 검색을 지원합니다.
- jobMonitoring은 Interval 컴포넌트와 콜백을 통해 자동 새로고침을 구현하며, 이전 데이터와 비교하여 변경 사항이 있는 경우에만 UI를 업데이트합니다.
- actions 모듈은 각각의 작업 관리 기능을 모달 및 콜백으로 구현하며, AG Grid의 cellRendererData를 통해 작업 정보를 전달받습니다.

### 5. 작업 관리 (job_set/jobManager.py)

실제 작업 생성 및 실행을 담당하는 클래스입니다.

**주요 기능:**
- 작업 디렉토리 생성 및 구성
- 작업 설정 파일 생성
- 환경 설정 파일 생성
- 작업 실행 및 모니터링

**구현 방식:**
- 작업 디렉토리는 워크스페이스 내에 생성되며, 애플리케이션 이름, 사용자 지정 작업 이름, PVT 코너, 서브회로 정보 등을 기반으로 이름이 지정됩니다.
- 작업 실행 스크립트는 RUNSCRIPTS 디렉토리에서 복사되어 작업 디렉토리에 배치됩니다.
- 작업 설정 및 상태 정보는 job_config.yaml 파일에 저장됩니다.
- 작업 실행은 subprocess 모듈을 통해 이루어지며, 작업 상태는 update_config 스크립트에 의해 업데이트됩니다.

### 6. 설정 관리 (utils/config_loader.py)

Signoff Application 설정 및 입력 구성을 로드하는 유틸리티 클래스입니다.

**주요 기능:**
- signoff_applications.yaml 파일 로드
- 각 애플리케이션의 input_config.yaml 파일 로드 및 통합
- 애플리케이션 설정 정보 제공

**구현 방식:**
- signoff_applications.yaml 파일은 지원되는 Signoff Application 목록과 각 애플리케이션의 RUNSCRIPTS 경로를 정의합니다.
- 각 애플리케이션의 input_config.yaml 파일은 해당 애플리케이션의 입력 필드 구성, 기본값, 설명 등을 정의합니다.
- ConfigLoader는 이러한 설정 파일들을 로드하여 통합된 설정 정보를 제공합니다.

```

