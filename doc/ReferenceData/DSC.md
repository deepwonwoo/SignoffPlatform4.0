

DSC 는 회로의 driver에 일정한 slew time의 input stimulus를 가했을 때 얻어지는 output slew를 측정함.

# 정책 :
* Input Vector Case : Slew simulation 은 all case input vector 조합을 만든다.
* Slew margin  : Simulation 의 측정 마진은 default 10%~90% 이다.
* Latch : latch net 과 weak inverter 가 driver 가 되는것은 제외한다.

# 결과 파일 :
* RESULT/result

# DSC 구성 클래스
* DriverSizeCheck : DSC 의 수행을 시작하며, 수행 옵션을 초기화함.
* SlewSimulation : DSC 의 Simulation 로직을 관리함.
* SlewSpiceDeck : DSC 의 Spice Deck Data 를 저장함.


# Command run : driver_size_check [-debug] [-step double] \[-slope  double] \[-time double] \[-temperature double] \[-voltage double] [-id int] [-start int] [-end int] [-o file_name]

-debug (default : false) : Simulation deck 을 보존 시킴 (삭제x).
-slope (default : 0.5ns): input 에 인가되는 input slope 설정.
-step (default : 0.01ns): simulation step 설정.
-time (default : 10ns): simulation time 설정
-temperature : simulation temperature 설정 ( tech file 덮어씀.)
-voltage : default driver voltage 설정
-id : 특정 deck ID 의 simulation 실행.
-start : simulation 시작 deck ID 설정. (구간 설정)
-end : simulation 종료 deck ID 설정. (구간 설정)

# Input 파일
Netlist : .spc, .blk, .star 사용 가능
MP, EDR : 모델 해석을 위해 입력.
Finesim Input(.sp) : 위 Netlist , MP, EDR 이 모두 첨부된 Finesim Input 파일을 최종 입력으로 사용.


# Result 파일 분석

Rise : rising slew 의 max 값
Fall : falling slew 의 max 값
Measure_Net : measure net 의 이름
Driver_NMOS : Driver stage 의 대표 nmos 이름
Master : driver 가 속한 최상단 master 이름 (blk 의 경우 존재하는 subckt 최상단 출력)
Coupling_Cap : measure net 의 total coupling cap
Ground_Cap : measure net 의 total ground cap
Number_of_Receiver_MOS : receiver 의 mos 개수
Driver_PMOS_Width : driver pmos 중 max width 값
Driver_PNOS_Width : driver nmos 중 max width 값
Sum_of_Receiver_Area : receiver mos 의 width * length * multiplier 의 총합

---


## 1. 개요

### 1.1 한줄 요약
DSC는 메모리 회로 설계에서 Driver의 크기 적절성을 평가하고 최적화하기 위한 정적 검증 도구입니다.

### 1.2 상세 설명

Driver는 메모리 회로 내에서 신호를 다음 단계로 전달하는 중요한 요소입니다. Driver가 너무 작으면 신호가 약해져 오작동의 원인이 될 수 있고, 너무 크면 불필요한 전력 소모와 면적 낭비를 초래합니다. 따라서 각 Driver의 크기를 최적화하는 것이 중요합니다.

DSC는 이러한 배경에서 개발되었으며, 다음과 같은 주요 기능을 제공합니다:
- 전체 회로에서 모든 Driver를 자동으로 식별 및 추출
- 각 Driver의 구동 능력을 분석
- 과다/과소 크기의 Driver 식별

DSC를 통한 Driver 최적화는 칩의 전반적인 성능 향상, 전력 효율성 증대, 신뢰성 확보에 기여하며, 결과적으로 고품질의 메모리 제품 개발을 가능하게 합니다.

## 2. 작동 원리

### 2.1 한줄 요약
DSC는 회로 Parsing, Driver 추출, SPICE Simulation, 결과 분석의 단계를 거쳐 Driver 크기의 적절성 판단에 도움을 줍니다.

### 2.2 상세 설명
DSC의 작동 원리는 다음의 주요 단계로 구성되며, 각 단계는 세부적인 알고리즘과 기술을 활용합니다:
1. 회로 Parsing 및 Driver 추출:
    - 입력된 SPICE Netlist를 Parsing하여 회로 Topology를 그래프 구조로 변환
    - Channel Connected Component (CCC) 알고리즘을 사용하여 Driver 회로 식별:
        - 전원(VDD)에서 접지(GND)까지 연결된 Transistor 그룹을 하나의 Driver로 인식
        - PMOS와 NMOS의 연결 구조를 분석하여 Driver 유형(인버터, 버퍼 등) 판별
    - 추출된 Driver의 Topology 정보(Transistor 크기, 연결 구조 등) 저장
2. Test Vector 생성:
    - 각 Driver 유형에 맞는 최적의 Test Vector 생성:
        - 일반적으로 500ps의 Rise/Fall 시간을 가진 Pulse 신호 사용
        - Driver의 입력단에 연결된 부하를 고려하여 입력 신호의 강도 조정
    - 다양한 동작 조건(PVT: Process, Voltage, Temperature) 고려:
        - 최악 조건 (SS, 낮은 전압, 높은 온도)
        - 최선 조건 (FF, 높은 전압, 낮은 온도)
        - 일반 조건 (TT, 공칭 전압, 상온)
3. SPICE Simulation:
    - 추출된 각 Driver에 대해 개별적인 SPICE 시뮬레이션 수행 (병렬 처리)
    - 입력 자극에 대한 Driver의 출력 응답 시뮬레이션
    - Simulation 중 주요 측정 포인트:
        - 입력 신호의 50% 지점
        - 출력 신호의 10%, 50%, 90% 지점
4. 결과 분석:
    - Simulation 결과로부터 주요 전기적 특성 추출:
        - Slew rate: (V90% - V10%) / (T90% - T10%)
        - Propagation delay: T50%(출력) - T50%(입력)
        - Rise/Fall time: T90% - T10%
    - 추출된 특성을 미리 정의된 기준과 비교하여 Driver 크기 평가:
        - Under-sized: 출력 특성이 기준의 80% 미만
        - Over-sized: 출력 특성이 기준의 120% 초과
        - Optimal: 출력 특성이 기준의 80%~120% 범위 내

## 결과

DSC의 실행 결과는 CSV 형식의 테이블로 제공됩니다. 주요 컬럼은 다음과 같습니다:

| 컬럼명         | 설명                                |
| ----------- | --------------------------------- |
| Rise_Delay  | 최대 지연 시간에서 Rise Slew의 50% 구간 (ns) |
| Fall_Delay  | 최대 지연 시간에서 Fall Slew의 50% 구간 (ns) |
| Rise        | MeasureNet의 최악의 Rise Slope 값 (ns) |
| Fall        | MeasureNet의 최악의 Fall Slope 값 (ns) |
| Data Net    | 데이터 네트 이름                         |
| Measure Net | 측정 네트 이름                          |
| Driver MOS  | 대표 NMOS의 드라이버 이름                  |
| Master      | Measure Net의 주 이름                 |

1. Rise_Delay와 Fall_Delay:
    - 이 값들은 Driver의 전파 지연 시간을 나타냅니다.
    - 일반적으로 이 값들이 작을수록 Driver의 성능이 좋다고 볼 수 있습니다.
    - 그러나 너무 작은 값은 과도한 전력 소비를 의미할 수 있으므로 주의가 필요합니다.
2. Rise와 Fall:
    - 이 값들은 출력 신호의 상승 및 하강 시간을 나타냅니다.
    - 빠른 상승/하강 시간은 고속 동작에 유리하지만, 너무 빠르면 오버슈트나 언더슈트 문제가 발생할 수 있습니다.
3. Data Net과 Measure Net:
    - 이 정보를 통해 문제가 있는 Driver의 위치를 정확히 파악할 수 있습니다.
    - 회로 설계 시 이 정보를 참조하여 해당 Driver를 최적화할 수 있습니다.
4. Driver MOS:
    - 대표 NMOS의 이름을 통해 해당 Driver의 구체적인 구현을 확인할 수 있습니다.
    - 이 정보는 Driver 크기 조정 시 유용하게 사용될 수 있습니다.
5. Master:
    - Measure Net의 주 이름을 통해 해당 Driver가 속한 상위 모듈이나 기능 블록을 식별할 수 있습니다.
    - 이는 시스템 레벨에서의 최적화 전략 수립에 도움이 됩니다.






수행 요약
1.Read Input File:  spc, blk ,star 파일을 입력 받아 Parsing 한다.
2.Stage 추출: 입력 받은 Netlist 파일을 분석하여 CCC 알고리즘으로 Stage를 추출. Driver Size를 측정하기 위한 Slew Simulation의 단위가 된다.
3.Slew Simulation
3.1 Spice Deck, Vector 생성: 추출한 Stage를 이용하여 Slew SImulation을 위한 Spice Deck과 Vector를 생성.
3.2 Slew 측정: Input Slope 500ps로 Finesim Simulation을 수행 하여 Rising Slew와 Falling Slew를 측정.

결과 
1. Rise_Delay: 최대 지연 시간에서 Rise Slew의 50% 구간 
2. Fall_Delay: 최대 지연 시간에서 Fall Slew의 50% 구간 
3. Rise: MeasureNet의 최악의 Rise Slope 값 (ns) 
4. Fall: MeasureNet의 최악의 Fall Slope 값 (ns) 
5. Data Net: 데이터 네트 이름 
6. Measure Net: 측정 네트 이름 
7. Driver MOS: 대표 NMOS의 드라이버 이름 
8. Master: Measure Net의 주 이름

"""










#   1. 개요
## 1.1. Drivier Size Check 개념

 회로의 driver에 일정한 slew time의 input stimulus를 가했을 떄 얻어지는 output 를 측정한다.
 실제 slew time과는 무관하며 input 대비 output slew의 비율로서사용자가 driver size가 취약하거나 과다한 부분을 판단하도록 돕는 도구이다.

## 1.2. Driver Size Check 동작 방식

Driver Size Check은 Channel Connected Components 알고리즘을 통해 Transistor Level의 회로를 Partition하며, Partition된 회로들을 Finesim Simulation을 통해 회로의 Slope를 측정한다.

Channel Connected Components는 Source, Drain과 연결되어 있는 Transistor들의 집합으로 Driver Size Check 수행 시 회로 Partition의 기본 단위이다. 영문 정의는 다음과 같다. 
* A Circuit partition unit connected by transistor junctions, aka 'stage', similar to a 'gate'.
실제 Driver Size Check에서는 Transmission Gate는 따로 관리하며, Simulation 회로 Partition에 포함된 경우 Transmission Gate는 열어둔(연결) 상태로 Simulation을 수행한다.

# 2. 수행 요약
## 2.1. Read Input File
 DSC의  Input으로 spc, blck, star 모두 가능하다. spc, blk, star 파일을 입력 받아 Parsing한다.

## 2.2. Stage 추출

입력 받은 Netlist 파일을 분석 하여 Stage를 추출한다. Stage는 Chaneel Connected Components 알고리즘으로 추출되어, Driver Size를  측정하기 위한 Slew Simulation의 단위가 된다.

## 2.3. Slew Simulation

### 2.3.1. Spice Deck, Vector 생성

추출한 Stage를 이용하여 Slew Simulation을 위한 Spice Deck과 Vector를 생성한다. 생성된 Spice Deck과 Vector로 SPICE(Sysnopsys사의 Primesim) Simulation이 수행된다.

### 2.3.2. Slew 측정

Input Slope 500ps로 Primesim Simulation을 수행하여 Rising Slew와 Falling Slew를 측정한다.





3. 