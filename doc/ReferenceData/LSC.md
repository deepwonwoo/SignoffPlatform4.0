
## LSC (Latch Strength Check) User Guide

### 1. 개요

#### 1.1 한줄 요약
LSC는 메모리 회로 설계에서 Latch의 강도를 검증하고 최적화하기 위한 시뮬레이션 기반 도구입니다.

#### 1.2 상세 설명
Latch는 메모리 회로 설계에서 핵심적인 역할을 하는 요소로, 일시적으로 데이터를 저장하고 유지하는 기능을 담당합니다. Latch의 올바른 동작은 전체 메모리 시스템의 신뢰성과 성능에 직접적인 영향을 미칩니다.

LSC 도구는 다음과 같은 주요 기능을 제공합니다:
- 전체 회로에서 모든 Latch를 자동으로 식별 및 추출
- 각 Latch의 강도를 정밀하게 분석
- Weak Inverter의 적절성 검증
- 다양한 동작 조건에서의 Latch 성능 평가

LSC를 통한 Latch 최적화는 다음과 같은 이점을 제공합니다:
- 데이터 무결성 향상: 적절한 Latch 강도로 데이터 보존 능력 개선
- 전력 효율성 증대: 불필요하게 강한 Latch로 인한 전력 낭비 방지
- 타이밍 마진 최적화: Latch의 응답 시간 개선으로 전체 회로의 성능 향상


### 2. 작동 원리

#### 2.1 한줄 요약
LSC는 회로 분석, Latch 식별, SPICE 시뮬레이션 수행, 결과 분석의 단계를 거쳐 Latch의 강도와 성능을 종합적으로 평가합니다.

#### 2.2 상세 설명
LSC의 작동 과정은 다음과 같은 주요 단계로 구성됩니다:

1. 회로 분석 및 Latch 식별:
   - SPC 또는 STAR 파일의 Netlist 파싱
   - MP, EDR, Power 정보(VDD/GND)를 이용한 회로 Topology 구성
   - Channel Connected Block (CCB) 알고리즘을 사용하여 Latch 구조 식별
   - Pull-Up 및 Pull-Down 네트워크 분석을 통한 Latch 특성 파악

2. 시뮬레이션 준비:
   - 식별된 각 Latch에 대한 SPICE Simulation Input Deck 생성
   - 기본 Slope 값 (일반적으로 400ps) 설정
   - 다중 입력 Latch에 대한 개별 시뮬레이션 설정

3. SPICE 시뮬레이션 실행:
   - Normal Slew Simulation: Latch의 기본 동작 특성 평가
   - Set/Reset Slew Simulation: Latch의 초기화 기능 검증
   - 주변 회로 영향을 고려한 추가 로딩 시뮬레이션

4. 결과 분석:
   - Delay 및 Slew 측정값 추출
   - Weak Inverter의 강도 평가
   - Set/Reset 기능의 정상 동작 확인
   - 주변 회로의 영향 분석

5. 보고서 생성:
   - 각 Latch의 성능 지표 요약
   - 문제가 있는 Latch 식별 및 상세 정보 제공
   - 최적화를 위한 제안사항 포함

### 3. 주요 검증 항목

#### 3.1 Normal Slew Simulation
- 목적: Latch의 기본 동작 특성 평가 (새로운 데이터 쓰기&기존 데이터 유지)
- 방법: 
  - Latch Data 입력에 테스트 신호(일반적으로  slope 400ps) 인가
  - Clock/Clockb는 DC로 열림 상태(데이터를 받아들일 수 있는 상태), Set/Reset은 DC로 닫힘 상태(신호들이 Latch의 동작에 영향을 주지 않도록 비활설화) 설정
  - Latch Output의 Delay와 Slew 측정
- 결과 해석: Delay 및 Slew 값이 클수록 Weak Inverter의 강도가 부족할 가능성이 높음

#### 3.2 Set/Reset Slew Simulation
- 목적: Latch의 초기화 기능 검증 (Set과 Reset 신호에 대한 Latch의 반응을 평가)
- 방법:
  - Set/Reset 입력에 테스트 신호 인가 
  - Clock/Clockb는 DC로 닫힘 상태(Latch가 일반적인 데이터 입력을 받지 않도록 함) 설정
  - Weak Inverter 출력과 Latch Output을 초기 상태로 설정
- 결과 해석: Delay 및 Slew 값을 통해 Set/Reset 기능의 정상 동작 여부 판단

#### 3.3 주변 회로 영향 분석
- 목적: Latch 주변 회로의 캐패시턴스 영향 평가
- 방법:
  - Latch의 Data, Latch Net, Output 등에 연결된 회로에 대한 Gate Cap 모델링
  - 추가 로딩을 고려한 시뮬레이션 수행
- 결과 해석: 실제 동작 환경에서의 Latch 성능 예측

#### 3.4 개선된 Stimulus 인가 방법
- 목적: 더 정확한 Latch/Driver Strength 평가
- 방법: Line Loading을 제거하여 Input Line Delay의 영향을 최소화 (기존 방식에서는 Driver의 Input Line Delay를 고려했었는데, 이는 긴 라인에서 과도한 Delay 결과를 초래할 수 있)
- 결과 해석: Driver와 Latch의 본질적인 Strength에 초점을 맞춘 평가 가능 (Line의 길이나 복잡성에 관계없이 일관된 결과를 얻을 수 있어, Latch의 성능을 더 정확히 평가할 수 있음음)

### 4. 결과 해석

LSC의 실행 결과는 CSV 형식의 테이블로 제공됩니다. 주요 컬럼과 그 의미는 다음과 같습니다:

| 컬럼명 | 설명 |
|--------|------|
| Rise_Delay | Rise Slew의 50% 구간에서의 최대 지연 값 |
| Fall_Delay | Fall Slew의 50% 구간에서의 최대 지연 값 |
| Rise | Measure Net의 최악의 Rise Slope 값 (ns) |
| Fall | Measure Net의 최악의 Fall Slope 값 (ns) |
| Data Net | 데이터 네트 이름 |
| Measure Net | 측정 네트 이름 |
| Driver MOS | 대표 NMOS 드라이버 이름 |
| Master | Measure Net의 주 이름 |

결과 분석 시 주의사항:
- Rise_Delay와 Fall_Delay: 이 값들이 크면 Weak Inverter의 강도가 부족할 수 있습니다.
- Rise와 Fall: 이 값들은 Latch의 응답 속도를 나타냅니다. 너무 크면 성능 저하의 원인이 될 수 있습니다.
- Data Net과 Measure Net: 이 정보를 통해 문제가 있는 Latch의 위치를 정확히 파악할 수 있습니다.
- Driver MOS: 대표 NMOS의 특성을 통해 Latch의 구동 능력을 판단할 수 있습니다.
- Master: 해당 Latch가 속한 상위 모듈을 식별하여 시스템 레벨의 최적화에 활용할 수 있습니다.
