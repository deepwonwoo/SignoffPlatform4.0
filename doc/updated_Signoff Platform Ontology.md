# Signoff Ontology 구조 설계서

---

## 목차

### Part 1: 개념 및 구조

1. [개요](https://claude.ai/chat/d585c994-75a9-4aea-99f1-4ec0bd7a1945#1-%EA%B0%9C%EC%9A%94)
2. [Ontology 기초 개념](https://claude.ai/chat/d585c994-75a9-4aea-99f1-4ec0bd7a1945#2-ontology-%EA%B8%B0%EC%B4%88-%EA%B0%9C%EB%85%90)
3. [Signoff Ontology 3-Layer 구조](https://claude.ai/chat/d585c994-75a9-4aea-99f1-4ec0bd7a1945#3-signoff-ontology-3-layer-%EA%B5%AC%EC%A1%B0)

### Part 2: 구현 상세

4. [Object Type 상세 정의](https://claude.ai/chat/d585c994-75a9-4aea-99f1-4ec0bd7a1945#4-object-type-%EC%83%81%EC%84%B8-%EC%A0%95%EC%9D%98)
5. [관계(Links) 전체 정의](https://claude.ai/chat/d585c994-75a9-4aea-99f1-4ec0bd7a1945#5-%EA%B4%80%EA%B3%84links-%EC%A0%84%EC%B2%B4-%EC%A0%95%EC%9D%98)
6. [Signoff Workflow와 Ontology 매핑](https://claude.ai/chat/d585c994-75a9-4aea-99f1-4ec0bd7a1945#6-signoff-workflow%EC%99%80-ontology-%EB%A7%A4%ED%95%91)
7. [예시 시나리오](https://claude.ai/chat/d585c994-75a9-4aea-99f1-4ec0bd7a1945#7-%EC%98%88%EC%8B%9C-%EC%8B%9C%EB%82%98%EB%A6%AC%EC%98%A4)
8. [향후 확장 계획](https://claude.ai/chat/d585c994-75a9-4aea-99f1-4ec0bd7a1945#8-%ED%96%A5%ED%9B%84-%ED%99%95%EC%9E%A5-%EA%B3%84%ED%9A%8D)

---

# Part 1: 개념 및 구조

---

## 1. 개요

### 1.1 이 문서의 목적

본 문서는 차세대 Signoff Platform의 핵심 기반인 **Signoff Ontology**의 구조를 정의한다.

**Signoff Ontology**란 메모리 회로 설계 검증(Signoff) 업무의 핵심 개체(Object)들과 그들 간의 관계(Relationship)를 체계적으로 정의한 **지식 표현 체계**이다. 기존의 File/Folder/DB 기반의 파편화된 데이터 관리 방식에서 벗어나, 데이터의 **"의미(Meaning)"**와 **"맥락(Context)"**을 시스템이 이해할 수 있는 Knowledge Graph 형태로 전환하는 것을 목표로 한다.

이를 통해 **AI Agent가 Signoff 업무를 스스로 수행하고 추론할 수 있는 기반**을 마련한다.

### 1.2 왜 Ontology가 필요한가?

개발자 관점에서 "기존 RDB(Relational Database)나 단순 대시보드로도 가능한 것 아닌가?"라는 의문이 들 수 있다. Signoff 도메인에서 Ontology가 필수적인 이유는 다음과 같다.

#### 1.2.1 Signoff 도메인의 특수성: "맥락(Context)의 연결"

**기존 DB의 한계:**

- RDB는 미리 정의된 스키마와 Join 연산에 의존한다.
- **문제점**: "왜 이 Block의 LSC 결과가 Fail인가?"라는 질문에 대해, RDB는 결과값만 보여줄 뿐, **"누가, 어떤 Netlist 버전으로, 어떤 Power 설정(InputConfig)을 써서, 어떤 Workspace에서 돌렸는지"**에 대한 복합적인 인과관계를 동적으로 추적하기 어렵다.

**Ontology의 강점 (Data Lineage & Graph Traversal):**

- Signoff의 모든 요소(사람, 파일, 설정, 결과)를 **객체(Object)**로 정의하고 이들을 **관계(Link)**로 연결한다.
- LLM/AI Agent는 이 연결망을 통해 "A 설계자가 변경한 Netlist 때문에 B Block의 DSC 결과가 악화되었다"는 식의 **추론(Reasoning)**이 가능해진다.

#### 1.2.2 유연한 확장성 (Flexible Schema)

- Signoff Tool은 수시로 변경된다 (파라미터 추가, 새로운 Check 항목 등).
- RDB는 컬럼 변경 비용이 크지만, Ontology는 속성(Property)이나 객체 타입을 유연하게 추가/확장할 수 있어 **Agile한 개발**에 적합하다.

#### 1.2.3 AI Agent의 "공용어(Common Language)"

- Signoff Launcher, ResultViewer, Inhouse Tool 등 서로 다른 언어(C++, Python, Web)로 된 시스템들이 소통하기 위한 **표준 프로토콜** 역할을 수행한다.
- AI Agent는 이 Ontology를 **지도(Map)** 삼아 데이터를 탐색한다.

### 1.3 현재 Signoff Platform의 구조적 한계

|문제|현재 상태|Ontology 도입 후|
|---|---|---|
|**Data Silo**|SOL/SORV 간 데이터 단절, Input↔Output 연결 부재|모든 데이터가 관계로 연결|
|**Operation Silo**|Application별 개별 point solution|통합된 공통 언어로 표준화|
|**Decision Silo**|Waiver 근거, 해결 이력 미기록|의사결정 이력 축적 및 재활용|

> **핵심 가치**: Ontology는 **AI Agent가 Signoff 업무를 이해하기 위한 공통 언어이자 기반 인프라**이다.

### 1.4 Object Type 요약 (11개)

|Layer|Object Type|역할|개수|
|---|---|---|---|
|**Semantic**|Product, Revision, Block, Designer, SignoffApplication|정적 마스터 데이터 (자산)|5개|
|**Kinetic**|SignoffJob, InputConfig, Workspace|실행 및 상태 추적 (행위)|3개|
|**Dynamic**|Result, WaiverDecision, SignoffIssue|결과 및 의사결정 이력 (지능)|3개|

---

## 2. Ontology 기초 개념

### 2.1 Ontology란?

**Ontology**는 특정 도메인의 **개념(Concept)**과 **관계(Relationship)**를 명시적으로 정의하여, 사람과 기계(AI)가 동일한 이해를 공유할 수 있게 하는 **지식 표현 방법**이다.

```
┌─────────────────────────────────────────────────────────────────┐
│        일반 데이터베이스          vs           Ontology          │
├─────────────────────────────────────────────────────────────────┤
│  • 테이블과 행/열                  • Object와 Property/Link      │
│  • 데이터만 저장                   • 데이터 + 의미 + 관계 저장    │
│  • JOIN으로 관계 조회              • 관계가 명시적으로 정의됨     │
│  • 스키마 변경 어려움              • 유연한 확장 가능             │
│  • "What" 만 저장                  • "What + Why + How" 저장     │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 핵심 구성 요소

|구성 요소|설명|Signoff 예시|
|---|---|---|
|**Object Type**|개체의 유형(클래스) 정의|Product, SignoffJob, Result|
|**Object (Instance)**|Object Type의 실제 인스턴스|"HBM4E", "JOB-20250119-001"|
|**Property**|Object의 속성|product_name, job_status|
|**Link**|Object 간의 관계|Product → has_revision → Revision|

### 2.3 왜 Knowledge Graph인가?

Ontology를 **Knowledge Graph** 형태로 구현하면 다음이 가능해진다:

**1. 관계 기반 탐색**

- "HBM4E R30의 모든 DSC 결과"를 관계를 따라 즉시 조회

**2. 맥락 이해**

- AI가 "이 Result가 어떤 제품의, 어떤 Revision의, 누가 수행한 것인지" 파악

**3. Multi-hop 추론**

- "R20에서 Waiver한 항목 중 R30에서 재발생한 것" 같은 복합 질의 가능

```
[HBM4E] ──has_revision──▶ [R30] ──has_job──▶ [JOB-001] ──produces──▶ [RESULT-001]
   │                        │                    │                        │
   │                        │                    └──executed_by──▶ [김철수]
   │                        │
   │                        └──has_block──▶ [FULLCHIP] ──responsible_designer──▶ [김철수]
   │
   └──has_revision──▶ [R20] ──has_job──▶ [JOB-000] ──produces──▶ [RESULT-000]
```

위 그래프를 통해 AI는 다음과 같은 질의에 답할 수 있다:

- "HBM4E R30 FULLCHIP의 Signoff 현황은?" → Graph Traversal로 즉시 조회
- "김철수가 수행한 모든 Job의 결과는?" → Designer → SignoffJob → Result 경로 탐색
- "R20 대비 R30에서 새로 발생한 Fail 항목은?" → 두 Result 비교

---

## 3. Signoff Ontology 3-Layer 구조

### 3.1 Palantir가 3-Layer를 도입한 배경

#### 3-Layer의 탄생 이유

일반적인 RDB나 Data Warehouse는 "데이터를 저장하고 조회"하는 데 최적화되어 있다. 하지만 Palantir의 목표는 **"의사결정(Decision)과 행동(Action)"**이다. 이를 위해 현실 세계를 3가지로 분해했다.

```
┌─────────────────────────────────────────────────────────────────┐
│  Palantir의 핵심 질문:                                          │
│  "데이터만 저장하면 AI가 알아서 판단하고 실행할 수 있나?"          │
│                                                                 │
│  답: 불가능. AI에게 3가지를 명시적으로 알려줘야 함                │
│                                                                 │
│  1. Semantic: "세상에 뭐가 있는가?" (명사, 개체와 관계)           │
│  2. Kinetic:  "어떤 일이 일어나고 있는가?" (동사, 프로세스/상태)  │
│  3. Dynamic:  "어떻게 반응해야 하는가?" (지능, 액션/워크플로우)   │
└─────────────────────────────────────────────────────────────────┘
```

**왜 나눴을까?** 이 셋을 섞어버리면(예: RDB 테이블 하나에 다 넣으면), AI가 **"무엇이 원인(Semantic)"이고, "무엇이 결과(Dynamic)"이며, "내가 할 수 있는 행동(Kinetic)"이 무엇인지 구분하지 못한다.**

이 구조는 AI에게 **"업무의 문법(Grammar)"**을 가르쳐주는 것과 같다.

### 3.2 Signoff 도메인에 3-Layer가 적합한가?

#### 현재 Signoff 업무의 특성

|측면|현재 상태|AI Agent 자동화 목표|
|---|---|---|
|**데이터**|파일 기반, 분산 저장|통합 관리 필요 ✅|
|**프로세스**|수동 실행, LSF 제출|자동 트리거 가능|
|**의사결정**|사람이 Waiver 판단|**판단 근거 축적 + 추천**|

#### 핵심 질문: Signoff에서 "Dynamic Layer"가 정말 필요한가?

**Palantir의 Dynamic Layer는:**

- 시스템이 **자동으로 액션을 실행**하는 것 (예: 재고 부족 → 자동 발주)
- **실시간 의사결정**이 필요한 경우

**Signoff의 현실은:**

- Waiver 판단은 **설계자의 전문 지식**이 필요
- 잘못된 자동 판단은 **실리콘 불량**으로 이어질 수 있음
- 현재 목표는 "자동 판단"보다 **"판단 근거 축적 + 추천"**에 가까움

#### 그럼에도 3-Layer 구조를 채택하는 이유

|질문|답변|
|---|---|
|**Palantir가 왜 3-Layer를 만들었나?**|AI가 "데이터 → 판단 → 실행"을 자율적으로 하려면 각 단계가 명시적으로 분리되어야 하기 때문|
|**Signoff에 3-Layer가 필수인가?**|**지금 당장은 아님.** 현재 목표는 "데이터 연결 + 이력 축적"이지 "자동 실행"이 아님|
|**그럼 왜 3-Layer를 적용하나?**|Palantir를 레퍼런스로 활용할 때 용어 통일성 + **향후 AI Agent 자동화를 위한 확장 방향성** 확보|
|**실제 구현은 어떻게?**|Phase 1에서는 Object Type 중심으로 단순하게 시작하고, 필요시 점진적으로 Layer별 역할 분리|

> **설계 원칙**: Signoff Ontology는 Palantir의 3-Layer 아키텍처를 **참조**하여 설계한다. 현재 Phase 1에서는 11개 Object Type의 정의와 관계 구축에 집중하며, 향후 AI Agent 자동화 단계에서 Layer별 역할 분리를 고도화할 예정이다.

### 3.3 Signoff Platform에 이 구조가 왜 필요한가?

Signoff Platform을 단순히 "결과 뷰어"가 아닌 **"AI가 설계를 검증하는 플랫폼"**으로 만들려면 이 구조가 필수적이다.

#### ① Semantic Layer (자산): "AI가 건드려야 할 대상 정의"

- **Signoff 적용:** Product, Revision, Block, Designer, SignoffApplication
- **이유:** AI Agent에게 "이 Block이 검증 대상이야"라고 알려주는 기준이다. 이 Layer가 탄탄해야 나중에 툴이 바뀌거나(SPACE → PrimeSim), 공정이 바뀌어도(HBM3 → HBM4) 전체 구조가 무너지지 않는다.

#### ② Kinetic Layer (행위): "AI가 수행할 수 있는 Action 정의"

- **Signoff 적용:** SignoffJob, InputConfig, Workspace
- **이유:** 여기가 핵심이다. 기존 DB는 '결과'만 저장하지만, Ontology는 **'과정'**을 저장한다.
    - AI Agent가 "결과가 이상하네? **재실행(Action)** 해볼까?"라고 판단하려면, 실행이라는 행위 자체가 객체(SignoffJob)로 정의되어 있어야 한다.
    - 이 Layer가 있어야 **Write-Back(시스템에 명령 내리기)**이 가능해진다.

#### ③ Dynamic Layer (지능): "AI의 판단 로직과 결과물"

- **Signoff 적용:** Result, WaiverDecision, SignoffIssue
- **이유:** 단순한 Pass/Fail 데이터(Result)뿐만 아니라, **"왜 Waiver했는지(WaiverDecision)"**에 대한 인간의 판단 지식을 별도로 관리해야 한다.
    - 그래야 나중에 AI가 "과거에 김책임님이 이런 패턴은 Waiver했으니, 이번에도 Waiver를 추천합니다"라고 **추론(Reasoning)**할 수 있다.

### 3.4 장기적인 이점 (Long-term Benefits)

이 구조로 가야만 얻을 수 있는 확실한 이점들이 있다.

**1. 확장성 (Scalability)**

- 새로운 Signoff Tool(예: 열 해석 툴)이 추가되어도 Semantic(Block)은 그대로 두고, Kinetic(새로운 Job 타입)과 Dynamic(새로운 결과 타입)만 붙이면 된다. 기존 구조를 엎을 필요가 없다.

**2. 설명 가능한 AI (Explainable AI)**

- AI가 어떤 결정을 내렸을 때, 역추적이 가능하다.
- _"Dynamic(이슈)이 발생한 원인은 Kinetic(어제 돌린 Job) 때문이고, 그 Job은 Semantic(변경된 Netlist)을 사용했다."_ 라는 식의 완벽한 문장형 설명이 가능해진다.

**3. Human-In-the-Loop에서 Out-of-the-Loop로의 진화**

- 처음에는 사람이 WaiverDecision(Dynamic)을 생성하지만, 데이터가 쌓이면 AI가 이 패턴을 학습하여 스스로 WaiverDecision 객체를 생성(제안)할 수 있게 된다.
- **구조가 같으므로 사람의 업무를 AI가 그대로 대체하기 쉽다.**

### 3.5 3-Layer 구조 요약

```
┌─────────────────────────────────────────────────────────────────┐
│  🎯 Dynamic Layer (동적 계층) - "The Brains"                    │
│  ───────────────────────────────────────────────────────────────│
│  "결과는 어떤가? 어떤 판단이 내려졌는가?"                         │
│                                                                 │
│  Result, WaiverDecision, SignoffIssue                          │
│  → 실행의 결과물과 그에 대한 인간/AI의 판단                       │
│  → 피드백 루프를 형성하는 핵심 지식 데이터                        │
├─────────────────────────────────────────────────────────────────┤
│  ⚡ Kinetic Layer (운동 계층) - "The Verbs"                     │
│  ───────────────────────────────────────────────────────────────│
│  "어떻게 실행되는가?"                                           │
│                                                                 │
│  SignoffJob, InputConfig, Workspace                            │
│  → 시간의 흐름에 따라 발생하는 이벤트                            │
│  → 누가, 무엇을 가지고, 어떤 행위를 했는가?                      │
├─────────────────────────────────────────────────────────────────┤
│  📚 Semantic Layer (의미 계층) - "The Nouns"                    │
│  ───────────────────────────────────────────────────────────────│
│  "무엇이 있는가?"                                               │
│                                                                 │
│  Product, Revision, Block, Designer, SignoffApplication        │
│  → 현실 세계의 물리적/논리적 자산과 환경 설정                    │
│  → Signoff 행위가 일어나기 전 이미 존재하는 불변/반고정 정보     │
└─────────────────────────────────────────────────────────────────┘
```

### 3.6 Layer별 Object Type 매핑

|Layer|역할|설명|포함 Object|
|---|---|---|---|
|**Semantic Layer** (정적 자산 계층)|**"The Nouns"** (주체, 자원)|현실 세계의 물리적/논리적 자산과 환경 설정. Signoff 행위가 일어나기 전 이미 존재하는 불변/반고정 정보.|Product, Revision, Block, Designer, SignoffApplication|
|**Kinetic Layer** (행위/프로세스 계층)|**"The Verbs"** (실행, 활동)|시간의 흐름에 따라 발생하는 이벤트. 누가, 무엇을 가지고, 어떤 행위를 했는가?|SignoffJob, InputConfig, Workspace|
|**Dynamic Layer** (지능/의사결정 계층)|**"The Brains"** (결과, 판단)|실행의 결과물과 그에 대한 인간/AI의 판단. 피드백 루프를 형성하는 핵심 지식 데이터.|Result, WaiverDecision, SignoffIssue|

### 3.7 전체 관계도

```
                         ┌─────────────────────────────────────────────────┐
                         │              Semantic Layer                     │
                         │         "무엇이 있는가?" (The Nouns)             │
                         │                                                 │
                         │  ┌─────────┐    ┌──────────┐    ┌─────────┐    │
                         │  │ Product │───▶│ Revision │───▶│  Block  │    │
                         │  └─────────┘    └──────────┘    └────┬────┘    │
                         │                                      │         │
                         │  ┌──────────────────┐          ┌─────▼─────┐   │
                         │  │SignoffApplication│          │  Designer │   │
                         │  └────────┬─────────┘          └───────────┘   │
                         └───────────┼─────────────────────────────────────┘
                                     │
                         ┌───────────┼─────────────────────────────────────┐
                         │           ▼        Kinetic Layer                │
                         │      "어떻게 실행되는가?" (The Verbs)            │
                         │                                                 │
                         │  ┌────────────────┐    ┌─────────────┐         │
                         │  │   SignoffJob   │◀───│ InputConfig │         │
                         │  └───────┬────────┘    └─────────────┘         │
                         │          │                                      │
                         │          │             ┌───────────┐           │
                         │          └────────────▶│ Workspace │           │
                         │                        └───────────┘           │
                         └───────────┬─────────────────────────────────────┘
                                     │
                         ┌───────────┼─────────────────────────────────────┐
                         │           ▼        Dynamic Layer                │
                         │   "어떤 결과와 판단이 있는가?" (The Brains)      │
                         │                                                 │
                         │  ┌────────────────┐                            │
                         │  │     Result     │◀─────────────────┐        │
                         │  └───────┬────────┘                  │        │
                         │          │                            │        │
                         │  ┌───────▼────────┐    ┌─────────────┴──┐     │
                         │  │ WaiverDecision │    │  SignoffIssue  │     │
                         │  └────────────────┘    └────────────────┘     │
                         └─────────────────────────────────────────────────┘
```

---

# Part 2: 구현 상세

---

## 4. Object Type 상세 정의

### 4.1 Object Type 전체 목록 (13개)

|Layer|Object Type|역할|변경 빈도|Phase|
|---|---|---|---|---|
|**Semantic**|Product|메모리 제품 (HBM4E, DDR5 등)|거의 없음|1|
||Revision|설계 버전 (R00~R60)|낮음|1|
||Block|회로 블록 (FULLCHIP, CORE 등)|낮음|1|
||Designer|담당자 (설계자/수행자/개발자)|낮음|1|
||SignoffApplication|검증 도구 (19종)|거의 없음|1|
||CriteriaSet|Pass/Fail 판정 기준|낮음|1|
||Workspace|작업 공간 (Local↔Central)|중간|1|
|**Kinetic**|SignoffJob|실행 이벤트 (InputConfig 포함)|높음|1|
||Result|검증 결과 (row 통계)|높음|1|
|**Dynamic**|CategorizePart|Part별 담당자 지정|중간|1~2|
||CompareResult|Revision 간 비교 결과|중간|1~2|
||WaiverDecision|Waiver 판단 이력|중간|2|
||SignoffIssue|이슈/문의 이력|중간|2|

---

### 4.2 Semantic Layer Objects (7개)

> **Semantic Layer**는 Signoff 업무가 시작되기 전에 이미 존재하는 **정적 자산(The Nouns)**을 정의한다. 이 Layer의 Object들은 거의 변하지 않으며, 전체 시스템의 **기준점(Reference)**이 된다.

---

#### 4.2.1 Product (제품)

메모리 제품의 **최상위 개체**이다. HBM4E, DDR5, LPDDR5 등이 해당한다.

**역할**: Signoff 대상의 최상위 컨테이너. 모든 Revision, Block, Job은 궁극적으로 하나의 Product에 귀속된다.

**Properties:**

|속성명|타입|필수|설명|예시|
|---|---|:-:|---|---|
|`product_id`|STRING|✅|제품 고유 ID (PK)|`"HBM4E"`|
|`product_name`|STRING|✅|제품 전체 이름|`"HBM4E 32GB Wide I/O"`|
|`product_type`|ENUM|✅|제품 종류|`HBM`, `DRAM`, `FLASH`, `LPDDR`|
|`technology_node`|STRING|❌|공정 노드|`"4nm"`, `"5nm"`|
|`status`|ENUM|✅|개발 상태|`PLANNING`, `ACTIVE`, `TAPED_OUT`, `EOL`|
|`tapeout_target_date`|DATE|❌|Tapeout 목표일|`"2026-06-30"`|
|`description`|TEXT|❌|제품 설명||
|`created_at`|TIMESTAMP|✅|생성 시각||
|`updated_at`|TIMESTAMP|✅|수정 시각||

**Links:**

|관계명|방향|대상|카디널리티|설명|
|---|:-:|---|:-:|---|
|`has_revision`|→|Revision|1:N|제품의 설계 버전들|
|`managed_by`|→|Designer|N:M|제품 담당 관리자들|

**예시 Instance:**

```json
{
  "product_id": "HBM4E",
  "product_name": "HBM4E 32GB Wide I/O",
  "product_type": "HBM",
  "technology_node": "4nm",
  "status": "ACTIVE",
  "tapeout_target_date": "2026-06-30",
  "created_at": "2025-01-15T09:00:00Z"
}
```

---

#### 4.2.2 Revision (설계 버전)

설계 버전(R00~R60)을 나타낸다. **Signoff 수행의 기준 단위**이다.

**역할**: 동일 제품 내에서 설계 진행 상황을 구분하는 버전. 각 Revision은 고유한 Netlist 버전과 필수 Signoff 목록을 가진다.

**Properties:**

|속성명|타입|필수|설명|예시|
|---|---|:-:|---|---|
|`revision_id`|STRING|✅|리비전 고유 ID (PK)|`"HBM4E_R30"`|
|`product_id`|STRING|✅|소속 제품 ID (FK)|`"HBM4E"`|
|`revision_code`|ENUM|✅|리비전 코드|`R00`, `R10`, `R20`, `R30`, `R40`, `R50`, `R60`|
|`design_stage`|ENUM|✅|설계 단계|`SCHEMATIC_ONLY`, `PRE_LAYOUT`, `POST_LAYOUT`|
|`status`|ENUM|✅|진행 상태|`NOT_STARTED`, `IN_PROGRESS`, `COMPLETED`, `SIGNED_OFF`|
|`netlist_version`|STRING|❌|Netlist 버전|`"v2.3.1"`|
|`netlist_path`|STRING|❌|Netlist 기준 경로|`"/data/HBM4E/R30/netlist/"`|
|`required_applications`|ARRAY[STRING]|✅|필수 Signoff App ID 목록|`["DSC", "LSC", "PEC", "CANATR"]`|
|`release_date`|DATE|❌|릴리즈 일자||
|`created_at`|TIMESTAMP|✅|생성 시각||
|`updated_at`|TIMESTAMP|✅|수정 시각||

**Links:**

|관계명|방향|대상|카디널리티|설명|
|---|:-:|---|:-:|---|
|`of_product`|→|Product|N:1|소속 제품|
|`has_block`|→|Block|1:N|이 Revision의 Block들|
|`previous_revision`|→|Revision|N:1|이전 Revision (비교 기준)|
|`has_job`|←|SignoffJob|1:N|실행된 Job들|
|`requires_signoff`|→|SignoffApplication|N:M|필수 Signoff Application들|

**예시 Instance:**

```json
{
  "revision_id": "HBM4E_R30",
  "product_id": "HBM4E",
  "revision_code": "R30",
  "design_stage": "POST_LAYOUT",
  "status": "IN_PROGRESS",
  "netlist_version": "v2.3.1",
  "required_applications": ["DSC", "LSC", "LS", "PEC", "CANATR", "ADV_MARGIN"],
  "created_at": "2025-03-01T09:00:00Z"
}
```

**Revision별 Signoff 수행 범위:**

|Revision|설계 단계|주요 Signoff|
|---|---|---|
|R00~R20|Pre-Layout (Schematic)|Voltage Finder, PN Ratio, Floating Node, PEC|
|R30~R40|Post-Layout (RC 반영)|DSC, LSC, LS, Cana-TR|
|R50~R60|Final (Waveform 기반)|ADV Margin, Glitch, Dynamic DC Path|

---

#### 4.2.3 Block (회로 블록)

회로 설계의 **계층적 블록**이다. FULLCHIP, CORE, PHY, IP 등이 해당한다.

**역할**: Signoff 수행의 대상 단위. 계층 구조를 가지며, 각 Block은 담당 설계자가 지정된다.

**Properties:**

|속성명|타입|필수|설명|예시|
|---|---|:-:|---|---|
|`block_id`|STRING|✅|블록 고유 ID (PK)|`"HBM4E_R30_FULLCHIP"`|
|`revision_id`|STRING|✅|소속 Revision ID (FK)|`"HBM4E_R30"`|
|`block_name`|STRING|✅|블록 이름|`"FULLCHIP"`|
|`block_type`|ENUM|✅|블록 유형|`TOP`, `CORE`, `PHY`, `IO`, `IP`, `MACRO`|
|`hierarchy_path`|STRING|✅|계층 경로|`"/FULLCHIP/CORE/BL_DECODER"`|
|`parent_block_id`|STRING|❌|상위 블록 ID (FK)|`"HBM4E_R30_CORE"`|
|`instance_count`|INTEGER|❌|인스턴스 수|`128`|
|`description`|TEXT|❌|블록 설명||
|`created_at`|TIMESTAMP|✅|생성 시각||
|`updated_at`|TIMESTAMP|✅|수정 시각||

**Links:**

|관계명|방향|대상|카디널리티|설명|
|---|:-:|---|:-:|---|
|`of_revision`|→|Revision|N:1|소속 Revision|
|`parent_block`|→|Block|N:1|상위 블록|
|`child_blocks`|←|Block|1:N|하위 블록들|
|`responsible_designer`|→|Designer|N:1|담당 설계자|
|`has_job`|←|SignoffJob|1:N|이 Block 대상 Job들|

**예시 Instance:**

```json
{
  "block_id": "HBM4E_R30_FULLCHIP",
  "revision_id": "HBM4E_R30",
  "block_name": "FULLCHIP",
  "block_type": "TOP",
  "hierarchy_path": "/FULLCHIP",
  "parent_block_id": null,
  "instance_count": 1,
  "created_at": "2025-03-01T09:00:00Z"
}
```

---

#### 4.2.4 Designer (담당자)

설계자, Signoff 수행자, Application 개발자 등 **모든 구성원**을 포함한다.

**역할**: Signoff 업무에 참여하는 모든 인력. Block 담당, Job 실행, Issue 보고/해결 등의 주체가 된다.

**Properties:**

|속성명|타입|필수|설명|예시|
|---|---|:-:|---|---|
|`designer_id`|STRING|✅|담당자 고유 ID (PK)|`"kim_cs"`|
|`name`|STRING|✅|이름|`"김철수"`|
|`email`|STRING|✅|이메일|`"kim_cs@samsung.com"`|
|`employee_id`|STRING|❌|사번|`"A12345"`|
|`team`|STRING|✅|소속 팀|`"HBM Design Team"`|
|`role`|ENUM|✅|역할|`DESIGNER`, `LEAD`, `DEVELOPER`, `MANAGER`|
|`is_active`|BOOLEAN|✅|활성 여부|`true`|
|`created_at`|TIMESTAMP|✅|생성 시각||
|`updated_at`|TIMESTAMP|✅|수정 시각||

**Links:**

|관계명|방향|대상|카디널리티|설명|
|---|:-:|---|:-:|---|
|`responsible_for`|←|Block|1:N|담당 블록들|
|`manages`|←|Product|N:M|관리하는 제품들|
|`develops`|←|SignoffApplication|N:M|개발 담당 Application들|
|`executed_jobs`|←|SignoffJob|1:N|실행한 Job들|
|`reported_issues`|←|SignoffIssue|1:N|보고한 이슈들|
|`assigned_issues`|←|SignoffIssue|1:N|담당 이슈들|

**예시 Instance:**

```json
{
  "designer_id": "kim_cs",
  "name": "김철수",
  "email": "kim_cs@samsung.com",
  "employee_id": "A12345",
  "team": "HBM Design Team",
  "role": "DESIGNER",
  "is_active": true,
  "created_at": "2024-01-15T09:00:00Z"
}
```

---

#### 4.2.5 SignoffApplication (검증 도구)

DSC, LSC, PEC 등 **19종의 Signoff Application**을 정의한다.

**역할**: Signoff 검증 도구의 메타데이터. 실행 방법, 지원 조건, 비교 기준 등을 정의한다.

**Properties:**

|속성명|타입|필수|설명|예시|
|---|---|:-:|---|---|
|`app_id`|STRING|✅|Application ID (PK)|`"DSC"`|
|`app_name`|STRING|✅|전체 이름|`"Driver Size Check"`|
|`app_group`|ENUM|✅|그룹 분류|`PRE_LAYOUT`, `STATIC`, `DYNAMIC`, `TIMING`|
|`engine_type`|ENUM|✅|실행 엔진|`SPACE`, `ADV`, `PRIMESIM`, `PRIMETIME`|
|`comparison_key`|STRING|✅|결과 비교 기준 컬럼|`"measure_net,driver_nmos"`|
|`supported_pvt_corners`|ARRAY[STRING]|✅|지원 PVT 조건들|`["SSPLVCT", "FFPHVHT", "SSPLVHT"]`|
|`runscript_base_path`|STRING|✅|RUNSCRIPT 기준 경로|`"/RUNSCRIPTS/DSC/"`|
|`default_criteria_id`|STRING|❌|기본 CriteriaSet ID|`"DSC_DEFAULT_V1"`|
|`description`|TEXT|❌|Application 설명||
|`created_at`|TIMESTAMP|✅|생성 시각||
|`updated_at`|TIMESTAMP|✅|수정 시각||

**Links:**

|관계명|방향|대상|카디널리티|설명|
|---|:-:|---|:-:|---|
|`developed_by`|→|Designer|N:M|개발 담당자들|
|`has_criteria`|←|CriteriaSet|1:N|이 App의 Criteria들|
|`required_by`|←|Revision|N:M|이 App을 필수로 하는 Revision들|
|`used_by_jobs`|←|SignoffJob|1:N|이 App을 사용한 Job들|
|`related_issues`|←|SignoffIssue|1:N|이 App 관련 이슈들|

**예시 Instance:**

```json
{
  "app_id": "DSC",
  "app_name": "Driver Size Check",
  "app_group": "STATIC",
  "engine_type": "SPACE",
  "comparison_key": "measure_net,driver_nmos",
  "supported_pvt_corners": ["SSPLVCT", "SSPLVHT", "FFPHVHT"],
  "runscript_base_path": "/RUNSCRIPTS/DSC/",
  "default_criteria_id": "DSC_TAPEOUT_V3",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Signoff Application 전체 목록 (19종):**

|ID|이름|그룹|엔진|comparison_key|
|---|---|---|---|---|
|DSC|Driver Size Check|STATIC|SPACE|measure_net,driver_nmos|
|LSC|Latch Setup Check|STATIC|SPACE|master,latch_name|
|LS|Level Shifter|STATIC|SPACE|master|
|CANATR|Coupling Analysis TR|STATIC|SPACE|victim_net,aggressor_net|
|CDA|Coupling Delay Analysis|TIMING|SPACE|victim_net,aggressor_net|
|PEC|Power/ESD Checker|PRE_LAYOUT|SPACE|unit_name,msg|
|PNRATIO|PN Ratio Checker|PRE_LAYOUT|PERC|inst_name,cell_name|
|FANOUT|Fan-Out Checker|PRE_LAYOUT|PERC|drv_net|
|DCPATH|DC Path Checker|STATIC|PRIMESIM|path_id,node|
|FLOATNODE|Floating Node Checker|PRE_LAYOUT|SPACE|node_name|
|ADV_MARGIN|ADV Margin Analyzer|DYNAMIC|ADV|name,fullmaster|
|DRIVER_KEEPER|Driver Keeper|DYNAMIC|ADV|instance_name,target_master|
|GLITCH|Glitch Margin Check|DYNAMIC|ADV|name,fullmaster|
|DYNAMIC_DC_PATH|Dynamic DC Path|DYNAMIC|SPACE|id,instance|
|CURRENT_ANALYZER|Current Analyzer|DYNAMIC|ADV|-|
|PT_DSC|PrimeTime DSC|TIMING|PRIMETIME|net,driver_full_master|
|PT_CANA|PrimeTime Cana|TIMING|PRIMETIME|victim_net,victim_driver_full_master|
|BA_DUMP_NETLIST|BA Dump Netlist|PRE_LAYOUT|PRIMESIM|-|
|VOLTAGE_FINDER|Voltage Power Finder|PRE_LAYOUT|PRIMESIM|top_net_name|

---

#### 4.2.6 CriteriaSet (판정 기준)

Signoff Application별 **Pass/Fail 판정 기준**을 정의한다.

**역할**: 동일한 결과값이라도 적용하는 Criteria에 따라 Pass/Fail이 달라질 수 있다. Waiver 판단의 근거가 되며, AI가 판단 기준을 학습하는 데 핵심 데이터가 된다.

**Properties:**

|속성명|타입|필수|설명|예시|
|---|---|:-:|---|---|
|`criteria_id`|STRING|✅|Criteria 고유 ID (PK)|`"DSC_TAPEOUT_V3"`|
|`app_id`|STRING|✅|적용 Application ID (FK)|`"DSC"`|
|`criteria_name`|STRING|✅|Criteria 이름|`"DSC Tapeout Criteria v3"`|
|`version`|STRING|✅|버전|`"v3.0"`|
|`criteria_type`|ENUM|✅|유형|`TAPEOUT`, `EARLY_CHECK`, `CUSTOM`|
|`rules`|JSON|✅|판정 규칙 정의|_(아래 예시 참조)_|
|`is_active`|BOOLEAN|✅|활성 여부|`true`|
|`effective_date`|DATE|❌|적용 시작일|`"2025-01-01"`|
|`description`|TEXT|❌|Criteria 설명||
|`created_at`|TIMESTAMP|✅|생성 시각||
|`updated_at`|TIMESTAMP|✅|수정 시각||

**Links:**

|관계명|방향|대상|카디널리티|설명|
|---|:-:|---|:-:|---|
|`of_application`|→|SignoffApplication|N:1|적용 Application|
|`used_by_jobs`|←|SignoffJob|1:N|이 Criteria를 사용한 Job들|

**예시 Instance:**

```json
{
  "criteria_id": "DSC_TAPEOUT_V3",
  "app_id": "DSC",
  "criteria_name": "DSC Tapeout Criteria v3",
  "version": "v3.0",
  "criteria_type": "TAPEOUT",
  "rules": {
    "fail_conditions": [
      {"column": "margin", "operator": "<", "value": 0},
      {"column": "driver_size", "operator": "<", "value": "min_spec"}
    ],
    "warning_conditions": [
      {"column": "margin", "operator": "<", "value": 0.1}
    ],
    "waiver_allowed": true,
    "auto_waiver_patterns": ["known_issue_*", "corner_case_*"]
  },
  "is_active": true,
  "effective_date": "2025-01-01",
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

#### 4.2.7 Workspace (작업 공간)

Signoff 작업이 실행되고 결과가 저장되는 **작업 공간**이다.

**역할**: Local Workspace(개인 실행 공간)와 Central Workspace(결과 공유 공간)를 통합 관리한다. Local에서 실행 후 Central로 동기화하는 흐름을 추적한다.

**Properties:**

|속성명|타입|필수|설명|예시|
|---|---|:-:|---|---|
|`workspace_id`|STRING|✅|Workspace 고유 ID (PK)|`"WS-LOCAL-kim_cs-001"`|
|`workspace_type`|ENUM|✅|타입|`LOCAL`, `CENTRAL`|
|`base_path`|STRING|✅|기본 경로|`"/user/HBM4E/VERIFY/SIGNOFF/..."`|
|`product_id`|STRING|❌|관련 Product ID|`"HBM4E"`|
|`owner_id`|STRING|❌|소유자 Designer ID|`"kim_cs"`|
|`storage_name`|STRING|❌|Storage 이름|`"hbm4e_storage"`|
|`is_synced`|BOOLEAN|✅|Central 동기화 여부|`false`|
|`synced_to_workspace_id`|STRING|❌|동기화된 Central Workspace ID|`"WS-CENTRAL-HBM4E-001"`|
|`synced_at`|TIMESTAMP|❌|동기화 시각||
|`created_at`|TIMESTAMP|✅|생성 시각||
|`updated_at`|TIMESTAMP|✅|수정 시각||

**Links:**

|관계명|방향|대상|카디널리티|설명|
|---|:-:|---|:-:|---|
|`owned_by`|→|Designer|N:1|소유자 (Local의 경우)|
|`of_product`|→|Product|N:1|관련 제품 (Central의 경우)|
|`synced_to`|→|Workspace|N:1|동기화 대상 Central Workspace|
|`has_jobs`|←|SignoffJob|1:N|이 공간에서 실행된 Job들|
|`stores_results`|←|Result|1:N|저장된 Result들|

**예시 Instance (Local):**

```json
{
  "workspace_id": "WS-LOCAL-kim_cs-001",
  "workspace_type": "LOCAL",
  "base_path": "/user/HBM4E/VERIFY/SIGNOFF/LIB/FULLCHIP/kim_cs/",
  "product_id": "HBM4E",
  "owner_id": "kim_cs",
  "storage_name": "hbm4e_storage",
  "is_synced": true,
  "synced_to_workspace_id": "WS-CENTRAL-HBM4E-001",
  "synced_at": "2025-01-19T15:30:00Z",
  "created_at": "2025-01-19T14:30:00Z"
}
```

**예시 Instance (Central):**

```json
{
  "workspace_id": "WS-CENTRAL-HBM4E-001",
  "workspace_type": "CENTRAL",
  "base_path": "/WORKSPACE/HBM4E/",
  "product_id": "HBM4E",
  "owner_id": null,
  "is_synced": true,
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

### 4.3 Kinetic Layer Objects (2개)

> **Kinetic Layer**는 시간의 흐름에 따라 발생하는 **이벤트와 행위(The Verbs)**를 정의한다. 이 Layer의 Object들은 "누가, 무엇을 가지고, 언제, 어떤 행위를 했는가"를 기록한다.

---
#### 4.3.1 SignoffJob (실행 이벤트)

실제 LSF에서 실행되는 **Signoff 작업 단위**이다. InputConfig 정보를 포함한다.

**역할**: Signoff 실행의 핵심 이벤트. 입력 설정, 실행 상태, 결과 연결 등 모든 실행 정보를 담는다. 동일 조건으로 재실행 시 새로운 Job이 생성된다.

**Properties:**

|속성명|타입|필수|설명|예시|
|---|---|---|---|---|
|**식별 정보**|||||
|`job_id`|STRING|✅|Job 고유 ID (PK)|`"JOB-20250119-143022-001"`|
|`revision_id`|STRING|✅|대상 Revision (FK)|`"HBM4E_R30"`|
|`block_id`|STRING|✅|대상 Block (FK)|`"HBM4E_R30_FULLCHIP"`|
|`app_id`|STRING|✅|사용 Application (FK)|`"DSC"`|
|`criteria_id`|STRING|✅|사용 Criteria (FK)|`"DSC_TAPEOUT_V3"`|
|`workspace_id`|STRING|✅|실행 Workspace (FK)|`"WS-LOCAL-kim_cs-001"`|
|`executed_by`|STRING|✅|실행자 Designer ID (FK)|`"kim_cs"`|
|**입력 설정 (InputConfig 통합)**|||||
|`netlist_path`|STRING|✅|Netlist 파일 경로|`"/data/HBM4E/R30/netlist.sp"`|
|`tech_file_path`|STRING|✅|Tech 파일 경로|`"/tech/4nm/tech.tf"`|
|`power_definition`|JSON|✅|Power 정의 정보|`{"VDD": ["vdd_core"], "VSS": ["vss"]}`|
|`pvt_corner`|STRING|✅|PVT 조건|`"SSPLVCT"`|
|`simulation_params`|JSON|❌|추가 시뮬레이션 파라미터|`{"threshold": 0.1, "max_iter": 100}`|
|**실행 상태**|||||
|`status`|ENUM|✅|실행 상태|`PENDING`, `RUNNING`, `DONE`, `FAILED`, `CANCELLED`|
|`lsf_job_id`|STRING|❌|LSF Job ID|`"12345678"`|
|`queue_name`|STRING|❌|LSF Queue 이름|`"normal"`|
|`submission_time`|TIMESTAMP|❌|제출 시각||
|`start_time`|TIMESTAMP|❌|시작 시각||
|`completion_time`|TIMESTAMP|❌|완료 시각||
|`runtime_seconds`|INTEGER|❌|실행 시간(초)|`43800`|
|**실행 환경**|||||
|`job_directory`|STRING|❌|실행 디렉토리 경로|`"/user/.../DSC_20250119_143022/"`|
|`log_path`|STRING|❌|로그 파일 경로|`"/user/.../logs/pipeline.log"`|
|`error_message`|TEXT|❌|에러 메시지 (실패 시)||
|**이력 관리**|||||
|`previous_job_id`|STRING|❌|재실행 시 이전 Job ID|`"JOB-20250118-001"`|
|`rerun_reason`|STRING|❌|재실행 사유|`"Power 설정 오류 수정"`|
|`created_at`|TIMESTAMP|✅|생성 시각||
|`updated_at`|TIMESTAMP|✅|수정 시각||

**Links:**

|관계명|방향|대상|카디널리티|설명|
|---|---|---|---|---|
|`of_revision`|→|Revision|N:1|대상 Revision|
|`targets_block`|→|Block|N:1|대상 Block|
|`uses_application`|→|SignoffApplication|N:1|사용 Application|
|`uses_criteria`|→|CriteriaSet|N:1|사용 Criteria|
|`executes_in`|→|Workspace|N:1|실행 Workspace|
|`executed_by`|→|Designer|N:1|실행자|
|`produces`|→|Result|1:1|생성된 결과|
|`previous_job`|→|SignoffJob|N:1|재실행 시 이전 Job|

**예시 Instance:**

json

```json
{
  "job_id": "JOB-20250119-143022-001",
  "revision_id": "HBM4E_R30",
  "block_id": "HBM4E_R30_FULLCHIP",
  "app_id": "DSC",
  "criteria_id": "DSC_TAPEOUT_V3",
  "workspace_id": "WS-LOCAL-kim_cs-001",
  "executed_by": "kim_cs",
  
  "netlist_path": "/data/HBM4E/R30/netlist.sp",
  "tech_file_path": "/tech/4nm/tech.tf",
  "power_definition": {
    "VDD": ["vdd_core", "vdd_io"],
    "VSS": ["vss_core", "vss_io"],
    "VDDQ": ["vddq_0", "vddq_1"]
  },
  "pvt_corner": "SSPLVCT",
  "simulation_params": {
    "temperature": 25,
    "voltage_margin": 0.05
  },
  
  "status": "DONE",
  "lsf_job_id": "12345678",
  "queue_name": "normal",
  "submission_time": "2025-01-19T14:30:22Z",
  "start_time": "2025-01-19T14:35:00Z",
  "completion_time": "2025-01-20T02:45:00Z",
  "runtime_seconds": 43800,
  
  "job_directory": "/user/HBM4E/VERIFY/SIGNOFF/LIB/FULLCHIP/kim_cs/DSC_20250119_143022/",
  "log_path": "/user/.../DSC_20250119_143022/logs/pipeline.log",
  
  "previous_job_id": null,
  "created_at": "2025-01-19T14:30:22Z",
  "updated_at": "2025-01-20T02:45:00Z"
}
```

**상태 전이 다이어그램:**

```
                    ┌─────────────────────────────────────────┐
                    │                                         │
                    ▼                                         │
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│ PENDING │───▶│ RUNNING │───▶│  DONE   │    │ FAILED  │     │
└─────────┘    └────┬────┘    └─────────┘    └────┬────┘     │
                    │                             │          │
                    │         ┌───────────┐       │          │
                    └────────▶│ CANCELLED │◀──────┘          │
                              └───────────┘                  │
                                    │                        │
                                    └── (재실행) ─────────────┘
```

---

#### 4.3.2 Result (검증 결과)

SignoffJob에서 생성된 **검증 결과**이다.

**역할**: Signoff 실행의 산출물. Row 단위 통계(전체/Waiver/Fixed/미처리)를 관리하고, Central Workspace 업로드 상태를 추적한다.

**Properties:**

|속성명|타입|필수|설명|예시|
|---|---|---|---|---|
|**식별 정보**|||||
|`result_id`|STRING|✅|Result 고유 ID (PK)|`"RESULT-20250119-001"`|
|`job_id`|STRING|✅|생성 Job ID (FK)|`"JOB-20250119-143022-001"`|
|`workspace_id`|STRING|✅|저장 Workspace ID (FK)|`"WS-LOCAL-kim_cs-001"`|
|**결과 파일 정보**|||||
|`result_file_path`|STRING|✅|결과 파일 경로|`"/user/.../result.parquet"`|
|`result_format`|ENUM|✅|파일 형식|`CSV`, `PARQUET`|
|`file_size_bytes`|BIGINT|❌|파일 크기|`1048576`|
|**Row 통계**|||||
|`row_count`|INTEGER|✅|전체 Row 수|`1500`|
|`pass_count`|INTEGER|✅|Pass 수|`0`|
|`fail_count`|INTEGER|✅|Fail 수 (미처리)|`1500`|
|`waiver_count`|INTEGER|✅|Waiver 처리 수|`0`|
|`fixed_count`|INTEGER|✅|Fixed 처리 수|`0`|
|**진행 상태**|||||
|`analysis_status`|ENUM|✅|분석 상태|`PENDING`, `IN_PROGRESS`, `COMPLETED`|
|`waiver_progress_pct`|FLOAT|✅|Waiver 진행률 (%)|`0.0`|
|**Central 동기화**|||||
|`is_uploaded`|BOOLEAN|✅|Central 업로드 여부|`false`|
|`central_workspace_id`|STRING|❌|업로드된 Central Workspace ID||
|`uploaded_at`|TIMESTAMP|❌|업로드 시각||
|**메타데이터**|||||
|`created_at`|TIMESTAMP|✅|생성 시각||
|`updated_at`|TIMESTAMP|✅|수정 시각||

**Links:**

|관계명|방향|대상|카디널리티|설명|
|---|---|---|---|---|
|`produced_by`|→|SignoffJob|1:1|생성한 Job|
|`stored_in`|→|Workspace|N:1|저장 Workspace|
|`uploaded_to`|→|Workspace|N:1|업로드된 Central Workspace|
|`has_comparison`|←|CompareResult|1:N|비교 결과들|
|`has_categorization`|←|CategorizePart|1:N|담당자 지정 내역|
|`has_waiver_decisions`|←|WaiverDecision|1:N|Waiver 판단들|

**예시 Instance:**

json

```json
{
  "result_id": "RESULT-20250119-001",
  "job_id": "JOB-20250119-143022-001",
  "workspace_id": "WS-LOCAL-kim_cs-001",
  
  "result_file_path": "/user/HBM4E/VERIFY/SIGNOFF/.../result.parquet",
  "result_format": "PARQUET",
  "file_size_bytes": 2097152,
  
  "row_count": 1500,
  "pass_count": 0,
  "fail_count": 1500,
  "waiver_count": 0,
  "fixed_count": 0,
  
  "analysis_status": "PENDING",
  "waiver_progress_pct": 0.0,
  
  "is_uploaded": false,
  "central_workspace_id": null,
  "uploaded_at": null,
  
  "created_at": "2025-01-20T02:45:00Z",
  "updated_at": "2025-01-20T02:45:00Z"
}
```

**Result 업데이트 흐름:**

```
1. Job 완료 → Result 생성 (row_count=1500, fail_count=1500, waiver=0, fixed=0)
                            analysis_status=PENDING
                            
2. Central 업로드 → is_uploaded=true, central_workspace_id 설정
                   → CompareResult 생성 (이전 Revision과 비교)
                   → CategorizePart 생성 (담당자 지정)
                   
3. 분석 진행 → analysis_status=IN_PROGRESS
              → WaiverDecision 생성될 때마다 waiver_count++, fail_count--
              → waiver_progress_pct 업데이트
              
4. 분석 완료 → analysis_status=COMPLETED
              → waiver_progress_pct = (waiver_count + fixed_count) / row_count * 100
```

---

### 4.4 Dynamic Layer Objects (4개)

> **Dynamic Layer**는 실행 결과에 대한 **판단과 의사결정(The Brains)**을 정의한다. 이 Layer의 Object들은 인간/AI의 지능적 활동 결과를 기록하며, 향후 AI 학습의 핵심 데이터가 된다.

---

#### 4.4.1 CategorizePart (담당자 지정)

Result 업로드 시 각 Part(항목 그룹)의 **담당자를 지정**하는 의사결정이다.

**역할**: 대량의 결과를 효율적으로 분배하고, "누가 이 항목을 분석해야 하는지"를 명확히 한다. 향후 AI가 자동 분류를 학습하는 데 활용된다.

**Properties:**

|속성명|타입|필수|설명|예시|
|---|---|---|---|---|
|`categorize_id`|STRING|✅|지정 고유 ID (PK)|`"CAT-20250120-001"`|
|`result_id`|STRING|✅|대상 Result ID (FK)|`"RESULT-20250119-001"`|
|`category_name`|STRING|✅|분류 이름|`"CORE_BLOCK"`|
|`category_rule`|JSON|✅|분류 규칙|`{"column": "hierarchy", "pattern": "*CORE*"}`|
|`assigned_to`|STRING|✅|담당자 Designer ID (FK)|`"kim_cs"`|
|`row_count`|INTEGER|✅|해당 Row 수|`500`|
|`assignment_type`|ENUM|✅|지정 방식|`AUTO`, `MANUAL`|
|`assigned_by`|STRING|❌|지정자 (MANUAL인 경우)|`"lee_yh"`|
|`created_at`|TIMESTAMP|✅|생성 시각||

**Links:**

|관계명|방향|대상|카디널리티|설명|
|---|---|---|---|---|
|`of_result`|→|Result|N:1|대상 Result|
|`assigned_to`|→|Designer|N:1|담당자|
|`assigned_by`|→|Designer|N:1|지정자|

**예시 Instance:**

json

```json
{
  "categorize_id": "CAT-20250120-001",
  "result_id": "RESULT-20250119-001",
  "category_name": "CORE_BLOCK",
  "category_rule": {
    "column": "hierarchy",
    "pattern": "*CORE*"
  },
  "assigned_to": "kim_cs",
  "row_count": 500,
  "assignment_type": "AUTO",
  "assigned_by": null,
  "created_at": "2025-01-20T10:00:00Z"
}
```

---

#### 4.4.2 CompareResult (비교 결과)

이전 Revision 결과와 **비교 분석**한 결과이다.

**역할**: Waiver Migration의 근거 데이터. "뭐가 바뀌었는지"를 AI가 이해하고, 설계 변경 영향도를 분석하는 데 활용된다.

**Properties:**

|속성명|타입|필수|설명|예시|
|---|---|---|---|---|
|`compare_id`|STRING|✅|비교 고유 ID (PK)|`"CMP-20250120-001"`|
|`source_result_id`|STRING|✅|이전(Source) Result ID (FK)|`"RESULT-R20-001"`|
|`target_result_id`|STRING|✅|현재(Target) Result ID (FK)|`"RESULT-R30-001"`|
|**비교 통계**|||||
|`new_fail_count`|INTEGER|✅|새로 발생한 Fail 수|`50`|
|`fixed_count`|INTEGER|✅|해결된 항목 수 (이전 Fail → 현재 Pass)|`30`|
|`regressed_count`|INTEGER|✅|회귀 항목 수 (이전 Pass → 현재 Fail)|`10`|
|`unchanged_fail_count`|INTEGER|✅|유지된 Fail 수|`1410`|
|`waiver_migrated_count`|INTEGER|✅|Waiver 이관된 수|`1200`|
|**메타데이터**|||||
|`comparison_key_used`|STRING|✅|비교에 사용된 Key|`"measure_net,driver_nmos"`|
|`compared_by`|STRING|❌|비교 실행자 (수동인 경우)|`"kim_cs"`|
|`comparison_type`|ENUM|✅|비교 유형|`AUTO_ON_UPLOAD`, `MANUAL`|
|`created_at`|TIMESTAMP|✅|생성 시각||

**Links:**

|관계명|방향|대상|카디널리티|설명|
|---|---|---|---|---|
|`source_result`|→|Result|N:1|이전 Result (비교 기준)|
|`target_result`|→|Result|N:1|현재 Result (비교 대상)|
|`compared_by`|→|Designer|N:1|비교 실행자|
|`has_waiver_migrations`|←|WaiverDecision|1:N|이 비교로 인한 Waiver 이관들|

**예시 Instance:**

json

```json
{
  "compare_id": "CMP-20250120-001",
  "source_result_id": "RESULT-R20-001",
  "target_result_id": "RESULT-R30-001",
  
  "new_fail_count": 50,
  "fixed_count": 30,
  "regressed_count": 10,
  "unchanged_fail_count": 1410,
  "waiver_migrated_count": 1200,
  
  "comparison_key_used": "measure_net,driver_nmos",
  "compared_by": null,
  "comparison_type": "AUTO_ON_UPLOAD",
  "created_at": "2025-01-20T10:05:00Z"
}
```

**비교 결과 시각화:**

```
┌─────────────────────────────────────────────────────────────────┐
│  R20 (Source)                    R30 (Target)                   │
│  ─────────────                   ─────────────                  │
│  Total: 1500                     Total: 1540                    │
│                                                                 │
│  ┌─────────────┐                 ┌─────────────┐               │
│  │   Fail      │────────────────▶│ Unchanged   │  1410건       │
│  │   1500건    │                 │   Fail      │               │
│  │             │                 ├─────────────┤               │
│  │             │─── Fixed ──────▶│   Pass      │  30건         │
│  └─────────────┘                 ├─────────────┤               │
│                                  │  New Fail   │  50건         │
│  ┌─────────────┐                 ├─────────────┤               │
│  │   Pass      │─── Regressed ──▶│  Regressed  │  10건         │
│  └─────────────┘                 └─────────────┘               │
│                                                                 │
│  Waiver 이관 가능: 1410건 중 1200건 (이전 Waiver 기준 매칭)      │
└─────────────────────────────────────────────────────────────────┘
```

---

#### 4.4.3 WaiverDecision (Waiver 판단)

Waiver 처리에 대한 **의사결정 이력**을 기록한다.

**역할**: "왜 이 항목을 Waiver했는지"에 대한 판단 근거를 축적한다. AI가 Waiver 패턴을 학습하여 자동 추천하는 데 핵심 데이터가 된다.

**Properties:**

|속성명|타입|필수|설명|예시|
|---|---|---|---|---|
|`decision_id`|STRING|✅|의사결정 고유 ID (PK)|`"WD-20250120-001"`|
|`result_id`|STRING|✅|대상 Result ID (FK)|`"RESULT-20250119-001"`|
|**결정 내용**|||||
|`decision_type`|ENUM|✅|결정 유형|`WAIVER`, `FIXED`, `PENDING`, `FALSE_POSITIVE`|
|`affected_row_ids`|ARRAY[STRING]|✅|영향받은 Row ID들|`["row_001", "row_002", ...]`|
|`affected_row_count`|INTEGER|✅|영향받은 Row 수|`50`|
|**판단 근거**|||||
|`decision_reason`|TEXT|✅|판단 근거 (자유 텍스트)|`"Known corner case, approved by lead"`|
|`reason_category`|ENUM|❌|근거 유형|`KNOWN_ISSUE`, `CORNER_CASE`, `DESIGN_INTENT`, `TOOL_LIMITATION`|
|**이관 정보**|||||
|`is_migrated`|BOOLEAN|✅|이전 Revision에서 이관 여부|`true`|
|`source_decision_id`|STRING|❌|이관 원본 Decision ID|`"WD-R20-001"`|
|`compare_result_id`|STRING|❌|관련 CompareResult ID|`"CMP-20250120-001"`|
|**결정자 정보**|||||
|`decided_by`|STRING|✅|결정자 Designer ID (FK)|`"kim_cs"`|
|`approved_by`|STRING|❌|승인자 Designer ID (FK)|`"lee_yh"`|
|`decided_at`|TIMESTAMP|✅|결정 시각||
|`approved_at`|TIMESTAMP|❌|승인 시각||
|**메타데이터**|||||
|`created_at`|TIMESTAMP|✅|생성 시각||
|`updated_at`|TIMESTAMP|✅|수정 시각||

**Links:**

|관계명|방향|대상|카디널리티|설명|
|---|---|---|---|---|
|`for_result`|→|Result|N:1|대상 Result|
|`decided_by`|→|Designer|N:1|결정자|
|`approved_by`|→|Designer|N:1|승인자|
|`migrated_from`|→|WaiverDecision|N:1|이관 원본|
|`via_comparison`|→|CompareResult|N:1|관련 비교 결과|

**예시 Instance:**

json

```json
{
  "decision_id": "WD-20250120-001",
  "result_id": "RESULT-20250119-001",
  
  "decision_type": "WAIVER",
  "affected_row_ids": ["row_001", "row_002", "row_003"],
  "affected_row_count": 3,
  
  "decision_reason": "Known corner case in CORE block. Same pattern waived in R20. Approved by design lead.",
  "reason_category": "CORNER_CASE",
  
  "is_migrated": true,
  "source_decision_id": "WD-R20-001",
  "compare_result_id": "CMP-20250120-001",
  
  "decided_by": "kim_cs",
  "approved_by": "lee_yh",
  "decided_at": "2025-01-20T11:30:00Z",
  "approved_at": "2025-01-20T14:00:00Z",
  
  "created_at": "2025-01-20T11:30:00Z",
  "updated_at": "2025-01-20T14:00:00Z"
}
```

---

#### 4.4.4 SignoffIssue (이슈/문의)

Signoff 수행 전체 라이프사이클에서 발생하는 **문의 및 이슈**를 기록한다.

**역할**: GUI 사용법, 시뮬레이션 에러, 결과 분석 등 다양한 시점의 문의를 관리한다. 해결 이력을 축적하여 반복 문의를 줄이고, AI 자동 답변의 학습 데이터가 된다.

**발생 시점:**

```
[수행 전]              [수행 중]              [수행 후]
    │                      │                      │
    ▼                      ▼                      ▼
┌──────────┐        ┌──────────────┐        ┌──────────────┐
│GUI 사용법│        │ Simulation   │        │ 결과 분석    │
│   문의   │        │  에러 문의   │        │    문의      │
└──────────┘        └──────────────┘        └──────────────┘
```

**Properties:**

| 속성명             | 타입            | 필수  | 설명                     | 예시                                                                                         |
| --------------- | ------------- | --- | ---------------------- | ------------------------------------------------------------------------------------------ |
| `issue_id`      | STRING        | ✅   | 이슈 고유 ID (PK)          | `"ISSUE-20250120-001"`                                                                     |
| `mlm_ticket_id` | STRING        | ❌   | MLM Jira 티켓 ID (연동 시)  | `"MLM-12345"`                                                                              |
| **이슈 내용**       |               |     |                        |                                                                                            |
| `title`         | STRING        | ✅   | 이슈 제목                  | `"DSC Power 설정 오류"`                                                                        |
| `description`   | TEXT          | ✅   | 상세 설명                  |                                                                                            |
| `issue_type`    | ENUM          | ✅   | 이슈 유형                  | `USAGE_GUIDE`, `SIMULATION_ERROR`, `RESULT_ANALYSIS`, `BUG_REPORT`, `ENHANCEMENT`, `OTHER` |
| **관련 정보**       |               |     |                        |                                                                                            |
| `app_id`        | STRING        | ✅   | 관련 Application ID (FK) | `"DSC"`                                                                                    |
| `job_id`        | STRING        | ❌   | 관련 Job ID (FK)         | `"JOB-20250119-001"`                                                                       |
| `result_id`     | STRING        | ❌   | 관련 Result ID (FK)      | `"RESULT-20250119-001"`                                                                    |
| **담당자**         |               |     |                        |                                                                                            |
| `reported_by`   | STRING        | ✅   | 보고자 Designer ID (FK)   | `"kim_cs"`                                                                                 |
| `assigned_to`   | STRING        | ❌   | 담당자 Designer ID (FK)   | `"park_dev"`                                                                               |
| **상태 관리**       |               |     |                        |                                                                                            |
| `status`        | ENUM          | ✅   | 처리 상태                  | `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`, `WONT_FIX`                                    |
| `priority`      | ENUM          | ❌   | 우선순위                   | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`                                                        |
| **해결 정보**       |               |     |                        |                                                                                            |
| `resolution`    | TEXT          | ❌   | 해결 방법                  | `"Power 정의 파일에서 VDD net 이름 오타 수정"`                                                         |
| `resolved_at`   | TIMESTAMP     | ❌   | 해결 시각                  |                                                                                            |
| **검색/분류**       |               |     |                        |                                                                                            |
| `tags`          | ARRAY[STRING] | ❌   | 태그 목록                  | `["power", "input_error", "config"]`                                                       |
| `keywords`      | ARRAY[STRING] | ❌   | 검색 키워드                 | `["VDD", "power_definition", "net_name"]`                                                  |
| **메타데이터**       |               |     |                        |                                                                                            |
| `created_at`    | TIMESTAMP     | ✅   | 생성 시각                  |                                                                                            |
| `updated_at`    | TIMESTAMP     | ✅   | 수정 시각                  |                                                                                            |
