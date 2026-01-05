# 1. Mission & Role

* 메모리 설계 검증을 위한 최적화된 Inhouse Signoff Tool과, 통합 Platform 구축을 통해, Agentic AI 기반 자동화 체계를 준비하여, 설계 검증 효율성 향상에 선도적 역할 수행.

### Inhouse Signoff Tool 개발 및 기능 개선 (SPACE / ADV)
	⮚ C++ 기반 회로 인식 엔진 개선 및 최신 Netlist 문법 지원
	⮚ Python wrapper 전환 및 모듈화 아키텍처 도입으로 유지보수성 및 확장성 강화	
	⮚ Ray 병렬 처리 기술 적용을 통한 대규모 시뮬레이션 성능 향상 및 Runtime 단축

### 사용자 중심 Signoff Platform 구축 (Launcher / ResultViewer)
	⮚ Signoff Launcher: 복잡한 Signoff 설정을 간소화하는 직관적 Interface 환경 및 통합 작업 관리 시스템 제공
	⮚ Signoff ResultViewer: Excel-like 대용량 결과 데이터 분석 환경과 Cross-Probing 등 Signoff 특화 기능 지원
	⮚ Signoff 방법론 및  Seamless Workflow 제공으로 검증 효율성 향상

### Agentic AI 기반 Signoff 자동화 체계 준비
	⮚ 비정형 데이터의 구조화 및 Workspace 아키텍처 구축을 통한 Signoff 데이터 관리 체계 확립
	⮚ Design Portal 연동을 통한 Event-Driven 자동 Signoff 실행 및 결과 피드백 시스템 구현
	⮚ ResultViewer에 LLM 기술을 접목하여  Signoff 결과에 대한 자동 해석 및 설계 개선 제안


# 2. 현황 및 과제

* Signoff Platform 구축을 통한 당면한 메모리 Signoff 도전 과제 해결 및 효율성 혁신 필요

### 현황: 
	- 설계 복잡도 및 난이도의 기하급수적 증가
	- Sign-off Productivity 저하와 검증 TAT 증가
	- 설계 resource cost 급증
	- Runtime↑, Garbage↑, Coverage↓ 문제
	- Signoff 수행 SETUP 난이도 ↑

* Signoff Launcher
	* 잘못된 입력으로 오류 발생
	* 툴별 상이한 수행 환경

* Inhouse Signoff Tools
	* SPIEC Simulation 병목현상
	* 최신 회로 인식 대응 한계

* Signoff ResultViewer
	* 결과 분석 협업 체계 미흡
	* 체계적 데이터 관리 부재

### 과제:
* 24-hour, No-Human-In-The-Loop
	* 설계 변경 감지 및 자동 Signoff 수행
	* 24시간 무중단 검증 환경
* 검증 효율성 혁신
	* Signoff TAT 단축
	* 설계 오류 조기 발견으로 설계 품질 향상
* AI기반 데이터 분석 및 Application 개발
	* 자동 waiver 처리 및 맞춤 결과 요약
	* AI Solution 연구 개발 기반 마련


# 3. 업무추진 전략계획

* 표준화된 데이터 관리와 단위 요소 기술 개발을 통해, 단계적 자동화 및 Agentic AI 기반 Signoff 실현

### 2025: Phase 1
	•통합 Signoff 환경 구축  
	- Launcher 3.0: 통합 작업 관리 및 워크플로우 체계화- ResultViewer 3.0: Workspace 개선 및 협업 시스템 구축
	•Inhouse Tool 현대화 및 확장성 강화  
	- Python Wrapper 전환: 오픈소스 활용 및 유지보수성 극대화- 외부 EDA Tool 모듈 활용: CCK, Simulation API 활용으로 기능 개선
	•데이터 표준화 및 관리 체계 구축  
	- 통합 DB구조 설계: Input/Output 규약 정의 및 저장소 중앙화- 설계 데이터 자동 수집 체계 구축: UDV, OA Netlist


### 2026: Phase 2
	•설계 변경 감지 및 Event-Driven Signoff 수행
	•표준화된 데이터 파이프라인 구축
	•일괄된 인터페이스와 API를 통한 확장성 확보

### 2027: Phase 3
	•Agent AI 기반 자율 Signoff 시스템 개발
	•AI기반 Garbage Reduction 및 자동 Report
	•데이터 분석 기반 설계 최적화 기술 개발


# 4. 2025 중점추진과제 – Signoff Launcher


##### 1. Signoff Launcher 표준화 및 안정화 (~2025.06)

1-1. Version 1&2(LEGO & BTS) 완전 대체
	•기존 레거시 시스템 기능 100% 대체 및 안정화
	•일관된 사용자 경험 제공을 위한 UI/UX 표준화
	•사용자 피드백 기반 개선사항 반영 및 성능 최적화

1-2. Tool 탑재 프로세스 간소화
	•YAML 기반 설정 시스템 고도화
	•Tool 담당자용 Launcher 탑재 가이드라인 작성
	•자동화된 툴 등록 및 검증 파이프라인 구축

1-3. 배포 프로세스 개선
	•중앙 저장소(Bitbucket Repository) 기반 버전 관리 시스템 도입
	•CI/CD 파이프라인을 통한 자동 배포 체계 구축
	•오류 모니터링 및 알림 시스템 구현

##### 2. WORKSPACE 표준화 (~2025.09)

2-1. 디렉토리 구조 표준화 및 데이터 관리
	•WORKSPACE 표준 디렉토리 구조 형식 강제화
	•변경 사항 추적 및 자동 알림
	•사용자별, 제품별 디스크 사용량 모니터링

##### 3. Design Portal 연동 자동화 (~2025.12)

3-1. API 연동 시스템 개발
	•Design Portal UDV/Netlist Query 시스템 구현
	•설계 변경 실시간 감지 및 자동 Event-Driven 자동화
	•변경 영향도 분석 및 최적 Signoff 선택 로직



# 4. 2025 중점추진과제 – Signoff ResultViewer

##### 1. 대용량 데이터 처리 시스템 고도화 (~2025.06)

1-1. SQL 쿼리 기반 데이터 로딩 시스템 
	•DuckDB  또는 Parquet 기반 로컬 데이터베이스 엔진 통합
	•Low-Code SQL 인터페이스 개발 (Mito 방식 참고)
	•2단계 로딩 프로세스 구현: 1단계: 데이터 메타데이터 및 요약 정보 표시, 2단계: 관심 영역만 선택적 로딩

##### 2. Workspace Explorer 개선 (~2025.09)

 2-1. 폴더 관리 기능 강화
	•폴더 생성/이동/이름 변경 인터페이스 개선
	•일괄 작업 지원
	•검색 및 필터링 기능 고도화

 2-2. Waiver Dashboard 개발 
	•폴더별 Signoff 결과 요약 시각화
	•누적 Waiver 통계 및 추세 분석
	•카테고리별 Comment 작성 (Confluence Page 연동)

 2-3. 버전 관리 시스템
	•Git 기반 변경 이력 추적
	•버전 간 비교 및 병합 기능
	•사용자 주석 및 피드백 시스템


##### 3. 협업 시스템 강화 (~2025.12)
3-1. 실시간 동시 편집 기능
	•WebSocket 기반 실시간 데이터 동기화
	•편집 충돌 해결 메커니즘
	•사용자 활동 표시 및 알림

3-2. 담당자 지정 및 Knox Messenger 알림
	•담당자 지정 및 알림
	•변경 사항 및 주요 이벤트 알림
	•데이터 액세스 요청 및 승인 시스템

##### 4. 시각화 및 분석 기능 확장 (~2025.12)

4-1. Application별 Predefined View 확장

	•툴 담당자 및 설계팀과 협업하여 특화 모드 개발
	•맞춤형 필터 및 분석 템플릿 지원


4-2. 고급 시각화 엔진

	•Plotly Resampler 방식의 대용량 차트 렌더링
	•인터랙티브 데이터 분석 지원

4-3. LLM 기반 AI 분석 지원

	•자연어 쿼리를 통한 데이터 조작 (예: "A의 오류 데이터 보여줘")
	•결과 요약 및 패턴 분석 자동화
	•최적 해결책 추천 시스템


# 4. 2025 중점추진과제 – Signoff Engine



##### 0. SPACE & ADV 업그레이드 

0-1. 인식 엔진 고도화

•최신 Netlist 문법 지원
•인식 정확도 향상 및 예외 처리 강화
•회로 토폴로지 인식 알고리즘 개선



##### 1. Python Wrapper 전환 (~2025.06)
1-1. SWIG 기반 Python API 개발
	•기존 Tcl Wrapper → Python Wrapper 전환
	•핵심 C++ 엔진 기능의 Pythonic 인터페이스 설계
	•API 문서화 및 사용 예제 개발

##### 2. Ray 기반 병렬 처리 시스템 개발 (~2025.09)

2-1. SPICE Simulation 병렬화  
	•HPC LSF Scheduler 환경과 Ray 클러스터 연동
	•분산 작업 제출 및 모니터링 시스템
	•실패한 시뮬레이션 자동 감지 및 재시도

2-2. 성능 최적화
	•I/O 병목 현상 해소를 위한 메모리 내 데이터 파이프라인
	•중간 결과 캐싱 및 재사용
	•리소스 사용량 동적 조정


##### 3. Application 레벨 개선 (~2025.12)

3-1. Signoff Application(ex: Driver Size Check) 모듈화
	•핵심 워크플로우 재구성
	•Python 기반 제어 로직 구현
	•단계별 모니터링 및 디버깅 기능

3-2. Primesim API 연동 
	•Synopsys Primesim Python API 통합
	•SPICE 시뮬레이션 직접 호출 인터페이스
	•시뮬레이션 결과 메모리 내 처리


# 5. Summary

메모리 설계 Signoff의 새로운 패러다임을 위해 표준화된 데이터 관리와 핵심 기술을 개발해 나가겠습니다.
단기적으로는 Signoff Platform 구축을 통해 설계팀 요구 기능을 모두 개발하겠으며, Signoff 파이프라인의 효율성을 높이겠습니다.
장기적으로는 Agentic AI 기반 No-human-in-the-loop 환경의 자율 Signoff 시스템을 실현하여 메모리 설계 완성도 향상에 기여하겠습니다.