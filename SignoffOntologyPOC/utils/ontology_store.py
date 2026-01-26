"""
Signoff Ontology Store - 13개 Object Type 구현 (v2.0)
Based on: updated_Signoff Platform Ontology.md

3-Layer Architecture:
  Semantic Layer (7개):
    1. Product - 제품 정보
    2. Revision - 설계 버전 (R00~R60)
    3. Block - 회로 블록
    4. Designer - 사용자
    5. SignoffApplication - 검증 도구 (19종)
    6. CriteriaSet - 판정 기준
    7. Workspace - 작업 공간
    
  Kinetic Layer (2개):
    8. SignoffJob - 실행 이벤트 (InputConfig 통합)
    9. Result - 검증 결과
    
  Dynamic Layer (4개):
    10. CategorizePart - 담당자 지정
    11. CompareResult - Revision 간 비교
    12. WaiverDecision - Waiver 판단 이력
    13. SignoffIssue - 문의/이슈 이력
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import random
import json
import uuid


class SignoffOntologyStore:
    """Signoff Ontology - 13개 핵심 Object Type 관리 (3-Layer Architecture)"""
    
    # ========== LAYER DEFINITIONS ==========
    LAYERS = {
        "Semantic": ["Product", "Revision", "Block", "Designer", "SignoffApplication", "CriteriaSet", "Workspace"],
        "Kinetic": ["SignoffJob", "Result"],
        "Dynamic": ["CategorizePart", "CompareResult", "WaiverDecision", "SignoffIssue"]
    }
    
    # Object 유형별 색상 (시각화용)
    COLORS = {
        # Semantic Layer - Blue/Yellow 계열
        "Product": "#4263eb",
        "Revision": "#5c7cfa",
        "Block": "#748ffc",
        "Designer": "#fab005",
        "SignoffApplication": "#fd7e14",
        "CriteriaSet": "#e8590c",
        "Workspace": "#fcc419",
        # Kinetic Layer - Green 계열
        "SignoffJob": "#40c057",
        "Result": "#69db7c",
        # Dynamic Layer - Pink/Purple 계열
        "CategorizePart": "#f06595",
        "CompareResult": "#e64980",
        "WaiverDecision": "#be4bdb",
        "SignoffIssue": "#9c36b5",
    }
    
    # Object Type별 아이콘
    ICONS = {
        "Product": "📦",
        "Revision": "📋",
        "Block": "🔲",
        "Designer": "👤",
        "SignoffApplication": "🔧",
        "CriteriaSet": "📏",
        "Workspace": "📁",
        "SignoffJob": "⚡",
        "Result": "📊",
        "CategorizePart": "👥",
        "CompareResult": "🔄",
        "WaiverDecision": "✅",
        "SignoffIssue": "❓",
    }
    
    # 레이어 순서 (그래프 레이아웃용)
    LAYER_ORDER = ["Product", "Revision", "Block", "Designer", "SignoffApplication", 
                   "CriteriaSet", "Workspace", "SignoffJob", "Result", 
                   "CategorizePart", "CompareResult", "WaiverDecision", "SignoffIssue"]
    
    # 19개 Signoff Application 목록
    APPLICATIONS = [
        {"app_id": "DSC", "app_name": "Driver Size Check", "app_group": "STATIC", 
         "engine_type": "SPACE", "comparison_key": "measure_net,driver_nmos",
         "supported_pvt_corners": ["SSPLVCT", "SSPLVHT"]},
        {"app_id": "LSC", "app_name": "Latch Setup Check", "app_group": "STATIC",
         "engine_type": "SPACE", "comparison_key": "master,latch_name",
         "supported_pvt_corners": ["SFLVCT", "FSLVCT"]},
        {"app_id": "LS", "app_name": "Level Shifter", "app_group": "STATIC",
         "engine_type": "SPACE", "comparison_key": "master",
         "supported_pvt_corners": ["SFLVCT", "FSLVCT"]},
        {"app_id": "CANATR", "app_name": "Coupling Analysis TR", "app_group": "STATIC",
         "engine_type": "SPACE", "comparison_key": "victim_net,aggressor_net",
         "supported_pvt_corners": ["FFPHVHT"]},
        {"app_id": "CDA", "app_name": "Coupling Delay Analysis", "app_group": "TIMING",
         "engine_type": "SPACE", "comparison_key": "victim_net,aggressor_net",
         "supported_pvt_corners": ["SSPLVCT"]},
        {"app_id": "PEC", "app_name": "Power/ESD Checker", "app_group": "PRE_LAYOUT",
         "engine_type": "SPACE", "comparison_key": "unit_name,msg",
         "supported_pvt_corners": ["TTTVCT"]},
        {"app_id": "PNRATIO", "app_name": "PN Ratio Checker", "app_group": "PRE_LAYOUT",
         "engine_type": "PERC", "comparison_key": "inst_name,cell_name",
         "supported_pvt_corners": ["SSPLVCT"]},
        {"app_id": "FANOUT", "app_name": "Fan-Out Checker", "app_group": "PRE_LAYOUT",
         "engine_type": "PERC", "comparison_key": "drv_net",
         "supported_pvt_corners": ["SSPLVCT"]},
        {"app_id": "DCPATH", "app_name": "DC Path Checker", "app_group": "STATIC",
         "engine_type": "PRIMESIM", "comparison_key": "path_id,node",
         "supported_pvt_corners": ["TTTVCT"]},
        {"app_id": "FLOATNODE", "app_name": "Floating Node Checker", "app_group": "PRE_LAYOUT",
         "engine_type": "SPACE", "comparison_key": "node_name",
         "supported_pvt_corners": ["TTTVCT"]},
        {"app_id": "ADV_MARGIN", "app_name": "ADV Margin Analyzer", "app_group": "DYNAMIC",
         "engine_type": "ADV", "comparison_key": "name,fullmaster",
         "supported_pvt_corners": ["SSPLVCT", "FFPHVHT"]},
        {"app_id": "DRIVER_KEEPER", "app_name": "Driver Keeper", "app_group": "DYNAMIC",
         "engine_type": "ADV", "comparison_key": "instance_name,target_master",
         "supported_pvt_corners": ["SFLVCT", "FSLVCT"]},
        {"app_id": "GLITCH", "app_name": "Glitch Margin Check", "app_group": "DYNAMIC",
         "engine_type": "ADV", "comparison_key": "name,fullmaster",
         "supported_pvt_corners": ["SSPLVCT", "FFPHVHT"]},
    ]
    
    # Revision Phases
    REVISION_PHASES = ["R00", "R10", "R20", "R30", "R40", "R50", "R60"]
    
    # Revision별 설계 단계
    DESIGN_STAGES = {
        "R00": "SCHEMATIC_ONLY", "R10": "SCHEMATIC_ONLY",
        "R20": "PRE_LAYOUT", 
        "R30": "POST_LAYOUT", "R40": "POST_LAYOUT",
        "R50": "POST_LAYOUT", "R60": "POST_LAYOUT"
    }
    
    # Block Names (Realistic)
    BLOCK_NAMES = [
        "FULLCHIP", "PAD", "BANTI_DC", "BTSV_16CH_B", "BTSV_4CH_B", 
        "BPHY_MID_B", "BPHY_1CH_B", "CORE", "IO_PHY", "PMIC"
    ]
    
    # PVT Corners
    PVT_CORNERS = [
        {"name": "SSPLVCT", "process": "SS", "voltage": "LV", "temp": "CT", "desc": "Slow/LowVolt/Cold"},
        {"name": "SSPLVHT", "process": "SS", "voltage": "LV", "temp": "HT", "desc": "Slow/LowVolt/Hot"},
        {"name": "SFLVCT", "process": "SF", "voltage": "LV", "temp": "CT", "desc": "SlowFast/LowVolt/Cold"},
        {"name": "FSLVCT", "process": "FS", "voltage": "LV", "temp": "CT", "desc": "FastSlow/LowVolt/Cold"},
        {"name": "FFPHVHT", "process": "FF", "voltage": "HV", "temp": "HT", "desc": "Fast/HighVolt/Hot"},
        {"name": "TTTVCT", "process": "TT", "voltage": "TV", "temp": "CT", "desc": "Typical/TypicalVolt/Cold"},
    ]
    
    # Designer 목록
    DESIGNERS_LIST = [
        {"id": "wonwoo", "name": "최원우", "role": "DEVELOPER", "team": "Signoff Platform Team"},
        {"id": "minji", "name": "권민지", "role": "DEVELOPER", "team": "Signoff Platform Team"},
        {"id": "kwangsun", "name": "김광선", "role": "ENGINEER", "team": "HBM Design Team"},
        {"id": "jinho", "name": "김진호", "role": "ENGINEER", "team": "HBM Design Team"},
        {"id": "hyungjung", "name": "서형중", "role": "ENGINEER", "team": "HBM Design Team"},
        {"id": "jieun", "name": "오지은", "role": "ENGINEER", "team": "DDR Design Team"},
        {"id": "changwoo", "name": "유창우", "role": "LEAD", "team": "HBM Design Team"},
        {"id": "sunghan", "name": "이성한", "role": "ENGINEER", "team": "DDR Design Team"},
        {"id": "sungju", "name": "이성주", "role": "MANAGER", "team": "Signoff Management"},
    ]
    
    # Application 수행 가능 Revision
    APP_AVAILABILITY = {
        "PEC": ["R00", "R10", "R20", "R30", "R40", "R50", "R60"],
        "PNRATIO": ["R00", "R10", "R20", "R30", "R40", "R50", "R60"],
        "FANOUT": ["R00", "R10", "R20", "R30", "R40", "R50", "R60"],
        "FLOATNODE": ["R00", "R10", "R20", "R30", "R40", "R50", "R60"],
        "LSC": ["R10", "R20", "R30", "R40", "R50", "R60"],
        "DSC": ["R20", "R30", "R40", "R50", "R60"],
        "LS": ["R20", "R30", "R40", "R50", "R60"],
        "DCPATH": ["R20", "R30", "R40", "R50", "R60"],
        "CANATR": ["R40", "R50", "R60"],
        "CDA": ["R50", "R60"],
        "ADV_MARGIN": ["R00", "R10", "R20", "R30", "R40", "R50", "R60"],
        "DRIVER_KEEPER": ["R00", "R10", "R20", "R30", "R40", "R50", "R60"],
        "GLITCH": ["R50", "R60"],
    }
    
    def __init__(self):
        self.clear_all()
    
    def clear_all(self):
        """모든 데이터 초기화"""
        # Semantic Layer
        self.products: List[Dict] = []
        self.revisions: List[Dict] = []
        self.blocks: List[Dict] = []
        self.designers: List[Dict] = []
        self.signoff_applications: List[Dict] = []
        self.criteria_sets: List[Dict] = []
        self.workspaces: List[Dict] = []
        # Kinetic Layer
        self.signoff_jobs: List[Dict] = []
        self.results: List[Dict] = []
        # Dynamic Layer
        self.categorize_parts: List[Dict] = []
        self.compare_results: List[Dict] = []
        self.waiver_decisions: List[Dict] = []
        self.signoff_issues: List[Dict] = []
    
    # ========== SEMANTIC LAYER: CRUD ==========
    
    def add_product(self, product_id: str, product_name: str = None, 
                    product_type: str = "HBM", technology_node: str = "4nm",
                    status: str = "ACTIVE") -> Optional[Dict]:
        """Product 추가"""
        if any(p["product_id"] == product_id for p in self.products):
            return None
        product = {
            "product_id": product_id,
            "product_name": product_name or f"{product_id} Memory",
            "product_type": product_type,
            "technology_node": technology_node,
            "status": status,
            "tapeout_target_date": "2026-06-30",
            "created_at": datetime.now().isoformat(),
        }
        self.products.append(product)
        return product
    
    def add_revision(self, revision_id: str, product_id: str, revision_code: str,
                     design_stage: str = None, status: str = "NOT_STARTED",
                     required_applications: List[str] = None,
                     netlist_version: str = None) -> Optional[Dict]:
        """Revision 추가"""
        if any(r["revision_id"] == revision_id for r in self.revisions):
            return None
        revision = {
            "revision_id": revision_id,
            "product_id": product_id,
            "revision_code": revision_code,
            "design_stage": design_stage or self.DESIGN_STAGES.get(revision_code, "POST_LAYOUT"),
            "status": status,
            "required_applications": required_applications or [],
            "netlist_version": netlist_version or "v1.0",
            "created_at": datetime.now().isoformat(),
        }
        self.revisions.append(revision)
        return revision
    
    def add_block(self, block_id: str, revision_id: str, block_name: str,
                  block_type: str = "TOP", hierarchy_path: str = None,
                  designer_id: str = None) -> Optional[Dict]:
        """Block 추가"""
        if any(b["block_id"] == block_id for b in self.blocks):
            return None
        block = {
            "block_id": block_id,
            "revision_id": revision_id,
            "block_name": block_name,
            "block_type": block_type,
            "hierarchy_path": hierarchy_path or f"/{block_name}",
            "designer_id": designer_id,
            "created_at": datetime.now().isoformat(),
        }
        self.blocks.append(block)
        return block
    
    def add_designer(self, designer_id: str, name: str = None,
                     email: str = None, team: str = None,
                     role: str = "ENGINEER") -> Optional[Dict]:
        """Designer 추가"""
        if any(d["designer_id"] == designer_id for d in self.designers):
            return None
        designer = {
            "designer_id": designer_id,
            "name": name or designer_id,
            "email": email or f"{designer_id}@company.com",
            "team": team or "Design Team",
            "role": role,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
        }
        self.designers.append(designer)
        return designer
    
    def add_signoff_application(self, app_id: str, app_name: str = None,
                                app_group: str = "STATIC", engine_type: str = "SPACE",
                                comparison_key: str = None,
                                supported_pvt_corners: List[str] = None) -> Optional[Dict]:
        """SignoffApplication 추가"""
        if any(a["app_id"] == app_id for a in self.signoff_applications):
            return None
        app = {
            "app_id": app_id,
            "app_name": app_name or app_id,
            "app_group": app_group,
            "engine_type": engine_type,
            "comparison_key": comparison_key or "default_key",
            "supported_pvt_corners": supported_pvt_corners or ["SSPLVCT"],
            "created_at": datetime.now().isoformat(),
        }
        self.signoff_applications.append(app)
        return app
    
    def add_criteria_set(self, criteria_id: str, app_id: str, criteria_name: str = None,
                         criteria_type: str = "TAPEOUT", version: str = "v1.0",
                         rules: Dict = None) -> Optional[Dict]:
        """CriteriaSet 추가"""
        if any(c["criteria_id"] == criteria_id for c in self.criteria_sets):
            return None
        criteria = {
            "criteria_id": criteria_id,
            "app_id": app_id,
            "criteria_name": criteria_name or f"{app_id} Criteria {version}",
            "criteria_type": criteria_type,
            "version": version,
            "rules": rules or {"fail_conditions": [], "warning_conditions": []},
            "is_active": True,
            "created_at": datetime.now().isoformat(),
        }
        self.criteria_sets.append(criteria)
        return criteria
    
    def add_workspace(self, workspace_id: str, workspace_type: str = "LOCAL",
                      base_path: str = None, product_id: str = None,
                      owner_id: str = None) -> Optional[Dict]:
        """Workspace 추가"""
        if any(w["workspace_id"] == workspace_id for w in self.workspaces):
            return None
        workspace = {
            "workspace_id": workspace_id,
            "workspace_type": workspace_type,
            "base_path": base_path or f"/workspace/{workspace_id}",
            "product_id": product_id,
            "owner_id": owner_id,
            "is_synced": False,
            "created_at": datetime.now().isoformat(),
        }
        self.workspaces.append(workspace)
        return workspace
    
    # ========== KINETIC LAYER: CRUD ==========
    
    def add_signoff_job(self, job_id: str, revision_id: str, block_id: str,
                        app_id: str, executed_by: str = None,
                        criteria_id: str = None, workspace_id: str = None,
                        pvt_corner: str = "SSPLVCT",
                        netlist_path: str = None, power_definition: Dict = None,
                        status: str = "PENDING") -> Optional[Dict]:
        """SignoffJob 추가 (InputConfig 통합)"""
        if any(j["job_id"] == job_id for j in self.signoff_jobs):
            return None
        
        # 시간 계산
        now = datetime.now()
        if status == "DONE":
            start_time = now - timedelta(hours=random.randint(1, 24))
            completion_time = now
            runtime = int((completion_time - start_time).total_seconds())
        elif status == "RUNNING":
            start_time = now - timedelta(hours=random.randint(1, 5))
            completion_time = None
            runtime = None
        else:
            start_time = None
            completion_time = None
            runtime = None
        
        job = {
            "job_id": job_id,
            "revision_id": revision_id,
            "block_id": block_id,
            "app_id": app_id,
            "criteria_id": criteria_id or f"{app_id}_TAPEOUT_V1",
            "workspace_id": workspace_id,
            "executed_by": executed_by,
            # InputConfig 통합
            "netlist_path": netlist_path or f"/data/{revision_id}/netlist.sp",
            "tech_file_path": "/tech/4nm/tech.tf",
            "power_definition": power_definition or {"VDD": ["vdd_core"], "VSS": ["vss"]},
            "pvt_corner": pvt_corner,
            "simulation_params": {"threshold": 0.1},
            # 실행 상태
            "status": status,
            "lsf_job_id": str(random.randint(10000000, 99999999)) if status in ["RUNNING", "DONE"] else None,
            "queue_name": "normal",
            "submission_time": (start_time - timedelta(minutes=5)).isoformat() if start_time else None,
            "start_time": start_time.isoformat() if start_time else None,
            "completion_time": completion_time.isoformat() if completion_time else None,
            "runtime_seconds": runtime,
            "created_at": datetime.now().isoformat(),
        }
        self.signoff_jobs.append(job)
        return job
    
    def add_result(self, result_id: str, job_id: str,
                   row_count: int = 1000, fail_count: int = None,
                   waiver_count: int = 0, fixed_count: int = 0,
                   analysis_status: str = "PENDING",
                   workspace_id: str = None) -> Optional[Dict]:
        """Result 추가"""
        if any(r["result_id"] == result_id for r in self.results):
            return None
        
        if fail_count is None:
            fail_count = row_count - waiver_count - fixed_count
        
        waiver_progress = ((waiver_count + fixed_count) / row_count * 100) if row_count > 0 else 0
        
        result = {
            "result_id": result_id,
            "job_id": job_id,
            "workspace_id": workspace_id,
            "result_file_path": f"/results/{result_id}/result.parquet",
            # Row 통계
            "row_count": row_count,
            "fail_count": fail_count,
            "waiver_count": waiver_count,
            "fixed_count": fixed_count,
            # 진행 상태
            "analysis_status": analysis_status,
            "waiver_progress_pct": round(waiver_progress, 1),
            # Central 동기화
            "is_uploaded": analysis_status == "COMPLETED",
            "created_at": datetime.now().isoformat(),
        }
        self.results.append(result)
        return result
    
    # ========== DYNAMIC LAYER: CRUD ==========
    
    def add_categorize_part(self, categorize_id: str, result_id: str,
                            category_name: str, assigned_to: str,
                            row_count: int = 100,
                            assignment_type: str = "AUTO") -> Optional[Dict]:
        """CategorizePart 추가"""
        cat = {
            "categorize_id": categorize_id,
            "result_id": result_id,
            "category_name": category_name,
            "category_rule": {"column": "hierarchy", "pattern": f"*{category_name}*"},
            "assigned_to": assigned_to,
            "row_count": row_count,
            "assignment_type": assignment_type,
            "created_at": datetime.now().isoformat(),
        }
        self.categorize_parts.append(cat)
        return cat
    
    def add_compare_result(self, compare_id: str, source_result_id: str, target_result_id: str,
                           new_fail_count: int = 0, fixed_count: int = 0,
                           regressed_count: int = 0, unchanged_fail_count: int = 0,
                           waiver_migrated_count: int = 0) -> Optional[Dict]:
        """CompareResult 추가"""
        compare = {
            "compare_id": compare_id,
            "source_result_id": source_result_id,
            "target_result_id": target_result_id,
            "new_fail_count": new_fail_count,
            "fixed_count": fixed_count,
            "regressed_count": regressed_count,
            "unchanged_fail_count": unchanged_fail_count,
            "waiver_migrated_count": waiver_migrated_count,
            "comparison_type": "AUTO_ON_UPLOAD",
            "created_at": datetime.now().isoformat(),
        }
        self.compare_results.append(compare)
        return compare
    
    def add_waiver_decision(self, decision_id: str, result_id: str, row_key: str,
                            decision_type: str = "WAIVER", reason: str = "",
                            decided_by: str = None) -> Optional[Dict]:
        """WaiverDecision 추가"""
        decision = {
            "decision_id": decision_id,
            "result_id": result_id,
            "row_key": row_key,
            "decision_type": decision_type,
            "reason": reason,
            "decided_by": decided_by,
            "created_at": datetime.now().isoformat(),
        }
        self.waiver_decisions.append(decision)
        return decision
    
    def add_signoff_issue(self, issue_id: str, app_id: str, title: str,
                          description: str = "", issue_type: str = "INQUIRY",
                          status: str = "OPEN", reported_by: str = None,
                          assigned_to: str = None, result_id: str = None) -> Optional[Dict]:
        """SignoffIssue 추가"""
        issue = {
            "issue_id": issue_id,
            "app_id": app_id,
            "result_id": result_id,
            "title": title,
            "description": description,
            "issue_type": issue_type,
            "status": status,
            "reported_by": reported_by,
            "assigned_to": assigned_to,
            "created_at": datetime.now().isoformat(),
        }
        self.signoff_issues.append(issue)
        return issue
    
    # ========== SCENARIO LOADERS ==========
    
    def load_scenario_a_full_lifecycle(self):
        """시나리오 A: HBM4E 전체 라이프사이클 (R00→R60)"""
        self.clear_all()
        
        # 1. Product
        self.add_product("HBM4E", "HBM4E 32GB Wide I/O", "HBM", "4nm", "ACTIVE")
        
        # 2. Designers
        for d in self.DESIGNERS_LIST:
            self.add_designer(d["id"], d["name"], team=d.get("team"), role=d["role"])
        
        # 3. Applications
        for app in self.APPLICATIONS:
            self.add_signoff_application(
                app["app_id"], app["app_name"], app["app_group"],
                app["engine_type"], app["comparison_key"], app["supported_pvt_corners"]
            )
        
        # 4. Criteria Sets
        for app in self.APPLICATIONS[:6]:  # 주요 6개 앱
            self.add_criteria_set(f"{app['app_id']}_TAPEOUT_V1", app["app_id"],
                                  f"{app['app_name']} Tapeout Criteria", "TAPEOUT", "v1.0")
        
        # 5. Workspaces (Central + Local)
        self.add_workspace("WS-CENTRAL-HBM4E", "CENTRAL", "/WORKSPACE/HBM4E/", "HBM4E")
        
        # 6. Revisions with progressive completion
        revision_progress = {
            "R00": 1.0, "R10": 1.0, "R30": 1.0,  # 완료
            "R40": 0.85,  # 진행 중
            "R60": 0.0   # 시작 전
        }
        
        for rev_code in ["R00", "R10", "R30", "R40", "R60"]:
            rev_id = f"HBM4E_{rev_code}"
            progress = revision_progress.get(rev_code, 0)
            status = "COMPLETED" if progress == 1.0 else ("IN_PROGRESS" if progress > 0 else "NOT_STARTED")
            
            # 해당 Revision에서 수행 가능한 App 목록
            available_apps = [
                app_id for app_id, revs in self.APP_AVAILABILITY.items()
                if rev_code in revs and app_id in [a["app_id"] for a in self.APPLICATIONS]
            ]
            
            self.add_revision(rev_id, "HBM4E", rev_code, status=status,
                              required_applications=available_apps)
            
            # 7. Blocks
            for block_name in self.BLOCK_NAMES[:5]:
                block_id = f"{rev_id}_{block_name}"
                designer = random.choice(self.DESIGNERS_LIST)
                self.add_block(block_id, rev_id, block_name, 
                               designer_id=designer["id"])
            
            if progress == 0:
                continue  # 시작 전인 Revision은 Job/Result 없음
            
            # 8. Jobs, Results
            blocks = [b for b in self.blocks if b["revision_id"] == rev_id]
            for block in blocks:
                block_apps = random.sample(available_apps, min(3, len(available_apps)))
                for app_id in block_apps:
                    pvt = random.choice(self.PVT_CORNERS)["name"]
                    job_id = f"JOB-{rev_code}-{block['block_name']}-{app_id}"
                    
                    # 상태 결정
                    if progress == 1.0:
                        status = "DONE"
                    elif progress >= 0.85:
                        status = random.choices(["DONE", "RUNNING", "PENDING"], [0.7, 0.2, 0.1])[0]
                    else:
                        status = random.choices(["PENDING", "RUNNING"], [0.7, 0.3])[0]
                    
                    designer = random.choice(self.DESIGNERS_LIST)
                    self.add_signoff_job(job_id, rev_id, block["block_id"], app_id,
                                         executed_by=designer["id"], pvt_corner=pvt, status=status)
                    
                    if status == "DONE":
                        # Result 생성
                        result_id = f"RESULT-{job_id}"
                        total_rows = random.randint(100000, 500000)
                        
                        if progress == 1.0:
                            waiver_pct = random.uniform(0.85, 0.98)
                            fixed_pct = random.uniform(0.01, 0.12)
                        else:
                            waiver_pct = random.uniform(0.60, 0.80)
                            fixed_pct = random.uniform(0.01, 0.10)
                        
                        waiver = int(total_rows * waiver_pct)
                        fixed = int(total_rows * fixed_pct)
                        
                        self.add_result(result_id, job_id, total_rows,
                                         waiver_count=waiver, fixed_count=fixed,
                                         analysis_status="COMPLETED" if progress == 1.0 else "IN_PROGRESS")
    
    def load_scenario_b_r40_detail(self):
        """시나리오 B: R40 상세 실행 결과 (Post-Layout Apps)"""
        self.clear_all()
        
        # 기본 설정
        self.add_product("HBM4E", "HBM4E 32GB Wide I/O", "HBM", "4nm")
        
        for d in self.DESIGNERS_LIST:
            self.add_designer(d["id"], d["name"], team=d.get("team"), role=d["role"])
        
        # R40에서 수행 가능한 Application들
        r40_apps = ["PEC", "DSC", "LSC", "LS", "CANATR"]
        for app in self.APPLICATIONS:
            if app["app_id"] in r40_apps:
                self.add_signoff_application(
                    app["app_id"], app["app_name"], app["app_group"],
                    app["engine_type"], app["comparison_key"], app["supported_pvt_corners"]
                )
                self.add_criteria_set(f"{app['app_id']}_TAPEOUT_V1", app["app_id"])
        
        # Workspace
        self.add_workspace("WS-CENTRAL-HBM4E", "CENTRAL", "/WORKSPACE/HBM4E/", "HBM4E")
        self.add_workspace("WS-LOCAL-kwangsun", "LOCAL", "/user/HBM4E/SIGNOFF/kwangsun/", "HBM4E", "kwangsun")
        
        # R40 Revision
        self.add_revision("HBM4E_R40", "HBM4E", "R40", "POST_LAYOUT", "IN_PROGRESS",
                          required_applications=r40_apps)
        
        # Blocks
        for block_name in self.BLOCK_NAMES[:5]:
            designer = random.choice(self.DESIGNERS_LIST)
            self.add_block(f"HBM4E_R40_{block_name}", "HBM4E_R40", block_name,
                           designer_id=designer["id"])
        
        # Jobs & Results for each Block x App
        for block in self.blocks:
            for app_id in r40_apps:
                pvt = random.choice(self.PVT_CORNERS)["name"]
                job_id = f"JOB-R40-{block['block_name']}-{app_id}"
                status = random.choices(["DONE", "RUNNING", "PENDING"], [0.7, 0.2, 0.1])[0]
                
                designer = random.choice(self.DESIGNERS_LIST)
                self.add_signoff_job(job_id, "HBM4E_R40", block["block_id"], app_id,
                                     executed_by=designer["id"], pvt_corner=pvt, status=status)
                
                if status == "DONE":
                    result_id = f"RESULT-{job_id}"
                    total = random.randint(100000, 400000)
                    waiver = int(total * random.uniform(0.70, 0.90))
                    fixed = int(total * random.uniform(0.05, 0.15))
                    
                    self.add_result(result_id, job_id, total,
                                    waiver_count=waiver, fixed_count=fixed,
                                    analysis_status="IN_PROGRESS")
    
    def load_scenario_c_compare_migration(self):
        """시나리오 C: R30 vs R40 비교 & Waiver Migration"""
        self.clear_all()
        
        # 기본 설정
        self.add_product("HBM4E", "HBM4E 32GB Wide I/O", "HBM")
        
        for d in self.DESIGNERS_LIST:
            self.add_designer(d["id"], d["name"], team=d.get("team"), role=d["role"])
        
        # Applications
        compare_apps = ["DSC", "LSC", "PEC"]
        for app in self.APPLICATIONS:
            if app["app_id"] in compare_apps:
                self.add_signoff_application(app["app_id"], app["app_name"], app["app_group"])
                self.add_criteria_set(f"{app['app_id']}_TAPEOUT_V1", app["app_id"])
        
        # R30 (완료) & R40 (진행 중)
        self.add_revision("HBM4E_R30", "HBM4E", "R30", "POST_LAYOUT", "COMPLETED", compare_apps)
        self.add_revision("HBM4E_R40", "HBM4E", "R40", "POST_LAYOUT", "IN_PROGRESS", compare_apps)
        
        # FULLCHIP Block만 비교
        self.add_block("HBM4E_R30_FULLCHIP", "HBM4E_R30", "FULLCHIP", designer_id="kwangsun")
        self.add_block("HBM4E_R40_FULLCHIP", "HBM4E_R40", "FULLCHIP", designer_id="kwangsun")
        
        # R30 Jobs & Results (완료)
        for app_id in compare_apps:
            job_r30 = f"JOB-R30-FULLCHIP-{app_id}"
            self.add_signoff_job(job_r30, "HBM4E_R30", "HBM4E_R30_FULLCHIP", app_id,
                                 executed_by="kwangsun", status="DONE")
            
            total = random.randint(200000, 300000)
            waiver = int(total * 0.95)
            fixed = int(total * 0.04)
            self.add_result(f"RESULT-{job_r30}", job_r30, total,
                            waiver_count=waiver, fixed_count=fixed, analysis_status="COMPLETED")
        
        # R40 Jobs & Results (진행 중)
        for app_id in compare_apps:
            job_r40 = f"JOB-R40-FULLCHIP-{app_id}"
            self.add_signoff_job(job_r40, "HBM4E_R40", "HBM4E_R40_FULLCHIP", app_id,
                                 executed_by="kwangsun", status="DONE")
            
            total = random.randint(250000, 350000)
            waiver = int(total * 0.75)  # Waiver 진행 중
            fixed = int(total * 0.10)
            result_r40 = self.add_result(f"RESULT-{job_r40}", job_r40, total,
                                         waiver_count=waiver, fixed_count=fixed,
                                         analysis_status="IN_PROGRESS")
            
            # CompareResult 생성
            source_result = f"RESULT-JOB-R30-FULLCHIP-{app_id}"
            target_result = f"RESULT-{job_r40}"
            
            base_total = 250000
            self.add_compare_result(
                f"CMP-R30-R40-{app_id}",
                source_result, target_result,
                new_fail_count=random.randint(1000, 5000),
                fixed_count=random.randint(500, 2000),
                regressed_count=random.randint(100, 500),
                unchanged_fail_count=random.randint(10000, 30000),
                waiver_migrated_count=int(base_total * 0.70)
            )
    
    def load_template(self, scenario: str = "full_lifecycle"):
        """시나리오 로드"""
        if scenario == "full_lifecycle":
            self.load_scenario_a_full_lifecycle()
        elif scenario == "r40_detail":
            self.load_scenario_b_r40_detail()
        elif scenario == "compare":
            self.load_scenario_c_compare_migration()
        else:
            self.load_scenario_a_full_lifecycle()
    
    # ========== STATISTICS & ANALYTICS ==========
    
    def get_statistics(self) -> Dict:
        """전체 통계"""
        total_rows = sum(r["row_count"] for r in self.results)
        total_waiver = sum(r["waiver_count"] for r in self.results)
        total_fixed = sum(r["fixed_count"] for r in self.results)
        total_pending = sum(r["fail_count"] for r in self.results)
        
        progress = ((total_waiver + total_fixed) / total_rows * 100) if total_rows > 0 else 0
        
        return {
            "products": len(self.products),
            "revisions": len(self.revisions),
            "blocks": len(self.blocks),
            "designers": len(self.designers),
            "applications": len(self.signoff_applications),
            "criteria_sets": len(self.criteria_sets),
            "workspaces": len(self.workspaces),
            "jobs": len(self.signoff_jobs),
            "results": len(self.results),
            "categorize_parts": len(self.categorize_parts),
            "compare_results": len(self.compare_results),
            "waiver_decisions": len(self.waiver_decisions),
            "issues": len(self.signoff_issues),
            "total_rows": total_rows,
            "waiver_count": total_waiver,
            "fixed_count": total_fixed,
            "pending_count": total_pending,
            "progress_pct": round(progress, 1),
        }
    
    def get_revision_progress(self) -> List[Dict]:
        """Revision별 진행률"""
        progress_list = []
        for rev in self.revisions:
            rev_jobs = [j for j in self.signoff_jobs if j["revision_id"] == rev["revision_id"]]
            rev_results = [r for r in self.results if r["job_id"] in [j["job_id"] for j in rev_jobs]]
            
            total = sum(r["row_count"] for r in rev_results)
            waiver = sum(r["waiver_count"] for r in rev_results)
            fixed = sum(r["fixed_count"] for r in rev_results)
            pending = sum(r["fail_count"] for r in rev_results)
            
            progress = ((waiver + fixed) / total * 100) if total > 0 else 0
            
            progress_list.append({
                "revision_id": rev["revision_id"],
                "revision_code": rev["revision_code"],
                "status": rev["status"],
                "total_jobs": len(rev_jobs),
                "done_jobs": len([j for j in rev_jobs if j["status"] == "DONE"]),
                "total_rows": total,
                "waiver_count": waiver,
                "fixed_count": fixed,
                "pending_count": pending,
                "progress_pct": round(progress, 1),
            })
        return progress_list
    
    def get_application_stats(self) -> List[Dict]:
        """Application별 통계"""
        stats = []
        for app in self.signoff_applications:
            app_jobs = [j for j in self.signoff_jobs if j["app_id"] == app["app_id"]]
            app_results = [r for r in self.results if r["job_id"] in [j["job_id"] for j in app_jobs]]
            
            total = sum(r["row_count"] for r in app_results)
            waiver = sum(r["waiver_count"] for r in app_results)
            fixed = sum(r["fixed_count"] for r in app_results)
            
            stats.append({
                "app_id": app["app_id"],
                "app_name": app["app_name"],
                "job_count": len(app_jobs),
                "result_count": len(app_results),
                "total_rows": total,
                "waiver_count": waiver,
                "fixed_count": fixed,
                "pending_count": total - waiver - fixed,
            })
        return stats
    
    # ========== GRAPH & EXPORT ==========
    
    def to_graph_elements(self) -> List[Dict]:
        """Cytoscape용 그래프 요소"""
        elements = []
        
        # Helper function
        def get_layer(obj_type):
            for layer, types in self.LAYERS.items():
                if obj_type in types:
                    return layer
            return "Unknown"
        
        # Nodes
        for p in self.products:
            elements.append({
                "data": {"id": p["product_id"], "label": p["product_id"], 
                         "type": "Product", "layer": "Semantic",
                         "color": self.COLORS["Product"]},
                "classes": "product semantic"
            })
        
        for r in self.revisions:
            elements.append({
                "data": {"id": r["revision_id"], "label": r["revision_code"],
                         "type": "Revision", "layer": "Semantic",
                         "color": self.COLORS["Revision"]},
                "classes": "revision semantic"
            })
            elements.append({"data": {"source": r["product_id"], "target": r["revision_id"],
                                      "label": "has_revision"}})
        
        for b in self.blocks:
            elements.append({
                "data": {"id": b["block_id"], "label": b["block_name"],
                         "type": "Block", "layer": "Semantic",
                         "color": self.COLORS["Block"]},
                "classes": "block semantic"
            })
            elements.append({"data": {"source": b["revision_id"], "target": b["block_id"],
                                      "label": "has_block"}})
            if b.get("designer_id"):
                elements.append({"data": {"source": b["block_id"], "target": b["designer_id"],
                                          "label": "responsible_designer"}})
        
        for d in self.designers:
            elements.append({
                "data": {"id": d["designer_id"], "label": d["name"],
                         "type": "Designer", "layer": "Semantic",
                         "color": self.COLORS["Designer"]},
                "classes": "designer semantic"
            })
        
        for a in self.signoff_applications:
            elements.append({
                "data": {"id": a["app_id"], "label": a["app_id"],
                         "type": "SignoffApplication", "layer": "Semantic",
                         "color": self.COLORS["SignoffApplication"]},
                "classes": "application semantic"
            })
        
        for c in self.criteria_sets:
            elements.append({
                "data": {"id": c["criteria_id"], "label": c["criteria_id"],
                         "type": "CriteriaSet", "layer": "Semantic",
                         "color": self.COLORS["CriteriaSet"]},
                "classes": "criteria semantic"
            })
        
        for j in self.signoff_jobs:
            elements.append({
                "data": {"id": j["job_id"], "label": f"{j['app_id']}",
                         "type": "SignoffJob", "layer": "Kinetic",
                         "color": self.COLORS["SignoffJob"]},
                "classes": "job kinetic"
            })
            elements.append({"data": {"source": j["block_id"], "target": j["job_id"],
                                      "label": "has_job"}})
            elements.append({"data": {"source": j["job_id"], "target": j["app_id"],
                                      "label": "uses_application"}})
        
        for r in self.results:
            elements.append({
                "data": {"id": r["result_id"], "label": f"{r['waiver_progress_pct']}%",
                         "type": "Result", "layer": "Kinetic",
                         "color": self.COLORS["Result"]},
                "classes": "result kinetic"
            })
            elements.append({"data": {"source": r["job_id"], "target": r["result_id"],
                                      "label": "produces"}})
        
        for cmp in self.compare_results:
            elements.append({
                "data": {"id": cmp["compare_id"], "label": "Compare",
                         "type": "CompareResult", "layer": "Dynamic",
                         "color": self.COLORS["CompareResult"]},
                "classes": "compare dynamic"
            })
        
        return elements
    
    def to_json_graphrag(self) -> Dict:
        """GraphRAG/LLM용 JSON Export"""
        return {
            "meta": {
                "version": "2.0",
                "created_at": datetime.now().isoformat(),
                "object_types": list(self.LAYERS.keys()),
                "total_objects": sum([
                    len(self.products), len(self.revisions), len(self.blocks),
                    len(self.designers), len(self.signoff_applications), len(self.criteria_sets),
                    len(self.workspaces), len(self.signoff_jobs), len(self.results),
                    len(self.categorize_parts), len(self.compare_results),
                    len(self.waiver_decisions), len(self.signoff_issues)
                ])
            },
            "ontology": {
                "products": self.products,
                "revisions": self.revisions,
                "blocks": self.blocks,
                "designers": self.designers,
                "applications": self.signoff_applications,
                "criteria_sets": self.criteria_sets,
                "workspaces": self.workspaces,
                "jobs": self.signoff_jobs,
                "results": self.results,
                "categorize_parts": self.categorize_parts,
                "compare_results": self.compare_results,
                "waiver_decisions": self.waiver_decisions,
                "issues": self.signoff_issues,
            },
            "statistics": self.get_statistics(),
        }
    
    def get_object_schema(self) -> Dict:
        """Object Type 스키마 정보 반환 (Schema Viewer용)"""
        return {
            "Product": {
                "layer": "Semantic",
                "color": self.COLORS["Product"],
                "icon": self.ICONS["Product"],
                "description": "메모리 제품의 최상위 개체 (HBM4E, DDR5 등)",
                "properties": ["product_id", "product_name", "product_type", "technology_node", "status"],
                "links": [("has_revision", "Revision", "1:N"), ("managed_by", "Designer", "N:M")]
            },
            "Revision": {
                "layer": "Semantic",
                "color": self.COLORS["Revision"],
                "icon": self.ICONS["Revision"],
                "description": "설계 버전 (R00~R60). Signoff 수행의 기준 단위",
                "properties": ["revision_id", "revision_code", "design_stage", "status", "required_applications"],
                "links": [("of_product", "Product", "N:1"), ("has_block", "Block", "1:N"), ("has_job", "SignoffJob", "1:N")]
            },
            "Block": {
                "layer": "Semantic",
                "color": self.COLORS["Block"],
                "icon": self.ICONS["Block"],
                "description": "회로 블록 (FULLCHIP, CORE, PHY 등). Signoff 대상 단위",
                "properties": ["block_id", "block_name", "block_type", "hierarchy_path"],
                "links": [("of_revision", "Revision", "N:1"), ("responsible_designer", "Designer", "N:1")]
            },
            "Designer": {
                "layer": "Semantic",
                "color": self.COLORS["Designer"],
                "icon": self.ICONS["Designer"],
                "description": "설계자, 검증 담당자, 개발자 등 모든 구성원",
                "properties": ["designer_id", "name", "email", "team", "role"],
                "links": [("responsible_for", "Block", "1:N"), ("executed_jobs", "SignoffJob", "1:N")]
            },
            "SignoffApplication": {
                "layer": "Semantic",
                "color": self.COLORS["SignoffApplication"],
                "icon": self.ICONS["SignoffApplication"],
                "description": "Signoff 검증 도구 (DSC, LSC, PEC 등 19종)",
                "properties": ["app_id", "app_name", "app_group", "engine_type", "comparison_key"],
                "links": [("has_criteria", "CriteriaSet", "1:N"), ("used_by_jobs", "SignoffJob", "1:N")]
            },
            "CriteriaSet": {
                "layer": "Semantic",
                "color": self.COLORS["CriteriaSet"],
                "icon": self.ICONS["CriteriaSet"],
                "description": "Application별 Pass/Fail 판정 기준 정의",
                "properties": ["criteria_id", "app_id", "criteria_type", "version", "rules"],
                "links": [("of_application", "SignoffApplication", "N:1")]
            },
            "Workspace": {
                "layer": "Semantic",
                "color": self.COLORS["Workspace"],
                "icon": self.ICONS["Workspace"],
                "description": "작업 공간 (Local/Central)",
                "properties": ["workspace_id", "workspace_type", "base_path", "is_synced"],
                "links": [("has_jobs", "SignoffJob", "1:N"), ("stores_results", "Result", "1:N")]
            },
            "SignoffJob": {
                "layer": "Kinetic",
                "color": self.COLORS["SignoffJob"],
                "icon": self.ICONS["SignoffJob"],
                "description": "실행 이벤트 (InputConfig 포함). 실제 Signoff 작업 단위",
                "properties": ["job_id", "status", "pvt_corner", "netlist_path", "lsf_job_id", "runtime_seconds"],
                "links": [("of_revision", "Revision", "N:1"), ("targets_block", "Block", "N:1"), 
                          ("uses_application", "SignoffApplication", "N:1"), ("produces", "Result", "1:1")]
            },
            "Result": {
                "layer": "Kinetic",
                "color": self.COLORS["Result"],
                "icon": self.ICONS["Result"],
                "description": "검증 결과. Row 단위 통계 (WAIVER/FIXED/PENDING)",
                "properties": ["result_id", "row_count", "waiver_count", "fixed_count", "waiver_progress_pct"],
                "links": [("produced_by", "SignoffJob", "1:1"), ("has_comparison", "CompareResult", "1:N")]
            },
            "CategorizePart": {
                "layer": "Dynamic",
                "color": self.COLORS["CategorizePart"],
                "icon": self.ICONS["CategorizePart"],
                "description": "Result 분석 시 Part별 담당자 지정",
                "properties": ["categorize_id", "category_name", "assigned_to", "row_count"],
                "links": [("of_result", "Result", "N:1"), ("assigned_to", "Designer", "N:1")]
            },
            "CompareResult": {
                "layer": "Dynamic",
                "color": self.COLORS["CompareResult"],
                "icon": self.ICONS["CompareResult"],
                "description": "Revision 간 비교 결과. Waiver Migration 근거",
                "properties": ["compare_id", "new_fail_count", "fixed_count", "regressed_count", "waiver_migrated_count"],
                "links": [("source_result", "Result", "N:1"), ("target_result", "Result", "N:1")]
            },
            "WaiverDecision": {
                "layer": "Dynamic",
                "color": self.COLORS["WaiverDecision"],
                "icon": self.ICONS["WaiverDecision"],
                "description": "개별 항목에 대한 Waiver/Fixed 판단 이력",
                "properties": ["decision_id", "decision_type", "reason", "decided_by"],
                "links": [("of_result", "Result", "N:1")]
            },
            "SignoffIssue": {
                "layer": "Dynamic",
                "color": self.COLORS["SignoffIssue"],
                "icon": self.ICONS["SignoffIssue"],
                "description": "Signoff 과정에서 발생한 이슈/문의 이력",
                "properties": ["issue_id", "title", "issue_type", "status", "reported_by"],
                "links": [("related_to", "SignoffApplication", "N:1"), ("assigned_to", "Designer", "N:1")]
            },
        }
    
    def get_all_objects(self) -> Dict[str, List]:
        """모든 Object 반환"""
        return {
            "Product": self.products,
            "Revision": self.revisions,
            "Block": self.blocks,
            "Designer": self.designers,
            "SignoffApplication": self.signoff_applications,
            "CriteriaSet": self.criteria_sets,
            "Workspace": self.workspaces,
            "SignoffJob": self.signoff_jobs,
            "Result": self.results,
            "CategorizePart": self.categorize_parts,
            "CompareResult": self.compare_results,
            "WaiverDecision": self.waiver_decisions,
            "SignoffIssue": self.signoff_issues,
        }


# 글로벌 인스턴스
store = SignoffOntologyStore()
