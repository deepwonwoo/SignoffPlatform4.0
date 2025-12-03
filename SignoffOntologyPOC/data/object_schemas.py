"""
Signoff Ontology Object Type 스키마 정의
"05. Signoff Platform Ontology 구축" 문서 기반
"""

OBJECT_SCHEMAS = {
    # ===== Semantic Layer =====
    "Product": {
        "layer": "Semantic",
        "color": "#4263eb",
        "description": "메모리 제품의 최상위 개체 (HBM4E, DDR5 등)",
        "properties": [
            {"name": "product_id", "type": "STRING", "required": True, "description": "제품 고유 ID"},
            {"name": "product_name", "type": "STRING", "required": True, "description": "제품 전체 이름"},
            {"name": "product_type", "type": "ENUM", "required": True, "description": "제품 종류", "options": ["HBM", "DRAM", "FLASH"]},
            {"name": "status", "type": "ENUM", "required": True, "description": "개발 상태", "options": ["ACTIVE", "COMPLETED"]},
            {"name": "created_at", "type": "TIMESTAMP", "required": True, "description": "생성 시각"},
        ],
        "links": [
            {"name": "has_revision", "target": "Revision", "cardinality": "1:N", "description": "제품의 설계 버전들"},
            {"name": "managed_by", "target": "Designer", "cardinality": "N:M", "description": "제품 담당 관리자들"},
        ]
    },
    
    "Revision": {
        "layer": "Semantic",
        "color": "#5c7cfa",
        "description": "설계 버전 (R00~R60). Signoff 기준 단위",
        "properties": [
            {"name": "revision_id", "type": "STRING", "required": True, "description": "리비전 고유 ID"},
            {"name": "product_id", "type": "STRING", "required": True, "description": "소속 제품 ID"},
            {"name": "revision_code", "type": "ENUM", "required": True, "description": "리비전 코드", "options": ["R00", "R10", "R20", "R30", "R40", "R50", "R60"]},
            {"name": "phase", "type": "STRING", "required": True, "description": "설계 단계"},
            {"name": "required_applications", "type": "ARRAY", "required": True, "description": "필수 Signoff 목록"},
            {"name": "previous_revision_id", "type": "STRING", "required": False, "description": "이전 리비전 ID"},
            {"name": "created_at", "type": "TIMESTAMP", "required": True, "description": "생성 시각"},
        ],
        "links": [
            {"name": "of_product", "target": "Product", "cardinality": "N:1", "description": "소속 제품"},
            {"name": "has_block", "target": "Block", "cardinality": "1:N", "description": "이 Revision의 Block들"},
            {"name": "defines_required_signoff", "target": "SignoffApplication", "cardinality": "N:M", "description": "수행해야 할 Application들"},
            {"name": "previous_version", "target": "Revision", "cardinality": "N:1", "description": "이전 Revision"},
            {"name": "has_task", "target": "SignoffTask", "cardinality": "1:N", "description": "생성된 작업들"},
        ]
    },
    
    "Block": {
        "layer": "Semantic",
        "color": "#748ffc",
        "description": "회로 설계의 계층적 블록. Signoff 검증의 대상 단위",
        "properties": [
            {"name": "block_id", "type": "STRING", "required": True, "description": "블록 고유 ID"},
            {"name": "revision_id", "type": "STRING", "required": True, "description": "소속 리비전 ID"},
            {"name": "block_name", "type": "STRING", "required": True, "description": "블록 이름"},
            {"name": "block_type", "type": "ENUM", "required": False, "description": "블록 유형", "options": ["ANALOG", "DIGITAL", "IO", "MIXED"]},
            {"name": "designer_id", "type": "STRING", "required": True, "description": "담당 설계자 ID"},
            {"name": "instance_count", "type": "INTEGER", "required": False, "description": "트랜지스터 인스턴스 수"},
            {"name": "created_at", "type": "TIMESTAMP", "required": True, "description": "생성 시각"},
        ],
        "links": [
            {"name": "of_revision", "target": "Revision", "cardinality": "N:1", "description": "소속 리비전"},
            {"name": "responsible_designer", "target": "Designer", "cardinality": "N:1", "description": "담당 설계자"},
            {"name": "requires_signoff_task", "target": "SignoffTask", "cardinality": "1:N", "description": "필요한 Signoff 작업들"},
        ]
    },
    
    "Designer": {
        "layer": "Semantic",
        "color": "#fab005",
        "description": "설계자, 검증 담당자, 툴 개발자 등 사람의 정보",
        "properties": [
            {"name": "designer_id", "type": "STRING", "required": True, "description": "사용자 고유 ID"},
            {"name": "name", "type": "STRING", "required": True, "description": "이름"},
            {"name": "email", "type": "STRING", "required": False, "description": "이메일"},
            {"name": "team", "type": "STRING", "required": True, "description": "소속 팀"},
            {"name": "role", "type": "ENUM", "required": True, "description": "역할", "options": ["ENGINEER", "LEAD", "MANAGER", "DEVELOPER"]},
            {"name": "created_at", "type": "TIMESTAMP", "required": True, "description": "생성 시각"},
        ],
        "links": [
            {"name": "manages_product", "target": "Product", "cardinality": "N:M", "description": "관리하는 제품들"},
            {"name": "responsible_for_block", "target": "Block", "cardinality": "1:N", "description": "담당 블록들"},
            {"name": "owns_task", "target": "SignoffTask", "cardinality": "1:N", "description": "담당 Task들"},
        ]
    },
    
    "SignoffApplication": {
        "layer": "Semantic",
        "color": "#fd7e14",
        "description": "Signoff 단계에서 사용되는 검증 도구/방법론 (19종)",
        "properties": [
            {"name": "app_id", "type": "STRING", "required": True, "description": "Application 고유 ID"},
            {"name": "app_name", "type": "STRING", "required": True, "description": "표시 이름"},
            {"name": "app_group", "type": "ENUM", "required": True, "description": "그룹 분류", "options": ["Pre-Layout", "Post-Layout", "Dynamic"]},
            {"name": "engine_type", "type": "ENUM", "required": True, "description": "엔진 종류", "options": ["SPACE", "ADV", "PrimeTime", "PERC"]},
            {"name": "default_pvt_conditions", "type": "ARRAY", "required": False, "description": "기본 PVT 조건들"},
            {"name": "created_at", "type": "TIMESTAMP", "required": True, "description": "생성 시각"},
        ],
        "links": [
            {"name": "required_by_revision", "target": "Revision", "cardinality": "N:M", "description": "필요로 하는 Revision들"},
            {"name": "used_by_task", "target": "SignoffTask", "cardinality": "1:N", "description": "사용하는 Task들"},
            {"name": "developed_by", "target": "Designer", "cardinality": "N:1", "description": "담당 개발자"},
        ]
    },
    
    # ===== Kinetic Layer =====
    "SignoffTask": {
        "layer": "Kinetic",
        "color": "#40c057",
        "description": "Block에 대해 특정 Application을 특정 조건으로 수행하는 작업 단위",
        "properties": [
            {"name": "task_id", "type": "STRING", "required": True, "description": "Task 고유 ID"},
            {"name": "revision_id", "type": "STRING", "required": True, "description": "대상 Revision ID"},
            {"name": "block_id", "type": "STRING", "required": True, "description": "대상 Block ID"},
            {"name": "app_id", "type": "STRING", "required": True, "description": "사용 Application ID"},
            {"name": "owner_id", "type": "STRING", "required": True, "description": "실행 담당자 ID"},
            {"name": "pvt_corner", "type": "STRING", "required": True, "description": "PVT 조건 (예: SSPLVCT)"},
            {"name": "status", "type": "ENUM", "required": True, "description": "상태", "options": ["PENDING", "RUNNING", "DONE", "FAILED"]},
            {"name": "lsf_job_id", "type": "STRING", "required": False, "description": "LSF Job ID"},
            {"name": "submission_time", "type": "TIMESTAMP", "required": False, "description": "제출 시각"},
            {"name": "completion_time", "type": "TIMESTAMP", "required": False, "description": "완료 시각"},
            {"name": "created_at", "type": "TIMESTAMP", "required": True, "description": "생성 시각"},
        ],
        "links": [
            {"name": "targets", "target": "Block", "cardinality": "N:1", "description": "대상 블록"},
            {"name": "uses_application", "target": "SignoffApplication", "cardinality": "N:1", "description": "사용 Application"},
            {"name": "belongs_to_revision", "target": "Revision", "cardinality": "N:1", "description": "소속 Revision"},
            {"name": "owned_by", "target": "Designer", "cardinality": "N:1", "description": "실행 담당자"},
            {"name": "produces", "target": "Result", "cardinality": "1:1", "description": "생성한 결과"},
        ]
    },

    "SignoffJob": {
        "layer": "Kinetic",
        "color": "#51cf66",
        "description": "SignoffTask의 실제 실행 인스턴스 (LSF Job 등)",
        "properties": [
            {"name": "job_id", "type": "STRING", "required": True, "description": "Job 고유 ID"},
            {"name": "task_id", "type": "STRING", "required": True, "description": "소속 Task ID"},
            {"name": "status", "type": "ENUM", "required": True, "description": "실행 상태", "options": ["PENDING", "RUNNING", "DONE", "FAILED"]},
            {"name": "start_time", "type": "TIMESTAMP", "required": False, "description": "시작 시각"},
            {"name": "end_time", "type": "TIMESTAMP", "required": False, "description": "종료 시각"},
            {"name": "workspace_path", "type": "STRING", "required": True, "description": "작업 공간 경로"},
            {"name": "error_msg", "type": "STRING", "required": False, "description": "에러 메시지"},
            {"name": "created_at", "type": "TIMESTAMP", "required": True, "description": "생성 시각"},
        ],
        "links": [
            {"name": "executes_task", "target": "SignoffTask", "cardinality": "1:1", "description": "실행하는 Task"},
            {"name": "produces_result", "target": "Result", "cardinality": "1:1", "description": "생성 결과"},
            {"name": "uses_workspace", "target": "Workspace", "cardinality": "1:1", "description": "사용 Workspace"},
        ]
    },
    
    "InputConfig": {
        "layer": "Kinetic",
        "color": "#69db7c",
        "description": "Signoff 실행에 필요한 입력 설정 (Netlist, Power 정의 등)",
        "properties": [
            {"name": "config_id", "type": "STRING", "required": True, "description": "설정 고유 ID"},
            {"name": "task_id", "type": "STRING", "required": True, "description": "소속 Task ID"},
            {"name": "netlist_path", "type": "STRING", "required": True, "description": "Netlist 파일 경로"},
            {"name": "power_definition", "type": "JSON", "required": False, "description": "Power 정의 정보"},
            {"name": "validation_status", "type": "ENUM", "required": False, "description": "검증 상태", "options": ["VALID", "INVALID", "WARNING"]},
            {"name": "created_at", "type": "TIMESTAMP", "required": True, "description": "생성 시각"},
        ],
        "links": [
            {"name": "used_by_task", "target": "SignoffTask", "cardinality": "1:1", "description": "사용하는 Task"},
        ]
    },
    
    "Workspace": {
        "layer": "Kinetic",
        "color": "#8ce99a",
        "description": "Signoff 작업이 실행되고 결과가 저장되는 공간 (Local/Central)",
        "properties": [
            {"name": "workspace_id", "type": "STRING", "required": True, "description": "Workspace 고유 ID"},
            {"name": "workspace_type", "type": "ENUM", "required": True, "description": "타입", "options": ["LOCAL", "CENTRAL"]},
            {"name": "base_path", "type": "STRING", "required": True, "description": "기본 경로"},
            {"name": "product_id", "type": "STRING", "required": False, "description": "소속 Product"},
            {"name": "owner_id", "type": "STRING", "required": False, "description": "소유자 ID"},
            {"name": "created_at", "type": "TIMESTAMP", "required": True, "description": "생성 시각"},
        ],
        "links": [
            {"name": "used_by_task", "target": "SignoffTask", "cardinality": "1:N", "description": "사용하는 Task들"},
            {"name": "stores_result", "target": "Result", "cardinality": "1:N", "description": "저장된 결과들"},
        ]
    },
    
    # ===== Dynamic Layer =====
    "Result": {
        "layer": "Dynamic",
        "color": "#f06595",
        "description": "SignoffTask에서 생성된 검증 결과. Waiver/Fixed 상태 포함",
        "properties": [
            {"name": "result_id", "type": "STRING", "required": True, "description": "Result 고유 ID"},
            {"name": "task_id", "type": "STRING", "required": True, "description": "소속 Task ID"},
            {"name": "result_file_path", "type": "STRING", "required": False, "description": "결과 파일 경로"},
            {"name": "row_count", "type": "INTEGER", "required": True, "description": "전체 Row 수"},
            {"name": "waiver_count", "type": "INTEGER", "required": True, "description": "Waiver 처리 수"},
            {"name": "fixed_count", "type": "INTEGER", "required": True, "description": "Fixed 처리 수"},
            {"name": "result_count", "type": "INTEGER", "required": True, "description": "미처리 수"},
            {"name": "waiver_progress_pct", "type": "FLOAT", "required": True, "description": "Waiver 진행률 (%)"},
            {"name": "comparison_summary", "type": "JSON", "required": False, "description": "비교 결과 요약"},
            {"name": "created_at", "type": "TIMESTAMP", "required": True, "description": "생성 시각"},
        ],
        "links": [
            {"name": "produced_by", "target": "SignoffTask", "cardinality": "1:1", "description": "생성 Task"},
            {"name": "stored_in", "target": "Workspace", "cardinality": "N:1", "description": "저장 Workspace"},
            {"name": "compared_with", "target": "ComparisonResult", "cardinality": "1:N", "description": "비교 결과들"},
        ]
    },
    
    "ComparisonResult": {
        "layer": "Dynamic",
        "color": "#e64980",
        "description": "이전 Revision과의 비교 분석 결과. Waiver Migration 지원",
        "properties": [
            {"name": "comparison_id", "type": "STRING", "required": True, "description": "비교 고유 ID"},
            {"name": "source_result_id", "type": "STRING", "required": True, "description": "이전 Result ID"},
            {"name": "target_result_id", "type": "STRING", "required": True, "description": "현재 Result ID"},
            {"name": "same_count", "type": "INTEGER", "required": True, "description": "동일 항목 수"},
            {"name": "diff_count", "type": "INTEGER", "required": True, "description": "변경 항목 수"},
            {"name": "new_count", "type": "INTEGER", "required": True, "description": "신규 항목 수"},
            {"name": "removed_count", "type": "INTEGER", "required": True, "description": "삭제 항목 수"},
            {"name": "waiver_migrated_count", "type": "INTEGER", "required": False, "description": "Waiver 자동 이관 수"},
            {"name": "created_at", "type": "TIMESTAMP", "required": True, "description": "생성 시각"},
        ],
        "links": [
            {"name": "compares_source", "target": "Result", "cardinality": "N:1", "description": "이전 결과"},
            {"name": "compares_target", "target": "Result", "cardinality": "N:1", "description": "현재 결과"},
        ]
    },
}

# Layer 정보
LAYERS = {
    "Semantic": {
        "name": "Semantic Layer (의미 계층)",
        "description": "무엇이 있는가? - 거의 변하지 않는 마스터 데이터",
        "color": "#e3f2fd",
        "objects": ["Product", "Revision", "Block", "Designer", "SignoffApplication"]
    },
    "Kinetic": {
        "name": "Kinetic Layer (운동 계층)",
        "description": "어떻게 실행되는가? - 상태가 변함, 프로세스 추적",
        "color": "#e8f5e9",
        "objects": ["SignoffTask", "InputConfig", "Workspace"]
    },
    "Dynamic": {
        "name": "Dynamic Layer (동적 계층)",
        "description": "결과는 어떤가? - 가장 자주 변함, AI 학습 대상",
        "color": "#fce4ec",
        "objects": ["Result", "ComparisonResult"]
    }
}
