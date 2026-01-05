
* Signoff 파트는 DRAM, FLASH, HBM 메모리 회로 설계의 Tr-level Signoff 검증을 위한 Inhouse Tool을 개발 및 유지보수, 문의 대응 및 Signoff 방법론 개발을 담당하고 있다.
  
* 배경 설명: 
  전통적인 DRAM 제품의 설계 방식은, full-custom 기반의 설계 기법을 채용하여 chip size reduction 중심의 설계(Tr.-level design)과 고성능 I/O (high bandwidth signaling) 설계, cost-effective 중심의 공정 특수성(# of metal) 등을 반영한 설계를 하고, 이를 검증하기 위하여 제품 SPEC과 설계자의 경험에 의존한 dynamic verification과 in-house signoff 과정을 수행하고 있습니다. 하지만 제품의 고사양화와 설계 복잡도/난이도 증가로 인하여 메모리 제품 완성도 향상을 위해서 병렬연산을 통한 대규모 Simulation 및 AI/ML기반 Signoff 방법론 방법론 개발의 필요성이 있습니다. 
  이 새로운 방법론에서는 DRAM domain knowledge 기반의 Inhouse Tool을 개선시켜 Signoff을 통하여 제품 완성도를 향상시키는 것을 목표로 하고 있습니다.
 
* 현황/이슈: 
	* CSR 목적 최적 설계를 위한 TR-level Sign-off Productivity↓, 실수/오류/미검출↑
	* 설계 복잡도/난이도 증가와 사용되는 설계 tool의 종류/수 지속 증가로 design resource cost(설계용 tool license/HW비용, ~1,200억원@22년, 전년 비 63%↑) 급증, 설계 productivity 이슈(pending 증가 등 VOE) 증가, resource 수요 예측-실 사용 시점/수량 간 차이로 인한 resource 부족/낭비 발생 하며, 전체 설계 TAT 증가 risk가 대두됨. (e.g. 21년 7월 XF ver. Rev.시 Pending으로 회로 검증 평균 2일 지연)
	* 주요 원인들: Runtime↑, 진성 오류 검출력↓(Garbage↑), Sign-off Coverage↓, GUI↓, etc. 


# 메모리 Design Simulation&Signoff Project Leader 업무 계획

Full-Custom 설계 방식에서의 설계 방식과 장점인 제품 경쟁력(칩 면접, 전력 소모, 전송 속도) 유지를 전제로하되, 제품의 무결성 확보와 설계/검증 기간의 단축을 통한 개발과정 효율화를 위하여 메모리향 신규 설계/검증 협업을 DRAM/FLASH 설계팀과의 협업을 통해서 D1b D5/LP5, D1c D5, HBM4E 제품 및 V11/V12 제품에 적용하여 설계/검증 방법론의 유효성을 증명하고자 합니다. 이를 위해, 1) Tr.Gate-level STA , 2) Signoff &Criteria 방법론 고도화, 3) User-friendly Signoff Platform 개발,  4) Circuit Simulation(Primesim) 적용 방법론 고도화 이원화(Spextre_FX), 5) Hierarchical Netlist 기반 Circuit Simulatino Full Flow 개발, 6) Advanced Simulation Feature: Co-simulation, AVA, ASO.ai 등 활용 방법론을 개발하고 있습니다.

* Pre-layout Simulation 방법론 개발 현황으로는, Layout 이전 Schematic 설계 단계에서 Post-layout 수준의 Simulation 방법론을 확보하여 초기 설계 완성도 향상과 Simulation 부정확에 따른 layout Revision을 최소화 하는 것을 목적으로 하여, 설계 단계별 pre vs post-layout 부정합 원인을 분석하고 필요 기술 개발을 통해서 해당 방법론을 개발하고 있습니다. (1) Digital Circuit향으로 'Cg/Cd 모사 + Stdcell Symbol size 예측 & Unit-level Earch  + Advanced Earch(@Peri-level)'을 통해서 ~98% 수준의 정합성을 확보하였으며, (2) Analog Circuit 향으로 AC gain, Timing Delay 정합성 평가 및 Modeling 기법을 개발하고 있습니다. 특히 (3) Layout Implementation 이전 단계에서의 Pre-viewer 기능(Design Contraint 반영)와 Bottom-up 방식의 Hierarchical Operation 기능 개발로 사용자 편의성을 강화할 예정입니다.
	- Pre-layout Simulation방법론 상세 개발현황으로, (1) Digital Circuit(MCG)향은 1. STD Cell 구성 단계에서는 Tr-level에서의 Drain Junction Loading(Cd)과 Gate Header loading(Cg) 부분을 보상함으로써 Post-layout 대비 ~95% 수준의 정합성을 확보하였으며, 2. Unit Cell 구성 단계에서는 Multi-row level에서의 MET Routing 제외시 80~90% 수준의 정합성을 확인하여 Pre-layout 단계에서STD CELL위치에 의한 Manhattan distance 방식을 고려한 Unit-earth를 개발하여 ~98% 수준의 정합성을 확보하였습니다. 3. 이를 바탕으로 Peri-level에서 Unit의 Symbol Size와 Port 예측력을 높여, Peri-level의 정합성 향상을 기대하고 있습니다. 아울러, 4. Advanced Earth는 layout의 abstract view를 바탕으로 Symbol Size와 Port 예측력을 높여, Peri-level의 정합성 향상을 기대하고 있습니다. 아울러 Advanced Earth는 layout의 abstract view를 바탕으로 Symbol size&Port를 현실화 하는 기능과 직접 PnR Tool(Unity)의 Routing 기능까지 적용하여 Schematic 상에서 Routing Congestion과 Coupling Effect까지 반영이 가능함으로써 DSC(Driver Strenght Check) 기준 90.6% 수준의 정합성을 확보하였습니다 (기준 70% 수준, LP6 VP제품). 25년에는 HBM4E C-die, D1c 32Gb D5, D1c LP6, LPW 제품에 적용할 예정입니다. 향후 계획으로, 1. Digital Circuit 향 Previewer 기능(Design Constrait 반영)와 Bottom-up 방식의 Hierarchical Operation 기능 개발로 사용자 편의성을 강화, 2. Analog Circuit향 정합성 향상 Modeling기법 개선 및 Peri-level Earch를 위한 symbol & port size 예측력 강화 등 설계팀과 긴밀한 협업을 진행하도록 하겠습니다.


* Custom Design향 Signoff Platform 개발 현황으로는, Signoff Tool의 활용성/편의성/분석력(Coverag up/User-friendly GUI/Garbage down)향상을 목적으로 (1) Signoff Result Viewer 3.0(SORV)를 개선하여 12종 Signoff Application별(DSC, LS, LSC, Cana, CDA, D&K, H.PEC, PN_ratio, FANOUT, DC Path, Current Analyzer, STD Cell Check) Waiver/Analysis 방법을 개발 및 제공하고 있으며(VM/HBM4), (2) Current 분석기 3.0 개발을 통해서 기존 ADV 기반 분석 과정의 단점(ex. Schematic Cross Probing)을 극복하고 단일 분석 Platform(SORV 3.0)으로 일원화하여 Hierarchical Current 분석 기능, Block별 상세 분석 기능, Block/Unit Filtering 기능 등을 개발하였습니다(WH/VH). Seamless Signoff 수행 분석 및 Flow 개발을 목표로 vse-vxl-sorv 연계 기능 개발 및 Signoff workspace 기반의 Signoff 수행 환경 및 결과에 대한 History관리, Signoff 진행 현황에 대한 Message 알림 기능 등을 개발하였으며, Signoff Launcher 3.0 개발을 통하여 User Input Data,  Signoff Crieteria 등 정형화된 Signoff 환경을 제공할 예정입니다. Signoff Launcher 3.0을 통하여 Prelayout check들을 최소한의 Input을 Manual 없이 수행할 수 있는 Platform을 만들고 있습니다. (a) Dynamic Input Setting 기능을 지원하여 통합 개별 수행이 모두 가능하도록 개발했고, (b) Portal에 탑재된 정규 data를 자동으로 가져올 수 있는 기능을 Universal Voltage Document(UDV) Query 기능으로 가능하도록 개발하고 있습니다. (c)Input 정규화를 통해 제품 별로 한번만 Setup하면 약속된 Rule을 따라 DB를 적재하고, 그 내용을 자동 반영하여 Revision별 수행이 One-click으로 가능하도록 준비하고 있으며, (d) 가벼운 Signoff들은 Netlist 의 변경점을 파악하여 변경점이 있을 경우 지정된 시간(자정)에 자동으로 수행하여 결과를 DB로 적재할 수 있도록 준비중입니다. 해당 과정을 통해 user가 특별히 신경쓰지 않더라도 DB가 발행되면 자동으로 Signoff Tool을 수행해두고, 바로바로 원하는 때에 Design을 분석할 수있는 환경을 제공할 수 있게 하겠습니다.



# Signoff Task Leader 업무 계획

* Runtime Reduction & Large Data Management : Code Renewal, Parallel Processing, Hierarchical Signoff
* User-friendly Signoff Platform : Signoff Laucher & Viwer Platform with SPACE/ADV, VSE 통합 개발 (@Portal)

### Memory향 Seamless Signoff Platform 구축
1) EDA Tool-based Tr-level Signoff 방법론 개발 : CCK API 기반 Signiff Platform 개발 및 Application 확대
2) 연구과제
	1)  AI/ML-based enhanced Signoff Coverage/Garbage 방법론 개발 : Pattern Matching, Dynamic-based Static Application etc.
	2) Generative AI & ChatGPT 활용한 문의/대응 방법론 개발 (Signoff Result Viewer, MLM/JIRA)
	3) Low Power 설계/검증 방법론 개발 : Current Analsys, Invalid Toggle & Glitch Signoff, Vector-based Inactive Logic Signoff


### Tr-level Signoff in-house Tool 제품 적용:

Custom 메모리 제품의 Function / Timing / Power Signoff를 위해 In-house Tool 기반의 Tr-level Signoff Methodology를 개발하여 메모리 제품에 적용하고 있습니다. 해당 방법론의 개발 방향은, 
1) 변화하는 제품 및 검증 환경에 대응하기 위해 새로운 Tool을 개발하거나 기존 Tool을 개선하는 활동을 진행 중이며(Signoff Coverage-up & Garbage-zero)
2) 제품 개발실 담당자들이 배포된 SW를 원활하게 사용할 수 있도록 지원하고 있으며(User-friendly)
3) DM/SOD documentation과 user’s guide 작성/배포를 통한 시스템화/정형화를 추진하고 있습니다(System & Platform). 
	    
설계 단계에 따른 활용성/편의성/분석력 향상을 위해서
1) Signoff Result Viewer 3.0(SORV)를 개선하여 PreSim. Signoff 7종 포함 12개 Signoff App.별 Waiver/Analysis 방법을 개발 및 제공하고 있으며(VM/HBM4)
2) Current 분석기 3.0을 재개발하여 기존의 Hierarchical Current 분석에 추가로 Cross Probing 등 Result Viewer의 기능을 활용한 고차원적의 분석이 가능하도록 개선했습니다(D1a WH/D1b VH 제품)
3) 마지막으로 User Input을 단순화할 수 있는 App.을 선정하여 (Std. Cell Checker) Tool 수행과 결과 분석 GUI 자동 실행, Data를 협업 가능한 Workspace에 등록하면서, User와 Tool 담당자에게 자동 알람을 전달하는 Seamless Flow를 개발하여 Tool 수행의 어려움을 모두 제거한 자동화 Flow를 개발했습니다. 
기준 정보 기반하여 쉽게 수행할 수 있는 App.부터 차례로 Seamless Flow로 전환할 예정이며, 다양한 User Input이 필요한 Tool(DSC/Cana, Corner, Voltage, DSPF, BlkStar 등이 필요)의 경우 Signoff Launcher 3.0 개발을 통해 User가 Manual 없이 Signoff를 수행하고 분석할 수 있는 환경 개발을 진행하려고 합니다.


- Signoff Result Viewer 3.0 개발 관점에서는, 기존 Basecamp BTS용으로 개발한 GUI 2.0의 후속으로 개발한 3.0을 강화하는 작업을 진행하며 제품에 횡전개 중입니다. ⓐ Signoff Tool 별로 적합한 Group 방법과 Waiver 기능을 자동 설정하는 Predefined View를 추가(5→7개, Current Analyzer, STD Cell Check)하여, 모든 설계 담당자들이 Result Viewer의 고급 기능을 App.에 맞게 사용할 수 있도록 제공했고, ⓑ VWP Workspace에 업로드한 분석 결과를 바탕으로 협업을 통해 Signoff 결과를 Check/Waiver 가능하도록 지원했습니다. 그 과정에서 ⓒ 작업 중인 Data를 타인이 수정할 수 없게 잠금을 걸게 하고 이를 접근하려는 경우 Knox Teams Messenger를 통해 알람을 발송할 수 있도록 했고(DT DVT그룹 Devworks 지원), ⓓ 지난 Revision의 Waiver 결과를 신규 결과에 안전하게 합칠 수 있는 Waiver Migration 기능을 구현했습니다. ⓔ VM/HBM4 Bdie에 Result Viewer를 횡전개하여, Excel/EDM이 아닌 Workspace 경로를 통해 Signoff를 수행하도록 지원했고, HBM4 Bdie Fullchip DSC의 경우 20M Line의 Data를 3초 이내에 Sort/Group/Filter 가능한 것 확인하여 기존의 Excel/EDM으로는 불가능한 분석을 지원할 수 있었습니다. 설계 담당자의 Feedback으로 기존 Excel을 사용하던 환경 대비 VWP내 분석을 통해 Schematic Cross Probing이 가능한 점을 최대 장점으로 꼽았으며, 이는 기존 Tool (Result Viewer 1.0/2.0) Cross Probing이 가능함에도 불구하고, User의 Data Handling 요구사항을 만족하지 못해, Excel/EDM을 사용했던 부분을 해소한 영향으로 보고 있으며, 아직 1.0을 사용 중인 Analog Digital Verifier(ADV) 계열 분석 결과 또한 동일하게 Excel/EDM을 사용하는 것 확인하여(HBM3E Glitch Margin 분석 결과 Review), SORV 적용이 가능하도록 개선할 예정.
- Current 분석기 3.0 개발 관점에서도, Current 분석기 2.0이 독자적인 GUI를 사용하는데 따른 Schematic Cross Probing 기능 지원의 어려움과, 변화하는 제품 상황을 고려한 추가 분석 결과가 필요한 부분을 User가 Raw Data 추출 이후 Excel로 Detail한 작업을 하는 부분을 일원화/내재화하기 위해 3.0 Version을 개발하고 있습니다. ⓐ Tree View 기반의 Current 분석 GUI에 특정 Hierarchy에 대한 Detail View를 지원할 수 있게 개선하여(SORV Sub View 기능), 특정 Block에 존재하는 Mosfet의 Length별 개수, Width Sum, Size, Current Sum. 정보나 On/Off 된 Tr.의 개수 까지 알 수 있도록 제공했습니다. ⓑ 추가로 Analog 회로 등 분석에 불필요한 Block/Tr.을 제거할 수 있도록 SORV의 Filter 기능과의 호환성을 점검하는 중이며, Hierarchy 별 Statistic을 Dynamic하게 계산하도록 변경하여 User가 원하는 Data에 대해 Python Polars Big Data Package 기반의 고속 처리가 가능하도록 지원할 예정입니다.
- Seamless Signoff 수행 및 분석 Flow 개발 관점에서는, Nelitst만으로 수행할 수 있는 STD Cell Check(DT LS그룹) App.을 OPUS Layout Editor에서 One-Click으로 수행하면, ⓐ Virtuoso Schematic Editor(VSE)를 켜서 Layout Cross Probing이 가능하도록 하고, ⓑ SORV를 Open하여 User 접근성을 높였으며, ⓒ 분석 결과를 Workspace에 자동 업로드하여 History가 관리될 수 있도록 했습니다. ⓓ Data가 업로드 되는 시점에 User에게 Messenger 알람을 제공하여 업무를 바로 시작할 수 있도록 했고, ⓔ Tool 담당자에게도 Messege를 전달하여, STD Cell Check 결과를 User가 잘 분석하는지를 Monitoring하고, Special Case에 대한 빠른 대응이 가능하도록 System을 구축했습니다. Seamless 환경을 통해 User가 분석 Tool을 수행한 후 Excel 등 타 Platform을 활용하여 Guide하는 분석 환경을 벗어날 수 있는 가능성을 미연에 차단할 수 있고, Manual/Sop가 없이도 직관적으로 분석을 수행할 수 있을 것으로 기대하며, App.을 수행하는 시점을 Tool 담당자가 알게 하여, Tool Issue가 있을 경우 조기에 Monitoring/대응할 수 있는 System을 확보했습니다.
- 향후 계획으로, Signoff Tool 수행 - 분석 - 제품 반영의 Cycle을 SOP나 Manual없이 가능하도록 Flow를 개선하려 합니다. Seamless Flow를 여러 App.에 확대하면서 One-Click으로 다양한 Tool을 수행/분석할 수 있게 하고, 다양한 User Input이 필요한 Tool의 경우는 Signoff Launcher 3.0 개발을 통해 Tool 별로 필요한 Input이 Dynamic하게 생성되어 빈칸을 메꾸기만 하면 Tool을 누구나 쉽게 수행할 수 있도록 지원하려고 합니다. Tool 수행의 전 과정에 담당자 알람 기능을 탑재하여, User Behavior를 Monitoring하면서 자주 하는 실수를 미리 파악하여 조기에 Solution을 제공할 수 있게 하겠으며, Tool Issue나 결과에 대한 문의가 있을 경우 환경을 그대로 MLM Ticket으로 변경하는 등의 UX 지원을 진행할 계획입니다(~25.3)








