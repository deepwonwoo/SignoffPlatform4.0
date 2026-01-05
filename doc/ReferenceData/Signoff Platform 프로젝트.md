## Signoff Platform 개발 업무

## 1. Signoff Platform 개요

Signoff Platform은 삼성전자 메모리 회로 설계의 Tr-level Signoff 검증을 위한 통합 솔루션입니다. Design Technology Team의 Design Simulation&Signoff Group의 Signoff Part 조직에서 개발하고 있는 이 플랫폼은 DRAM, FLASH, HBM 등 다양한 메모리 제품의 Tr-Level 회로 설계 검증을 위한 Inhouse Tool 및 Signoff Application들을 통합하고, GUI를 제공하여 User(회로설계)-Friendly한 GUI를 제공하여 사용을 효율적이게 만들며 Seamless한 Signoff 방법론 및 프로세스를 개발을 목표로 합니다..

### 1.1 배경 및 필요성

#### 메모리 설계의 특수성

전통적인 메모리 제품, 특히 DRAM 제품의 설계는 full-custom 기반의 설계 기법을 채용하여 다음과 같은 특성을 갖습니다:
* Memory Architecture: Cell-oriented Architecture, APP-focused, High-speed IO, Peripheral Control Logic
* Custom Design Flow: Tr.-level Custom Design, Pitched-layout, Manual-placement & semi Auto-routing, Tr.-level Signoff
* Design Coverage: Knowledge/ experience-based Dynamic Verification, Productivity and Signoff
* Process & Design parallel development: many Iteration for Design Optimization

#### 현황 및 도전 과제

최근 제품의 고사양화와 설계 복잡도/난이도 증가로 인해 다음과 같은 문제점들이 대두되고 있습니다:
1. **설계 검증 효율성 저하**:
   - CSR(Chip Size Reduction) 목적의 최적 설계를 위한 TR-level Sign-off Productivity 저하
   - 설계 실수/오류/미검출 증가로 인한 제품 완성도 저하

2. **리소스 관리 문제**:
   - 설계 복잡도/난이도 증가와 사용되는 설계 tool의 종류/수 지속 증가로 design resource cost 급증  (설계용 tool license/HW비용, ~1,200억원@22년, 전년 대비 63% 증가)
   - 설계 productivity 이슈(pending 증가 등 VOE)와 resource 수요 예측-실 사용 시점/수량 간 차이로 인한 resource 부족/낭비 발생
   - 전체 설계 TAT(Turn Around Time) 증가 리스크 발생  (예: 21년 7월 XF ver. Rev.시 Pending으로 회로 검증 평균 2일 지연)

3. **주요 원인 분석**:
   - Runtime 증가: 복잡한 회로 구조로 인한 검증 시간 증가
   - 진성 오류 검출력 저하(Garbage 증가): 중요한 오류를 놓치는 문제 발생
   - Signoff Coverage 부족: 모든 설계 케이스를 검증하지 못하는 문제
   - GUI 사용성 문제: 기존 도구의 사용자 인터페이스 한계

특히나 Signoff Inhouse Tool의 핵심 엔진은 레거시 코드로 개발된지 오래되었고 핵심개발자는 퇴사한지 오래되어 유지보수가 어려우며, Signoff Tool을 사용하는 각  Signoff Application 담당자들은 가각 따로 툴의 전처리 및 후처리를 산재되어 관리되고 있어서 전반적인 Signoff SW 개발에 어려움이 점점 커지고 있다.

## 2. 개발환경 

### 2.1 사내 HPC 환경

삼성전자 반도체 메모리 사업부에서는  사내 전용의 HPC(High Performance Computing)를 사용하고 있습니다. 사내 HPC는 IBM Spectrum LSF(LSF: Load Sharing Facility) Job Scheduler를 통해 운영되고 있습니다. `

각각의 사용자들은 진행하고 있는 자신이 개발하고있는 제품별로 프로젝트 공간의 권한을 가지게 됩니다.
예를 들어 내가 HBM3E 제품을 개발하고있다면 리눅스 시스템에 /user/hbm3e/ 라는 계정 공간(다른 storage에서 network mount)에서 작업하게 되며, 이 공간의 권한은 newgrp hbm3e 명령어로 권한을 획득(프로젝트 멤버만 가능)하여 작업을 수행합니다.  Signoff관련 작업은 보통 /user/{PRJ명}/VERIFY/SIGNOFF 에서 작업을 진행합니다.

### 2.2 GUI 애플리케이션 실행 방식

Signoff Launcher나 Signoff ResultViewer와 같은 Signoff GUI들은 HPC 환경에서 bsub를 wrapping한 특수 명령어를 사용합니다:
- **sol_sub**: Signoff Launcher를 실행하기 위한 명령어
- **sorv_sub**: Signoff ResultViewer를 실행하기 위한 명령어

이러한 GUI 작업들은 flaskwebgui를 사용하여 다음과 같은 프로세스로 진행됩니다:
1. 'gui' queue로 작업이 제출되어 해당 계산노드에서 dash web server가 실행됨
2. 사용자의 chrome browser가 해당 web server에 접속 (하나의 web 서버에 한 명의 사용자가 접속하는 형태)
즉, one user마다 하나의 one web server를 실행시켜서 수행되어 사용자는 웹앱이 아니라 하나의 Standalone Application처럼 사용하는 방식으로 운영되고 있습니다.

### 2.3 Signoff Simulation 실행 방식


Signoff 수행을 위해서는 각 Application마다의 run script(run.sh)를 통해서 전처리 수행후 bsub과 같은 명령어(bsub를 wrapping한 특수한 명령어 사용)로 HPC에 해당 signoff simulation 작업을 제출하고 후처리를 수행하는 방식으로 사용하고 있다. 사용자는 복잡한 LSF 옵션을 직접 지정할 필요 없이 사내 메모리 부서에서 정한 표준 설정으로 작업을 제출합니다. 대표적인 Signoff Engine으로는 space와 adv가 있으며 각 엔진을 활용한 Signoff Application 툴은 해당 엔진에 tcl파일을 argument로 넘겨줘서 수행하게 된다.

ex) Driver Size Check 수행 run.sh 
```bash
# DSC_RUNSCRIPT/run.sh
dsc_preprocess.py
space_sub -f dsc_run.tcl 
dsc_postprocess.py
```

- **space_sub**: Static Signoff Applications 계열의 작업을 제출하는 명령어, SPACE는 C++로 만들어진 SW로 입력받은 Netlist를 바탕으로 Static Signoff를 수행 
- **adv_sub**: Dynamic Signoff Applications 계열 작업 제출 명령어, ADV는 AnalogDigitalVerification의 약자로 C++로 만들어진 SW로 입력받은 Netlist를 바탕으로 Dynamic Signoff를 수행

## 3. Signoff Platform 구성 요소

Signoff Platform은 크게 세 가지 핵심 구성 요소로 이루어져 있습니다:
### 3.1 Signoff Launcher (SOL)

Signoff Launcher는 삼성전자 메모리 회로 설계의 Tr-level Signoff 수행을 위한 웹 기반 인터페이스 도구입니다. Signoff 수행을 위해 C++로 만들어진 Signoff Engine에 입력과 복잡한 Signoff 설정 과정을 단순화하고 통합된 인터페이스를 제공하여 다양한 Signoff Application을 효율적으로 실행할 수 있게 합니다.

**주요 특징:**
- Signoff Launcher는 작업 workspace공간을 설정해서 수행하고 해당 workspace 공간에서 Signoff Application RUNSCRIPT를 복사해와서 Signoff 작업 수행, workspace공간의 표준 경로는 /user/{PRJ 제품 계정  공간}/VERIFY/SIGNOFF/{LIB}/{CELL}/{USER}/{TOOL} 구조임.
- Tool별 필수 입력 수 최소화, 여러 툴을 동시에 생성해서 수행할수 있는데 이때 공통 입력들에 대해서는 입력을 share하여 생성하도록 하여 입력을 최소화하고 interface를 간단하게 만들고자 하였음.
- Universal Voltage Document(UVD) 등 설계 DB 입력 자동 Query 기능
- Job Queue 기능으로 다중 Corner/Block 동시 실행 지원.
- 작업제출을 위해 sub process로 HPC LSF Scheduler에 해당 Signoff 작업 제출, 이때 Launcher의 해당 Signoff 입력은 환경변수로 넘겨주기 위해 입력값들을 env파이로 만들고 subprocess에서 run.sh수행전에 source env 수행.

**기술 스택:**
- Frontend: Plotly Dash 기반 웹 애플리케이션 (UI Component로 dash_mantine_component, dash_blueprint_component을 주로 사용, tableview는 dash_ag_grid 사용)
- Backend: Python, LSF Job 제출, rest api를 통해 Devworks(사내 메세지 알림 시스템) API 혹은 Design Portal(사내 설계 관련 DB: netlist, MP, EDR, PowerVoltage),C++ Inhouse Signoff Tool 연동
- 데이터 저장: YAML, JSON, 파일 시스템 기반 Workspace
- 작업 관리: Subprocess, LSF Scheduler(HPC)

### 3.2 Signoff ResultViewer (SORV)

Signoff ResultViewer는 Signoff 수행 결과를 효율적으로 분석하기 위한 웹 기반 CSV Editor Tool입니다. Excel과 유사한 인터페이스를 제공하면서도 대용량 데이터 처리가 가능하고, Signoff 특화 기능을 통해 설계 검증 프로세스를 최적화합니다.

**주요 특징:**
- 10M+ 라인 데이터 1초 이내 처리 성능 (Dash AG Grid를 사용해서 ServerSideRowModel 방식으로 구현, Grid Data(dataframe) 처리를 위해 backend에서는 Rust 기반 Polars를 활용하여 연산)
- Signoff 특화기능 중 하나인 Schematic Editor와의 (VSE 및 BTS) CrossProbing
- Excel과 유사한 직관적인 UI (Sorting, Filtering, Grouping 등, backend에서 dataframe을 polars로 처리)
- Signoff 특화기능 중 하나인 Waiver에 대한 작업 및 이전버전 혹은 협업한 내용을 현재 버전의 dataframe에 적용하기 위해 Waiver Migration 기능 제공
- WORKSPACE를 활용한 중앙 집중식 결과 관리 : /user/signoff라는 전용 Signoff 공간을 이용하여 마치 ResultViewer에 데이터를 업로드 시키면 클라우드 Drive에 데이터를 업로드 시키는 것과 같이 데이터를 저장하여 다른 사용자들에게 공유하고 협업이 가능하도록 지원. 업로드된  Signoff 결과 데이터(result.csv)는 parquet으로 변환시키고 ResultViewer에서 작업하는이기에 필수로 

**기술 스택:**
- Frontend: Web 기반 (Plotly Dash)
- Backend: 대용량 데이터 처리에 최적화된 기술 (Polars - Rust 기반)
- 데이터 관리: WORKSPACE 기반 중앙 집중식 관리
- 인터페이스: Excel과 유사한 UI/UX

### 3.3 Signoff Inhouse Tool

Signoff Inhouse Tool은 실제 회로 검증을 수행하는 Core 기능을 담당하는 요소입니다. SPACE(Static Signoff Applications)와 ADV(Advanced Dynamic Verification) Tool을 통한 Static/Dynamic Signoff를 수행하며, 다양한 Signoff Application에 대한 검증 로직과 방법론을 포함합니다.

**주요 특징:**
- SPACE와 ADV Tool을 통한 Static/Dynamic Signoff 수행
- Pre-layout Simulation 방법론 개발 (Digital Circuit에서 Post-layout 대비 ~98% 정합성 확보)
- 12종 Signoff Application별 Waiver/Analysis 방법 개발
- C++ 기반 핵심 알고리즘 구현

**주요 Signoff Applications:**
- **Static Signoff Applications (SPACE)**: 
  - DSC(Device Stress Checker)
  - LSC(Level Shifter Checker)
  - Cana-Tr(Capacitance Analysis)
  - PN RATIO
  - FOCHECK(Fan-Out Checker)
  - 기타
- **Dynamic Signoff Applications (ADV)**:
  - Glitch Margin Analysis
  - Dynamic DC Path
  - IDDQ Analysis
  - 기타

## 4. 결론 및 기대 효과

Signoff Platform의 통합 개발 및 고도화를 통해 삼성전자 메모리 회로 설계의 검증 프로세스를 획기적으로 개선하고, 제품 완성도 향상과 개발 TAT 단축을 실현할 수 있을 것으로 기대합니다. 

### 주요 기대 효과

1. **설계 품질 향상**:
   - Signoff Coverage 확대로 설계 결함 조기 발견
   - 오류 검출력 강화로 제품 신뢰성 제고
   - 더 정확한 검증 결과로 최종 제품 완성도 향상

2. **개발 기간 단축**:
   - 효율적인 검증 프로세스로 TAT 단축
   - 자동화된 워크플로우로 반복 작업 최소화
   - 병렬 처리 및 최적화로 실행 시간 단축

3. **리소스 활용 효율화**:
   - 분석 부담 감소로 설계자 생산성 향상
   - 컴퓨팅 리소스 최적화로 비용 절감
   - 협업 환경 개선으로 팀 효율성 제고

4. **방법론 고도화**:
   - AI/ML 기반의 지능형 검증 방법론 확립
   - 저전력 설계 검증 역량 강화
   - Pre-layout Simulation 정확도 향상

이러한 목표 달성을 위해 체계적인 계획 수립과 지속적인 개선, 그리고 관련 부서와의 긴밀한 협력을 통해 Signoff Platform을 지속적으로 발전시켜 나갈 것입니다.
