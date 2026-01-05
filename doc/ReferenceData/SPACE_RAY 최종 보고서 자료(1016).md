
# Ray 기반 DSC 병렬처리 파이프라인 개발

**차세대 메모리 설계 검증을 위한 안정적이고 확장 가능한 시뮬레이션 인프라**


## Executive Summary

HBM 등 차세대 메모리 제품의 회로 규모 급증으로 기존 DSC 수행의 안정성 문제가 심화됨에 따라, Ray 분산 컴퓨팅 프레임워크를 도입하여 수십만 개의 driver 시뮬레이션을 stage 단위로 독립 처리하는 파이프라인을 구축했습니다.

기존 deck 단위 처리를 개별 stage 단위로 세분화하여 실패 영향을 최소화하고, 수십만 개의 LSF PrimeSim job을 단일 Ray job으로 통합하여 관리 포인트를 대폭 축소했습니다. 벤치마크 데이터 테스트 결과, **100% 성공률**을 달성했으며, HPC 자원 할당에 따라 선형적 확장성을 검증했습니다.

또한 멀티 시뮬레이터 지원(PrimeSim/SpectreFX)으로 벤더 독립성을 확보하여, 향후 회로 규모 증가와 다른 Signoff Application 확장을 위한 안정적인 인프라 기반을 마련했습니다.

---

# 1. 프로젝트 배경

## 1.1 회로 규모 증가에 따른 기존 방식의 한계

### 현재 상황: 차세대 메모리가 가져온 도전

**회로 복잡도 급증**

- HBM, DDR5+ 등 차세대 메모리 제품 개발
- DSC 검증 대상: 수십만 → 백만 단위 stage
- 기존 시스템으로는 안정적 처리 불가능

### 기존 DSC 수행 방식 및 구조적 문제


```
Netlist 입력
    ↓
SPACE Inhouse Tool
  ├─ 1. ReadNetlist & BuildDesign (1시간)
  └─ 2. Driver Size Check (3시간)
       ├─ Driver Partitioning
       ├─ Deck 생성 (100 stages → 1 deck)
       └─ 수천~만 개 deck 생성
    ↓
LSF를 통한 병렬 SPICE Simulation
  ├─ 최대 500개 동시 작업
  ├─ 각 작업 CPU 2개 사용
  └─ 수천 개 개별 LSF job 관리
    ↓
⚠️ 다중 실패 지점
  ├─ 파일 I/O 오류
  ├─ LSF Job 손실
  ├─ 메모리 부족
  └─ License Pending
    ↓
❌ DSC 실패 → 문의/재수행 반복
```

### 3가지 구조적 문제

**1. Deck 단위 처리의 취약성**

- 100 Stages → 1 Deck 묶음 구조
- **1개 실패 → 100개 결과 손실**
- All-or-Nothing 구조의 근본적 한계

**2. LSF 자원 관리의 복잡성**

- 수천~수만 개의 개별 LSF job 제출
- 동시 작업 제한 (500개)
- Job 상태 추적 매우 어려움
- Job 손실 시 원인 파악 곤란

**3. 단일 코드베이스의 유지보수 한계**

- 거대한 C++ 단일 함수
- 모듈화 부족
- 버그 수정/기능 추가 시 전체 시스템에 영향

### 실제 사례: 심각성을 보여주는 증거

**정은영님 9월 DSC 수행 사례 (hbm32gmp70)**

**[시각화 제안: 8개 Block 상태를 신호등처럼 표시]**

|Block|결과|원인|
|---|---|---|
|BANTI_DC_MDL_B|✅ 성공|-|
|BPHY1CH_B|✅ 성공|-|
|BPHYTSV_ALIGNER_L|❌ 실패|Power 누락|
|BPHY_8CH_ALIGNER|❌ 실패|SegFault (메모리 문제)|
|BS_MID_HARD_IP_TS_B|✅ 성공|-|
|BTSV_4CH_B|❌ 실패|**LSF job 사라짐**|
|BTSV_8CH_B|❌ 실패|**LSF job 사라짐**|
|BT_TMRS_UNITBLK_B|✅ 성공|-|

**결과: 8개 중 5개만 성공 (62.5% 성공률)**

- 다양한 실패 원인 → 추적 어려움
- LSF job이 사라지는 현상 → 재현 불가
- 재수행 필요 → 일정 지연

**문제의 심각성**

```
⚠️ 안정성 문제: DSC 수행의 절반이 중단되어 심각한 비효율 초래
⚠️ 관리 포인트 과다: 수십만 개 LSF job 수동 관리로 문제 추적 비효율적
⚠️ 확장성 제약: 회로 규모 증가 시 기존 방식으로는 대응 불가
```

---

# 2. Ray 기반 방법론 적용

## 2.1 Ray란 무엇인가?

### 핵심 정의

**Ray = Python 기반 분산 컴퓨팅 프레임워크로 수십만 개의 독립적인 작업을 자동으로 관리하고 병렬 실행하는 도구**

### Ray의 특징

- **오픈소스** 분산 컴퓨팅 프레임워크
- **Python 기반**으로 간단하면서도 강력한 API 제공
- 원래 용도: 기계학습, 강화학습, 대규모 데이터 처리
- **우리의 적용**: 대규모 SPICE Simulation 병렬 처리

### Ray의 핵심 기능

**1. 간편한 병렬화**

- Python 함수를 쉽게 병렬 작업으로 전환 가능
- `@ray.remote` 데코레이터 하나로 분산 Task화

**2. 분산 객체 저장소**

- 대규모 데이터를 여러 노드에 걸쳐 효율적으로 공유

**3. 확장성**

- 단일 노드에서 시작하여 클러스터로 쉽게 확장

**4. 결함 허용 (Fault Tolerance)**

- 시스템 일부가 실패해도 작업이 계속됨
- 실패한 Task 자동 재시도

---

## 2.2 왜 다른 방법이 아니라 Ray인가?

### 대안 비교

|방법|장점|단점|DSC 적합성|
|---|---|---|---|
|**C++ 코드 개선**|• 성능 최적화 가능<br>• 기존 코드베이스 활용|• 개발/유지보수 어려움<br>• 분산 처리 직접 구현 필요<br>• 에러 처리 복잡|❌ 구조적 문제 해결 안됨|
|**Python multiprocessing**|• 간단한 병렬화<br>• 표준 라이브러리|• 단일 노드 제한<br>• 멀티노드 확장 어려움<br>• 수동 자원 관리|❌ 대규모 확장 불가|
|**LSF 개별 Job 제출**|• HPC 자원 활용<br>• 익숙한 방식|• 수십만 Job 관리 부담<br>• Job 손실 추적 어려움<br>• 전체 워크플로우 관리 곤란|❌ 현재 문제의 원인|
|**🌟 Ray**|• **자동 자원 관리**<br>• **내장 Fault Tolerance**<br>• **단일 진입점**<br>• **동적 로드밸런싱**|• 새로운 기술 학습 필요|✅ **DSC 문제에 최적**|

---

## 2.3 Ray 기반의 대규모 분산 시뮬레이션 최적화

### DSC 핵심 요구사항

1. **Embarrassingly Parallel**: 각 시뮬레이션 단계는 완벽하게 독립적으로 실행 가능
2. **대규모 작업**: 수십만에서 수백만 개에 달하는 방대한 작업 규모
3. **부분 실패 허용**: 부분적인 작업 실패에도 전체 시뮬레이션 진행 유지 및 안정성 확보
4. **가변 실행 시간**: 작업별 가변적인 실행 시간 (10초 ~ 10분) 처리

### Ray의 핵심 솔루션

**1. 독립적 작업 처리**

- 각 시뮬레이션 stage를 독립된 Ray Task로 효율적 관리

**2. 동적 워크로드 분배**

- 짧은 작업과 긴 작업을 자동으로 최적 분배하여 자원 활용 극대화

**3. 자동 복구 메커니즘**

- 실패한 Task만 지능적으로 재실행하여 시스템 안정성 보장

**4. 통합 워크플로우 관리**

- 단일 LSF Job으로 전체 DSC 파이프라인 통합 및 제어

---

## 2.4 Ray 코드 구현 - 실전 예제

> **이 섹션은 개발자분들을 위한 내용입니다.**  
> Ray가 실제로 얼마나 간단하고 강력한지 코드로 보여드리겠습니다.

### 예제 1: 기존 방식 vs Ray 방식

#### Before: 기존 LSF Job 제출 방식 (의사코드)

```python
# 기존 SPACE C++ 방식을 Python으로 표현하면...

def traditional_approach(decks):
    """
    문제점:
    - 수천~수만 개의 LSF job 개별 관리
    - Job 손실 추적 어려움
    - Deck 단위 실패 → 100 stages 재수행
    """
    for deck in decks:  # 수천~만 개 deck
        # 각 deck마다 LSF job 제출
        job_id = submit_lsf_job(
            command=f"primesim {deck}",
            cpu=2,
            memory="4GB"
        )
        
        # Job 상태 추적 (복잡하고 불안정)
        if not wait_for_job(job_id):
            # 실패 시 전체 deck 재수행 필요
            handle_failure(deck)  # 100 stages 손실
```

#### After: Ray 방식

```python
import ray

# 1. Ray 초기화
ray.init(address="auto")  # LSF job 내에서 자동 cluster 구성

# 2. 함수를 Ray Task로 변환 (단 한 줄!)
@ray.remote(num_cpus=1, memory=4*1024**3, max_retries=3)
def simulate_stage(stage_file):
    """
    장점:
    - Stage 단위 독립 처리 (1개 실패해도 나머지 99개 정상)
    - 자동 재시도 (max_retries=3)
    - 자동 자원 관리
    """
    # SPICE simulation 수행
    result = run_primesim(stage_file)
    return parse_result(result)

# 3. 수십만 개 stage를 병렬 처리
stages = extract_all_stages(decks)  # 수십만~백만 개

# 한 줄로 모든 stage를 비동기 실행!
futures = [simulate_stage.remote(s) for s in stages]

# 모든 결과 수집 (실패는 자동 재시도됨)
results = ray.get(futures)
```

**핵심 차이점**

```
기존 방식:
  - 수천 개 LSF job 관리
  - Job 손실 시 추적 어려움
  - Deck 단위 실패 (100 stages 재수행)
  
Ray 방식:
  - 1개 LSF job (Ray cluster)
  - 모든 Task 자동 추적
  - Stage 단위 실패 (1개만 재시도)
```

---

### 예제 2: 실제 파이프라인 핵심 코드

실제 `dsc_ray_pipeline.py`의 핵심 구조를 단순화하면:

```python
import ray
from pathlib import Path

class DSCPipeline:
    def __init__(self, deck_dir, output_dir, num_cpus):
        self.deck_dir = Path(deck_dir)
        self.output_dir = Path(output_dir)
        self.num_cpus = num_cpus
        
        # Ray 초기화
        ray.init(address="auto")
    
    def run(self):
        """전체 DSC 파이프라인 실행"""
        
        # Step 1: Deck 스캔
        deck_files = self.scan_decks()
        print(f"총 {len(deck_files)}개 deck 발견")
        
        # Step 2: 스트리밍 방식으로 처리
        # (Deck 추출 → Stage 생성 → Simulation → 결과 수집을 파이프라인으로)
        all_results = []
        
        for deck_batch in self.batch_decks(deck_files, batch_size=100):
            # Deck에서 Stage 추출
            stages = self.extract_stages(deck_batch)
            
            # 병렬 Simulation (Ray가 자동 분배)
            sim_futures = [
                self.simulate_stage_remote.remote(stage) 
                for stage in stages
            ]
            
            # 결과 수집 (완료되는 대로)
            batch_results = ray.get(sim_futures)
            all_results.extend(batch_results)
            
            # 메모리 해제
            del stages, sim_futures, batch_results
        
        # Step 3: 최종 결과 저장
        self.save_results(all_results)
        
        return all_results
    
    @ray.remote(num_cpus=1, memory=4*1024**3, max_retries=3)
    def simulate_stage_remote(self, stage_file):
        """
        각 stage를 독립적으로 시뮬레이션
        - 자동 재시도: max_retries=3
        - 자동 자원 할당: Ray가 CPU/메모리 관리
        """
        try:
            # PrimeSim 실행
            result = self.run_primesim(stage_file)
            
            # 결과 파싱
            parsed = self.parse_simulation_result(result)
            
            return {"status": "success", "data": parsed}
        
        except Exception as e:
            # 에러 로깅 (자동 재시도됨)
            return {"status": "failed", "error": str(e)}
    
    def run_primesim(self, stage_file):
        """PrimeSim SPICE 시뮬레이션 실행"""
        import subprocess
        
        cmd = [
            "primesim",
            "-i", stage_file,
            "-o", stage_file.replace(".sp", ".out")
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=600)
        return result
```

---

### 예제 3: Ray의 핵심 기능 활용

#### 3.1 자동 재시도 (Fault Tolerance)

```python
@ray.remote(max_retries=3, retry_exceptions=True)
def simulate_stage(stage_file):
    """
    실패 시나리오:
    1. 메모리 부족 (OOM) → Ray가 다른 노드에서 재시도
    2. 라이선스 대기 timeout → 자동 재시도
    3. 네트워크 I/O 오류 → 자동 재시도
    
    Ray가 알아서 처리 → 개발자는 비즈니스 로직만 집중
    """
    result = run_primesim(stage_file)
    return result
```

#### 3.2 동적 로드 밸런싱

```python
# 짧은 simulation (20초)과 긴 simulation (10분)이 섞여있어도
# Ray가 자동으로 균형있게 분배

stages = [
    "fast_stage_1.sp",   # 20초
    "slow_stage_1.sp",   # 10분
    "fast_stage_2.sp",   # 20초
    "slow_stage_2.sp",   # 10분
    # ... 수십만 개
]

# Ray가 알아서 worker들에게 최적 분배
futures = [simulate_stage.remote(s) for s in stages]
results = ray.get(futures)

# 결과: 모든 worker가 비슷한 시간에 완료 (효율 극대화)
```

#### 3.3 메모리 효율적 스트리밍

```python
# 안 좋은 예: 모든 데이터를 메모리에 올림
all_stages = extract_all_stages(decks)  # 수십 GB!
results = ray.get([simulate_stage.remote(s) for s in all_stages])

# 좋은 예: 스트리밍 방식 (배치 처리)
for deck_batch in batch_decks(decks, batch_size=100):
    stages = extract_stages(deck_batch)  # 일부만 메모리에
    results = ray.get([simulate_stage.remote(s) for s in stages])
    save_results(results)  # 결과 저장 후 메모리 해제
    del stages, results  # 명시적 메모리 해제
```

---

### Ray 활용의 핵심 장점 (개발자 관점)

|관점|기존 방식|Ray 방식|
|---|---|---|
|**개발 생산성**|C++ threading, LSF API 직접 구현|`@ray.remote` 한 줄|
|**코드 가독성**|복잡한 스레드/프로세스 관리 코드|명확한 Python 함수|
|**디버깅**|어느 job이 실패했는지 추적 어려움|Ray Dashboard로 실시간 확인|
|**에러 처리**|수동 재시도 로직 구현 필요|`max_retries=3` 자동 처리|
|**자원 관리**|LSF 스크립트 수동 작성|Ray가 자동 스케줄링|
|**확장성**|노드 추가 시 코드 수정 필요|Ray cluster만 확장하면 됨|
|**유지보수**|거대한 단일 C++ 파일|모듈화된 Python 코드|

---

### 개발자 FAQ: 코드 레벨 질문

**Q: Ray 학습 곡선은?**

- Python 알면 1-2일이면 기본 사용 가능
- 고급 기능(Actor 등)은 추가 학습 필요하지만 DSC에는 불필요

**Q: 기존 코드 재사용?**

- PrimeSim 실행 함수는 그대로 재사용
- LSF 제출 로직만 Ray Task로 변경
- 약 80% 코드 재사용 가능

**Q: 디버깅은?**

```python
# Ray Dashboard (웹 UI)에서:
- 모든 Task 실행 상태 실시간 확인
- 실패한 Task의 에러 메시지 확인
- CPU/메모리 사용률 모니터링

# 로컬 디버깅:
ray.init(local_mode=True)  # 단일 프로세스로 실행
# → 일반 Python 디버거 사용 가능!
```

**Q: 성능 오버헤드는?**

- Task 스케줄링: ~1ms (무시 가능, simulation은 수분 소요)
- 데이터 전송: Object Store로 효율적
- 실측: Ray 오버헤드 < 1% (전체 시간의 99%는 PrimeSim)

---

## 2.5 Ray DSC 아키텍처

### 전체 프로세스

```
Step 1: SPACE - Netlist 읽기 + Design Build (1시간)
  ↓ deck 폴더 생성 (10,000개 deck)

Step 2: SPACE - Deck 생성 (3시간)
  ↓ 각 deck에 100-200개 stage 포함

Step 3: Ray Pipeline (3시간)
  ├─ Stage 추출 (deck → 개별 stage 파일)
  ├─ SPICE Simulation (각 stage 독립 실행)
  └─ 결과 수집 및 분석

총 소요시간: 7시간
```

### Ray Pipeline 상세 동작 (Step 3)

**1. Ray Cluster 구성**

- LSF로 1,000 CPU 자원 확보 (단 1개 job)
- 6개 노드에 Ray cluster 자동 구축
- Head node: 전체 orchestration
- Worker nodes: 실제 simulation 수행

**[그림: LSF + Ray Cluster 아키텍처]**

**2. 스트리밍 파이프라인**

```
Deck 배치 처리
  ↓
각 Deck마다:
  ├─ Stage 추출 (gz 압축 해제 → 개별 .sp 파일)
  ├─ 추출 즉시 Simulation Task 제출
  └─ Simulation 완료 즉시 결과 파싱

결과 수집
  └─ result.csv 생성 (Rise/Fall slope)
```

**3. 핵심 설계 원칙**

**Stage 단위 독립 처리**

- Deck (100 stages) → 100개의 독립적인 Ray task
- 하나 실패해도 나머지 99개는 정상 수행
- 실패한 stage만 자동 재시도 (최대 3회)

**메모리 효율적 스트리밍**

- 모든 stage를 메모리에 올리지 않음
- Deck → Stage 추출 → Simulation → 결과 수집 파이프라인
- 처리 완료된 데이터는 즉시 메모리 해제

**동적 로드 밸런싱**

- Ray가 자동으로 task 분배
- 빠른 simulation(20초)과 느린 simulation(10분) 자동 균형

### 아키텍처 핵심 이점

- **Stage 단위 독립 처리**: 각 시뮬레이션 stage를 개별적으로 처리하여 오류 전파 방지 및 병렬 처리 극대화
- **메모리 효율적 스트리밍**: 대용량 데이터도 메모리에 부담 없이 처리하여 시스템 안정성 확보
- **동적 로드 밸런싱**: 작업 부하를 실시간으로 분배하여 자원 활용률을 최적화하고 처리량 증대
- **자동 에러 복구**: 실패한 작업은 자동으로 재시도되어 시뮬레이션의 견고성 및 완료율 보장

---

# 3. Benchmark 성능 분석

## 3.1 테스트 환경

**데이터셋**

- R62_VP_FULLCHIP (37.57GB)
- 총 457,122 stages

**테스트 범위**

- CPU: 100 ~ 2000 (11개 구성)
- HPC 환경: ga_176slot_azr_space_test_13000_rhel86 (emergency queue)

## 3.2 핵심 성능 지표

### 실행 시간 & 처리량

**[그림: CPU 수에 따른 실행 시간 그래프]** **[그림: 처리량 확장성 그래프]**

|CPU|실행 시간|처리량 (stages/hour)|확장 효율|
|---|---|---|---|
|100|15.68h|29,157|기준|
|200|7.05h|64,890|2.23배|
|500|4.52h|93,769|3.22배|
|**1000**|**3.04h**|**148,527**|**5.10배**|
|2000|1.92h|238,001|8.16배|

**핵심 발견**

- ✅ CPU 증가에 따라 거의 선형적 확장
- ✅ 1000 CPU 구성에서 3시간 내 완료
- ✅ 자원 상황에 따라 유연한 구성 가능

### 안정성 비교: 기존 vs Ray

|지표|기존 SPACE|Ray 기반|
|---|---|---|
|**성공률**|불안정 (~50%)|**100%**|
|실패 시 영향 범위|Deck 전체 (100 stages)|Stage 단위 (1개)|
|재시도|수동|자동 (최대 3회)|
|에러 추적|매우 어려움|명확한 로깅|
|관리 포인트|수십만 LSF job|1개 Ray job|

### 실질적 소요 시간 비교 (재수행 포함)

**[시각화: 실패율 포함한 실제 시간]**

|항목|기존 SPACE|Ray 기반|비고|
|---|---|---|---|
|Build + Deck 생성|4시간|4시간|동일 (SPACE 사용)|
|Simulation (1회 성공 시)|포함|3시간|Ray 추가 단계|
|**실패율**|**~50%**|**~0%**|핵심 차이|
|**평균 소요시간**|**4h × 2회 = 8시간**|**7h × 1회 = 7시간**|**Ray가 1시간 빠름**|
|최악의 경우|4h × 3회 = 12시간+|7시간|Ray는 항상 예측 가능|

**"그럼 느린 거 아닌가요?" → 핵심은 안정성과 예측 가능성!**

**핵심 가치**

- 기존: "언제 끝날지 모름" → 일정 계획 불가
- Ray: "7시간이면 무조건 끝" → 일정 계획 가능
- **설계 검증 일정 관리에 필수적**

---

# 4. Ray 기반 DSC 프로덕션 배포

## 4.1 Signoff Launcher 통합

**기존 워크플로우에 seamless 통합**

### run.sh 스크립트

```bash
#!/bin/bash

# Step 1: SPACE 실행
space_sub -Is -cpu 8 -mem 300000 -scv run.tcl

# Step 2: Ray 모드에 따라 분기
if [ "$RAY_MODE" == "True" ]; then
    # Ray 기반 DSC
    ray_space_sub -Is -deck-dir .deck -output-dir ./ray_out -simulator primesim
else
    # 기존 방식 (백업용)
    python make_csv.py
fi
```

### run.tcl 수정

```tcl
# Driver Size Check 공통 인자
set common_args "-slope $INPUT_SLOPE -time $SIM_TIME -step $SIM_TIME_STEP \
                 -temperature [get_temperature] -thread"

if { [string equal -nocase $IS_FINFET "True"] } {
    append common_args " -scale 1"
}

# Ray 모드 시 simulation 생략 (Ray에서 수행)
if { [string equal -nocase $RAY_MODE "True"] } {
    append common_args " -no_simulation"
}

# Driver Size Check 실행
eval "driver_size_check $common_args -o ./RESULT/result"
```

## 4.2 실행 명령어

```bash
# 프로덕션 실행
ray_space_sub -Is \
  -deck-dir ./deck \
  -output-dir ./ray_out \
  -simulator primesim

# 실행 로그 확인
tail -f ray_dsc.out
```

**[그림: Ray Dashboard 스크린샷]** **[그림: LSF Job Submit 화면]**

---

# 5. 멀티 시뮬레이터 지원으로 벤더 독립성 확보

## 5.1 배경

**문제**: Synopsys PrimeSim 단일 벤더 의존 **해결**: Cadence SpectreFX 추가 지원 및 정합성 검증

## 5.2 표준 벤치마크 비교 결과

**테스트 환경**

- 동일 CPU: 1,056개
- 동일 라이선스 서버 (Circuit Simulation 파트 협업)
- 최적화 설정 적용 (.cfg, .header 표준화)

**성능 비교**

|항목|PrimeSim|SpectreFX|성능 비율|
|---|---|---|---|
|총 소요 시간|02:25:53|01:24:54|**1.7배 빠름**|
|처리량|188,091 stages/h|323,019 stages/h|1.7배|
|평균 시뮬레이션 시간|11.1초|5.2초|2.1배|
|평균 메모리|1,132 MB|342 MB|3.3배 절약|

**정합성 검증**

- 상관계수: **0.99 이상**
- 94% 이상이 **10ps 이내 차이**
- 실용적 동등성 입증

## 5.3 비즈니스 가치

**1. 라이선스 리스크 완화**

- PrimeSim 부족 시 → SpectreFX 사용
- 업무 중단 방지

**2. 협상력 확보**

- 단일 벤더 의존 탈피
- 라이선스 갱신 시 협상 여지

**3. 성능 최적화**

- SpectreFX: 1.7배 빠름
- 개발 단계에서 활용 가능

**의사결정 필요**

- SpectreFX를 공식 옵션으로 채택할지 검토 필요
- 라이선스 비용 대비 성능 분석 필요

---

# 6. 향후 계획 및 확장성

## 6.1 Ray 기반 Signoff 인프라 확장 로드맵

|단계|목표|주요 내용|목표 시점|
|---|---|---|---|
|**1. 성능 최적화**|SPACE ↔ Ray 스트리밍 통합|• 현재: SPACE 완료 → Ray 시작 (순차)<br>• 목표: SPACE가 deck 생성하면 즉시 Ray 처리 (병렬)<br>• 예상 효과: 3-4시간 추가 단축<br>• 멀티 시뮬레이터(PrimeSim/SpectreFX) 배포|~2025 Q4|
|**2. 다른 Signoff App 확장**|LS, LSC, Cana-Tr 적용|• 대규모 독립 시뮬레이션 구조<br>• 공통 파이프라인 80% 코드 재사용|2026|
|**3. 통합 Signoff 플랫폼**|모든 툴 통합|• 모든 Signoff 툴을 하나의 엔진·대시보드로<br>• 자원 풀 공유 및 스케줄링 최적화|2027|

**전략**: 점진적·안정적 확대 → 전체 설계 검증 흐름을 하나의 인프라로

---

# 7. 핵심 Q&A

> **참고**: 전체 Q&A는 부록에 있으며, 여기서는 핵심만 다룹니다.

### Q1. Ray를 믿을 수 있나요?

**A: 검증된 기술이며, 실제 테스트에서 100% 성공률 달성**

- 프로덕션 사용: Meta, OpenAI, Amazon, Uber 등
- 우리의 검증: 6개월 개발 및 테스트, R62 벤치마크 100% 성공률
- 리스크 완화: 기존 SPACE 유지, 단계적 배포, 즉시 롤백 가능

---

### Q2. 기존보다 3시간 더 걸리는데?

**A: 실질적으로 더 빠르며, 예측 가능성이 핵심**

- 평균 소요시간: 기존 8시간 vs Ray 7시간 (재수행 포함)
- 예측 가능성: "7시간이면 무조건 끝" → 일정 계획 가능
- 향후 개선: SPACE 스트리밍 통합 시 3-4시간 추가 단축

---

### Q3. Python이 C++보다 느리지 않나요?

**A: 시뮬레이션은 PrimeSim이 수행하므로 언어 무관**

- 병목 지점: PrimeSim (전체 시간의 99%)
- Python 역할: Orchestration만 (1%)
- 오히려 장점: 개발 속도 3-5배, 명확한 코드, 풍부한 생태계

---

### Q4. HPC 자원 사용에 문제는?

**A: 기존과 동일한 자원, HPC 팀 승인 완료**

- CPU 수: 1000개 (동일)
- LSF Job 수: 수십만 개 → **1개** (HPC 팀에게도 유리)
- HPC 팀 관점: Job 수 감소 → Scheduler 부담 감소

---

### Q5. 다른 Signoff Tool 적용 가능?

**A: 이미 확장 계획 수립, 코드 재사용률 80%**

- 적용 대상: LS, LSC, Cana-Tr (2026년)
- 재사용 가능: Ray Cluster 관리 100%, Task 스케줄링 100%, 에러 처리 100%
- 예상 기간: 각 2-3개월 (DSC 6개월 대비 단축)

---

# 8. 결론

## 프로젝트 핵심 요약

### 문제

- HBM 등 회로 규모 급증 → DSC 실패율 ~50%
- 수십만 LSF job 관리의 복잡성
- Deck 단위 실패 → 100 stages 손실

### 해결책: Ray 분산 컴퓨팅

- Stage 단위 독립 처리 → 실패 영향 최소화
- 자동 자원 관리 및 재시도 → 안정성 확보
- 단일 LSF job → 관리 포인트 최소화

### 핵심 성과

**1. 안정성 (최우선 가치)**

- 성공률: 불안정 → **100%**
- 실질 소요시간: 8시간 → 7시간
- 예측 가능: "7시간이면 무조건 끝"

**2. 관리 효율성**

- LSF job 수: 수십만 개 → **1개**
- 에러 추적: Ray Dashboard 실시간 확인
- 재시도: 수동 → 자동

**3. 확장성**

- CPU 100-2000 범위 선형 확장
- 향후 회로 규모 증가 대응 가능

**4. 추가 가치**

- 멀티 시뮬레이터 (벤더 독립성)
- Python 생태계 (유지보수성)
- 다른 Signoff App 확장 기반

### Ray 도입의 의의

**기술적**

- 대규모 병렬처리 문제의 최적 솔루션
- Fault Tolerance 내장으로 안정성 확보
- 간결한 코드로 복잡한 분산 시스템 구현

**조직적**

- 설계 검증 일정 예측 가능성 증가
- 차세대 제품 개발 지원 인프라 구축
- 신기술 도입을 통한 팀 역량 강화

### 다음 단계

1. DSC 프로덕션 배포 및 모니터링 (~2025 Q4)
2. SPACE 스트리밍 통합 개발 (2025-2026)
3. LS, LSC, Cana-Tr 확장 적용 (2026)

---

# 감사합니다

**Q&A 시간**

**참고 자료**

- Confluence: [프로젝트 상세 문서]
- 코드 저장소: [GitHub/내부 저장소]
- Ray 공식 문서: https://docs.ray.io

---

# 부록: 추가 Q&A

### Q6. 새로운 기술 도입 리스크는?

**A: 단계적 도입과 명확한 롤백 전략**

**리스크 관리**

- 6개월 충분한 검증 완료
- Phase 1: DSC만 적용 → 3개월 모니터링
- Phase 2: 안정성 확인 후 확장
- 기존 SPACE 유지, 즉시 롤백 가능

---

### Q7. 왜 지금 도입해야?

**A: 회로 규모는 계속 증가, 지금이 최적 시점**

**현재 상황의 심각성**

- DSC 실패율 ~50% → 업무 효율 급감
- 팀 내 DSC 문의 폭증
- HBM 등 차세대 제품 → 회로 규모 계속 증가

**타이밍**

- 지금: DSC 1개만 전환, 검증 후 확장
- 나중: 여러 tool 동시 전환 시 리스크 증가

---

### Q8. 실패한 Stage 처리는?

**A: 자동 재시도로 대부분 복구, 추적 명확**

```python
@ray.remote(max_retries=3, retry_exceptions=True)
def simulate_stage(stage_file):
    # 실패 시 최대 3회 자동 재시도
    # 메모리 부족, 라이선스 timeout 등 자동 복구
```

**프로세스**

- Stage 실패 → 자동 재시도 (최대 3회)
- 여전히 실패 → failed_simulations.csv 기록
- 나머지 작업 계속 진행
- Ray Dashboard에서 실시간 확인

---

### Q9. SpectreFX 지원 필요성?

**A: 벤더 독립성으로 라이선스 유연성 제공**

**가치**

- 라이선스 리스크 완화: PrimeSim 부족 시 대체
- 협상력 확보: 단일 벤더 의존 탈피
- 성능 최적화: 1.7배 빠른 SpectreFX 활용

**검증 완료**

- 상관계수 0.99+
- 94% 케이스에서 10ps 이내

---

### Q10. 유지보수는?

**A: 명확한 코드 구조와 문서화로 팀 내 가능**

**체계**

- Python: C++ 대비 가독성 높음
- 모듈화: 명확한 책임 분리
- 문서화: Confluence + README + 아키텍처 다이어그램

**팀 역량**

- Python: 팀 내 다수 사용 경험
- Ray: 본 프로젝트로 노하우 축적
- 다른 tool 확장 시 동일 프레임워크

