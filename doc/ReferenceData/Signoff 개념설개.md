# DRAM Signoff 개념설계

## Tool간 관계성

* PNRATIO VS FANOUT :	PN RATIO 는 단일 Cell 내의 P/N 비율 (W 기준)을 보고, FANOUT은 Driver - Receiver 간의 Rise/Fall Driving Strength의 비율 (W 기준)을 본다.
* FANOUT VS Driver&Keeper :	FANOUT은 Driver - Receiver 간의 Rise/Fall Driving Strength의 비율 (W 기준)을 보고 너무 낮거나/높은 Driving Strength를 거르고, Driver&Keeper는 Latch의 Driver와 Keeper (값을 저장하는 목적의 Holder) 사이의 저항비 (Ion@Bias)를 보고 낮은 저항비를 갖는 Latch를 거른다.
* FANOUT VS DSC : FANOUT은 Driver - Receiver 간의 Rise/Fall Driving Strength의 비율 (W 기준)을 Std. Cell을 기준으로 보고, DSC는 Driver - Receiver 간의 Rise/Fall Slew를 Simulation으로 보지만 너무 큰 Load (Fanout 개수 기준 1000개 이상) 의 경우 Warning 띄우고 Skip한다.
* Driver&Keeper	VS LSC :	Driver & Keeper는 Latch의 Driver와 Keeper (값을 저장하는 목적의 Holder) 사이의 저항비 (Ion@Bias)를 보고, LSC는 Driver가 값을 변화시키는 Simulation을 수행하여 Slew/Delay를 분석한다.
* Static Cana Tr VS Dynamic Cana Tr : Static Cana는 All Aggressor/Victim 관계를 Single (기준 이상 Aggr.을 하나씩 Toggle시켜보고 Bump 출력), Multiple (모든 Aggr.를 동시에 Toggle시켜보고 Bump 출력)로 Noise Simulation 분석하고, Dynamic Cana는 Static Cana의 Aggr/Victim 후보 중 입력 TRN/FSDB (PrimeSim Nano 혹은 VTS 결과)에 관계가 확인된 것들 중 가장 나쁜 Case만 Multiple로 Noise/Delay로 분석한다.
* Static Cana Tr VS Coupling Delay Analyzer(CDA) : CDA는 All Aggressor/Victim 관계를 Single (기준 이상 Aggr.을 하나씩 Toggle시켜보고 Bump 출력)로 Delay Simulation 분석하고, Verilog TRN에 관계가 확인된 Aggr./Victim만을 진성 표기하여 출력한다.


## Prerequisite

### 1. Voltage 정의: 
- 배경: power 로 선언해야할 모든 net 을 탐색하는 tool 이다. 여러 hiearchy 에 걸쳐 존재하는 net 인 경우에는 top net 에 global 선언해야만 한다.  virtual power 가 많아 유실된 power 가 존재할 수 있어 탐색 기능이 필요했다. Signoff Tool의 입력에 Power 정의가 빠진 경우 아래의 Log로 출력된다. 하지만 PVCCH 등 Large Fanout을 갖는 신호가 많아지면서 해당 Net이 유실된 Power인지, 단순히 Large Fanout Net을 갖는 Driver Net인지 구분이 어려워 Tool을 만들었다.
- 입력: Ckt파일, power.in

- Q&A: global list 과 power/ground list 가 다른가요? (global 과 power 과 같은 의미 아닌가요?
global 은 netlist 내 모든 동일한 이름을 가진 net 들을 hierarchy 와 무관하게 하나의 net 으로 간주하겠다는 의미입니다. (spice 입장에서 .global 과 동일)
power/ground 는 그 net 이 power/ground net 임을 의미합니다. (spice 입장에서 vvpwr vwpr 0 1.0)
흔히 말하는 global power net 은 global 선언 + power 선언 된 net 입니다.
 
### 2. BA DB를 BlkStar로 변환: 
- 배경: DRAM 설계 방법론 중 가장 큰 비중을 차지하는 SPICE Simulation 방법론에 Back Annotation (BA) 방법론이 들어오면서 (2024) Signoff Tool도 Back Annotation을 준비해야 할 필요성이 생겼다. 하지만 Cell Skip이나, ECO (Engineering Change Order) 등의 Needs가 분명한 SPICE Simulation 대비 정규 Netlist로 진행하는 Signoff는 기능 개발의 필요성이 다소 낮고 In-house로 개발된 모든 Tool에 BA 기능을 각각 개발하기 어려운 현실적인 문제로 Synopsys PrimeSim Tool의 Netlist Dump 기능을 활용한 Workaround를 Setup하여 진행하게 되었다. 이를 사용하면 BA 이전 BlkStar (Flattend Nelist 기반) DB를 PrimeSim으로 생성할 수 있어 Signoff에 입력으로 사용 가능하다.

## Pre-Layout Signoff

### 3. PNRATIO:

기존 Signoff Tool들은 회로를 인식한 다음 단위 회로로 쪼개어 SPICE Simulation을 수행하고, 그 결과를 취합하여 출력하는 방식이었다. (ex. Driver Strength Check, Cana.-Tr) Layout에 대한 실제 특성을 분석하는 것을 중요시하며, Layout이 만들어지지 않은 시점에서는 Earth 등의 모델링 된 Netlist를 사용하여 실제 Layout과 근사한 특성 값을 얻을 수 있었으나, Time to Market이 중요한 DRAM Business 특성 상 Design Time 단축이 요구되고, Shift-left가 필수적인 최근의 Trend에 맞지 않다는 요구가 지속되고 있었다. 이에 대응하기 위해 Netlist 자체의 특성을 분석하여 Signoff하는 방법론을 개발하게 되었고, 회로에 사용된 Std. Cell의 P/N Ratio와 Fan Out 을 Width 기반으로 Check하는 Tool을 개발하여 배포하게 되었다. Std. Cell은 따로 관리되어 중복 Check으로 생각할 수 있지만, 실제 회로에 사용되는 모든 회로를 관리할 수 있다는 점에서 차별점이 발생하고, Fan Out Check의 경우 Std. Cell의 다양한 사용 Case를 관리할 수 있기 때문에 반드시 수행해야하는 Signoff로 제공하고 있다.

### 4. FANOUT: 
### 5. Power Error Check (PEC):
### 6. Driver & Keeper: 

DriverKeeper는 Latch와 Driver 간의 경쟁하는 부분에서의  저항비를 파악하여 Latch의 정상 동작여부를 검증하는 Tool입니다.
DriverKeeper(저항비) 값은 Driver의 Driving Strength와 유관합니다.

### 7. DCPATH: 
### 8. Floating Node Check:

## Post-Layout Signoff

### 9. Level Shifter Check (LSC)
### 10. Cana Tr.
### 11. Driver Size Check (DSC):
### 12. Latch Strength Check (LSC):
### 13. Coupling Delay Analyzer (CDA):


## Dynamic/Verilog Signoff

### 14. Analog Digital Verifier (ADV):

## PrimeSim Nano혹은 VTS 기반

### 15. Glitch Margin Check:
### 16. Dynamic DC Path:

---

# 1. Signoff Tool 개념
## Static Signoff (DSC/LSC/LS/...)
Simulation Deck (=Unit/BlkStar) 기반으로 회로 인식 -> Cell 단위 Simulation 수행.


# 2. Signoff Tool Line-Up & 수행 시점 & Condition
* 제품마다 다를 수 있음
```
Tool Name,Condition,Criteria,R00,R10,R20,R30,R40,R50,R60
Voltage Finder,,,●,●,●,●,●,●,●
Powet at Gate,,,●,●,●,●,●,●,●
PN Ratio,SSPLVCT,,●,●,●,●,●,●,●
FO Check,SSPLVCT,,●,●,●,●,●,●,●
Driver & Keeper,"SFLVCT, FSLVCT",,●,●,●,●,●,●,●
DC Path,TTTVCT (2P 조건),,●,●,●,●,●,●,●
Floating Node Check,TTTVCT (2P 조건),,●,●,●,●,●,●,●
PEC,Normal,All Violations,●,●,●,●,●,●,●
DSC,"SSPLVCT, SSPLVHT",,,,●,●,●,●,●
LSC,"SFLVCT, FSLVCT",Rs/Fs > 250ps?,,,●,●,●,●,●
LS,"SFLVCT, FSLVCT",,,,●,●,●,●,●
Cana.-TR (Static),FFPHVHT,All Violations,,,,,●,●,●
Cana.-TR (Dynamic),FFPHVHT,All Violations,,,,,●,●,●
CDA / STA,SSPLVCT,,,,,,●,●,●
Glitch Margin Analysis,FSDB,,,,,,●,●,●
Dynamic DC Path,TRN/FSDB,,,,,,●,●,●
ADV Margin Analyzer,FSDB,,●,●,●,●,●,●,●
ADV Latch Setup-Hold,FSDB,,,,,,●,●,●
열화 검증 자동화,FSDB,,,,,,,●,●
```