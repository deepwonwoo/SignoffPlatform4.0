
Sign-off Tools:
메모리 설계의 특성상 일반 EDA 툴 대신 C++ 기반의 자체 개발 Inhouse Tool인 "SPACE"와 "ADV"를 사용합니다.
* 주요 기술: 회로 인식 기술, Stage Simulation & Analysis 방법론, Waveform 분석

Sign-off Tool 현황: Static (9종), Dynamic (13종)
1) Static: Static topology 인식, Simulation 결과 도출, DSC (Driver Size Check), LSC (Latch Strength Check), cana Tr (Coupling noise), etc.
2) Dynamic: 설계 spec/criteria 기반 simulation 결과 분석, ADV, dynamic coupling noise check, glitch margin analysis, etc. 


# Signoff Inhouse Tool #1 : SPACE
 
 : 주로 Static Signoff Application을 담당하며, 회로 토폴로지 기반의 분석을 수행합니다.
 : SPACE는 기본적으로  input으로 spice netlist, Techfile, Power info 등의 input을 받고 DSC, LS, LSC 등의 Application을 수행해. 각각의 Application들에 따라 추가로 필요로 하는 input들이 있을수있어.
## 1) Driver Size Check(DSC)

### 1.1) 개념
회로의 Driver에 일정한 Slew를 갖는 Input을 가했을 때 Output Slew를 검사
* 목적: Driver 크기의 적절성 판단 및 회로 성능 최적화

일정한 slew time의 input 신호를 driver에 가하고 그에 대한 output 신호의 slew time을 측정하여 input 대비 output slew 비율을 계산.
이 비율은 실제 slew time과는 무관하며, driver의 크기가 적절한지, 취약한지 또는 과다한지 등을 판단하는 데 도움을 줌.
이를 통해 회로 설계자는 driver 크기를 조정하거나 최적화하여 회로의 성능을 향상시키는데 도움을 얻을 수 있습니다.


### 1.2) 동작 방식
DSC은 Channel Connected Component(CCC) 알고리즘을 통해 Transistor Level의 회로를 Partition하며, Partition된 회로들을 Finesim Simulation을 통해 회로의 Slope을 측정.
CCC는 Source, Drain과 연결되어 있는 Trasistor들의 집합으로 DSC 수행 시 회로 Partition의 기본 단위. (CCC: A Circuit partition unit connected by transistor junctions, aka 'stage', similar to a 'gate'.)
실제 DSC에서는 Transmission Gate는 따로 관리하며, Simulation 회로 Partition에 포함된 경우 Transmission Gate는 연결 상태로 Simulation을 수행.

### 1.3) 수행 요약
1.Read Input File:  spc, blk ,star 파일을 입력 받아 Parsing 한다.
2.Stage 추출: 입력 받은 Netlist 파일을 분석하여 CCC 알고리즘으로 Stage를 추출. Driver Size를 측정하기 위한 Slew Simulation의 단위가 된다.
3.Slew Simulation
3.1 Spice Deck, Vector 생성: 추출한 Stage를 이용하여 Slew SImulation을 위한 Spice Deck과 Vector를 생성.
3.2 Slew 측정: Input Slope 500ps로 Finesim Simulation을 수행 하여 Rising Slew와 Falling Slew를 측정.


### 1.4) 결과 
1. Rise_Delay: 최대 지연 시간에서 Rise Slew의 50% 구간 
2. Fall_Delay: 최대 지연 시간에서 Fall Slew의 50% 구간 
3. Rise: MeasureNet의 최악의 Rise Slope 값 (ns) 
4. Fall: MeasureNet의 최악의 Fall Slope 값 (ns) 
5. Data Net: 데이터 네트 이름 
6. Measure Net: 측정 네트 이름 
7. Driver MOS: 대표 NMOS의 드라이버 이름 
8. Master: Measure Net의 주 이름



## 2) Level Shifter Check(LS)

* 기능: Level Shifter에 Input Stimulus를 가했을 때 Output Slew와 Duty 검사
- 목적: 전압 도메인 간 안전한 신호 변환 보장
- 추가 설명:
  Level Shifter Check은 아래와 같은 원리로 진행된다. 먼저 SPC 혹은 STAR파일의 Netlist과 MP, EDR, Power 정보(VDD/GND)를 토대로 모든 Level Shifter의 Topology를 인식한다. 이때 vdd_list와 gnd_list에 모든 power정보를 기술해야 제대로 된 Level Shifter 추출이 가능하다. 충분히 Power가 기술되지 않으면 Warning과 함께 topology가 제대로 인식되지 않을 것이고 Garbage가 많이 생성된다.
  본 Tool은 기본적으로 Power Network인 Pull-Up Network와 Ground Network인 Pull-Down Network를 인식하여 Channel Connected Block(CCB)를 구성하고, 이를 토대로 회로를 Topology를 구성하기 때문이다. 모든 Level Shifter에 대한 인식이 완료됐다면, 인식된 Level Shifter들을 대상으로 정해진 Slope(Default Slope, 400p) 값을 각 Level Shifter 입력에 인가하는 SPICE Slew Simulation input deck을 생성한다. 마지막으로 SPICE Simulation을 진행 후 모든 Simulation이 완료되면 Level Shifter 출력에 대한 Measure logic에 따라 결과를 출력한다.
  이때 Measure Logic은 다음과 같다. Level Shifter 입력에 사용자가 지정한 High->Low Transition을 인가하여, 출력으로 나오는 High->Low Transition의 Duty를 측정한다. 해당 Duty는 전체 Transition 구간 대비 Max Vth값의 구간의 비율이며, 해당 비율이 낮으면 낮을수록 Level Shifter가 정상적으로 동작하지 않을 확률이 높은 것으로, 정밀 검사가 필요한 Level Shifter일 것이다.

	* Level Shifter에 Input Stimulus를 가했을때 output Slew와 duty 검사
	* Level Shifter의 배치와 동작을 확인하는 중요한 검증
	* Level Shifter는 전압 도메인 간의 신호 변환을 담당하는 회로로, 특히 Low Voltage Domain에서 High Voltage Domain는 그 반대로 전압 도메인이 변환될 때 안전한 동작을 보장


### 2.1) 필요성
메모리 설계 과정에서는 Level Shifter의 올바른 배치와 동작이 매우 중요한 요소.
Level Shifter는 전압 도메인 간의 신호 변환을 담당하는 회로로서, Low Voltage Domain에서 High Voltage Domain으로, 혹은 그 반대로 전압 도메인이 변환되는 경우에 안전하게 동작할 수 있도록 해줍니다.
Level Shifter가 없을 때 발생할 수 있는 문제점
1. Low Voltage Domain에서 High Voltage Domain으로 변경될 때: Level Shifter가 없다면 Vth(임계 전압) 이상의 전압을 드라이버하지 못하여 회로가 동작하지 않는 문제가 발생. 이 경우, 신호가 제대로 전달되지 않아 전체 회로의 동작에 영향을 줌.
2. High Voltage Domain에서 Low Voltage Domain으로 변경될 때: Level Shifter가 없다면, 지속적인 부하로 인해 Low Voltage Domain의 트랜지스터가 손상될 수 있음. 이는 전력 소모 증가와 함께 회로의 신뢰성을 저하시키는 원인.
Level Shifter를 올바르게 배치하고 동작하는지 확인하는 작업은 FULLCHIP Level의 Schematic에서 모든 Level Shifter를 찾고 이를 동작하는 Vector를 만든 후 SPICE Simulation 결과를 확인하는 과정을 거쳐야 하는데 수작업으로는 오류가 발생하기 쉽습니다. LS는 이러한 문제를 해결하기 위해 개발된 자동 검증 TOOL. LS는 주어진 회로에서 Level Shifter가 올바르게 배치되었는지 Full Chip Level 의 Schematic에서 모든 Level Shifter를 찾고 SPICE Simulation을 수행 후 그 결과를 Report 로 정리하여 설계자에게 제공.

### 2.2) 원리
1. Netlist 및 Power 정보를 인식하여 Level Shifter의 Topology를 파악: SPC 혹은 STAR파일의 Netlist과 MP, EDR, Power 정보(VDD/GND)를 토대로 모든 Level Shifter의 Topology를 인식. 특히 Power정보를 정확하게 입력하지 않으면 제대로 된 Level Shifter 추출이 불가능. 
2. Power Network와 Ground Network를 인식하여 회로의 Topology를 구성: 본 도구는 기본적으로 Power Network인 Pull-Up Network와 Ground Network인 Pull-Down Network를 인식하여 Channel Connected Block(CCB)를 구성. 이를 토대로 회로의 Topology를 구성.
3. 인식된 Level Shifter에 대해 SPICE Simulation Input Deck을 생성: Level Shifter 인식이 완료되면, 인식된 Level Shifter들을 대상으로 사용자가 지정한 Slope (Default Slope: 400ps) 값을 각 Level Shifter 입력에 인가하는 SPICE Slew Simulation input deck을 생성.
4. 생성된 Input Deck을 사용하여 Level Shifter에 대한 SPICE Simulation을 수행: 생성된 SPICE Simulation Input Deck을 사용하여 Level Shifter에 대한 Simulation을 수행. Simulation을 통해 Level Shifter 출력에 대한 성능과 동작 안정성을 평가.
5. Simulation 결과를 분석하여 Level Shifter의 성능을 평가하고 결과를 출력: Simulation 결과를 기반으로 Level Shifter 출력에 대한 Measure Logic을 사용하여 성능을 분석하고 결과를 출력. 이때, Measure Logic은 Level Shifter 입력에 사용자가 지정한 High->Low Transition을 인가하여, 출력으로 나오는 High->Low Transition의 Duty를 측정합니다. 이 Duty는 전체 Transition 구간 대비 Max Vth값의 구간의 비율로, 해당 비율이 낮을수록 Level Shifter가 정상적으로 동작하지 않을 확률이 높아집니다. 이를 통해 설계자들은 올바르게 동작하는 Level Shifter를 확인하고, 문제가 있는 Level Shifter에 대한 정밀 검사를 수행. 결과 분석을 통해 올바르게 동작하지 않는 Level Shifter를 수정하거나 교체함으로써 설계의 안정성을 높일 수 있습니다.

### 2.3) 결과
1. Rise/Fall: Measure Net의 최악의 Rise/Fall Slope 값 (ns) 
2. Rs/Fs: Rise/Fall 비율 
3. Duty: Level Shifter의 duty 값 
4. Data Net: 데이터 네트 이름 
5. Measure Net: 측정 네트 이름 
6. Driver NMOS: 대표 NMOS 드라이버 이름 
7. Master: Measure Net의 주 이름


## 3) Cana-TR

* 기능: Crosstalk noise의 영향을 분석
* 과정: Aggressor Slew 계산 → Multi/Single Aggressor Simulation → Victim 검사
* 추가 설명:
  * Slew Simulation: Agressor Candidate의 Slew를 DSC로 계산 (Driver가 없다면 Default 값: 500ps)
  * Multi-Aggre. Simulation: 모든 Aggressor 들의 Slew를 동시에 인가하여 Victim을 검사(Worst Case)
  * Simgle-Aggr. Simulation: Aggressor를 1개씩 Toggle시키면서 Victim을 검사 (Best Case)
  * crosstalk noise의 영향을 분석하는 과정 (CrossTalk = delay&noise)
  * Layout -> RCXT -> Coupling Analysis -> (if Problem, repeat) -> MTO
  * Layout 수정은 metal line의 spacing 혹은 routing 변경, guard ring 삽입.
### 3.1) 소개
Crosstalk Effect: Crosstalk 가 회로에 미치는 영향은 크게 나누면 crosstalk delay 와 crosstalk noise 가 있다. 이 중 Cana-TR 에서는 crosstalk noise 의 영향만을 분석한다. 

### 3.2) 과정
Aggressor Slew 계산 → Multi/Single Aggressor Simulation → Victim 검사

### 3.3) 상세 설명:
* 개요:  Cana-Tr은 반도체 설계 과정에서 신호 무결성을 확보하기 위한 중요한 정적 커플링 노이즈 검사 도구입니다. 반도체 마이크로 프로세스에서 분리된 라인 간에 발생할 수 있는 커플링 캐패시터로 인한 문제를 해결하기 위해 사용됩니다.
* 목적: 
	* 신호의 비정상적인 동작 방지
	- 칩에 미치는 부정적 영향 최소화
	- 커스텀 설계의 신호 무결성 달성
- 사용 시점:
	- LVS (Layout vs. Schematic) 단계 완료 후
	- 풀칩 레벨의 설계 넷리스트에 대해 실행
* 입력 데이터:
	* SPICE 넷리스트
	- SPICE 모델 파라미터
	- SPICE 시뮬레이션 코너 및 전원 조건
- 작동 원리: SPICE 시뮬레이션을 통해 각 라인의 커플링 캐패시터에 대한 노이즈 경향을 분석하고 보고
- 출력 데이터:
	- CSV 형식의 노이즈 분석 리포트
	- 도구 능력 범위 밖의 스킵된 넷리스트
	- 로그 파일
- 결과 분석 및 활용:
	- 노이즈 분석 리포트 검토
		- 각 라인의 커플링 노이즈 수준 확인
		- 허용 가능한 노이즈 수준을 초과하는 라인 식별
	* 스킵된 넷리스트 확인
		* 도구의 기준에 의해 검출되지 않은 넷 확인
		- 필요시 해당 넷에 대해 추가적인 SPICE 노이즈 시뮬레이션 수행
	- 오류 결과 식별 및 분석
		- 제로 노이즈 값 (시뮬레이션 오류로 인한) 확인
		- 비정상적으로 큰 노이즈 값 (거짓 양성 오류) 확인
		- 커플링 캐패시턴스 값, 커플링 대 기생 캐패시턴스 비율, 드라이버 트랜지스터 등 관련 값 분석
	- 추가 검증
		- 도구가 제공하는 SPICE 시뮬레이션 입력 데크를 사용하여 의심되는 부분 재시뮬레이션
		- 필요시 SPICE 데크 수정 후 잠재적 오류 지점 재시뮬레이션
		- 결과를 통한 교차 검증 수행
- 주의사항
	- 잘못된 입력 자극으로 인한 부정확한 SPICE 결과 가능성
	- 토폴로지 인식 실패로 인한 일부 넷 분석 누락 가능성
	- 부정확하거나 누락된 결과는 잠재적인 신호 무결성 문제를 야기할 수 있으며, 이는 설계의 오작동으로 이어질 수 있음
*  결과 활용
	* 문제가 있는 라인 식별 및 수정
	- 레이아웃 개선 (예: 메탈 라인 간격 조정, 라우팅 변경, 가드 링 삽입 등)
	- 전체적인 설계 최적화 및 신호 무결성 향상
- 장점
	- 풀칩 레벨에서의 포괄적인 커플링 노이즈 분석 가능
	- 자동화된 프로세스로 대규모 설계의 효율적인 검증
	- 잠재적인 신호 무결성 문제를 조기에 발견하여 설계 품질 향상


### 3.4) 요약
read input file: SPF, spice model를 입력
Extract Victim & Aggressor: Input 파일들을 parsing 하여 victim과 aggressor를 추출
Slew Simulation
Spice Deck Generation
Vector Generation: Aggressor 의 rise slew 를 얻기 위해서 아래와 같은 simulation deck을 생성 ; (PMOS gate : falling, NMOS gate : falling, Pass transistor : turn on)
Hspice run: Simulation 수행
Read hspice measure result: 20%~80% 지점을 측정하여 rising/falling slew를 구한다. 모든 node의 aggressor slew 값을 추출
Multiple Aggressor Noise Simulation
Spice deck generation: Slew Simulation에서 얻은 aggressor slew 를 voltage source로 모델링하여 coupling noise를 분석할 SPICE deck을 생성
Vector Generation ; (Low 에서 High로 toggle하는 noise 크기를 검사하기 위해 아래의 deck을 생성, PMOS gate : falling, NMOS gate : falling, Pass transistor : turn on)
Hspice run: Simulation 수행
Read hspice measure result: Receiver node에 생기는 noise 중 가장 큰 noise pulse를 victim의 noise로 저장한다. (DSPF의 경우 victim net의 sub node가 2개 이상임.)
Single Aggressor Noise Simulation
Spice Deck Generation: Slew Simulation에서 얻은 aggressor slew 를 voltage source로 모델링하여 coupling noise를 분석할 SPICE deck을 생성
Vector Generation: (Low 에서 high로 toggle하는 noise 크기를 검사하기 위해 아래의 deck을 생성, PMOS gate : falling, NMOS gate : falling, Pass transistor : turn on)
Hspice run: Simulation 수행
Read hspice measure result: Receiver node에 생기는 noise 중 가장 큰 noise pulse 를 victim 의 noise 로 저장한다 (DSPF 의 경우 victim net 의 sub node 가 2 개 이상임

* 추가 설명: 
	* Slew Simulation: Agressor Candidate의 Slew를 DSC로 계산 (Driver가 없다면 Default 값: 500ps)
	* Multi-Aggre. Simulation: 모든 Aggressor 들의 Slew를 동시에 인가하여 Victim을 검사(Worst Case)
	* Simgle-Aggr. Simulation: Aggressor를 1개씩 Toggle시키면서 Victim을 검사 (Best Case)
	* crosstalk noise의 영향을 분석하는 과정 (CrossTalk = delay&noise)
	* Layout -> RCXT -> Coupling Analysis -> (if Problem, repeat) -> MTO
	* Layout 수정은 metal line의 spacing 혹은 routing 변경, guard ring 삽입.

### 3.5) 결과

Multiple Aggressor Noise Simulation 결과
1. Victim: 피해 네트 이름 
2. noise: 최대 노이즈 값 (vl-vth_n, vh-vth_p 중 최대) 
3. volt: Victim's 스윙 범위 
4. vl/vh: Victim이 낮은/높은 상태일 때의 노이즈 
5. vth_n/vth_p: NMOS/PMOS 임계 전압 
6. coupling_cap: Victim의 총 커플링 용량 
7. total_cap: Victim의 총 용량
Single Aggressor Noise Simulation 결과
1. Noise: 최대 노이즈 값 (VL-Vth_n, VH-Vth_p 중 최대) 
2. Rise/Fall: 상승/하강 시간 
3. VL/VH: Victim이 낮은/높은 상태일 때의 노이즈 
4. Vth_n/Vth_p: NMOS/PMOS 임계 전압 
5. Coupling_Cap: Victim의 총 커플링 용량 
6. Total_Cap: Victim의 총 용량 
7. Victim_Net/Aggressor_Net: 피해/공격 네트 이름





## 4) Latch Strength Check(LSC)

- 기능: Latch를 Load로 갖는 Driver의 Output Slew 검사
- 목적: Latch의 Feed-back Loop와 Driver 간의 전압 경쟁 상황 검증
* 추가 설명:
	* Latch를 Load로 갖는 Driver에 일정한 Slew를 갖는 Input을 가했을때 Output Slew를 검사
	* Latch에서 상태 저장 기능을 위해 Driver와 Feed-back Loop사이에서 전압 경쟁이 발생시, Feed-back Loop보다 강한 전압을 인가해야 회로가 정상적으로 동작. 이를 위해 Latch의 Feed-back Loop에서 Driver와 경쟁하는 부분에 Inverter를 Weak Inverter로 구성
	* LSC는 Weak Inverter가 제대로 설계되었는지 확인(driver와 weak inverter 간의 'Fighting'을 발생, Latch의 출력이 정상적으로 나오는지 검증


### 4.1) 필요성
Latch 회로는 메모리 설계 전반에 사용되는 중요한 회로. Latch는 Feed-back Loop 구조의 2개의 Inverter Logic과 Clock/Clockb, Reset/Reset 등의 Control Logic으로 구성되어 있는 회로로 Feed-back Loop에 의해서 State를 저장하는 기능. Latch에 신규 Data가 들어오면 Feed-back Loop에서 저장된 회로의 값이 갱신되고 신규 State를 저장하게 되는데, 이때 Driver를 통해서 들어오는 Data와, Feed-back Loop에 의해 유지되는 Data간의 Fighting 현상이 발생. 이 현상에서 Driver가 Feed-back Loop보다 더 강한 전압을 인가해야 경쟁에서 이길 수 있고, 정상적인 회로 동작이 가능. 이를 위해 Latch Feed-back Loop에선, Driver와 경쟁하는 부분의 Inverter를 Weak Inverter로 구성하게 되는데, Latch Strength Check는 이러한 Weak Inverter가 제대로 설계 되었는지를 확인하기 위해, Driver와 Weak Inverter간의 Fighting을 발생시켜 Latch의 Output이 정상적으로 나오는지를 검증.

### 4.2) 원리
SPC 혹은 STAR파일의 Netlist과 MP, EDR, Power 정보(VDD/GND)를 토대로 모든 Latch의 Topology를 인식. Power 정보를 올바르게 입력하지 않으면 제대로 된 Latch 추출이 불가능(본 Tool은 기본적으로 Power Network인 Pull-Up Network와 Ground Network인 Pull-Down Network를 인식하여 Channel Connected Block(CCB)를 구성하고, 이를 토대로 회로를 Topology를 구성).
모든 Latch 에 대한 인식이 완료됐다면, 인식된 Latch들을 대상으로 정해진 Slope(Default Slope, 400p) 값을 각 Latch 입력에 인가하는 SPICE Slew Simulation Input Deck을 생성. 이때 Latch에 입력이 여러 개가 존재 할 경우, 입력 수만큼 별도의 Simulation Input Deck을 추가 생성.
마지막으로 SPICE Simulation을 진행 후 모든 Simulation이 완료되면 Latch 출력에 대한 Measure logic에 따라 결과를 출력.


### 4.3) 검증 항목 설명

1 : Normal Slew Sim

Latch Strength Check의 가장 기본이 되는 검증 항목으로, Latch Data를 찾아 해당 Net의 Driver에 입력을 인가하고 그에 따른 Latch Output의 Delay와 Slew를 측정하는 항목. 이때 Latch의 Clock / Clockb는 DC로 열어놓고, Set / Reset은 DC로 닫아놓고 Simulation을 진행. 측정된 Delay 및 Slew(Slope)값이 클수록 Weak Inverter를 뒤집는 힘이 약한 경우일 확률이 높은 Latch로 설계자의 추가 검증이 필요한 포인트 일 것이다.

2 : Set / Reset Slew Sim

Latch의 Set / Reset으로 값이 정상적으로 초기화 되는지를 검증하는 항목. Latch Set / Reset에 입력을 인가하고 그에 따른 Latch Output의 Delay와 Slew를 측정. 이때 Clock과 Clockb는 DC로 닫아놓고, Weak Inverter 출력 Net(Latch Net, Set일 경우 0, Reset일 경우 1)과 Latch Output(Set일 경우 1, Reset일 경우 0)을 초기화하여 Simulation을 수행하며, 위 검증 항목에 과 마찬가지로 Delay 및 Slew(Slope)값을 통해 정상 동작이 가능한지 파악.

3. Latch 주변 회로 모델링

Latch 를 인식하고 , 해당 Latch 를 추출 할 때 주위 회로에 대한 영향을 고려할 필요가 있다 실제 동작에는 관여를 하지 않더라도 연결된 MOS 들의 Cap에 따라서 Delay 와 Slew 의 값에 영향을 주기 때문이다. LSC 에서는 이러한 점을 고려하여 Latch 의 Data, Latch Net, Output 등에 추가로 연결된 회로를 대상으로 Gate Cap 을 달아 추가 Loading 처리를 진행하고 Simulation 을 수행. 

4. Latch Driver S timulus 인가 방식

Latch Driver의 Stimulus 인가 방식을 기존 버전에선 Driver의 Input Line Delay를 고려하여 Line이 긴 경우에 한해서 Delay결과가 과도하게 높게 나오는 경우가 존재하였는데, 이러한 문제를 인식하여 Input Line Delay 유발 요소인 Line Loading을 제거하여 이전보다 더욱 Driver / Latch의 Strength Check에 집중하도록 개선.


### 4.4) 결과
1. Rise_Delay: Rise Slew의 50% 구간에서 최대 지연 값 
2. Fall_Delay: Fall Slew의 50% 구간에서 최대 지연 값 
3. Rise/Fall: Measure Net의 최악의 Rise/Fall Slope 값 (ns) 
4. Data Net: 데이터 네트 이름 
5. Measure Net: 측정 네트 이름 
6. Driver MOS: 대표 NMOS 드라이버 이름 
7. Master: Measure Net의 주 이름

## 5) Coupling Delay Analyze (CDA)

- 기능: Aggressor의 Slew에 따른 Victim의 Slew 변화량 검사
* 추가 설명:
	* Slew Simulation: Agressor Candidate의 Slew를 DSC로 계산 (Driver가 없다면 Default 값: 500ps)
	* Coupling Delay Simulaion: 각 Aggressor들의 Slew에 대해 Victim의 Slew 변화량을 검사.

### 5.1) DRAM 의 Coupling Delay 분석
*  Coupling Delay Signoff: 
DRAM 설계 방법론은 Dynamic Simulation을 기반으로 한 Timing/Power Signoff를 수행하는데, Fast Spice Tool에 기반한 방법론은 Simulation Time의 부담으로 인한 Coverage 문제를 갖고 있기 때문에, 전통적으로 In-house Tool을 활용한 Static Signoff 를 통해 Coverage를 보완. Signoff Item 중 Coupling의 경우 Net의 Parasitic Capacitance에 의한 Noise 때문에 Function Fail이 발생하는 Coupling Noise Error를 주로 검사하는데 (Cana-TR), 이는 Victim Net의 Toggle 여부와는 관계 없이, Victim Net의 State를 반대로 뒤집을 수 있기 때문에 반드시 확인해야 하는 Signoff Item이고, Noise 값 자체가 Vth를 넘어가는지를 확인하기 때문에 분명한 기준이 있는 Signoff Item이다. (Multiple Aggressor의 경우 Function을 고려하여 동시 Aggressing을 판단해야 하는 문제가 있다.)
반면, Coupling Delay Signoff의 경우 상기 기술한 Noise Signoff에 비해 발생 가능성이 낮으나, 공정이 미세화 되면서 Victim의 Toggle 시점에 Coupling이 발생하고, 이로 인해 Toggle의 특성 (Slope) 이 변하여 Timing Error 및 불량 사례가 다발하고 있어 Signoff 개발의 필요성이 생겼다. 물론 기존에도 Dynamic Cana-TR 에서는 FineSim Nano Simulation에서 검출된 Victim / Aggressor 동시 Toggle의 Case가 Variation 때문에 만들 수 있는 최대한의 Coupling Delay Delta (Coupling 최대로 생겼을 경우 - Coupling 없을 경우의 Delay 차이) 를 구하는 Simulation을 수행했지만, Simulation Coverage의 문제로 다발하는 불량 사례를 사전에 검출하지 못했고, 이를 극복하기 위해 Static한 방법론을 활용하여 Coupling Delay를 검사하기에는 기준의 불분명함 (Noise는 Vth만 보면 되지만, Delay는 해당 Point가 영향을 끼칠 Path를 검사하여 Timing Margin을 Corner별로 살펴보아야 함) 으로 인해 도입이 어려웠다.
DDR5 제품의 불량 사례를 기점으로 높은 Coverage 를 가지면서 불량을 검출할 수 있는, Coupling Delay Signoff를 개발하기 위한 T/F를 조직하여 설계-DT팀의 공동 개발이 진행되었다. 그 결과로 본문에서 설명하는 Coupling Delay Analyzer (CDA) 를 개발했고, 이는 Static한 방법론을 기반으로 하여 다량의 데이터를 확보한 다음, FineSim Nano가 아닌 Verilog Simulation에서 동시 Toggle의 Case를 Margin을 갖고 검출하여 Filtering하는 방식으로 Coverage와 Garbage Reduction, 두 가지 측면에서의 이점을 확보했다. 여기에 추가로 Net Name에 기반한 Group Rule을 도입하여 유사한 Net 이름들이 Chain으로 연결되었을 때, 그 Path의 Coupling 영향도를 확인할 수 있는 방법론을 갖추었다. 물론 이 방법은 Net Name이 Naming Convention에 맞게 설계되었음을 가정하기에 약점이 존재하지만, 현 시점에서는 유일한 방법으로 판단하여 도입했고, 추후 Path Tracing 기법에 기반한 Static Timing Analysis (STA) Tool을 평가하여 도입할 예정이다.


### 5.2) CDA는 Static CDA, Overlap Check, Grouping 세 단계로 수행

##### 5.2.1) Static CDA
CDA에서의 Coupling Simulation은 우선 Aggressor Net의 Slope을 파악하기 위한 Slew Simulation을 진행. A의 점선으로 표기된 그림으로 Driver Size Check (DSC)에서 수행하는 Simulation과 동일. 입력 Slope을 기준으로 출력 Slope을 구한다. 
이 값이 Aggressor의 Slope이 된다. 구한 Aggressor Slope을 PWL로 정의하여 Victim / Aggressor 사이의 Coupling Simulation을 수행한다. 
Coupling Delay의 Delta를 구해야 하기 때문에 Coupling Aggressor의 Toggle이 없는 경우와 존재하는 경우를 2번에 걸쳐 분석하며, Aggressor의 Toggle은 Victim의 Slope에 맞춰 Coupling이 가장 심한 시기를 맞추어 Toggle하게 한다. 
(신호가 Transition하기 시작하는 초반 2~30% 시점) 두 Simulation 결과를 통해 Delay를 확인

##### 5.2.2). Overlap Checker
Static CDA 결과는 회로에서 모든 Victim - Aggressor Pair를 추출하기 때문에 필터링이 필요하다. Coupling Delay는 두 신호가 동시에 Toggle하는 현상을 나타내지만, 실제 회로에서는 이런 상황이 드물다. 이를 모두 Capture하려면 Static Timing Analysis(STA)가 필요하지만, 이 도구는 DRAM 횡전개에 제한이 있다. 이를 보완하기 위해, Verilog Simulation Dump를 분석하여 동시 Toggle Case를 추출하는 방법론을 개발하였다. 또한, User Margin을 부여하여 Timing 정보가 없는 문제를 해결하였다. 이를 위해선 특정 Vector Set이 필요하다.

##### 5.2.2.1) 필요 Vector Set
기존 실패 사례와 설계 실무자들이 제공한 Keyword를 기반으로 Verilog Vector들을 추가하여 Verilog Basic Vector Set을 구성하였다. 이때, Power On, Off에 따른 Coverage와 REZ Vector 일부의 Keyword Coverage를 고려했다. 이를 바탕으로 "Basic Vector + Warm Booting Vector + Write Leveling"의 총 216개의 Vector를 표준 Vector Set_216으로 지정했다. 이 Set은 DDR5 Vector set을 기반으로 작성되었으므로 DDR5 표준 Vector set으로도 사용할 수 있다.

##### 5.2.2.2) Overlap Checker 판별 방식
Victim 기준 앞, 뒤로 Aggressor의 Toggle 여부를 측정, Rising/Falling으로 발생할 수 있는 모든 조합에 대해서 검사하여 Overlap여부를 측정

##### 5.2.2.3) Overlap Checker 수행 방법
Verilog trn 파일에 대해 Overlap Check를 수행하여 Victim Net과 Aggressor Net이 겹치는지 검사한다. 최소 겹치는 영역을 찾아내어, 겹치는 정도와 시간, 발생한 trn을 결과에 기록한다. 단, SPICE Netlist와 Verilog Netlist의 대소문자 구분, 요소 차이로 인해 Miss Match가 발생할 수 있으므로, Overlap Checker를 사용할 때 중요한 Net의 Miss Match 여부를 확인해야 한다.

##### 5.3) Grouping
Overlap Check를 통해 동시에 Toggle하지 않는 Victim - Aggressor Case를 걸러내지만, 결과 수가 많아 Grouping 방식을 제안했다. 이는 Repeater의 Naming Convention에 따라 Grouping을 하고, Coupling Delay는 Buffer Chain의 종단점에 존재하는 Margin Point에 대해 합산한다는 개념에서 착안한 것이다. 이 방법은 STA를 활용하지 않는 현재 상황에서 최선의 방법이다. 합산 Delay가 작다면 대세에 영향을 주지 않는다고 해석하여 필터링하고, 그룹에 따라 분석한다.

##### 5.3.3.1) Grouping 원리
CDA는 Victim Net의 Coupling으로 인한 Delay값을 측정하고, 다수의 Gate를 통과하는 대상을 Grouping해 Delay 값을 합산, Coupling으로 인한 누적 Delay를 도출한다. Grouping Rule에 따라 Rule Pattern이 포함된 모든 Net들을 추출하고, 같은 Rule Pattern을 가지는 Victim과 Aggressor Net의 Delay를 합산, "Sum_Delay" 컬럼에 기록한다. 이를 통해 다수의 Gate를 통과하는 동작의 Coupling에 대한 Delay 영향을 분석한다. "Victim_Net Grouping"과 "Aggressor_Net Grouping" 컬럼에서 각각의 Net에 적용된 Grouping Rule을 확인할 수 있다.

##### 5.3.3.2) Golden Group Rule
기존 Grouping Rule을 DDR5에 적용한 결과, CDA 결과를 충분히 반영하지 못하고 많은 Garbage가 확인되어, Z를 제외한 모든 Grouping Rule을 제거하여 분석했다. 결과적으로 BUS, DQ, GBank Group)가 Major한 Net Grouping이 필요하며, 각 Grouping 간에 종속 관계가 필요하다는 것을 발견했다. 따라서 DDR5에 최종 적용된 Grouping Rule이 수정되었다.

Victim Net인 x_mid.bus_g0_a ~ x_mid.bus_g5_a를 예로 들면, 해당 패턴을 인식하고 busb와 x_mid.bus)_g(숫자)()(_g0 ~ _)가 있어 1순위 Grouping Rule로 판단한다. 이에 따라 x_mid.bus_g0_a ~ x_mid.bus_g5_a는 bus_g*_a로 묶여 각 Victim Net의 Delay 값을 합산해 결과를 보여준다. 2순위부터는 Instance Hierarchy를 고려하여 Grouping한다. 만약 1순위와 2순위가 동시에 존재한다면, 우선순위에 따라 1순위만 결과에 기록하여 중복 결과를 방지한다.

### 5.3) 결과:
1. Victim_Net: Victim Net 이름 
2. Victim_Net Grouping: 그룹화 된 Victim Net의 대표 이름 
3. Aggressor_Net: Aggressor Net 이름 
4. Aggressor_Net Grouping: 그룹화 된 Aggressor Net의 대표 이름 
5. Driver_NMOS: Victim Net을 구동하는 NMOS 장치 이름 
6. Total_Cap: Victim Net의 전체 패러사이트 용량 
7. CC/CT: 총 용량 대비 커플링 용량 비율 
8. Coupling_Cap: Victim과 Aggressor Net 사이의 패러사이트 커플링 용량 합 
9. Victim/Aggressor Fall/Rise: Victim의 커플링 딜레이 델타 값에 따른 Victim과 Aggressor의 동작 
10. Sum_Delay: 같은 Victim/Aggressor 그룹 내 모든 딜레이의 합계의 최대값 
11. Victim/Aggressor Fall/Rise Ratio: Victim의 커플링 딜레이 델타 값에 대한 Victim 딜레이 값의 비율



## 6) PEC (Power Error Check)

기능: Netlist Topology, Voltage Level, Model Parameter 등을 이용한 Circuit Integrity 검사
- 목적: Multiple Power Design에서의 설계 오류 자동 탐지
- 추가 설명
	* Pre/Post Layout Netlist Topology와 Voltage Level, Model Parameter 등의 정보를 이용하여 Circuit Integrity를 빠르게 검사 (ex: Multi-Power Domain)
	* Multiple Power Design에서 발생 가능한 설계 오류를 자동으로 탐지회로 설계의 정확성을 보장하는데 활용
	* Netlist, Voltage Level, MP 등의 정보를 사용하여 회로의 무결성을 검증하는 circuit check을 수행
	  ex) Multiple Power, Multiple Power On Single Transistor, Wrong Bulk Connection, ...



# Signoff Inhouse Tool #2 : ADV

   : Static 및 Dynamic Signoff Application을 지원하며, 다양한 Waveform 포맷(FSDB, TRN/VWDB)을 통합 관리합니다.
   : ADV도 SPACE Tool처럼 입력된 회로 data를 바탕으로 인식된 회로에 대해 다음과 같은 application들을 수행해.

### 2.2.1. Static Applications:

* Power Gating Check: Power Gating 적용에 필요한 회로 구성 요건 만족 여부 검사
	: Power Gating  적용에 필요한 회로 구성 요건을 만족했는지를 검사.
### 2.2.2. Dynamic Applications:
  - ADV Checker: 설계 spec/criteria 기반 simulation 결과 분석
  - ADV Compare: 서로 다른 simulation 결과 비교 분석
  - ADV Xtracer: 특정 신호의 추적 및 분석
  - Latch Setup-Hold: Latch의 Setup 및 Hold 시간 검증
  - Waveform API: Python 기반 API를 통한 waveform 조작 및 분석
  - Margin Analysis: 회로의 동작 마진 분석
  - Current Analyzer: 전류 소모 분석



# Signoff Inhouse Tool Flow

## Step 1) Read_Spice_netlist
* Circuit Parsing: SPC 혹은 STAR파일의 Netlist과 MP, EDR, Power 정보(VDD/GND)를 토대로 모든 Latch의 Topology를 인식한다.
- SPC 또는 STAR 파일의 Netlist, MP, EDR, Power 정보 파싱
- 모든 Latch의 Topology 인식
Parsing: SPC 혹은 STAR파일의 Netlist과 MP, EDR, Power 정보(VDD/GND)를 토대로 모든 Latch의 Topology를 인식한다.

## Step 2) Build_Design
* Circuit Partition: 입력 받은 Tr. Level Netlist 파일을 분석 하여 Channel Connected Component(CCC) 알고리즘으로 Stage(similar to a 'gate')를 추출
* Power Network인 Pull-Up Network와 Ground Network인 Pull-Down Network를 인식하여 Channel Connected Block(CCB)를 구성하고 이를 토대로 회로 Topology를 구성
*  Channel Connected Component(CCC) 알고리즘으로 Stage 추출
- Pull-Up/Pull-Down Network 인식 및 Channel Connected Block(CCB) 구성
- 회로 Topology 구성
Partition: 입력 받은 Tr. Level Netlist 파일을 분석 하여 Channel Connected Component(CCC) 알고리즘으로 Stage(similar to a 'gate')를 추출  
Power Network인 Pull-Up Network와 Ground Network인 Pull-Down Network를 인식하여 Channel Connected Block(CCB)를 구성하고 이를 토대로 회로 Topology를 구성
## Step 3) Signoff Simulation

* Partition된 회로를 Finesim Simulation
- Static/Dynamic 검증 수행

ex) DSC(driver size check)
(: 회로(fullchip)에서 인식된 모든 driver에 대해 일정한 slew time의 input stibulus를 가했을때 얻어지는 outputslew 측정.)
: 일정한 slew time의 input 신호를 driver에 가하고 그에 대한 output 신호의 slew time을 측정하여 input 대비 output slew 비율을 계산.
: 이 비율은 실제 slew time과는 무관하며, driver의 크기가 적절한지, 취약한지 또는 과다한지 등을 판단하는 데 도움을 줌.
: 이를 통해 회로 설계자는 driver 크기를 조정하거나 최적화하여 회로의 성능을 향상시키는데 도움을 얻을 수 있습니다.

ex) LSC (Latch Strength Check)
(: 회로(fullchip)에서 인식된 모든 Latch회로에 대해 정해진 Slope값을 입력에 인가하는 SPICE Slew Simulation Input Deck 생성, 이때 Latch에 입력이 여러 개가 존재 할 경우, 입력 수만큼 별도의 Simulation Input Deck을 추가 생성한다.)
: Latch에서 상태 저장 기능을 위해 Driver와 Feed-back Loop사이에서 전압 경쟁이 발생시, Feed-back Loop보다 강한 전압을 인가해야 회로가 정상적으로 동작. 이를 위해 Latch의 Feed-back Loop에서 Driver와 경쟁하는 부분에 Inverter를 Weak Inverter로 구성
: LSC는 Weak Inverter가 제대로 설계되었는지 확인(driver와 weak inverter 간의 'Fighting'을 발생, Latch의 출력이 정상적으로 나오는지 검증

