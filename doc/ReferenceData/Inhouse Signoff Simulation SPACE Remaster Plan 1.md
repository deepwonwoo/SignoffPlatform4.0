
현재 SPACE 기반의 Inhouse Signoff Tool들은 아래와 같이 동일한 space engine을 사용해서 작동해.

1. read tech file, set powers, read spice netlist
2. build design(Channel Connected Component(CCC) 알고리즘을 통해 Transistor Level의 회로를 Partition)
3. Signoff Application에 해당하는 작업을 위해 필요한 spice deck파일을 생성후 SPICE Simulation 수행 후 결과 취합. 

""" 
DSC example: 1.Read Input File:  spc, blk ,star 파일을 입력 받아 Parsing 한다. 2.Stage 추출: 입력 받은 Netlist 파일을 분석하여 CCC 알고리즘으로 Stage를 추출. Driver Size를 측정하기 위한 Slew Simulation의 단위가 된다. 3.Slew Simulation 3.1 Spice Deck, Vector 생성: 추출한 Stage를 이용하여 Slew SImulation을 위한 Spice Deck과 Vector를 생성. 3.2 Slew 측정: Input Slope 500ps로 SPICE Simulation을 수행 하여 Rising Slew와 Falling Slew를 측정.
"""

위에 언급했다 싶이 지금 회로의크기가 기하급수적으로 증가함에 따라 signoff simulation에 run time issue, coverage issue, garbage issue가 생기고잇어. runtime 같은 경우 ray를 통해 자원을 최대로 활용하는 병렬성으로 개선하려고해.
더 자세한 내용에 대해서는  아래를 참고해.


<space remaster>
현재 SPACE는 Signoff Inhouse Tool로 C++로 작성되었어. make를 통해서 컴파일하면 swig로 tcl wrapper를 사용해서 사용자는 space를 실행시키면 tcl script가 동작하고 이를  통해 space에 C++로 작성된 함수들을 사용하여 원하는 Signoff Application을 수행해. 대부분의 Signoff Application들은 공통적으로 1.회로 인식(read_spice_netslit, set power, read_techfile), 2. 회로자료구조 생성(transistor level의 회로를 partition, build_design: netlist파일을 분석하여 Channel Connected Component알고리즘으로 stage를 추출) 3.Signoff Application에 해당하는 작업을 위해 필요한 spice deck파일을 생성후 SPICE Simulation 수행 후 결과 취합 으로 진행되.  이때 생기는 문제로는 FullChip Netlist와 같이 회로가 굉장히 크다면 진행도중에 메모리 이슈로 segmentation fault가 발생한다던지, SPICE deck simulation들이 많게는 100만개가 수행되어야하는데 이것들이 모두 HPC로 spice job summit 형태로 진행되고있는데 HPC LSF Scheduler에서 작업 제출 시 bottleneck이 생기기 때문에 수행시간이 오래 걸려. 그리고 C++로 되어있어서 코드 유지보수하는데 어려움이 있어. 그렇기에 이를 tcl이 아닌 python wrapper를 사용하도록 업데이트하여 유지보수성을 높이고 각 SPACE 코드를 최대한 모듈화 하여 재사용성을 높이고 simulation 작업제출시 C++내에서 system call 함수로 작업제출을 일일히 하는게 아니라 python ray를 이용해서 python ray cluster작업을 제출하고 그 안에서 필요한 deck spice simulation들을 병렬처리로 수행하게 만드려고해. 이렇게되면 자원관리 및 HPC 작업제출시 발생하는 bottleneck과 simulation fail문제를 해결할수있을거 같아서 개선하려고해.
</space remaster>



