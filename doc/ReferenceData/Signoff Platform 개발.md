
Signoff Platform 메모리 회로 설계의 검증을 위한 통합 솔루션
* 주요 구성 요소
  1. Signoff Launcher : Signoff Application 실행을 위한 사용자 친화적 인터페이스 제공
  2. Signoff ResultViewer: Excel-like tool로서 Signoff 수행 결과 확인 및 분석
  3. Signoff Engine : C++ 기반 회로 검증 SW로 Signoff Applicaiton들을 수행

# 1. Signoff Launcher

**Signoff Launcher Dash App** : Signoff Launcher is a web application that aims to simplify setting up Signoff Simulation by providing a user-friendly graphical user interface.  It relies on the Inhouse Signoff Tool Engine for the backend, and Plotly Dash for the frontend.

1. 시스템 아키텍처
   - Frontend: Plotly Dash 기반 웹 애플리케이션
   - Backend: C++ Inhouse Signoff Tool과 bash및 python으로 연동
2. 주요 기능 및 워크플로우
   a) Job 생성 및 설정
   b) Simulation Input 관리
   c) 병렬 작업 실행 
   d) 실시간 모니터링 및 로그 확인
   e) 결과 저장 및 관리
3. 기술 스택
       - Frontend: Plotly Dash
       - Backend: Python, bash, C++
       - 데이터 저장: YAML, json, 파일 시스템 기반 Workspace
       - 작업 관리: Subprocess, LSF Scheduler(HPC)

특징:
 * 웹기반 GUI로, Signoff Application 수행에 필요한 입력 데이터를 받고,  LSF Scheduler(HPC)에 작업 제출
 * 한 번의 Input File 입력으로 모든 Tool/Corner에 대해 Signoff 수행 가능하여 Workpsace에서 수행되는 job들 Monitoring
 * Input/Output 데이터 관리 및 재사용성 향상

# 2. Signoff ResultViewer

Signoff ResultViewer(SORV)는 Signoff 수행 결과를 효율적으로 분석하기 위해 개발된 웹 기반 CSV Editor Tool입니다. 다음과 같은 기존 분석 과정의 문제점을 해결하고자 개발되었습니다:

1. 주요 기능 
   - 대규모 CSV 데이터 처리가 가능한 Excel과 유사한 UI/UX
   - WORKSPACE 기반 중앙 집중식 데이터 관리
   - 데이터 조작 (Sorting, Filtering, Grouping)
   - 설계 특화 기능 (예: Cross-Probing, Compare, Categorize, Waiver처리 등)
2. 기술 스택
   - Frontend: Web 기반 (Dash)
   - Backend: 대용량 데이터 처리에 최적화된 기술 (Polars)

특징:
- **HPC망 호환성**:
    - Excel과 유사한 기능을 HPC망에서 직접 사용 가능하여 작업 환경 전환의 필요성을 줄입니다.
    - OA망으로의 데이터 이동 없이 보안을 유지하며 효율적인 작업이 가능합니다.
- **고성능 대용량 데이터 처리**:
    - Rust 기반 API(polars)를 사용하여 대규모 데이터도 빠르고 원활하게 처리합니다.
    - SSRM(Server-Side Row Model) 기반의 Lazy Loading을 구현하여 필요한 데이터만 효율적으로 로드합니다.
- **사용자 친화적 인터페이스**:
    - Excel과 유사한 직관적인 UI로 기존 사용자들이 빠르게 적응할 수 있습니다.
    - Sorting, Filtering, Grouping 등 익숙한 데이터 조작 기능을 제공하여 사용자의 생산성을 높입니다.
- **Signoff 특화 분석 기능**:
    - CrossProbing, Compare, Categorize 등 Signoff 결과 분석에 최적화된 기능을 제공하여 설계 검증 프로세스를 가속화합니다.
- **효율적인 워크플로우**:
    - WORKSPACE를 활용한 중앙 집중식 결과 관리로 팀 내 데이터 공유와 협업을 강화합니다.
    - 버전 관리 및 공유 기능으로 팀 협업의 효율성을 높이고 데이터의 일관성을 유지합니다.
- **확장성 및 커스터마이징**:
    - 사용자 정의 스크립트 실행이 가능하여 특정 분석 요구사항에 맞춤 대응할 수 있습니다.
    - Predefined Views를 통해 Signoff Tool별로 최적화된 분석 환경을 제공하여 작업 효율성을 극대화합니다.

# 3. Signoff Engine

### Custom 설계 Sign-off Tools:

* 메모리 설계의 특성상 일반 EDA 툴 대신 C++ 기반의 자체 개발 Inhouse Tool인 "SPACE"와 "ADV"를 사용
* 주요 기술: 회로 인식 기술, Stage Simulation & Analysis 방법론, Waveform 분석
* C++ 기반 회로 검증 SW로 Signoff Applicaiton들을 수행.
* 입력된 회로정보(Netlist, Process/Voltage/Temperature)를 기반으로 아래 Application들에 해당하는 SPICE Simulation 수행.
  - Inhouse Signoff Applications :  Static (9종), Dynamic (13종)
	  - 1) Static: Static topology 인식, Simulation 결과 도출, DSC (Driver Size Check), LSC (Latch Strength Check), cana Tr (Coupling noise), etc.
	  - 2) Dynamic: 설계 spec/criteria 기반 simulation 결과 분석, ADV, dynamic coupling noise check, glitch margin analysis, etc. 

### 중장기 계획: 

1) Signoff – Full chip 수준 TR-level STA 개발/적용: Coverage↑, Runtime↓  
2) Circuit Simulation – HTV, AVA, RTVS 등 advanced feature 조기 enable 및 활용
3) 개발 및 유지보수 전략
   3.1 모듈화
       - Signoff Engine의 Python wrapper 개발로 각 Signoff 단계 모듈화
       - 유지보수 및 기능 확장의 용이성 확보
   3.2 확장성
       - 새로운 Signoff Application 추가 용이
       - 사용자 정의 분석 기능 지원 가능성
   3.3 성능 최적화
       - 병렬 처리를 통한 대규모 시뮬레이션 효율화
       - 대용량 데이터 처리를 위한 최적화 기법 적용
4) 향후 계획 및 발전 방향
- C++ 기반 레거시 코드의 유지보수 어려움 → 현대적 프로그래밍 기법 및 언어로의 마이그레이션 고려 
- 회로 고도화에 따른 성능 개선 필요 → 병렬처리 및 AI/ML 기법 도입 검토 - 사용자 친화적이지 않은 GUI → 새로운 UI/UX 설계 및 구현 
- HBM 등 대규모 트랜지스터 처리 → 알고리즘 최적화 및 분산 컴퓨팅 도입 고려
### Signoff 배경 지식: 

## 1. Tr-level Signoff Methodology
* 메모리향 Tr-level Signoff Tool 기반 설계/검증 방법론 개발
* Inhouse Tool(SPACE&ADV) 개발 및 유지보수를 통한 Tr-level Signoff 설계 방법론 전파 및 제공
	* 주요 기술: 
		* 회로 인식 기술, Stage Simulation & Analysis 방법
		* Static 기법을 활용한 Tr-level Signoff Tool 개발 -> Coverage vs. Garbage
		* Dynamic Vector-based Timing Signoff -> Case Definition vs. TAT

### 1.1. Static Signoff methodology
: Simulation Deck(=Unit / BlkStar) 기반으로 회로 인식 -> Cell 단위 Simulation 수행
* Dynamic SO의 Coverage 문제 해결을 위해 개발
* 전통적인 약점(XOR), 설계 Schem 변경 (Bus), 분석 영역 확장 (Core, GIO)으로 인한 Tool Update 필요성 많음

#### 1.1.1." SPACE" Tool Static Signoff Applications
* DSC (Driver Size Check)
* Cana-Tr (Static Coupling Noise Check)
* LS (Level Shifter Check)
* LSC (Latch Strength Check)
* PEC (Power Error Check)
* CDA(Static Coupling Delay Check)

#### 1.1.2. "ADV": Tool Static Signoff Applications
* Power Gating Check

### 1.2. Dynamic Signoff Methodology
: 회로 인식 (Verilog/CKT) + Waveform 인식 (TRN/FSDB) 으로 각 구조에 대한 Simulation 결과 Check

* Dynamic Simulation 기반 Timing SO Tool(ADV)
* Verilog Simulator upgrade에 따른 추가 개발 필요 (python2.7->3.x)

#### 1.2.1. "ADV" Tool Dynamic Signoff Applications
- ADV Checker
- ADV Compare
- ADV Xtracer
- ADV Latch Setup-Hold
- ADV Waveform API
- ADV Margin Analysis
- Current Analyzer
- 열화 검증 자동화
- 마진 검증 자동화

#### 1.2.2. "SPACE" Tool Dynamic Signoff Applications
- Dynamic Coupling Noise Check
- Glitch Margin Analysis
- Dynamic DC Path




