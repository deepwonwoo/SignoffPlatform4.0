



# 1. 배경 및 도입 목적

## 기존 수동 배포 방식의 한계점

현재 우리 팀은 19종의 Signoff Application을 운영하고 있으며, 각 Application마다 전담 개발자(정/부 1-2명)가 배정되어 있습니다. 이들 Application은 모두 현재 활발하게 사용되고 있으며, 설계 검증 과정에서 핵심적인 역할을 담당하고 있습니다.

### 기존 배포 방식의 구조와 한계점

#### 기존 배포 프로세스 (사내 HPC망 Bitbucket 기반)


기존 시스템은 다음과 같은 방식으로 운영되어 왔습니다:

```
[개발자] → [Bitbucket Repository] → [Launcher 담당자] → [배포 경로]
   ↓              ↓                    ↓               ↓
코드 수정       git push            수동 검수        git pull
업데이트        Bitbucket           권한 획득       /user/signoff.dsa/
```

이 과정을 구체적으로 살펴보면, Application 개발자가 코드를 수정하고 Bitbucket에 push한 후, Launcher 담당자가 직접 배포 경로(`/user/signoff.dsa/RUNSCRIPTS/`)로 이동하여 `newgrp signoff.dsa` 명령어로 권한을 획득하고 `git pull`을 수행하는 방식이었습니다.


- **기존 시스템 개요**:
    - 사내 HPC망의 Bitbucket을 Remote Repository로 사용.
    - 19개 Signoff Application(모두 활발히 개발 중, 점점 증가)마다 별도 Repository.
    - 개발 담당자(1-2명/Application): 코드 수정/업데이트 후 Bitbucket에 Push.
    - Launcher 담당자: 배포 요청 받으면, 배포 경로(/user/signoff.dsa/RUNSCRIPTS/)에서 newgrp signoff.dsa로 권한 획득 후 git pull 수행.
    - Signoff Launcher 동작: signoff_applications.yaml에서 배포 경로 참조 → input_config.yaml 기반 GUI 입력 필드 생성 → Run 시 RUNSCRIPTS 폴더 복사해 수행.

#### 수동 배포 방식의 실질적 문제점

**시간 지연 문제**: 현재 월평균 배포 요청이 Application별로 다르지만, 활발한 Application의 경우 월 5회까지 배포 요청이 발생합니다. Launcher 담당자가 즉시 대응할 수 있을 때는 빠르게 처리되지만, 담당자가 바쁘거나 부재중일 때는 배포가 지연됩니다. 실제로 월 1일 정도는 담당자 부재로 인한 배포 지연이 발생하고 있습니다.

**업무 효율성 저하**: 개발자들이 개발 업무에 절반 이상의 시간을 할애하고 있는 상황에서, 배포 대기 시간은 전체 개발 사이클을 늦추는 요인으로 작용합니다. 특히 긴급한 버그 수정이나 설계 변경 대응이 필요한 경우, 배포 지연은 설계 검증 일정에 직접적인 영향을 미칩니다.

**확장성 한계**: 현재 19개 Application이 모두 활발히 사용되고 있으며, 새로운 Application이 지속적으로 추가되고 있는 상황입니다. 수동 배포 방식으로는 향후 증가하는 배포 요청량을 효율적으로 처리하기 어려운 구조적 한계가 있습니다.

- **주요 문제점**:
    - 배포 지연: Launcher 담당자 대기 필요 (바쁘거나 휴가 시 지연, 월 평균 1일 정도 전체 배포 중단 가능).
    - 효율성 저하: 월 배포 요청 0~5회/Application → 누적 대기 시간 증가, 특히 활발한 Application에서 TAT(turn-around time) ↑.
    - 개발자 부담: Push 후 기다림 → 회로 설계 본업(50%+ 시간 할애) 중 개발 업무 효율 ↓.
    - 실수 가능성: 수동 과정에서 오류(아직 사례 없지만 잠재적 위험).


## 자동화 도입의 필요성과 전략적 가치

### CI/CD 자동화의 핵심 개념

CI/CD(Continuous Integration/Continuous Deployment)를 제조업에 비유하면, 기존의 수작업 조립 라인을 자동화된 생산 라인으로 전환하는 것과 같습니다. 자동차 제조 공정에서 각 부품이 조립되고 품질 검사를 거쳐 최종 제품이 출하되는 과정이 자동화되어 있듯이, 소프트웨어 개발에서도 코드 변경부터 배포까지의 전 과정을 자동화하는 것이 CI/CD의 핵심입니다.

### GitHub로의 전환이 가져오는 전략적 이점

#### 조직 차원의 표준화

우리 그룹에서는 GitHub를 표준 CI/CD 툴로 정했으며, 이는 IT 업계의 일반적인 표준과도 일치합니다. 이러한 표준 도구 사용은 다음과 같은 조직적 이점을 제공합니다:

**기술 스택 통일화**: 다른 팀과의 협업이나 지식 공유가 용이해지며, 사내 다른 프로젝트와의 연동 가능성이 높아집니다.

**확장 가능한 인프라**: GitHub Actions는 개별 팀이 원하는 대로 runner를 구축하거나 팀 단위 runner를 사용할 수 있는 유연성을 제공합니다. 이는 향후 더 복잡한 자동화 워크플로우 구현의 기반이 됩니다.

#### 기술적 우위성

**풍부한 생태계**: GitHub Actions는 광범위한 community actions와 강력한 CI/CD 기능을 제공합니다. 이는 단순한 배포 자동화를 넘어서 테스트 자동화, 코드 품질 검사 등으로 확장할 수 있는 확장성을 의미합니다.

**직관적인 사용자 경험**: GitHub의 웹 인터페이스는 비전공자도 쉽게 이해할 수 있도록 설계되어 있어, 회로 설계 전문가들이 CI/CD 개념을 학습하고 활용하기에 적합합니다.

**실시간 모니터링**: 배포 과정의 모든 단계가 실시간으로 시각화되어 제공되므로, 문제 발생 시 빠른 진단과 대응이 가능합니다.
## 개발자들에게 미치는 직접적인 혜택

### 워크플로우의 혁신적 단순화

#### Before: 복잡한 다단계 프로세스

```
코드 수정 → Bitbucket Push → 배포 요청 → 담당자 대기 → 수동 배포 → 확인
   (개발자)      (개발자)        (개발자)      (지연 가능)     (타인 의존)    (개발자)
```
- Before: Push 후 Launcher 담당자에게 요청 → 대기(바쁠 때 지연) → 배포.
#### After: 스트림라인화된 자동 프로세스

```
코드 수정 → GitHub Push → 자동 배포 완료 + 알림
   (개발자)      (개발자)        (시스템 자동)
```
- - After: Push만 하면 자동 (검증 → 배포) → 즉시 Launcher 반영.
### 개발 생산성의 근본적 향상

**즉시성**: 코드를 push하는 순간 자동으로 검증과 배포가 시작되어, 개발자가 다른 업무를 진행하는 동안 백그라운드에서 배포가 완료됩니다.

**예측 가능성**: 배포 과정이 표준화되고 자동화되어, 언제나 동일한 결과를 기대할 수 있습니다. 이는 특히 긴급한 버그 수정이나 설계 변경 대응 시 중요한 요소입니다.

**자율성 증대**: 다른 사람의 일정에 의존하지 않고 독립적으로 배포를 수행할 수 있어, 개발자의 업무 자율성이 크게 향상됩니다.

### 품질 관리의 체계화

자동화된 배포 시스템은 단순히 배포 속도를 높이는 것을 넘어서, 품질 관리 측면에서도 중요한 개선을 제공합니다. 모든 배포는 사전 정의된 검증 단계(`validate_check.py`, `validate_check_for_run.py`)를 통과해야 하므로, Signoff Launcher와의 호환성이 보장된 코드만이 배포됩니다.

이러한 자동화된 품질 검증은 수동 검수보다 일관성이 높고, 사람에 의한 실수 가능성을 근본적으로 제거합니다. 또한 모든 배포 과정이 로그로 기록되어 추적 가능하므로, 문제 발생 시 빠른 원인 분석과 롤백이 가능합니다.

### 미래 확장성의 확보

이번 자동화 도입은 단순한 배포 자동화를 넘어서, 향후 더 고도화된 DevOps 프랙티스 도입의 기반을 마련합니다. 예를 들어, 자동화된 테스트 실행, 성능 모니터링, 점진적 배포(Blue-Green Deployment) 등의 고급 기능들을 순차적으로 도입할 수 있는 플랫폼이 구축되는 것입니다.

이러한 확장성은 19개 Application이 지속적으로 증가하고 복잡해지는 상황에서, 팀의 기술적 역량을 지속적으로 발전시킬 수 있는 토대를 제공합니다.

- **구체적 혜택**:
    - 시간 절약: 월 0~5회 배포 대기 없음 → TAT 단축, 부재 시에도 문제없음.
    - 독립성 향상: Launcher 담당자 의존 ↓ → 자유로운 업데이트 (1-2명 담당자 효율 ↑).
    - GitHub 전환 혜택: 전사/조직 표준 Repository 사용 → 협업 용이. 원하면 직접 Runner 구축해 추가 자동화 (e.g., 테스트 워크플로우) 가능.
    - 추가 편의: nkox 메신저 알림으로 성공/실패 즉시 확인, git 버전 관리로 배포 이력 추적.
    - 전체: 19개 Application 공통 혜택 – 개발 업무(50%+) 더 효율적, 회로 설계 본업 집중.




# 2. GitHub Actions 기본 개념 이해

## CI/CD란 무엇인가? - 일상생활 속 자동화 시스템으로 이해하기

### CI/CD를 자동차 생산라인으로 이해하기

CI/CD(Continuous Integration/Continuous Deployment)를 이해하는 가장 쉬운 방법은 현대 자동차 생산라인을 생각해보는 것입니다.

#### 전통적인 수작업 방식 (기존 수동 배포)

```
부품 준비 → 수동 조립 → 수동 검사 → 수동 포장 → 수동 출하
    ↓           ↓           ↓           ↓           ↓
  작업자A      작업자B      검사자C      작업자D      작업자E
 (대기 시간)  (실수 가능)  (주관적)   (지연 가능)  (담당자 의존)
```

#### 현대적 자동화 생산라인 (CI/CD)

```
부품 투입 → 자동 조립 → 자동 검사 → 자동 포장 → 자동 출하
    ↓           ↓           ↓           ↓           ↓
  원재료만    로봇 시스템   센서 검증   자동 시스템   즉시 배송
  준비하면      자동          객관적       일관성      예측 가능
```

### CI/CD의 핵심 가치

**지속적 통합(CI)**: 여러 개발자가 작업한 코드를 지속적으로 통합하고 검증하는 과정

- 마치 여러 부품이 조립라인에서 지속적으로 결합되어 하나의 제품이 되는 것과 같음

**지속적 배포(CD)**: 검증된 코드를 자동으로 운영 환경에 배포하는 과정

- 품질 검사를 통과한 제품이 자동으로 고객에게 배송되는 것과 같음

## GitHub Actions 핵심 개념 - 4가지 기본 요소

GitHub Actions는 4가지 핵심 구성 요소로 이루어져 있습니다. 이를 건물 건설 프로젝트에 비유해서 설명해보겠습니다.
### GitHub Actions 핵심 용어 정리

- **핵심 용어** (간단히, 비유로 설명):
    
    - **Workflow**: 전체 자동화 프로세스. 비유: "회로 설계의 전체 테스트 플로우 – 시작부터 끝까지 자동."     
    - **Job**: Workflow 안의 큰 작업 단위. 비유: "테스트 플로우에서 '검증'과 '배포' 두 단계."
    - **Step**: Job 안의 세부 실행 명령. 비유: "검증 단계에서 '파일 체크'나 '스크립트 실행' 같은 세부 작업."
    - **Runner**: 작업을 실행하는 서버. 비유: "테스트 장비 자체 – 우리 팀은 signoff-runner 사용."

- **Workflow, Job, Step 관계**:
    
    - Workflow는 Job들로 구성, Job은 Step들로 구성.
    - 우리 경우: Workflow(자동 배포) → Job1(validate-checker) + Job2(update-app) → 각 Job의 Step(clone, 검증, 배포 등).


### 1. Workflow (전체 프로젝트 계획서)

```yaml
GitHub Actions Workflow:
├── 이름: "Signoff Application 자동 배포"
├── 트리거: "master 브랜치에 코드 push 시"  
├── 전체 흐름: 검증 → 배포
└── 완료: "배포 성공 알림"
```

**Workflow**는 자동화하고자 하는 전체 과정의 설계도입니다. `.github/workflows/` 폴더에 YAML 파일로 정의됩니다.

### 2. Job (각 공종별 작업)

Workflow 내에서 각각의 독립적인 작업 단위가 Job입니다.

```yaml
# 우리 Signoff 시스템의 Job 구조
Job 1: validate-checker (품질 검사팀)
└── 역할: 코드가 Launcher와 호환되는지 검증

Job 2: update-app (배포팀)  
└── 역할: 검증 통과 후 실제 배포 수행
└── 조건: validate-checker가 성공해야 실행
```

**Job의 특징**:

- 각 Job은 독립적인 실행 환경에서 동작
- 병렬 실행 가능 (단, 우리 시스템은 순차 실행)
- 다른 Job의 성공/실패에 따라 실행 여부 결정 가능

### 3. Step (세부 작업 단계)

각 Job 내에서 순차적으로 실행되는 개별 명령어들이 Step입니다.

```yaml

validate-checker Job의 Steps:
1. git clone: 최신 코드 가져오기
2. input_config.yaml 검증
3. run.sh 스크립트 검증  
4. 임시 파일 정리
```

**Step의 특징**:
- 순차적 실행 (앞 단계 실패 시 뒤 단계 중단)
- 각 Step은 명확한 목적과 결과를 가짐
- 실행 결과가 로그로 상세히 기록됨

### 4. Runner (작업을 수행하는 환경)

Runner는 실제로 Workflow를 실행하는 컴퓨터/서버 환경입니다. 건설 현장에 비유하면 작업이 이루어지는 실제 부지와 같습니다.

```yaml
signoff-runner:
├── 위치: /user/signoff.dsa/ 개발서버
├── 시설: Python 환경, Git, 배포 스크립트
├── 접근권한: signoff.dsa 그룹 권한
└── 작업환경: 검증 도구, 배포 도구 설치
```

**우리 시스템의 Runner 특징**:

- **Self-hosted Runner**: GitHub에서 제공하는 클라우드가 아닌 우리 자체 서버
- **전용 환경**: Signoff Application 전용으로 설정된 환경
- **권한 관리**: `newgrp signoff.dsa` 명령으로 필요한 권한 자동 획득

## 4가지 요소의 관계도

```mermaid
graph TD
    A[Workflow: 전체 자동화 계획] --> B[Job 1: validate-checker]
    A --> C[Job 2: update-app]
    
    B --> D[Step 1: git clone]
    B --> E[Step 2: yaml 검증]
    B --> F[Step 3: script 검증]
    B --> G[Step 4: 정리]
    
    C --> H[Step 1: deploy.sh 실행]
    
    I[Runner: signoff-runner 서버] -.-> B
    I -.-> C
    
    B -->|성공 시에만| C
```

## 실제 동작 방식 - 우리 시스템 기준

### 전체 프로세스 흐름

```
1. 개발자가 코드 수정 후 git push
          ↓
2. GitHub에서 Workflow 자동 감지
          ↓  
3. signoff-runner 서버에서 실행 시작
          ↓
4. Job 1 (validate-checker) 실행:
   - 최신 코드를 임시로 clone
   - Launcher 호환성 검증
   - 임시 파일 정리
          ↓
5. 검증 성공 시 Job 2 (update-app) 실행:
   - deploy.sh 스크립트 실행
   - 배포 경로에 최신 코드 반영
          ↓
6. 성공/실패 알림 발송 (nkox, 이메일)
```
```mermaid
sequenceDiagram
  participant Dev as 개발자
  participant GH as GitHub
  participant SR as signoff-runner
  participant DP as 배포 경로
  participant NK as nkox 알림
  Dev->>GH: Push 코드
  GH->>SR: Workflow 실행
  SR->>SR: Job1: 검증 (validate_check.py 등)
  SR->>DP: Job2: 배포 (deploy.sh)
  SR->>NK: 성공/실패 알림
  DP->>Dev: Launcher에서 즉시 사용 가능
```

![[Pasted image 20250816010428.png]]

**발표자 노트 (스크립트)**: "이제 GitHub Actions가 실제로 어떻게 동작하는지 보죠. 여러분이 코드를 Push하면, 우리 서버(signoff-runner)가 검증하고 배포합니다. 검증은 input_config.yaml과 run.sh가 Launcher와 맞는지 확인하는 과정이에요. 성공하면 바로 배포 경로에 반영되고, nkox로 알림이 옵니다. 회로 설계도를 업데이트하고 바로 생산 라인에 넘기는 것과 같죠."


**우리 사례 (Signoff)**: DSC Application 업데이트 → Push → 자동 검증 → /user/signoff.dsa/RUNSCRIPTS/에 배포 → Launcher GUI 즉시 반영.
### 타이밍과 자동화의 핵심

**트리거 조건**: master 브랜치에 push 발생 시 즉시 시작
- 개발자가 별도 명령어나 설정 불필요
- 코드 변경과 동시에 배포 프로세스 자동 시작

**병렬 vs 순차 처리**: 우리 시스템은 안정성을 위해 순차 처리
- 검증이 먼저 완료되어야 배포 진행
- 검증 실패 시 배포 단계 자동 중단


## 우리 시스템에 GitHub Actions를 도입한 핵심 이유

### 1. 표준화와 호환성

- 업계 표준 도구 사용으로 다른 팀과의 협업 용이
- 풍부한 커뮤니티 리소스와 문서 활용 가능

### 2. 학습 곡선의 완만함

- 직관적인 YAML 문법과 웹 인터페이스
- 회로 설계 전문가도 쉽게 이해할 수 있는 구조

### 3. 확장성과 유연성

- 현재는 단순 배포만 하지만, 향후 테스트 자동화, 성능 모니터링 등으로 확장 가능
- 각 팀의 필요에 따라 커스터마이징 가능

### 4. 안정성과 신뢰성

- 모든 과정이 로그로 기록되어 문제 추적 용이
- 표준화된 프로세스로 인한 일관된 결과 보장

이러한 기본 개념을 바탕으로, 다음 섹션에서는 우리 Signoff Application 시스템에 특화된 자동 배포 아키텍처를 자세히 살펴보겠습니다.


# 3. Signoff Application 자동 배포 시스템 상세

## 전체 시스템 아키텍처

우리 Signoff Application 자동 배포 시스템은 3개의 주요 구성 요소로 이루어져 있습니다:

```
┌─────────────────────────────────────────────────────────────────┐
│                     전체 시스템 아키텍처                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   개발자 환경    │    │  GitHub Actions │    │   배포 서버     │
│                 │    │   (자동화 엔진)  │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ 코드 수정   │ │    │ │validate-    │ │    │ │/user/signoff│ │
│ │input_config │ │    │ │checker      │ │    │ │.dsa/        │ │
│ │run.sh       │ ├──➤ │ │(검증 단계)  │ ├──➤ │ │RUNSCRIPTS/  │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│        │        │    │        │       │    │       ↑        │
│        v        │    │        v       │    │       │        │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │git push     │ │    │ │update-app   │ │    │ │deploy.sh    │ │
│ │master       │ │    │ │(배포 단계)  │ │    │ │실행         │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
     GitHub              signoff-runner           배포 경로
   Repository              (Self-hosted)
```

### 각 구성 요소의 역할

#### 1. 개발자 환경 (GitHub Repository)

- **19개 Signoff Application**의 소스코드 저장소
- 각 Repository는 `MDT` Organization 하위에 위치
- 개발자가 코드 수정 후 `master` 브랜치에 push 시 자동화 트리거

#### 2. GitHub Actions (자동화 엔진)

- **signoff-runner**: 우리 전용 Self-hosted Runner
- **2단계 파이프라인**: 검증 → 배포 순차 실행
- **실시간 모니터링**: 웹 인터페이스를 통한 진행 상황 추적

#### 3. 배포 서버 (운영 환경)

- **배포 경로**: `/user/signoff.dsa/RUNSCRIPTS/`
- **권한 관리**: `signoff.dsa` 그룹 기반 접근 제어
- **Signoff Launcher**: 이 경로의 코드를 참조하여 실제 서비스 제공


```mermaid
graph TD

  A[개발자 PC: 코드 수정 & Push] -->|GitHub Repository| B[GitHub Actions Workflow]

  B -->|Trigger| C[signoff-runner 서버]

  subgraph signoff-runner

    D[Job1: Validation\nvalidate_check.py 등]

    E[Job2: Deployment\ndeploy.sh 실행]

  end

  C --> D

  D -->|성공 시| E

  E --> F[배포 경로: /user/signoff.dsa/RUNSCRIPTS/]

  F --> G[Signoff Launcher: 즉시 반영]

  E -->|알림| H[nkox 메신저: 성공/실패]

  style D fill:#ffffcc,stroke:#ffd700

  style E fill:#ccffcc,stroke:#00ff00
```


- - **구성 요소**: 개발자 PC → GitHub Repository → GitHub Actions Workflow → signoff-runner (Self-hosted 서버) → 배포 경로 (/user/signoff.dsa/RUNSCRIPTS/).
- **주요 특징**: Push 트리거 → 자동 검증 → 배포. 모든 과정이 MDT Organization 내에서 안전하게 실행 (HPC망 내 GitHub Enterprise 사용).
- **비유 예시**: "회로 설계 시스템에서 입력 신호(Push)가 들어오면 자동으로 필터(검증)를 거쳐 출력(배포)으로 나가는 것과 같습니다. 중간에 로봇(signoff-runner)이 모든 작업을 처리해줍니다."

## 3단계 자동화 프로세스: Push → 검증 → 배포

```mermaid
flowchart LR

  A[ Push: master 브랜치] -->|Trigger Workflow| B[ Validation: 임시 clone & 검증 스크립트 실행]

  B -->|실패: nkox 알림| C[중단]

  B -->|성공| D[Deployment: deploy.sh로 배포 경로 업데이트]

  D -->|nkox 알림| E[Launcher 반영 완료]

  style B fill:#ffffcc,stroke:#ffd700

  style D fill:#ccffcc,stroke:#00ff00
```

- **발표자 노트 (스크립트)**: "이 시스템은 3단계로 동작합니다. Push하면 바로 검증이 시작되고, 통과 시 배포 – 실패하면 알림만 옵니다. input_config.yaml이 Launcher와 맞는지 자동 체크하니, 여러분은 그냥 Push만 하세요. 회로 검사처럼 안전하게 설계됐어요."

### Phase 0: 트리거 (Trigger)

```yaml
# 자동화 시작 조건
on:
  push:
    branches: [master]  # master 브랜치 push 시에만 실행
```

**동작 방식**:

- 개발자가 `git push origin master` 실행
- GitHub에서 즉시 Workflow 감지 및 signoff-runner에 작업 전달
- 평균 5초 이내 자동화 프로세스 시작

### Phase 1: 자동 검증 (validate-checker Job)

이 단계는 마치 제품 출하 전 품질검사와 같은 역할을 합니다.

```yaml
validate-checker:
  runs-on: signoff-runner
  steps:
    1. git clone: 최신 코드 임시 다운로드
    2. input_config.yaml 호환성 검증  
    3. run.sh 스크립트 문법 검증
    4. 임시 파일 정리
```

#### Step-by-Step 검증 과정

**Step 1: 코드 복제 (git clone)**

```bash
# 실제 실행되는 명령어
git clone https://deep.choi:${GITHUB_PAT}@cae.github.samsungds.net/MDT/${REPO_NAME} repo
```

- Personal Access Token(PAT)을 사용한 인증
- 임시 디렉토리 `repo`에 최신 코드 다운로드
- 네트워크 문제나 권한 오류 시 즉시 실패 처리

**Step 2: input_config.yaml 검증**

```bash
# Signoff Launcher 호환성 검사
/user/signoff.dsa/miniconda3/envs/launcher/bin/python validate_check.py --file input_config.yaml
```

- Launcher가 입력 필드를 올바르게 생성할 수 있는지 확인
- YAML 문법 오류, 필수 필드 누락, 데이터 타입 오류 등을 사전 감지
- 검증 실패 시 구체적인 오류 메시지 제공

**Step 3: run.sh 스크립트 검증**

```bash
# 실행 스크립트 호환성 검사
/user/signoff.dsa/miniconda3/envs/launcher/bin/python validate_check_for_run.py --file input_config.yaml --run run.sh
```

- 스크립트 실행 권한, 경로 설정, 환경변수 등 확인
- Launcher 실행 환경과의 호환성 검증
- 잠재적 실행 오류 사전 방지

**Step 4: 정리 작업**

```bash
# 보안과 공간 관리를 위한 임시 파일 삭제
rm -rf repo
```

- 임시로 다운받은 코드 완전 삭제
- 서버 저장 공간 관리 및 보안 유지

### Phase 2: 자동 배포 (update-app Job)

검증이 성공적으로 완료된 경우에만 실행되는 배포 단계입니다.

```yaml
update-app:
  runs-on: signoff-runner  
  needs: validate-checker  # 검증 성공 시에만 실행
  steps:
    1. deploy.sh 스크립트 실행
    2. 배포 완료 알림
```

#### 핵심 배포 로직: deploy.sh 스크립트

```bash
#!/bin/bash
# 우리 시스템의 핵심 배포 스크립트

APP_NAME="$1"  # GitHub Repository 이름 자동 전달
DEPLOY_BASE="/user/signoff.dsa/RUNSCRIPTS"

# 1. 입력 검증
if [ -z "$APP_NAME" ]; then
    echo "Usage: $0 <signoff-app-name>"
    exit 1
fi

# 2. 배포 경로 확인
APP_PATH="$DEPLOY_BASE/$APP_NAME"
if [ ! -d "$APP_PATH/.git" ]; then
    echo "Error: $APP_PATH is not a valid git repository."
    exit 1
fi

# 3. 권한 획득 및 배포 실행
cd "$APP_PATH" || exit 1
newgrp signoff.dsa <<EONG
echo "Deploying $APP_NAME..."
git reset --hard    # 로컬 변경사항 완전 초기화
git clean -fd       # 추적되지 않는 파일 정리  
git pull           # 최신 코드 동기화
EONG

echo "Deployment of $APP_NAME completed."
```

**배포 과정의 핵심 특징**:

- **원자적 배포**: 모든 과정이 성공하거나 모두 실패 (중간 상태 없음)
- **안전한 초기화**: `git reset --hard`로 일관된 상태 보장
- **권한 자동 관리**: `newgrp signoff.dsa`로 필요한 권한 자동 획득

## signoff-runner 환경과 권한 관리

- **signoff-runner 개요**:
    - Self-hosted runner: MDT Organization에 등록, Runner Group으로 19개 Repository 연동.
    - 실행 환경: 내 개발 서버 (ID: deep.choi / Linux ID: deepwonwoo)에서 동작.
    - 접근: /user/signoff.dsa/ 경로 읽기/쓰기 가능, newgrp signoff.dsa 자동 실행 확인됨.
    - 비유: "전용 테스트 벤치: 우리 팀만 쓰는 자동화 서버 – 외부 접근 불가로 보안 안전."
- **권한 관리**:
    - newgrp signoff.dsa: 배포 시 자동 호출 → 읽기/쓰기/실행 권한 획득 (signoff 멤버만 가능).
    - 보안: HPC망 내, PAT 인증으로 ID/PW 대신 사용.
    - 비유: "회로 보안 게이트: 올바른 키(권한)로만 접근 허용."
### Self-hosted Runner의 구성


```
signoff-runner 서버 환경:
├── 위치: deep.choi 개발서버 (/user/signoff.dsa/)
├── 운영체제: Linux (HPC망 내부)
├── 권한: signoff.dsa 그룹 멤버십
├── 네트워크: 사내 GitHub Enterprise 접근 가능
└── 소프트웨어:
    ├── Git
    ├── Python (miniconda3/envs/launcher)
    ├── 검증 스크립트 (validate_check.py)
    └── 배포 스크립트 (deploy.sh)
```

### 권한 관리 체계

#### signoff.dsa 그룹 기반 보안

```bash
# 권한 확인 명령어
groups $USER | grep signoff.dsa

# 권한 전환 (자동화에서 사용)
newgrp signoff.dsa
```

**보안 특징**:

- **최소 권한 원칙**: Signoff 관련 경로에만 접근 가능
- **그룹 기반 관리**: 개별 사용자가 아닌 그룹 단위 권한 부여
- **자동 권한 전환**: 스크립트 내에서 필요시에만 권한 상승

#### MDT Organization 연동

```
GitHub Enterprise 구조:
└── MDT Organization
    ├── signoff-runner (Runner Group)
    │   └── 모든 Signoff Repository와 연동
    ├── signoff-dsc/
    ├── signoff-app2/
    ├── signoff-app3/
    └── ... (19개 Repository)
```

## 배포 경로 구조와 관리 체계

### 실제 배포 디렉토리 구조

```
/user/signoff.dsa/RUNSCRIPTS/
├── deploy.sh                    # 공용 배포 스크립트 (모든 앱 공통)
├── signoff-dsc/                 # DSC Application
│   ├── .git/                    # Git 메타데이터
│   ├── input_config.yaml        # Launcher 인터페이스 설정
│   ├── run.sh                   # 실행 스크립트
│   ├── validate_check.py        # 검증 스크립트 (공통)
│   ├── validate_check_for_run.py # 실행 검증 스크립트 (공통)
│   └── [기타 Application 파일들]
├── signoff-timinganalysis/      # Timing Analysis Application  
│   ├── .git/
│   ├── input_config.yaml
│   ├── run.sh
│   └── [Application 특화 파일들]
└── signoff-poweranalysis/       # Power Analysis Application
    ├── .git/
    ├── input_config.yaml  
    ├── run.sh
    └── [Application 특화 파일들]
```

### Signoff Launcher와의 연동 방식

#### signoff_applications.yaml 설정

```yaml
# Launcher 메인 설정 파일
applications:
  signoff-dsc:
    path: "/user/signoff.dsa/RUNSCRIPTS/signoff-dsc"
    config: "input_config.yaml"
    
  signoff-timinganalysis:  
    path: "/user/signoff.dsa/RUNSCRIPTS/signoff-timinganalysis"
    config: "input_config.yaml"
```

#### 런타임 동작 과정

```
1. Launcher 시작 시:
   └── signoff_applications.yaml 읽기
   └── 각 Application의 input_config.yaml 파싱
   └── 동적으로 입력 인터페이스 생성

2. 사용자가 Signoff 실행 시:
   └── 해당 Application RUNSCRIPT 폴더 전체 복사
   └── 사용자 입력값으로 환경변수 설정
   └── run.sh 실행
```

## 실제 배포 경로와 deploy.sh 스크립트 동작 원리

- **배포 경로 구조**:
    - /user/signoff.dsa/RUNSCRIPTS/:
        - deploy.sh (공용 스크립트)
        - signoff-dsc/ (개별 Application Repository clone)
        - signoff-app2/ 등 (총 19개).
    - 동작: Push 시 해당 Application 폴더에 git pull.
- **deploy.sh 원리**:
    - 입력: 앱 이름 (e.g., signoff-dsc).
    - 과정: cd to 경로 → newgrp signoff.dsa → git reset/clean/pull.
    - 비유: "회로 업데이트: 새 설계도를 자동으로 기존 보드에 교체."
- **발표자 노트 (스크립트)**: "배포 경로는 기존과 같아요 – deploy.sh가 git pull을 자동으로 합니다. 여러분 Application 폴더에 바로 반영되니, Launcher가 즉시 사용 가능합니다."


## 혁신적 아이디어: 앱 이름 자동 추출 메커니즘

### 문제 상황

19개의 서로 다른 Signoff Application마다 각각 다른 Workflow 설정을 유지해야 한다면, 관리 복잡도가 기하급수적으로 증가합니다.

### 해결책: 환경변수 기반 자동 식별

#### GitHub 기본 환경변수 활용

```yaml
# GitHub에서 자동 제공하는 환경변수
$GITHUB_REPOSITORY = "MDT/signoff-dsc"

# bash 명령어로 Repository 이름만 추출  
REPO_NAME=$(basename "$GITHUB_REPOSITORY")
# 결과: "signoff-dsc"
```

#### 완전 공통화 달성

```yaml
# 모든 Repository에 동일하게 사용 가능한 설정
env:
  REPO_NAME: $(basename "$GITHUB_REPOSITORY")

jobs:
  update-app:
    steps:
      - name: Deploy this Signoff Application
        run: |
          /user/signoff.dsa/RUNSCRIPTS/deploy.sh "${{ env.REPO_NAME }}"
```
## 앱 이름 자동 추출 메커니즘의 핵심 아이디어

- **메커니즘**:
    - GITHUB_REPOSITORY 환경 변수 사용: "owner/repo" → basename으로 "repo" (e.g., signoff-dsc) 추출.
    - 장점: YAML 공통화 (19개 Repository 동일 파일 사용), 오타 방지, 신규 앱 추가 시 수정 불필요.
    - 비유: "자동 라벨링: 코드가 들어오면 이름표를 스스로 붙여 배포 장소로 가는 것."
### 핵심 이점

#### 1. 완전한 설정 표준화

```
기존 방식 (문제):
├── signoff-dsc: deploy.sh "signoff-dsc"
├── signoff-app2: deploy.sh "signoff-app2"  
└── signoff-app3: deploy.sh "signoff-app3"
   (19개 Repository × 각각 다른 설정)

새로운 방식 (해결):
├── 모든 Repository: deploy.sh "${{ env.REPO_NAME }}"
└── GitHub에서 자동으로 올바른 이름 추출
   (19개 Repository × 동일한 설정)
```

#### 2. 신규 Application 추가 시 제로 설정

```bash
# 새로운 Signoff Application 추가 과정
1. GitHub에서 새 Repository 생성 (예: signoff-newapp)
2. 배포 경로에 동일한 이름으로 clone
   └── git clone [repo-url] /user/signoff.dsa/RUNSCRIPTS/signoff-newapp
3. 표준 Workflow 파일 복사
   └── 기존 19개와 동일한 auto-deploy.yaml 사용
4. 즉시 자동 배포 시스템 동작!
```

#### 3. 휴먼 에러 완전 제거

- **오타 방지**: 수동으로 앱 이름을 입력할 필요 없음
- **일관성 보장**: 모든 Repository에서 동일한 메커니즘 동작
- **유지보수성**: 설정 변경 시 한 곳만 수정하면 모든 앱에 적용

## 시스템의 확장성과 미래 계획

### 현재 시스템의 확장 포인트

#### 검증 단계 확장 가능성

```yaml
# 현재: 기본 호환성 검증
validate-checker:
  steps:
    - input_config.yaml 검증
    - run.sh 스크립트 검증

# 미래: 고도화된 검증  
validate-checker:
  steps:
    - 기본 호환성 검증
    - 단위 테스트 실행      # 추가 가능
    - 성능 벤치마크         # 추가 가능
    - 보안 스캔             # 추가 가능
    - 문서 생성             # 추가 가능
```

#### 배포 단계 고도화 가능성

```yaml
# 현재: 단순 배포
update-app:
  steps:
    - deploy.sh 실행

# 미래: 스마트 배포
update-app:
  steps:
    - 점진적 배포 (Canary Deployment)
    - 실시간 헬스체크
    - 자동 롤백 (배포 실패 시)
    - 사용자 알림 (nkox, 이메일)
```

이러한 아키텍처를 통해 우리는 19개 Signoff Application의 완전 자동화된 배포 시스템을 구축했으며, 향후 더 많은 Application이 추가되어도 확장 가능한 기반을 마련했습니다.




# 4. 개발자 실무 가이드 - Step by Step

- **단계별 가이드**:
    
    1. **GitHub 계정 확인**:
        
        - 사내 GitHub Enterprise (HPC망 내) 사용, MDT Organization 소속 확인.
            
        - 계정: 사내 ID (예: deep.choi), 비밀번호 대신 PAT(Personal Access Token) 설정.
            
        - 비유: "회로 테스트 장비에 접속하려면 ID 카드(PAT)가 필요합니다."
            
    2. **Repository 접근**:
        
        - Repository 이름: signoff-<app_name> (예: signoff-dsc).
            
        - 권한: signoff 멤버로 등록 (조직 관리자가 이미 설정 완료).
            
        - 확인 명령어: git remote -v (원격 Repository URL 확인, 예: https://github..com/MDT/signoff-dsc.git).
            
    3. **PAT 발급 및 설정**:
        
        - GitHub 웹 → Settings → Developer settings → Personal access tokens → Generate new token.
            
        - 권한 선택: repo (full control), workflow (Actions 실행).
            
        - 로컬 설정: git config --global credential.helper store, Push 시 PAT 입력.
            
        - 비유: "PAT는 보안 키 – 이걸로 Repository 문을 엽니다."

```mermaid
flowchart TD

  A[개발자: 사내 ID 확인] --> B[PAT 발급: GitHub 웹]

  B --> C[Repository 접근: signoff-app_name]

  C --> D[로컬 설정: git config & PAT 저장]

  style B fill:#e6f3ff,stroke:#0000ff

  style C fill:#ccffcc,stroke:#00ff00
```

**발표자 노트 (스크립트)**: "먼저, GitHub Repository에 접속하는 법을 보죠. 여러분은 이미 signoff-dsc 같은 Repository에 접근 권한이 있어요. 사내 ID로 로그인하고, PAT라는 보안 키를 발급받아야 합니다. 회로 테스트 장비에 ID 카드로 접속하는 것과 비슷하죠. 터미널에서 git remote -v로 확인하면 준비 끝입니다!"


## 사전 준비사항

### 1. 권한 확인 및 설정

#### Signoff 그룹 멤버십 확인

먼저 본인이 signoff.dsa 그룹에 속해있는지 확인해야 합니다.

```bash
# 터미널에서 실행
groups $USER | grep signoff.dsa

# 결과 예시 (정상):
# your_username : users signoff.dsa other_groups

# 결과 예시 (문제):  
# your_username : users other_groups
# (signoff.dsa가 없으면 관리자에게 문의)
```

#### newgrp 명령어 테스트

```bash
# signoff.dsa 그룹 권한 전환 테스트
newgrp signoff.dsa

# 성공하면 프롬프트가 바뀌고 새로운 쉘이 시작됨
# exit 명령어로 원래 쉘로 복귀 가능
exit
```

**⚠️ 문제 해결**: 위 명령어가 실패하면 Signoff Launcher 담당자(deep.choi)에게 연락하여 권한 요청

### 2. Personal Access Token (PAT) 발급

사내 GitHub Enterprise는 ID/Password 로그인이 안되고 PAT를 통해서만 인증이 가능합니다.

#### PAT 발급 과정

```
1. 사내 GitHub (cae.github.samsungds.net) 로그인
2. 우측 상단 프로필 클릭 → Settings
3. 좌측 메뉴에서 "Developer settings" 클릭  
4. "Personal access tokens" → "Tokens (classic)" 클릭
5. "Generate new token" → "Generate new token (classic)" 선택
6. 설정값:
   - Note: "Signoff Application Development"
   - Expiration: 1 year (또는 원하는 기간)
   - Scopes: repo (전체 체크)
7. "Generate token" 클릭
8. 🔴 중요: 생성된 토큰을 즉시 복사하여 안전한 곳에 저장
   (페이지를 벗어나면 다시 볼 수 없음)
```

#### Git 설정에 PAT 적용

```bash
# Git에 PAT 저장 (한 번만 설정하면 됨)
git config --global credential.helper store

# 처음 git clone이나 push 시 다음과 같이 입력:
# Username: your_github_username
# Password: 발급받은_PAT_토큰 (실제 비밀번호 아님)
```

### 3. Repository 구조 확인

자신의 Signoff Application Repository가 다음 구조를 가지고 있는지 확인하세요:

```
your-signoff-app/
├── .github/                     # 이 폴더를 새로 만들어야 함
│   └── workflows/               # 이 폴더를 새로 만들어야 함  
│       └── auto-deploy.yaml     # 이 파일을 새로 추가해야 함
├── input_config.yaml            # 기존 파일 (필수)
├── run.sh                       # 기존 파일 (필수)
├── validate_check.py            # 기존 파일 (필수)
├── validate_check_for_run.py    # 기존 파일 (필수)
└── [기타 Application 파일들]    # 기존 파일들
```

## 최초 설정: GitHub Actions Workflow 추가 (생애 1회)


## 코드 수정 및 Push: Git 기본 명령어

- **목표**: 기존 Git 워크플로우를 활용해 코드를 수정하고 Push합니다.
    
- **단계별 가이드**:
    
    1. **로컬 Repository 업데이트**:
        
        - 명령어: git clone https://github.{}.com/MDT/signoff-{app_name}.git (최초 1회).
        - 기존 클론한 경우: git pull로 최신 상태 유지.
        - 비유: "회로 설계도를 최신 버전으로 다운로드."
    2. **코드 수정**:
        - 수정 대상: input_config.yaml (GUI 입력 필드 정의), run.sh (실행 스크립트).
        - 주의: YAML 형식 준수, run.sh 실행 가능 확인 (chmod +x run.sh).

- **커밋 및 Push**:
    
    - 명령어:
        
        ```bash
        git add .
        git commit -m "Update input_config.yaml for new feature"
        git push origin master
        ```
        
    - 비유: "설계도를 수정한 뒤 중앙 저장소에 업로드."

```mermaid
flowchart LR

  A[로컬: 코드 수정\ninput_config.yaml, run.sh] --> B[git add & commit]

  B --> C[git push origin master]

  C --> D[GitHub Repository: signoff-app]

  style A fill:#ffffcc,stroke:#ffd700

  style C fill:#ccffcc,stroke:#00ff00
```

**발표자 노트 (스크립트)**: "여러분이 이미 익숙한 Git 명령어로 시작합니다. Repository를 클론하고, input_config.yaml이나 run.sh를 수정한 뒤, 커밋하고 Push하세요. 회로 설계도를 업데이트해서 중앙 저장소에 보내는 것과 같아요. 이 Push가 자동 배포를 시작합니다!"
### Step 4: 자동화 동작 확인

푸시 후 즉시 GitHub 웹사이트에서 확인해보세요:

```
1. 브라우저에서 본인 Repository 이동
2. "Actions" 탭 클릭
3. "[SOL] Auto-Deploy Signoff Application" Workflow 실행 확인
4. 녹색 체크마크(✅) 또는 빨간 X(❌) 확인
```

## Workflow 실행 확인: nkox 알림과 로그 점검

- **목표**: Push 후 Workflow 실행 상태를 확인하고 결과를 점검합니다.
    
- **단계별 가이드**:
    
    1. **nkox 알림 확인**:
        
        - Push 후 1-2분 내 nkox 메신저로 성공/실패 알림 수신.
            
        - 성공: "Workflow completed for signoff-dsc", 배포 경로 반영 완료.
            
        - 실패: 에러 메시지 (예: "validate_check.py failed: invalid YAML").
            
        - 비유: "테스트 장비가 검사 결과를 문자로 보내주는 것."
            
    2. **GitHub Actions 로그 확인**:
        
        - GitHub 웹 → Repository → Actions 탭 → 최신 Workflow Run 클릭.
            
        - Job 세부사항: validate-checker (검증), update-app (배포) 로그 확인.
            
        - 실패 시: 에러 원인 (YAML 형식 오류 등) 확인 후 수정.
            
    3. **배포 경로 확인** (선택):
        
        - SSH로 서버 접속 → ls /user/signoff.dsa/RUNSCRIPTS/signoff-<app_name>/ 확인.
            
        - 비유: "생산 라인에서 최신 설계도가 적용됐는지 확인."

## 배포 상태 모니터링 및 확인

### GitHub 웹 인터페이스에서 확인

#### 실행 상태 확인 경로

```
1. GitHub Repository 메인 페이지 이동
2. 상단 탭에서 "Actions" 클릭
3. 최신 Workflow run 클릭
4. 실행 상태 및 진행도 확인
```

#### 상태별 의미

**🔄 노란색 (In Progress)**

```
⚪ validate-checker (실행 중)
⚪ update-app (대기 중)

현재 검증 단계가 진행 중입니다.
보통 1-2분 소요됩니다.
```

**✅ 녹색 (Success)**

```
✅ validate-checker (완료)
✅ update-app (완료)

배포가 성공적으로 완료되었습니다!
Signoff Launcher에서 최신 코드를 사용할 수 있습니다.
```

**❌ 빨간색 (Failed)**

```
❌ validate-checker (실패)
⚪ update-app (실행되지 않음)

검증 단계에서 문제가 발견되었습니다.
배포가 중단되었으므로 문제를 해결 후 다시 푸시하세요.
```

### 상세 로그 확인 방법

#### 성공적인 배포 로그 예시

```
✅ validate-checker
  ✅ git clone repository code (12s)
      Cloning into 'repo'...
      remote: Counting objects: 47, done.
      
  ✅ Check Validation of input_config.yaml (8s)
      Validation passed: input_config.yaml is compatible
      
  ✅ Check Validation of run.sh (5s)  
      Validation passed: run.sh is executable and compatible
      
  ✅ Remove Repo (2s)
      Deleting repo directory...
      Cleanup completed

✅ update-app
  ✅ Deploy this Signoff Application (15s)
      Deploying signoff-dsc...
      git reset --hard
      git clean -fd  
      git pull
      Already up to date.
      Deployment of signoff-dsc completed.
```

#### 실패 시 로그 예시

```
❌ validate-checker
  ✅ git clone repository code (12s)
  ❌ Check Validation of input_config.yaml (3s)
      Error: Missing required field 'name' in input_config.yaml
      Line 15: category field has invalid value
      Validation failed
      
⚪ update-app (실행되지 않음)
```

### 알림 시스템

#### 성공 알림 (nkox 메신저)

```
🎉 [Signoff] 배포 성공
Application: signoff-dsc
Commit: "Update input configuration for new parameter"  
배포 시간: 2분 35초
상태: ✅ 성공
```

#### 실패 알림 (이메일)

```
제목: [Signoff] 배포 실패 - signoff-dsc
내용:
안녕하세요,

signoff-dsc Application의 자동 배포가 실패했습니다.

실패 단계: validate-checker
실패 원인: input_config.yaml 검증 실패
자세한 로그: [GitHub Actions 링크]

문제 해결 후 다시 푸시해주세요.
```


```mermaid
sequenceDiagram

  participant Dev as 개발자

  participant GH as GitHub Actions

  participant NK as nkox 알림

  participant SR as 배포 경로

  Dev->>GH: git push

  GH->>NK: Workflow 시작 알림

  GH->>SR: 검증 & 배포

  SR->>NK: 성공/실패 알림

  Dev->>GH: 로그 확인

  Dev->>SR: 배포확인
```


**발표자 노트 (스크립트)**: "여러분이 이미 익숙한 Git 명령어로 시작합니다. Repository를 클론하고, input_config.yaml이나 run.sh를 수정한 뒤, 커밋하고 Push하세요. 회로 설계도를 업데이트해서 중앙 저장소에 보내는 것과 같아요. 이 Push가 자동 배포를 시작합니다!"





# 5. GitHub Actions 고급 기능 및 미래 확장성

## 현재를 넘어서: 더 스마트한 자동화를 위한 고급 기능들

현재 우리가 구현한 시스템은 기본적인 push 기반 배포 자동화입니다. 하지만 GitHub Actions는 훨씬 더 정교하고 강력한 기능들을 제공합니다. 이번 섹션에서는 향후 Signoff AI Agent 개발과 고도화된 워크플로우 구축에 활용할 수 있는 고급 기능들을 살펴보겠습니다.

## 고급 트리거 (Trigger) 옵션들

### 1. 파일/경로 기반 조건부 트리거

현재는 master 브랜치의 모든 변경사항에 대해 배포가 실행되지만, 특정 파일이나 폴더의 변경에만 반응하도록 할 수 있습니다.

```yaml
# 현재 우리 시스템 (모든 변경사항에 반응)
on:
  push:
    branches: [master]

# 고급 옵션 1: 특정 파일 변경 시에만 실행
on:
  push:
    branches: [master]
    paths:
      - 'input_config.yaml'      # 설정 파일 변경 시에만
      - 'run.sh'                 # 실행 스크립트 변경 시에만
      - 'src/**'                 # src 폴더 내 모든 파일

# 고급 옵션 2: 특정 파일 제외
on:
  push:
    branches: [master]
    paths-ignore:
      - 'docs/**'                # 문서 변경은 무시
      - '*.md'                   # 마크다운 파일 무시
      - '.gitignore'             # 설정 파일 무시
```

- - 기본 트리거: on: push는 모든 Push에 Workflow 실행.
        
    - 고급 트리거: paths 또는 paths-ignore로 특정 파일/폴더 변경 시에만 Workflow 실행.
        
    - 예: input_config.yaml 또는 run.sh 변경 시만 배포 실행.
        
    - 용도: 불필요한 Workflow 실행 감소 → signoff-runner 자원 절약.

- **Signoff AI Agent 연계 가능성**:
    
    - AI Agent가 특정 파일(예: AI 모델 설정 YAML)을 업데이트 시 트리거 설정 가능.
        
    - 예: AI Agent가 새로운 검증 룰 생성 → ai_rules.yaml 변경 → Workflow로 자동 테스트/배포.
    
```mermaid
flowchart LR

  A[Push: input_config.yaml 변경] -->|paths 필터| B[Workflow 실행]

  A2[Push: 다른 파일 변경] -->|paths 제외| C[Workflow 실행 안 함]

  B --> D[signoff-runner: 검증 & 배포]

  style B fill:#ccffcc,stroke:#00ff00

  style C fill:#ffcccc,stroke:#ff0000
```

**발표자 노트 (스크립트)**: "GitHub Actions는 Push 전부를 실행하지 않고, 특정 파일만 감지할 수 있어요. 예를 들어, input_config.yaml이나 run.sh만 변경될 때 배포를 시작합니다. 회로 설계에서 특정 부품만 테스트하듯, 자원을 아끼죠. 나중에 AI Agent가 설정 파일을 업데이트하면 이런 식으로 연동할 수 있습니다."



**Signoff AI Agent 활용 예시**:


```yaml
# AI 모델 업데이트 시에만 재훈련 워크플로우 실행
on:
  push:
    paths:
      - 'ai_models/**'
      - 'training_data/**'
      - 'model_config.yaml'
```

### 2. 일정 기반 자동 실행 (Cron Schedule)

```yaml
# 매일 오전 9시에 자동 실행 (정기 검증)
on:
  schedule:
    - cron: '0 9 * * *'         # 매일 09:00 UTC
    - cron: '0 21 * * 1-5'      # 평일 오후 9시

# 주말마다 전체 시스템 검증
on:
  schedule:
    - cron: '0 10 * * 6'        # 토요일 오전 10시
```

**Signoff AI Agent 활용 예시**:

```yaml
# 매주 월요일 오전에 AI 모델 성능 평가 및 리포트 생성
on:
  schedule:
    - cron: '0 9 * * 1'         # 매주 월요일 09:00
```

### 3. 이벤트 기반 트리거

```yaml
# 이슈나 PR 생성 시 자동 검증
on:
  issues:
    types: [opened, edited]
  pull_request:
    types: [opened, synchronize]
  
# 릴리스 태그 생성 시 배포
on:
  push:
    tags:
      - 'v*'                    # v1.0, v2.1 등의 태그

# 외부 Repository 이벤트 감지
on:
  repository_dispatch:
    types: [design-updated]     # 설계 변경 알림
```

**Signoff AI Agent 활용 예시**:

```yaml
# Design Portal에서 새로운 설계 데이터 업로드 시 AI 분석 시작
on:
  repository_dispatch:
    types: [new-design-data, design-rule-updated]
```

## 내장 함수와 환경변수 활용

### 1. GitHub Context 변수들

```yaml
# 현재 사용 중인 기본 변수
${{ github.repository }}        # "MDT/signoff-dsc"
${{ github.ref }}              # "refs/heads/master"
${{ github.sha }}              # 커밋 해시
${{ github.actor }}            # 푸시한 사용자

# 유용한 추가 변수들
${{ github.event.head_commit.message }}  # 커밋 메시지
${{ github.event.head_commit.author }}   # 커밋 작성자
${{ github.run_number }}                 # 실행 번호 (자동 증가)
${{ github.run_id }}                     # 고유 실행 ID
${{ github.workspace }}                  # 작업 디렉토리 경로
${{ github.token }}                      # 자동 생성 토큰
```

**활용 예시**:

```yaml
# 커밋 메시지에 따른 조건부 실행
steps:
  - name: Check if hotfix
    if: contains(github.event.head_commit.message, '[HOTFIX]')
    run: echo "Emergency deployment triggered"
    
  - name: Normal deployment  
    if: "!contains(github.event.head_commit.message, '[HOTFIX]')"
    run: echo "Standard deployment process"
```

### 2. 강력한 내장 Actions들

#### actions/checkout - 코드 다운로드

```yaml
# 현재 우리는 수동으로 git clone 사용
- name: "git clone repository code"
  run: git clone https://...

# 개선된 방법: actions/checkout 사용
- name: "Checkout repository"
  uses: actions/checkout@v4
  with:
    fetch-depth: 0           # 전체 히스토리
    token: ${{ secrets.GITHUB_TOKEN }}
    path: custom-directory   # 사용자 정의 경로
```

#### actions/cache - 의존성 캐싱

```yaml
# Python 환경 캐싱으로 실행 시간 단축
- name: Cache Python dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

#### actions/upload-artifact - 결과 파일 저장

```yaml
# 검증 결과나 로그 파일 저장
- name: Upload validation results
  uses: actions/upload-artifact@v3
  with:
    name: validation-report-${{ github.run_number }}
    path: |
      validation_results.json
      error_logs.txt
    retention-days: 30
```


## 환경 변수 활용 및 관리

- **주요 환경 변수**:
    
    - **GITHUB_REPOSITORY**: Repository 이름 (예: MDT/signoff-dsc) → 앱 이름 추출 (basename $GITHUB_REPOSITORY).
        
    - **GITHUB_SHA**: 커밋 해시 → 배포 로그 추적.
        
    - **Secrets**: PAT, nkox API 키 등 보안 정보 저장.
        
        - 설정: GitHub 웹 → Repository → Settings → Secrets and variables → Actions.
            
        - 예: env: PAT: ${{ secrets.PAT }}.
            
- **Signoff AI Agent 연계 가능성**:
    
    - AI Agent용 환경 변수: 모델 경로, API 키 등을 Secrets로 저장 → 안전한 실행.
        
    - 예: MODEL_PATH=/ai/models/signoff-ai로 AI 모델 실행 환경 설정.
- **구현 예시** (Workflow YAML snippet):
    
    ```yaml
    jobs:
      update-app:
        runs-on: signoff-runner
        env:
          APP_NAME: ${{ github.repository_owner }}/signoff-dsc
          NKOX_TOKEN: ${{ secrets.NKOX_TOKEN }}
        steps:
          - run: ./deploy.sh $APP_NAME
    ```
```mermaid
graph TD

  A[GitHub Repository] -->|GITHUB_REPOSITORY| B[Workflow: APP_NAME 추출]

  A -->|Secrets| C[NKOX_TOKEN 사용]

  B --> D[deploy.sh: 앱 이름 전달]

  C --> E[nkox 알림 전송]

  style B fill:#e6f3ff,stroke:#0000ff

  style C fill:#e6f3ff,stroke:#0000ff
```


## 주요 GitHub Actions 함수 및 액션 활용

- **핵심 액션**:
    
    - **actions/checkout@v3**: Repository 코드를 Runner에 클론. 모든 Workflow의 첫 Step.
        - 예: uses: actions/checkout@v3.
        - 비유: "회로 설계도를 작업대에 올리는 첫 단계."
            
    - **actions/setup-python@v4**: Python 환경 설정 (validate_check.py 등 실행).
        - 예: uses: actions/setup-python@v4 with: python-version: '3.8'.
            
    - **Community Actions**: Marketplace에서 제공 (예: nkox 알림 전송 액션).
        - 예: uses: Ilshidur/action-slack@master (nkox 대신 Slack 예시).
            
- **Signoff AI Agent 연계 가능성**:
    
    - AI Agent 실행 스크립트 호출: actions/setup-python으로 환경 설정 후 AI 모델 실행.
        
    - 예: AI 기반 코드 검증 스크립트(예: linting, ML 모델 점검)를 Workflow에 추가.
        
    - 비유: "AI Agent는 회로 분석기 – 자동으로 설계 오류를 찾아주는 도구."
        
- **구현 예시** (Workflow YAML snippet):
    
    ```yaml
    jobs:
      validate-checker:
        runs-on: signoff-runner
        steps:
          - uses: actions/checkout@v3
          - uses: actions/setup-python@v4
            with:
              python-version: '3.8'
          - run: python validate_check.py
    ```
    
- **발표자 노트 (스크립트)**: "GitHub Actions는 레고 블록처럼 조립 가능한 액션을 제공합니다. checkout은 코드를 가져오고, setup-python은 Python 환경을 준비해요. AI Agent를 쓰려면 이런 액션으로 AI 스크립트를 실행할 수 있습니다. 회로 설계도를 분석기로 점검하는 것처럼요."




## Job과 Step의 고급 문법

### 1. 조건부 실행 (Conditional Execution)

```yaml
jobs:
  validate-checker:
    runs-on: signoff-runner
    steps:
      - name: "Always run validation"
        run: echo "Running validation..."
        
      - name: "Run only on hotfix"
        if: contains(github.event.head_commit.message, '[HOTFIX]')
        run: echo "Emergency validation protocol"
        
      - name: "Skip on documentation changes"
        if: "!contains(github.event.head_commit.message, '[DOCS]')"
        run: echo "Skipping validation for docs"
        
      - name: "Run on working hours only"
        if: github.event_name == 'schedule'
        run: echo "Scheduled validation"
```

### 2. 매트릭스 빌드 (Matrix Strategy)

```yaml
# 여러 환경에서 동시 테스트
jobs:
  test-multiple-environments:
    runs-on: signoff-runner
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]
        test-suite: [unit, integration, performance]
        
    steps:
      - name: Test with Python ${{ matrix.python-version }}
        run: |
          echo "Testing ${{ matrix.test-suite }} with Python ${{ matrix.python-version }}"
          # 실제 테스트 명령어
```

**Signoff AI Agent 활용 예시**:

```yaml
# 다양한 AI 모델로 동시 검증
strategy:
  matrix:
    model: [bert-base, roberta-large, custom-signoff-model]
    dataset: [hbm4e, v12, legacy]
```

### 3. 병렬 및 순차 Job 제어

```yaml
jobs:
  # 병렬 실행되는 검증 작업들
  syntax-check:
    runs-on: signoff-runner
    steps: [...]
    
  security-scan:
    runs-on: signoff-runner  
    steps: [...]
    
  performance-test:
    runs-on: signoff-runner
    steps: [...]
    
  # 모든 검증이 완료된 후 배포
  deploy:
    needs: [syntax-check, security-scan, performance-test]
    runs-on: signoff-runner
    steps: [...]
    
  # 배포 후 알림
  notify:
    needs: deploy
    if: always()  # 배포 성공/실패 관계없이 실행
    runs-on: signoff-runner
    steps: [...]
```

### 4. 출력 변수와 Job 간 데이터 전달

```yaml
jobs:
  analyze:
    runs-on: signoff-runner
    outputs:
      validation-score: ${{ steps.validate.outputs.score }}
      risk-level: ${{ steps.validate.outputs.risk }}
    steps:
      - name: Analyze code quality
        id: validate
        run: |
          score=$(python analyze_quality.py)
          risk=$(python assess_risk.py)
          echo "score=$score" >> $GITHUB_OUTPUT
          echo "risk=$risk" >> $GITHUB_OUTPUT
          
  deploy:
    needs: analyze
    if: needs.analyze.outputs.validation-score > 80
    runs-on: signoff-runner
    steps:
      - name: Deploy with score ${{ needs.analyze.outputs.validation-score }}
        run: echo "Deploying high-quality code"
```

## Workflow 관리 고급 기법

### 1. 재사용 가능한 Workflow

```yaml
# .github/workflows/reusable-validation.yml
name: Reusable Validation Workflow
on:
  workflow_call:
    inputs:
      app-name:
        required: true
        type: string
      python-version:
        required: false
        type: string
        default: '3.9'
    outputs:
      validation-result:
        value: ${{ jobs.validate.outputs.result }}

jobs:
  validate:
    runs-on: signoff-runner
    outputs:
      result: ${{ steps.validate.outputs.result }}
    steps:
      - name: Validate ${{ inputs.app-name }}
        id: validate
        run: |
          # 재사용 가능한 검증 로직
          python validate.py --app ${{ inputs.app-name }}
```

```yaml
# 다른 워크플로우에서 재사용
name: Main Deployment
on: [push]
jobs:
  call-validation:
    uses: ./.github/workflows/reusable-validation.yml
    with:
      app-name: signoff-dsc
      python-version: '3.10'
```

### 2. 환경별 설정 관리

```yaml
# 환경별 시크릿과 변수 활용
jobs:
  deploy:
    runs-on: signoff-runner
    environment: ${{ github.ref == 'refs/heads/master' && 'production' || 'development' }}
    steps:
      - name: Deploy to environment
        run: |
          echo "Deploying to ${{ environment }}"
          echo "Using API key: ${{ secrets.API_KEY }}"
          echo "Server URL: ${{ vars.SERVER_URL }}"
```

### 3. 워크플로우 보안 강화

```yaml
jobs:
  secure-deploy:
    runs-on: signoff-runner
    permissions:
      contents: read          # 코드 읽기만 허용
      deployments: write      # 배포 권한만 허용
      id-token: write         # OIDC 토큰 발급
    steps:
      - name: Verify signatures
        run: |
          # 코드 서명 검증
          gpg --verify commit.sig
          
      - name: Audit trail
        run: |
          # 모든 배포 기록 로깅
          echo "${{ github.actor }} deployed at $(date)" >> deployment.log
```

## Signoff AI Agent를 위한 고급 워크플로우 설계

### 1. AI 기반 코드 분석 및 자동 수정

```yaml
name: AI-Powered Code Review and Auto-Fix
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  ai-code-analysis:
    runs-on: signoff-runner
    steps:
      - uses: actions/checkout@v4
      
      - name: AI Code Quality Analysis
        id: ai-analysis
        run: |
          # AI 모델로 코드 품질 분석
          python ai_code_analyzer.py \
            --input-path . \
            --model signoff-code-quality-v2 \
            --output analysis-result.json
            
      - name: Generate Improvement Suggestions
        if: steps.ai-analysis.outputs.score < 85
        run: |
          # AI가 개선 제안 생성
          python ai_code_improver.py \
            --analysis analysis-result.json \
            --generate-fixes \
            --output suggested-fixes.patch
            
      - name: Create Auto-Fix PR
        if: steps.ai-analysis.outputs.fixable-issues > 0
        uses: peter-evans/create-pull-request@v5
        with:
          title: '[AI] Automated Code Quality Improvements'
          body: |
            AI-generated improvements for code quality:
            - Score: ${{ steps.ai-analysis.outputs.score }}/100
            - Issues fixed: ${{ steps.ai-analysis.outputs.fixable-issues }}
          branch: ai-auto-fix-${{ github.run_number }}
```

### 2. 지능형 배포 결정 시스템

```yaml
name: Intelligent Deployment Decision
on: [push]

jobs:
  ai-deployment-advisor:
    runs-on: signoff-runner
    outputs:
      deploy-recommendation: ${{ steps.ai-advisor.outputs.recommendation }}
      confidence-score: ${{ steps.ai-advisor.outputs.confidence }}
      risk-factors: ${{ steps.ai-advisor.outputs.risks }}
    steps:
      - name: AI Deployment Risk Assessment  
        id: ai-advisor
        run: |
          # 과거 배포 데이터와 현재 변경사항 분석
          python ai_deployment_advisor.py \
            --commit-hash ${{ github.sha }} \
            --history-depth 100 \
            --risk-threshold 0.3
            
  conditional-deploy:
    needs: ai-deployment-advisor
    if: needs.ai-deployment-advisor.outputs.deploy-recommendation == 'APPROVE'
    runs-on: signoff-runner
    steps:
      - name: AI-Approved Deployment
        run: |
          echo "AI recommends deployment with confidence: ${{ needs.ai-deployment-advisor.outputs.confidence-score }}"
          # 정상 배포 실행
          
  human-review-required:
    needs: ai-deployment-advisor
    if: needs.ai-deployment-advisor.outputs.deploy-recommendation == 'REVIEW_REQUIRED'
    runs-on: signoff-runner
    steps:
      - name: Request Human Review
        run: |
          # 인간 검토 요청 알림
          python send_review_request.py \
            --risks "${{ needs.ai-deployment-advisor.outputs.risk-factors }}" \
            --confidence "${{ needs.ai-deployment-advisor.outputs.confidence-score }}"
```

### 3. 자동 테스트 케이스 생성

```yaml
name: AI Test Case Generation
on:
  push:
    paths: ['input_config.yaml', 'run.sh']

jobs:
  generate-ai-tests:
    runs-on: signoff-runner
    steps:
      - uses: actions/checkout@v4
      
      - name: Analyze Configuration Changes
        id: config-analysis
        run: |
          # 설정 변경사항 분석
          python analyze_config_changes.py \
            --current input_config.yaml \
            --previous ${{ github.event.before }}/input_config.yaml
            
      - name: Generate Test Cases with AI
        run: |
          # AI가 변경사항 기반으로 테스트 케이스 자동 생성
          python ai_test_generator.py \
            --config-changes config-changes.json \
            --coverage-target 95 \
            --output generated_tests/
            
      - name: Execute Generated Tests
        run: |
          # 생성된 테스트 실행
          python -m pytest generated_tests/ -v --coverage
          
      - name: Update Test Suite
        if: success()
        run: |
          # 성공한 테스트를 정식 테스트 슈트에 추가
          cp generated_tests/*.py tests/
          git add tests/
          git commit -m "[AI] Add generated test cases"
          git push
```

### 4. 실시간 성능 모니터링 및 자동 최적화

```yaml
name: AI Performance Optimization
on:
  schedule:
    - cron: '0 */4 * * *'  # 4시간마다 실행

jobs:
  performance-monitoring:
    runs-on: signoff-runner
    steps:
      - name: Collect Performance Metrics
        run: |
          # 실제 Signoff Application 성능 데이터 수집
          python collect_performance_data.py \
            --duration 4h \
            --metrics execution_time,memory_usage,error_rate
            
      - name: AI Performance Analysis
        id: perf-analysis
        run: |
          # AI로 성능 패턴 분석 및 최적화 포인트 식별
          python ai_performance_analyzer.py \
            --data performance_data.json \
            --identify-bottlenecks \
            --suggest-optimizations
            
      - name: Auto-Apply Safe Optimizations
        if: steps.perf-analysis.outputs.safe-optimizations > 0
        run: |
          # 안전한 최적화는 자동 적용
          python apply_optimizations.py \
            --optimizations ${{ steps.perf-analysis.outputs.safe-optimizations }} \
            --create-pr
            
      - name: Alert on Critical Issues
        if: steps.perf-analysis.outputs.critical-issues > 0
        run: |
          # 심각한 성능 문제는 즉시 알림
          python send_critical_alert.py \
            --issues ${{ steps.perf-analysis.outputs.critical-issues }} \
            --channels nkox,email,slack
```

## 실무 적용을 위한 점진적 도입 계획

### Phase 1: 현재 시스템 안정화 (완료)

```yaml
# 기본 push → validate → deploy 워크플로우
✅ 구현 완료
```

### Phase 2: 스마트 트리거 도입 (단기)

```yaml
# 파일별 조건부 실행, 스케줄 기반 정기 검증
on:
  push:
    paths: ['input_config.yaml', 'run.sh']
  schedule:
    - cron: '0 9 * * 1'  # 주간 정기 검증
```

### Phase 3: 병렬 처리 및 고급 검증 (중기)

```yaml
# 병렬 검증, 매트릭스 빌드, 조건부 배포
jobs:
  parallel-validation: [syntax, security, performance]
  intelligent-deploy: needs parallel-validation
```

### Phase 4: AI Agent 통합 (장기)

```yaml
# AI 기반 코드 분석, 자동 테스트 생성, 지능형 배포 결정
jobs:
  ai-analysis: AI 코드 품질 분석
  ai-test-gen: 자동 테스트 케이스 생성  
  ai-deploy-decision: 지능형 배포 승인
```

이러한 고급 기능들을 단계적으로 도입하면, 현재의 단순한 배포 자동화에서 시작하여 궁극적으로는 AI가 주도하는 완전 자율적인 DevOps 시스템으로 발전시킬 수 있습니다. 특히 Signoff AI Agent의 경우, 설계 검증 과정에서 발생하는 패턴을 학습하고 예측하여 더욱 정교하고 지능적인 검증 프로세스를 구축할 수 있을 것입니다.



## 재사용 가능한 Workflow와 YAML 관리

- **재사용 Workflow**:
    
    - 공통 Workflow를 별도 YAML 파일로 정의 → 여러 Repository에서 호출.
        
    - 예: signoff-common.yml에 검증/배포 로직 정의, 각 signoff-<app_name>에서 호출.
        
    - 장점: 19개 Repository 동일 로직 유지, 업데이트 시 한 파일만 수정.
        
    - 비유: "회로 설계 템플릿: 한 번 만들어두면 모든 프로젝트에 적용."
        
- **구현 예시** (signoff-common.yml):
    
    ```yaml
    name: Reusable Signoff Workflow
    on:
      workflow_call:
        inputs:
          app_name:
            required: true
    jobs:
      deploy:
        runs-on: signoff-runner
        steps:
          - uses: actions/checkout@v3
          - run: ./deploy.sh ${{ inputs.app_name }}
    ```
    
    - 호출 (signoff-dsc.yml):
        
    
    ```yaml
    on:
      push:
        branches: [ master ]
    jobs:
      call-deploy:
        uses: MDT/signoff-common/.github/workflows/signoff-common.yml@main
        with:
          app_name: signoff-dsc
    ```
    
- **Signoff AI Agent 연계 가능성**:
    
    - AI Agent용 공통 Workflow: 모델 학습/검증 워크플로우를 재사용 가능.
        
    - 예: AI 기반 코드 분석 → 공통 YAML로 모든 Application 적용.
        
- **발표자 노트 (스크립트)**: "재사용 Workflow는 설계 템플릿 같은 거예요. 한 번 잘 만들어두면 19개 Application 모두에 똑같이 적용됩니다. AI Agent를 추가할 때도 공통 로직으로 쉽게 확장할 수 있죠."
    

## Signoff AI Agent를 위한 고급 기능 제안

- **AI Agent 연계 가능성**:
    
    1. **자동 코드 검증**: AI로 YAML/run.sh 품질 분석 (예: linting, 규칙 위반 탐지).
        
        - 액션: actions/setup-python + AI 스크립트 실행.
            
    2. **모델 배포 자동화**: AI Agent가 학습한 모델을 /user/signoff.dsa/AI_MODELS/에 배포.
        
        - Workflow 예: Push → 모델 검증 → 배포.
            
    3. **실시간 모니터링**: AI Agent가 배포 결과 분석 → nkox로 상세 보고.
        
        - 예: actions/slack-notify로 AI 분석 결과 전송.
            
- **구현 예시** (AI 검증 Workflow snippet):
    
    ```yaml
    jobs:
      ai-validate:
        runs-on: signoff-runner
        steps:
          - uses: actions/checkout@v3
          - uses: actions/setup-python@v4
            with:
              python-version: '3.8'
          - run: python ai_validate.py input_config.yaml
          - run: |
              if [ $? -ne 0 ]; then
                echo "AI validation failed" | nkox_notify
                exit 1
              fi
    ```
    
```mermaid
sequenceDiagram

  participant Dev as 개발자

  participant GH as GitHub Actions

  participant AI as Signoff AI Agent

  participant SR as 배포 경로

  participant NK as nkox 알림

  Dev->>GH: Push 코드

  GH->>AI: AI 검증 (ai_validate.py)

  AI->>GH: 검증 결과

  GH->>SR: 배포 (deploy.sh)

  SR->>NK: 성공/실패 + AI 분석 보고
```

**발표자 노트 (스크립트)**: "Signoff AI Agent는 미래에 큰 도움이 될 거예요. AI로 코드를 분석하거나 모델을 배포할 수 있습니다. 예를 들어, YAML 오류를 AI가 잡아내고, 결과를 nkox로 보내줄 수 있죠. 회로 분석기를 추가로 붙이는 것처럼, 이 시스템은 계속 확장 가능합니다."










### GitHub Context 변수 완전 가이드

#### 기본 정보 변수들

yaml

```yaml
steps:
  - name: Display GitHub Context
    run: |
      echo "Repository: ${{ github.repository }}"          # MDT/signoff-dsc
      echo "Repository Owner: ${{ github.repository_owner }}" # MDT
      echo "Repository Name: ${{ github.event.repository.name }}" # signoff-dsc
      echo "Ref: ${{ github.ref }}"                        # refs/heads/master
      echo "Ref Name: ${{ github.ref_name }}"              # master
      echo "SHA: ${{ github.sha }}"                        # 커밋 해시
      echo "Actor: ${{ github.actor }}"                    # 실행한 사용자
      echo "Workflow: ${{ github.workflow }}"              # Workflow 이름
      echo "Job: ${{ github.job }}"                        # 현재 Job 이름
      echo "Run ID: ${{ github.run_id }}"                  # 고유 실행 ID
      echo "Run Number: ${{ github.run_number }}"          # 실행 번호
      echo "Event Name: ${{ github.event_name }}"          # push, pull_request 등
```

#### 커밋 및 이벤트 정보

yaml

```yaml
steps:
  - name: Commit Information
    run: |
      echo "Commit Message: ${{ github.event.head_commit.message }}"
      echo "Commit Author: ${{ github.event.head_commit.author.name }}"
      echo "Commit Email: ${{ github.event.head_commit.author.email }}"
      echo "Commit Timestamp: ${{ github.event.head_commit.timestamp }}"
      echo "Modified Files: ${{ toJson(github.event.head_commit.modified) }}"
      echo "Added Files: ${{ toJson(github.event.head_commit.added) }}"
      echo "Removed Files: ${{ toJson(github.event.head_commit.removed) }}"
```





# 폐쇄망 HPC 환경에서의 GitHub Actions 고급 활용 가이드

## 1. GitHub Actions 버전 시스템 완전 해부

### 왜 각 Action마다 다른 버전을 사용하는가?

GitHub Actions의 버전은 각 Action의 **개발 주기와 안정성**에 따라 결정됩니다.

#### 버전 진화 과정 이해하기

```yaml
# 실제 Action들의 버전 진화 과정

actions/checkout:
├── v1 (2019년) - 초기 버전, 현재 deprecated
├── v2 (2020년) - Node.js 12 기반, 기본 기능
├── v3 (2021년) - Node.js 16 기반, 성능 개선
└── v4 (2023년) - Node.js 20 기반, 최신 Git 기능

actions/setup-python:
├── v1 (2019년) - 기본 Python 설치만
├── v2 (2020년) - 캐싱 기능 추가
├── v3 (2021년) - 성능 최적화
└── v4 (2022년) - PyPy 지원, 향상된 캐싱

actions/upload-artifact:
├── v1 (2019년) - 기본 업로드
├── v2 (2020년) - 압축 기능
└── v3 (2021년) - 대용량 파일 지원, 현재 최신

docker/setup-buildx-action:
├── v1 (2020년) - Docker Buildx 초기 지원
└── v2 (2021년) - 멀티플랫폼 빌드 지원, 현재 최신
```

#### 버전 선택 기준과 전략

```yaml
# 1. 최신 안정 버전 사용 (권장)
- uses: actions/checkout@v4          # 2023년 출시, 최신 기능
- uses: actions/setup-python@v4      # 2022년 출시, 안정적

# 2. 검증된 버전 사용 (보수적)
- uses: actions/upload-artifact@v3   # v4가 없어서 v3이 최신
- uses: actions/setup-node@v3        # v4가 베타이므로 v3 사용

# 3. 호환성 고려 버전
- uses: docker/setup-buildx-action@v2  # Docker 환경에 따라 결정
```

#### 폐쇄망 환경에서의 버전 관리 전략

```yaml
# HPC 폐쇄망에서는 외부 Action을 직접 사용할 수 없으므로
# Self-hosted runner에서 직접 구현하는 방식 사용

# 기존 방식 (외부 의존)
- uses: actions/checkout@v4
- uses: actions/setup-python@v4

# 폐쇄망 적용 방식 (내부 구현)
- name: "Manual Checkout (HPC Compatible)"
  run: |
    git clone https://deep.choi:${{env.GITHUB_PAT}}@cae.github.samsungds.net/MDT/${{ env.REPO_NAME}} repo
    
- name: "Use Pre-installed Python (HPC)"
  run: |
    /user/signoff.dsa/miniconda3/envs/launcher/bin/python --version
```

## 2. 폐쇄망 HPC 환경에서의 실용적 트리거 옵션들

### 폐쇄망 환경의 제약사항과 대안

#### 제약사항 분석

```
❌ 불가능한 기능들:
- repository_dispatch (외부 HTTP API 호출 불가)
- 외부 webhook 수신
- 인터넷 기반 서비스 연동
- 외부 Actions Marketplace 사용

✅ 사용 가능한 기능들:
- Push/PR 기반 트리거
- Schedule 기반 트리거  
- 파일/경로 기반 조건부 실행
- 내부 스크립트 기반 이벤트 감지
```

### 폐쇄망 환경 최적화 트리거 전략

#### 1. 지능형 파일 모니터링 트리거

```yaml
name: Smart File Monitoring
on:
  push:
    branches: [master]
    paths:
      # 핵심 설정 파일들만 모니터링
      - 'input_config.yaml'
      - 'run.sh'
      - 'models/**'
      - 'config/**'
    paths-ignore:
      # 불필요한 파일들은 제외하여 효율성 증대
      - 'docs/**'
      - '*.md'
      - '.gitignore'
      - 'logs/**'
      - 'temp/**'

jobs:
  analyze-changes:
    runs-on: signoff-runner
    outputs:
      change-type: ${{ steps.analyze.outputs.type }}
      critical-files: ${{ steps.analyze.outputs.critical }}
    steps:
      - name: Analyze File Changes
        id: analyze
        run: |
          # 변경된 파일 유형 분석
          CHANGED_FILES="${{ github.event.head_commit.modified }}"
          
          if echo "$CHANGED_FILES" | grep -q "input_config.yaml"; then
            echo "type=config-update" >> $GITHUB_OUTPUT
            echo "critical=true" >> $GITHUB_OUTPUT
          elif echo "$CHANGED_FILES" | grep -q "models/"; then
            echo "type=model-update" >> $GITHUB_OUTPUT  
            echo "critical=true" >> $GITHUB_OUTPUT
          else
            echo "type=minor-update" >> $GITHUB_OUTPUT
            echo "critical=false" >> $GITHUB_OUTPUT
          fi
          
  conditional-deploy:
    needs: analyze-changes
    if: needs.analyze-changes.outputs.critical == 'true'
    runs-on: signoff-runner
    steps:
      - name: Deploy Critical Changes
        run: |
          echo "Deploying critical changes: ${{ needs.analyze-changes.outputs.change-type }}"
          /user/signoff.dsa/RUNSCRIPTS/deploy.sh "${{ env.REPO_NAME }}"
```

#### 2. 시간 기반 지능형 스케줄링

```yaml
name: Intelligent Scheduling
on:
  schedule:
    # 업무 시간 중 정기 검증 (한국 시간 고려)
    - cron: '0 1 * * 1-5'   # 평일 오전 10시 (UTC+9)
    - cron: '0 5 * * 1-5'   # 평일 오후 2시 
    - cron: '0 9 * * 1-5'   # 평일 오후 6시
    
    # 주말 전체 시스템 점검
    - cron: '0 15 * * 6'    # 토요일 자정
    
    # 월초 종합 리포트
    - cron: '0 2 1 * *'     # 매월 1일 오전 11시

jobs:
  scheduled-maintenance:
    runs-on: signoff-runner
    steps:
      - name: Determine Maintenance Type
        id: maintenance-type
        run: |
          HOUR=$(date +%H)
          DAY=$(date +%u)  # 1=Monday, 7=Sunday
          DATE=$(date +%d)
          
          if [ "$DATE" = "01" ]; then
            echo "type=monthly-report" >> $GITHUB_OUTPUT
          elif [ "$DAY" = "6" ]; then
            echo "type=weekly-cleanup" >> $GITHUB_OUTPUT
          else
            echo "type=daily-check" >> $GITHUB_OUTPUT
          fi
          
      - name: Execute Maintenance
        run: |
          case "${{ steps.maintenance-type.outputs.type }}" in
            "monthly-report")
              python generate_monthly_report.py
              ;;
            "weekly-cleanup")
              python cleanup_old_files.py --days 30
              python validate_all_apps.py
              ;;
            "daily-check")
              python health_check.py --quick
              ;;
          esac
```

#### 3. 커밋 메시지 기반 동작 제어

```yaml
name: Commit Message Driven Actions
on:
  push:
    branches: [master]

jobs:
  parse-commit-intent:
    runs-on: signoff-runner
    outputs:
      action-type: ${{ steps.parse.outputs.action }}
      priority: ${{ steps.parse.outputs.priority }}
    steps:
      - name: Parse Commit Message
        id: parse
        run: |
          COMMIT_MSG="${{ github.event.head_commit.message }}"
          
          # 특별한 키워드 기반 동작 결정
          if echo "$COMMIT_MSG" | grep -qi "\[HOTFIX\]"; then
            echo "action=emergency-deploy" >> $GITHUB_OUTPUT
            echo "priority=high" >> $GITHUB_OUTPUT
          elif echo "$COMMIT_MSG" | grep -qi "\[AI\]"; then
            echo "action=ai-training" >> $GITHUB_OUTPUT
            echo "priority=medium" >> $GITHUB_OUTPUT
          elif echo "$COMMIT_MSG" | grep -qi "\[TEST\]"; then
            echo "action=test-only" >> $GITHUB_OUTPUT
            echo "priority=low" >> $GITHUB_OUTPUT
          else
            echo "action=normal-deploy" >> $GITHUB_OUTPUT
            echo "priority=medium" >> $GITHUB_OUTPUT
          fi

  emergency-deploy:
    needs: parse-commit-intent
    if: needs.parse-commit-intent.outputs.action == 'emergency-deploy'
    runs-on: signoff-runner
    steps:
      - name: Emergency Deployment
        run: |
          echo "🚨 Emergency deployment initiated"
          # 빠른 검증 후 즉시 배포
          python quick_validate.py
          /user/signoff.dsa/RUNSCRIPTS/deploy.sh "${{ env.REPO_NAME }}"
          
          # 긴급 알림
          python send_emergency_alert.py \
            --message "Emergency deployment completed" \
            --commit "${{ github.sha }}"

  ai-training:
    needs: parse-commit-intent  
    if: needs.parse-commit-intent.outputs.action == 'ai-training'
    runs-on: signoff-runner
    steps:
      - name: Trigger AI Training
        run: |
          echo "🤖 AI training workflow initiated"
          python trigger_ai_training.py \
            --commit-hash "${{ github.sha }}" \
            --priority "${{ needs.parse-commit-intent.outputs.priority }}"
```

## 3. Design Portal 연동: DB 및 파일시스템 모니터링

### 폐쇄망에서의 Design Portal 연동 전략

#### 전략 1: 파일시스템 폴링 기반 트리거

```yaml
name: File System Monitoring
on:
  schedule:
    - cron: '*/10 * * * *'  # 10분마다 파일시스템 체크

jobs:
  monitor-design-files:
    runs-on: signoff-runner
    outputs:
      new-designs: ${{ steps.check-files.outputs.new-designs }}
      updated-designs: ${{ steps.check-files.outputs.updated-designs }}
    steps:
      - name: Check for New/Updated Design Files
        id: check-files
        run: |
          # Design Portal이 업로드하는 경로 모니터링
          DESIGN_PATH="/shared/design_portal/uploads"
          LAST_CHECK_FILE="/user/signoff.dsa/monitoring/last_check.timestamp"
          
          # 마지막 체크 시간 읽기
          if [ -f "$LAST_CHECK_FILE" ]; then
            LAST_CHECK=$(cat $LAST_CHECK_FILE)
          else
            LAST_CHECK=$(date -d "1 hour ago" +%s)
          fi
          
          # 새로운/수정된 파일 검색
          NEW_FILES=$(find $DESIGN_PATH -type f -newer $LAST_CHECK_FILE 2>/dev/null || true)
          
          if [ -n "$NEW_FILES" ]; then
            # 파일 정보 분석
            python analyze_design_files.py \
              --file-list "$NEW_FILES" \
              --output design_changes.json
              
            NEW_DESIGNS=$(cat design_changes.json | jq -r '.new_designs | length')
            UPDATED_DESIGNS=$(cat design_changes.json | jq -r '.updated_designs | length')
            
            echo "new-designs=$NEW_DESIGNS" >> $GITHUB_OUTPUT
            echo "updated-designs=$UPDATED_DESIGNS" >> $GITHUB_OUTPUT
            
            # 현재 시간 저장
            date +%s > $LAST_CHECK_FILE
          else
            echo "new-designs=0" >> $GITHUB_OUTPUT
            echo "updated-designs=0" >> $GITHUB_OUTPUT
          fi

  process-design-changes:
    needs: monitor-design-files
    if: needs.monitor-design-files.outputs.new-designs > 0 || needs.monitor-design-files.outputs.updated-designs > 0
    runs-on: signoff-runner
    strategy:
      matrix:
        # 발견된 각 설계 파일에 대해 병렬 처리
        design-file: ${{ fromJson(steps.get-files.outputs.files) }}
    steps:
      - name: Get Design Files List
        id: get-files
        run: |
          FILES=$(cat design_changes.json | jq -c '.all_files')
          echo "files=$FILES" >> $GITHUB_OUTPUT
          
      - name: Process Design File
        run: |
          echo "Processing: ${{ matrix.design-file }}"
          
          # 파일 유형 분석
          python classify_design_file.py \
            --file "${{ matrix.design-file }}" \
            --output file_info.json
            
          FILE_TYPE=$(cat file_info.json | jq -r '.file_type')
          
          case "$FILE_TYPE" in
            "netlist")
              python process_netlist.py --file "${{ matrix.design-file }}"
              ;;
            "layout")  
              python process_layout.py --file "${{ matrix.design-file }}"
              ;;
            "constraints")
              python process_constraints.py --file "${{ matrix.design-file }}"
              ;;
          esac
          
      - name: Trigger Signoff Analysis
        run: |
          # 해당 설계에 적합한 Signoff Application 실행
          python trigger_signoff_analysis.py \
            --design-file "${{ matrix.design-file }}" \
            --auto-select-apps \
            --priority high
```

#### 전략 2: DB 모니터링 기반 트리거

```yaml
name: Database Monitoring  
on:
  schedule:
    - cron: '*/5 * * * *'  # 5분마다 DB 체크

jobs:
  monitor-design-db:
    runs-on: signoff-runner
    outputs:
      db-changes: ${{ steps.check-db.outputs.changes }}
      change-details: ${{ steps.check-db.outputs.details }}
    steps:
      - name: Check Design Portal Database
        id: check-db
        run: |
          # Design Portal DB 연결 및 변경사항 체크
          python monitor_design_db.py \
            --db-host ${{ secrets.DESIGN_PORTAL_DB_HOST }} \
            --db-user ${{ secrets.DESIGN_PORTAL_DB_USER }} \
            --db-pass ${{ secrets.DESIGN_PORTAL_DB_PASS }} \
            --last-check-file /user/signoff.dsa/monitoring/db_last_check.json \
            --output db_changes.json
            
          # 변경사항 확인
          CHANGES=$(cat db_changes.json | jq -r '.changes | length')
          echo "changes=$CHANGES" >> $GITHUB_OUTPUT
          
          if [ "$CHANGES" -gt 0 ]; then
            DETAILS=$(cat db_changes.json | jq -c '.')
            echo "details=$DETAILS" >> $GITHUB_OUTPUT
          fi

  process-db-changes:
    needs: monitor-design-db
    if: needs.monitor-design-db.outputs.db-changes > 0
    runs-on: signoff-runner
    steps:
      - name: Process Database Changes
        run: |
          echo "Processing ${{ needs.monitor-design-db.outputs.db-changes }} DB changes"
          
          # 변경 유형별 처리
          python process_db_changes.py \
            --changes '${{ needs.monitor-design-db.outputs.change-details }}' \
            --action-map /user/signoff.dsa/config/db_action_mapping.yaml \
            --output processed_actions.json
            
      - name: Execute Triggered Actions
        run: |
          # 처리된 액션들 실행
          python execute_db_triggered_actions.py \
            --actions processed_actions.json \
            --signoff-apps-config /user/signoff.dsa/signoff_applications.yaml
```

#### 전략 3: 파일 워치독 + 즉시 트리거 (고급)

```bash
# 별도의 모니터링 데몬 스크립트 (signoff-runner에서 상시 실행)
#!/bin/bash
# /user/signoff.dsa/monitoring/design_watcher.sh

WATCH_PATH="/shared/design_portal/uploads"
TRIGGER_SCRIPT="/user/signoff.dsa/monitoring/trigger_github_action.py"

# inotify를 사용한 실시간 파일 모니터링
inotifywait -m -r -e create,modify,moved_to $WATCH_PATH --format '%w%f %e' | while read FILE EVENT; do
    echo "$(date): Detected $EVENT on $FILE"
    
    # 파일 안정화 대기 (업로드 완료 확인)
    sleep 5
    
    # GitHub Actions 트리거
    python $TRIGGER_SCRIPT \
        --file "$FILE" \
        --event "$EVENT" \
        --timestamp "$(date +%s)"
done
```

```python
# /user/signoff.dsa/monitoring/trigger_github_action.py
import os
import json
import subprocess
from pathlib import Path

def trigger_github_action(file_path, event_type):
    """파일 변경사항을 GitHub Repository에 커밋하여 Actions 트리거"""
    
    # 임시 트리거 파일 생성
    trigger_data = {
        "timestamp": datetime.now().isoformat(),
        "triggered_by": "design_portal_watcher",
        "file_path": file_path,
        "event_type": event_type,
        "design_id": extract_design_id(file_path)
    }
    
    # Signoff Applications Repository에 트리거 파일 커밋
    trigger_file = f"/tmp/design_trigger_{int(time.time())}.json"
    with open(trigger_file, 'w') as f:
        json.dump(trigger_data, f)
        
    # Repository 업데이트 (빈 커밋으로 트리거)
    subprocess.run([
        "git", "commit", "--allow-empty", 
        "-m", f"[DESIGN-TRIGGER] {trigger_data['design_id']} updated"
    ], cwd="/path/to/signoff/repo")
    
    subprocess.run(["git", "push"], cwd="/path/to/signoff/repo")
```
