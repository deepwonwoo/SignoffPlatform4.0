# Channel Connected Component(CCC)
* TR Level DB 에서 Gate 를 찾기 위한 알고리즘.
* Vdd 에서 Gnd 로 연결된 MOS 를 Tracing 하며 Searching.
* 함수 : topology_builder.h:traceCCC 

MaxFETSizeInNet : net 에 연결된 fet 의 개수를 제한하여, large CCC 가 생성되지 않도록 처리함.



# Topology 는 Inv, Nand, Nor, Latch, Level Shifter 와 같은 Gate 를 Logical Searching 함.

findParallelFET  		: Parallel 한 FET 을 parallel_fet_hash 에 저장.
setOpenAndCloseFET		: FET 의 Gate 에 Supply 가 고정된 case 를 체크.
propagateSupplyFromOpenFET	: Open 된 FET 의 Supply 를 S-D 방향으로 전파시킴.
checkNetIsSupply		: Net 이 Supply 인지 체크.
createSameInstanceStage	: Master 이름이 같은 TR 을 찾음.
createTransmissonGateStage	: TG Gate를 logical Search 함.
createTriStateStage		: Tri Gate를 logical Search 함.
createCCC		: CCC 를 찾음.
setTransmissionGateInOut	: TG Gate 의 In, Out 을 저장.
setStageInOut		: Stage 의 In, Out 을 저장.
setStagePower		: Stage 의 Supply 를 저장.
addParallelFET		: parallel_fet_hash 의 fet 을 stage 에 추가함.
findSRLatch		: Logical SR Latch 를 찾음.
findLatch			: Logical Latch 를 찾음.
findLevelShfiter		: Logical LevelShifter 를 찾음.


