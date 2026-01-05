Coupling Delay Analyze (CDA)

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

