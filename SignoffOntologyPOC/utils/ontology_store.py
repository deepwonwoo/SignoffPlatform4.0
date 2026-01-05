"""
Signoff Ontology Store - 10개 핵심 Object Type 구현
Based on: updated_Signoff Platform Ontology.md

Objects:
  1. Product - 제품 정보
  2. Revision - 설계 버전 (R00~R60)
  3. Block - 회로 블록
  4. SignoffApplication - 검증 도구 (DSC, LSC, LS, PEC, CANATR, CDA)
  5. SignoffTask - 작업 정의
  6. SignoffJob - 실행 인스턴스
  7. InputConfig - 입력 설정
  8. Workspace - 작업 공간
  9. Result - 검증 결과 (WAIVER/FIXED/PENDING)
  10. Designer - 사용자
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import random
import json
import uuid


class SignoffOntologyStore:
    """Signoff Ontology - 10개 핵심 Object Type 관리"""
    
    # Object 유형별 색상 (시각화용)
    COLORS = {
        "Product": "#4263eb",           # 파란색
        "Revision": "#5c7cfa",
        "Block": "#748ffc",
        "SignoffApplication": "#20c997", # 초록색
        "SignoffTask": "#38d9a9",
        "SignoffJob": "#63e6be",
        "InputConfig": "#ffd43b",        # 노란색
        "Workspace": "#fab005",
        "Result": "#ff6b6b",             # 빨간색
        "Designer": "#9775fa",           # 보라색
    }
    
    # 레이어 순서 (그래프 레이아웃용)
    LAYER_ORDER = ["Product", "Revision", "Block", "Designer", "SignoffApplication",
                   "SignoffTask", "InputConfig", "SignoffJob", "Workspace", "Result"]
    
    # 6개 핵심 Application
    APPLICATIONS = [
        {"app_id": "DSC", "app_name": "Driver Size Check", "app_group": "Static", 
         "engine_type": "SPACE", "comparison_key": "measure_net + driver_net",
         "required_inputs": ["NETLIST", "EDR", "MP", "POWER"]},
        {"app_id": "LSC", "app_name": "Latch Strength Check", "app_group": "Static",
         "engine_type": "SPACE", "comparison_key": "latch_name + input_pin",
         "required_inputs": ["NETLIST", "EDR", "MP", "POWER"]},
        {"app_id": "LS", "app_name": "Level Shifter Check", "app_group": "Static",
         "engine_type": "SPACE", "comparison_key": "ls_name + input_net",
         "required_inputs": ["NETLIST", "EDR", "MP", "POWER"]},
        {"app_id": "PEC", "app_name": "Power Error Check", "app_group": "Static",
         "engine_type": "SPACE", "comparison_key": "net_name + error_type",
         "required_inputs": ["NETLIST", "MP", "POWER"]},
        {"app_id": "CANATR", "app_name": "Coupling Noise Analysis", "app_group": "Static",
         "engine_type": "SPACE", "comparison_key": "victim_net + aggressor_net",
         "required_inputs": ["NETLIST", "SPF", "POWER"]},
        {"app_id": "CDA", "app_name": "Coupling Delay Analyzer", "app_group": "Static",
         "engine_type": "SPACE", "comparison_key": "path_name + coupling_net",
         "required_inputs": ["NETLIST", "SPF", "POWER", "VERILOG"]},
    ]
    
    # Revision Phases
    REVISION_PHASES = ["R00", "R10", "R20", "R30", "R40", "R50", "R60"]
    
    # Realistic Block Names
    BLOCK_TYPES = [
        "FULLCHIP", "PAD", 
        "BANTI_DC", "BTSV_16CH_B", "BTSV_4CH_B", 
        "BPHY_MID_B", "BPHY_1CH_B"
    ]
    
    # PVT Corners (Process_Voltage_Temperature)
    PVT_CORNERS = [
        {"name": "SSPLVCT", "process": "SS", "voltage": "LV", "temp": "CT", "desc": "Slow/LowVolt/Cold"},
        {"name": "SSPLVHT", "process": "SS", "voltage": "LV", "temp": "HT", "desc": "Slow/LowVolt/Hot"},
        {"name": "SFLVCT", "process": "SF", "voltage": "LV", "temp": "CT", "desc": "SlowFast/LowVolt/Cold"},
        {"name": "FSLVCT", "process": "FS", "voltage": "LV", "temp": "CT", "desc": "FastSlow/LowVolt/Cold"},
        {"name": "FFPHVHT", "process": "FF", "voltage": "HV", "temp": "HT", "desc": "Fast/HighVolt/Hot"},
        {"name": "TTTVCT", "process": "TT", "voltage": "TV", "temp": "CT", "desc": "Typical/TypicalVolt/Cold"},
    ]
    
    # Designer 목록 (실제 팀원 이름)
    DESIGNERS_LIST = [
        {"id": "wonwoo", "name": "최원우", "role": "DEVELOPER"},
        {"id": "minji", "name": "권민지", "role": "DEVELOPER"},
        {"id": "kwangsun", "name": "김광선", "role": "ENGINEER"},
        {"id": "jinho", "name": "김진호", "role": "ENGINEER"},
        {"id": "hyungjung", "name": "서형중", "role": "ENGINEER"},
        {"id": "jieun", "name": "오지은", "role": "ENGINEER"},
        {"id": "changwoo", "name": "유창우", "role": "LEAD"},
        {"id": "sunghan", "name": "이성한", "role": "ENGINEER"},
        {"id": "sungju", "name": "이성주", "role": "MANAGER"},
    ]
    
    # Application 수행 가능 Revision (문서 3.2.2 참고)
    APP_AVAILABILITY = {
        "PEC": ["R00", "R10", "R20", "R30", "R40", "R50", "R60"],  # 모든 Revision
        "DSC": ["R20", "R30", "R40", "R50", "R60"],  # R20부터
        "LSC": ["R10", "R20", "R30", "R40", "R50", "R60"],  # R10부터
        "LS": ["R20", "R30", "R40", "R50", "R60"],  # R20부터
        "CANATR": ["R40", "R50", "R60"],  # R40부터
        "CDA": ["R50", "R60"],  # R50부터
    }
    
    def __init__(self):
        self.clear_all()
    
    def clear_all(self):
        """모든 데이터 초기화"""
        self.products: List[Dict] = []
        self.revisions: List[Dict] = []
        self.blocks: List[Dict] = []
        self.signoff_applications: List[Dict] = []
        self.signoff_tasks: List[Dict] = []
        self.signoff_jobs: List[Dict] = []
        self.input_configs: List[Dict] = []
        self.workspaces: List[Dict] = []
        self.results: List[Dict] = []
        self.designers: List[Dict] = []
    
    # ========== CRUD: Product ==========
    def add_product(self, product_id: str, product_name: str = None, 
                    product_type: str = "HBM") -> Optional[Dict]:
        """Product 추가"""
        if any(p["product_id"] == product_id for p in self.products):
            return None
        
        product = {
            "product_id": product_id,
            "product_name": product_name or product_id,
            "product_type": product_type,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "_type": "Product"
        }
        self.products.append(product)
        return product
    
    # ========== CRUD: Revision ==========
    def add_revision(self, revision_id: str, product_id: str, revision_phase: str,
                     signoff_status: str = "NOT_STARTED",
                     required_applications: List[str] = None,
                     previous_revision_id: str = None,
                     due_date: str = None) -> Optional[Dict]:
        """Revision 추가"""
        if not any(p["product_id"] == product_id for p in self.products):
            return None
        if any(r["revision_id"] == revision_id for r in self.revisions):
            return None
        
        revision = {
            "revision_id": revision_id,
            "product_id": product_id,
            "revision_phase": revision_phase,
            "signoff_status": signoff_status,  # NOT_STARTED, IN_PROGRESS, COMPLETED
            "required_applications": required_applications or ["DSC", "LSC", "LS", "PEC", "CANATR", "CDA"],
            "previous_revision_id": previous_revision_id,
            "due_date": due_date,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "_type": "Revision"
        }
        self.revisions.append(revision)
        return revision
    
    # ========== CRUD: Block ==========
    def add_block(self, block_id: str, revision_id: str, block_name: str,
                  netlist_path: str = None, top_subckt: str = None,
                  instance_count: int = None) -> Optional[Dict]:
        """Block 추가"""
        if not any(r["revision_id"] == revision_id for r in self.revisions):
            return None
        if any(b["block_id"] == block_id for b in self.blocks):
            return None
        
        block = {
            "block_id": block_id,
            "revision_id": revision_id,
            "block_name": block_name,
            "netlist_path": netlist_path or f"/data/netlist/{block_name.lower()}.star",
            "top_subckt": top_subckt or f"{block_name}_TOP",
            "instance_count": instance_count or random.randint(100000, 5000000),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "_type": "Block"
        }
        self.blocks.append(block)
        return block
    
    # ========== CRUD: SignoffApplication ==========
    def add_signoff_application(self, app_id: str, app_name: str = None,
                                 app_group: str = "Static", engine_type: str = "SPACE",
                                 comparison_key: str = None,
                                 required_inputs: List[str] = None) -> Optional[Dict]:
        """SignoffApplication 추가"""
        if any(a["app_id"] == app_id for a in self.signoff_applications):
            return None
        
        # 기본 Application 정보 찾기
        default = next((a for a in self.APPLICATIONS if a["app_id"] == app_id), None)
        
        app = {
            "app_id": app_id,
            "app_name": app_name or (default["app_name"] if default else app_id),
            "app_group": app_group,
            "engine_type": engine_type,
            "comparison_key": comparison_key or (default["comparison_key"] if default else ""),
            "required_inputs": required_inputs or (default["required_inputs"] if default else []),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "_type": "SignoffApplication"
        }
        self.signoff_applications.append(app)
        return app
    
    # ========== CRUD: Designer ==========
    def add_designer(self, designer_id: str, name: str = None,
                     email: str = None, team: str = None,
                     role: str = "ENGINEER") -> Optional[Dict]:
        """Designer 추가"""
        if any(d["designer_id"] == designer_id for d in self.designers):
            return None
        
        designer = {
            "designer_id": designer_id,
            "name": name or designer_id,
            "email": email or f"{designer_id}@samsung.com",
            "team": team or "Design Simulation & Signoff Group",
            "role": role,  # ENGINEER, LEAD, MANAGER, DEVELOPER
            "created_at": datetime.now().isoformat(),
            "_type": "Designer"
        }
        self.designers.append(designer)
        return designer
    
    # ========== CRUD: InputConfig ==========
    def add_input_config(self, config_id: str, task_id: str,
                         netlist_file: str = None, edr_file: str = None,
                         mp_file: str = None, power_definition: Dict = None,
                         validation_status: str = "NOT_VALIDATED",
                         base_config_id: str = None) -> Optional[Dict]:
        """InputConfig 추가"""
        if any(c["config_id"] == config_id for c in self.input_configs):
            return None
        
        config = {
            "config_id": config_id,
            "task_id": task_id,
            "netlist_file": netlist_file or "/path/to/netlist.star",
            "edr_file": edr_file or "/path/to/edr_file",
            "mp_file": mp_file or "/path/to/mp_file",
            "power_definition": power_definition or {"VDD": ["VDD_CORE", "VDD_IO"], "GND": ["VSS"]},
            "additional_options": {},
            "validation_status": validation_status,  # NOT_VALIDATED, VALIDATED, ERROR
            "base_config_id": base_config_id,
            "created_at": datetime.now().isoformat(),
            "_type": "InputConfig"
        }
        self.input_configs.append(config)
        return config
    
    # ========== CRUD: SignoffTask ==========
    def add_signoff_task(self, task_id: str, revision_id: str, block_id: str,
                          app_id: str, owner_id: str = None,
                          pvt_corner: Dict = None,
                          status: str = "DEFINED") -> Optional[Dict]:
        """SignoffTask 추가"""
        if any(t["task_id"] == task_id for t in self.signoff_tasks):
            return None
        
        task = {
            "task_id": task_id,
            "revision_id": revision_id,
            "block_id": block_id,
            "app_id": app_id,
            "owner_id": owner_id,
            "pvt_corner": pvt_corner or {"process": "SS", "voltage": "LV", "temp": "CT"},
            "status": status,  # DEFINED, IN_PROGRESS, COMPLETED, BLOCKED
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "_type": "SignoffTask"
        }
        self.signoff_tasks.append(task)
        
        # InputConfig 자동 생성
        config_id = f"CONFIG_{task_id}"
        self.add_input_config(config_id, task_id)
        
        return task
    
    # ========== CRUD: Workspace ==========
    def add_workspace(self, workspace_id: str, job_id: str,
                       local_path: str = None, central_path: str = None,
                       uploaded: str = "NOT_UPLOADED") -> Optional[Dict]:
        """Workspace 추가"""
        if any(w["workspace_id"] == workspace_id for w in self.workspaces):
            return None
        
        workspace = {
            "workspace_id": workspace_id,
            "job_id": job_id,
            "local_path": local_path or f"/user/signoff/job_{job_id}/",
            "central_path": central_path or f"/WORKSPACE/job_{job_id}/",
            "uploaded": uploaded,  # NOT_UPLOADED, UPLOADED, UPLOAD_FAILED
            "uploaded_time": None,
            "created_at": datetime.now().isoformat(),
            "_type": "Workspace"
        }
        self.workspaces.append(workspace)
        return workspace
    
    # ========== CRUD: SignoffJob ==========
    def add_signoff_job(self, job_id: str, task_id: str,
                         lsf_job_id: str = None,
                         status: str = "PENDING") -> Optional[Dict]:
        """SignoffJob 추가"""
        task = next((t for t in self.signoff_tasks if t["task_id"] == task_id), None)
        if not task:
            return None
        if any(j["job_id"] == job_id for j in self.signoff_jobs):
            return None
        
        job = {
            "job_id": job_id,
            "task_id": task_id,
            "lsf_job_id": lsf_job_id or str(random.randint(10000000, 99999999)),
            "status": status,  # PENDING, RUNNING, DONE, FAILED
            "power_warning_nets": [],
            "start_time": None,
            "end_time": None,
            "log_path": None,
            "created_at": datetime.now().isoformat(),
            "_type": "SignoffJob"
        }
        self.signoff_jobs.append(job)
        
        # Workspace 자동 생성
        ws_id = f"WS_{job_id}"
        self.add_workspace(ws_id, job_id)
        
        # Task 상태 업데이트
        task["status"] = "IN_PROGRESS"
        
        return job
    
    # ========== CRUD: Result ==========
    def add_result(self, result_id: str, job_id: str,
                   row_count: int = 1000,
                   waiver_count: int = 0,
                   fixed_count: int = 0,
                   base_result_id: str = None,
                   comparison_summary: Dict = None) -> Optional[Dict]:
        """Result 추가 - WAIVER/FIXED/PENDING 기반"""
        job = next((j for j in self.signoff_jobs if j["job_id"] == job_id), None)
        if not job:
            return None
        if any(r["result_id"] == result_id for r in self.results):
            return None
        
        # pending 계산
        pending_count = row_count - waiver_count - fixed_count
        pending_count = max(0, pending_count)
        
        # 진행률 계산: (waiver + fixed) / total * 100
        progress_pct = ((waiver_count + fixed_count) / row_count * 100) if row_count > 0 else 0
        
        # waiver_migrated_count 계산 (비교 시)
        waiver_migrated = 0
        if comparison_summary:
            waiver_migrated = comparison_summary.get("same_count", 0)
        
        result = {
            "result_id": result_id,
            "job_id": job_id,
            "row_count": row_count,
            "waiver_count": waiver_count,
            "fixed_count": fixed_count,
            "pending_count": pending_count,
            "waiver_progress_pct": round(progress_pct, 1),
            "base_result_id": base_result_id,
            "comparison_summary": comparison_summary or {
                "same_count": 0,
                "diff_count": 0,
                "new_count": row_count,
                "removed_count": 0
            },
            "waiver_migrated_count": waiver_migrated,
            "result_file_path": f"/WORKSPACE/result_{result_id}.parquet",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "_type": "Result"
        }
        self.results.append(result)
        
        # Job/Task 상태 업데이트
        job["status"] = "DONE"
        job["end_time"] = datetime.now().isoformat()
        
        task = next((t for t in self.signoff_tasks if t["task_id"] == job["task_id"]), None)
        if task:
            task["status"] = "COMPLETED" if pending_count == 0 else "IN_PROGRESS"
            task["updated_at"] = datetime.now().isoformat()
        
        # Workspace 업로드 상태 업데이트
        ws = next((w for w in self.workspaces if w["job_id"] == job_id), None)
        if ws:
            ws["uploaded"] = "UPLOADED"
            ws["uploaded_time"] = datetime.now().isoformat()
        
        return result
    
    # ========== 템플릿 데이터 로드 ==========
    def load_scenario_a_full_lifecycle(self):
        """시나리오 A: HBM4E 전체 라이프사이클 (R00→R10→R30→R40→R60)"""
        self.clear_all()
        
        # 1. Product
        self.add_product("HBM4E", "HBM4E 32GB Wide I/O", "HBM")
        
        # 2. 6개 Application
        for app in self.APPLICATIONS:
            self.add_signoff_application(**app)
        
        # 3. Designers (실제 팀원 이름)
        for d in self.DESIGNERS_LIST:
            self.add_designer(d["id"], d["name"], role=d["role"])
        
        # 4. Revisions & Blocks & Tasks & Jobs & Results
        # 각 Revision이 100% 완료되어야 다음으로 진행
        revisions_data = [
            ("R00", 100, 1.0),   # 완료됨
            ("R10", 100, 1.0),   # 완료됨
            ("R30", 100, 1.0),   # 완료됨
            ("R40", 85, 0.85),   # 진행 중
            ("R60", 0, 0),       # 아직 시작 안함
        ]
        
        blocks = self.BLOCK_TYPES[:5]  # FULLCHIP, PAD, BANTI_DC, BTSV_16CH_B, BTSV_4CH_B
        prev_rev_id = None
        
        for rev_phase, progress, completion in revisions_data:
            rev_id = f"HBM4E_{rev_phase}"
            status = "COMPLETED" if progress == 100 else ("IN_PROGRESS" if progress > 0 else "NOT_STARTED")
            
            self.add_revision(rev_id, "HBM4E", rev_phase, status, 
                              previous_revision_id=prev_rev_id)
            
            # Blocks for this revision
            for block_name in blocks:
                block_id = f"{rev_id}_{block_name}"
                self.add_block(block_id, rev_id, block_name)
                
                # Tasks for each block x app (Revision별 수행 가능 Application만)
                for app in self.signoff_applications:
                    app_id = app["app_id"]
                    
                    # 해당 Revision에서 수행 가능한 Application인지 확인
                    if rev_phase not in self.APP_AVAILABILITY.get(app_id, []):
                        continue
                    
                    task_id = f"{block_id}_{app_id}"
                    # PVT Corner 선택
                    pvt = random.choice(self.PVT_CORNERS)
                    owner = random.choice(self.designers)["designer_id"]
                    
                    self.add_signoff_task(task_id, rev_id, block_id, app_id, owner,
                                          pvt_corner={"name": pvt["name"], "process": pvt["process"],
                                                      "voltage": pvt["voltage"], "temp": pvt["temp"]})
                    
                    # Create Job and Result based on progress
                    if completion > 0 and random.random() < completion:
                        job_id = f"JOB_{task_id}"
                        self.add_signoff_job(job_id, task_id, status="DONE")
                        
                        # Update job times
                        job = next(j for j in self.signoff_jobs if j["job_id"] == job_id)
                        job["start_time"] = (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
                        job["end_time"] = datetime.now().isoformat()
                        
                        # Result data - 현실적인 10만~100만 행
                        total_rows = random.randint(100000, 500000)
                        # 완료된 Revision은 100% waiver+fixed
                        if completion >= 1.0:
                            processed = total_rows
                        else:
                            processed = int(total_rows * (0.7 + completion * 0.25))
                        waiver = int(processed * 0.75)  # 75%는 WAIVER (가성)
                        fixed = processed - waiver       # 나머지는 FIXED (진성 수정)
                        
                        # Comparison with previous revision
                        prev_result_id = None
                        comparison = None
                        if prev_rev_id:
                            prev_result_id = f"RESULT_{prev_rev_id}_{block_name}_{app_id}"
                            same = int(total_rows * 0.6)
                            comparison = {
                                "same_count": same,
                                "diff_count": int(total_rows * 0.15),
                                "new_count": int(total_rows * 0.2),
                                "removed_count": int(total_rows * 0.05)
                            }
                        
                        result_id = f"RESULT_{task_id}"
                        self.add_result(result_id, job_id, total_rows, waiver, fixed,
                                        prev_result_id, comparison)
            
            prev_rev_id = rev_id
    
    def load_scenario_b_r30_detail(self):
        """시나리오 B: R40 상세 실행 결과 (5개 Application - R40에서 수행 가능한 것들)"""
        self.clear_all()
        
        # Product
        self.add_product("HBM4E", "HBM4E 32GB Wide I/O", "HBM")
        
        # Applications
        for app in self.APPLICATIONS:
            self.add_signoff_application(**app)
        
        # Designers (실제 팀원)
        for d in self.DESIGNERS_LIST:
            self.add_designer(d["id"], d["name"], role=d["role"])
        
        # R40 Revision
        self.add_revision("HBM4E_R40", "HBM4E", "R40", "IN_PROGRESS")
        
        # 5 Blocks (실제 Block 이름)
        for block_name in self.BLOCK_TYPES[:5]:
            block_id = f"HBM4E_R40_{block_name}"
            self.add_block(block_id, "HBM4E_R40", block_name)
            
            # R40에서 수행 가능한 Applications: PEC, DSC, LSC, LS, CANATR (5개)
            available_apps = ["PEC", "DSC", "LSC", "LS", "CANATR"]
            for app in self.signoff_applications:
                if app["app_id"] not in available_apps:
                    continue
                    
                task_id = f"{block_id}_{app['app_id']}"
                pvt = random.choice(self.PVT_CORNERS)
                owner = random.choice(self.designers)["designer_id"]
                
                self.add_signoff_task(task_id, "HBM4E_R40", block_id, app["app_id"], owner,
                                      pvt_corner={"name": pvt["name"], "process": pvt["process"],
                                                  "voltage": pvt["voltage"], "temp": pvt["temp"]})
                
                # Job and Result (현실적인 데이터)
                job_id = f"JOB_{task_id}"
                self.add_signoff_job(job_id, task_id, status="DONE")
                
                # 현실적인 10만~50만 행
                total = random.randint(100000, 300000)
                # R40: 약 85% 완료
                processed = int(total * 0.85)
                waiver = int(processed * 0.78)
                fixed = processed - waiver
                
                self.add_result(f"RESULT_{task_id}", job_id, total, waiver, fixed)
    
    def load_scenario_c_compare_migration(self):
        """시나리오 C: R30 vs R40 비교 & Waiver Migration 시뮬레이션"""
        self.clear_all()
        
        # Product
        self.add_product("HBM4E", "HBM4E 32GB Wide I/O", "HBM")
        
        # Applications
        for app in self.APPLICATIONS:
            self.add_signoff_application(**app)
        
        # Designers (일부)
        for d in self.DESIGNERS_LIST[:4]:
            self.add_designer(d["id"], d["name"], role=d["role"])
        
        # R30 (이전 버전 - 완료됨)
        self.add_revision("HBM4E_R30", "HBM4E", "R30", "COMPLETED")
        
        # R40에서 수행 가능한 Applications로 제한 (비교 대상)
        compare_apps = ["DSC", "LSC", "LS", "PEC"]
        
        for block_name in ["FULLCHIP", "PAD", "BANTI_DC"]:
            block_id = f"HBM4E_R30_{block_name}"
            self.add_block(block_id, "HBM4E_R30", block_name)
            
            for app in self.signoff_applications:
                if app["app_id"] not in compare_apps:
                    continue
                    
                task_id = f"{block_id}_{app['app_id']}"
                pvt = random.choice(self.PVT_CORNERS)
                owner = random.choice(self.designers)["designer_id"]
                
                self.add_signoff_task(task_id, "HBM4E_R30", block_id, 
                                       app["app_id"], owner, status="COMPLETED",
                                       pvt_corner={"name": pvt["name"], "process": pvt["process"],
                                                   "voltage": pvt["voltage"], "temp": pvt["temp"]})
                
                job_id = f"JOB_{task_id}"
                self.add_signoff_job(job_id, task_id, status="DONE")
                
                # R30 - 100% 완료 (현실적인 데이터)
                total = random.randint(150000, 250000)
                waiver = int(total * 0.75)
                fixed = total - waiver
                self.add_result(f"RESULT_{task_id}", job_id, total, waiver, fixed)
        
        # R40 (현재 버전 - 진행중)
        self.add_revision("HBM4E_R40", "HBM4E", "R40", "IN_PROGRESS",
                          previous_revision_id="HBM4E_R30")
        
        for block_name in ["FULLCHIP", "PAD", "BANTI_DC"]:
            block_id = f"HBM4E_R40_{block_name}"
            self.add_block(block_id, "HBM4E_R40", block_name)
            
            for app in self.signoff_applications:
                if app["app_id"] not in compare_apps:
                    continue
                    
                task_id = f"{block_id}_{app['app_id']}"
                pvt = random.choice(self.PVT_CORNERS)
                owner = random.choice(self.designers)["designer_id"]
                
                self.add_signoff_task(task_id, "HBM4E_R40", block_id,
                                       app["app_id"], owner,
                                       pvt_corner={"name": pvt["name"], "process": pvt["process"],
                                                   "voltage": pvt["voltage"], "temp": pvt["temp"]})
                
                job_id = f"JOB_{task_id}"
                self.add_signoff_job(job_id, task_id, status="DONE")
                
                # R40 with comparison to R30 (현실적인 비교 데이터)
                total = random.randint(180000, 280000)  # R40이 약간 더 많음
                prev_result_id = f"RESULT_HBM4E_R30_{block_name}_{app['app_id']}"
                
                # 비교 결과: 약 60% same, 15% diff, 20% new, 5% removed
                same_count = int(total * 0.60)
                diff_count = int(total * 0.15)
                new_count = int(total * 0.20)
                removed_count = int(total * 0.05)
                
                comparison = {
                    "same_count": same_count,     # 이전과 동일 → WAIVER 자동 이관
                    "diff_count": diff_count,     # 값 변경 → 재검토 필요
                    "new_count": new_count,       # 신규 → 검토 필요
                    "removed_count": removed_count # 이전에만 있음 (해결됨)
                }
                
                # Waiver 이관: same은 자동 이관, diff와 new는 80% 처리됨
                waiver = int(same_count * 0.95) + int((diff_count + new_count) * 0.40)  # 이관 + 신규 처리
                fixed = int((diff_count + new_count) * 0.35)
                # pending = 나머지 (new 중 미처리)
                
                self.add_result(f"RESULT_{task_id}", job_id, total, waiver, fixed,
                                prev_result_id, comparison)
    
    def load_template(self, scenario: str = "full_lifecycle"):
        """시나리오 로드"""
        if scenario == "full_lifecycle" or scenario == "a":
            self.load_scenario_a_full_lifecycle()
        elif scenario == "r30_detail" or scenario == "b":
            self.load_scenario_b_r30_detail()
        elif scenario == "compare" or scenario == "c":
            self.load_scenario_c_compare_migration()
        else:
            self.load_scenario_a_full_lifecycle()
    
    # ========== 통계 ==========
    def get_statistics(self) -> Dict:
        """전체 통계"""
        total_rows = sum(r["row_count"] for r in self.results)
        total_waiver = sum(r["waiver_count"] for r in self.results)
        total_fixed = sum(r["fixed_count"] for r in self.results)
        total_pending = sum(r["pending_count"] for r in self.results)
        
        completed_tasks = len([t for t in self.signoff_tasks if t["status"] == "COMPLETED"])
        
        return {
            "products": len(self.products),
            "revisions": len(self.revisions),
            "blocks": len(self.blocks),
            "applications": len(self.signoff_applications),
            "tasks": len(self.signoff_tasks),
            "jobs": len(self.signoff_jobs),
            "configs": len(self.input_configs),
            "workspaces": len(self.workspaces),
            "results": len(self.results),
            "designers": len(self.designers),
            "total_rows": total_rows,
            "total_waiver": total_waiver,
            "total_fixed": total_fixed,
            "total_pending": total_pending,
            "overall_progress": round((total_waiver + total_fixed) / total_rows * 100, 1) if total_rows > 0 else 0,
            "completed_tasks": completed_tasks,
        }
    
    def get_revision_progress(self) -> List[Dict]:
        """Revision별 진행률"""
        result = []
        for rev in self.revisions:
            tasks = [t for t in self.signoff_tasks if t["revision_id"] == rev["revision_id"]]
            jobs = [j for j in self.signoff_jobs if j["task_id"] in [t["task_id"] for t in tasks]]
            results = [r for r in self.results if r["job_id"] in [j["job_id"] for j in jobs]]
            
            total = sum(r["row_count"] for r in results)
            waiver = sum(r["waiver_count"] for r in results)
            fixed = sum(r["fixed_count"] for r in results)
            pending = sum(r["pending_count"] for r in results)
            
            result.append({
                "revision_id": rev["revision_id"],
                "revision_phase": rev["revision_phase"],
                "status": rev["signoff_status"],
                "total_tasks": len(tasks),
                "completed_jobs": len([j for j in jobs if j["status"] == "DONE"]),
                "total_rows": total,
                "waiver_count": waiver,
                "fixed_count": fixed,
                "pending_count": pending,
                "progress_pct": round((waiver + fixed) / total * 100, 1) if total > 0 else 0
            })
        return result
    
    # ========== Export ==========
    def to_json_graphrag(self) -> str:
        """GraphRAG/LLM용 JSON Export"""
        nodes = []
        edges = []
        
        # Nodes
        for p in self.products:
            nodes.append({"id": p["product_id"], "type": "Product", "properties": p})
        for r in self.revisions:
            nodes.append({"id": r["revision_id"], "type": "Revision", "properties": r})
        for b in self.blocks:
            nodes.append({"id": b["block_id"], "type": "Block", "properties": b})
        for a in self.signoff_applications:
            nodes.append({"id": a["app_id"], "type": "SignoffApplication", "properties": a})
        for d in self.designers:
            nodes.append({"id": d["designer_id"], "type": "Designer", "properties": d})
        for t in self.signoff_tasks:
            nodes.append({"id": t["task_id"], "type": "SignoffTask", "properties": t})
        for c in self.input_configs:
            nodes.append({"id": c["config_id"], "type": "InputConfig", "properties": c})
        for j in self.signoff_jobs:
            nodes.append({"id": j["job_id"], "type": "SignoffJob", "properties": j})
        for w in self.workspaces:
            nodes.append({"id": w["workspace_id"], "type": "Workspace", "properties": w})
        for res in self.results:
            nodes.append({"id": res["result_id"], "type": "Result", "properties": res})
        
        # Edges
        edge_id = 0
        for r in self.revisions:
            edges.append({"id": f"e{edge_id}", "source": r["product_id"], "target": r["revision_id"], 
                          "relationship": "has_revision"})
            edge_id += 1
            if r["previous_revision_id"]:
                edges.append({"id": f"e{edge_id}", "source": r["revision_id"], 
                              "target": r["previous_revision_id"], "relationship": "previous_version"})
                edge_id += 1
        
        for b in self.blocks:
            edges.append({"id": f"e{edge_id}", "source": b["revision_id"], "target": b["block_id"],
                          "relationship": "has_block"})
            edge_id += 1
        
        for t in self.signoff_tasks:
            edges.append({"id": f"e{edge_id}", "source": t["block_id"], "target": t["task_id"],
                          "relationship": "target_of"})
            edge_id += 1
            edges.append({"id": f"e{edge_id}", "source": t["task_id"], "target": t["app_id"],
                          "relationship": "uses_application"})
            edge_id += 1
            if t["owner_id"]:
                edges.append({"id": f"e{edge_id}", "source": t["task_id"], "target": t["owner_id"],
                              "relationship": "owned_by"})
                edge_id += 1
        
        for c in self.input_configs:
            edges.append({"id": f"e{edge_id}", "source": c["task_id"], "target": c["config_id"],
                          "relationship": "uses_config"})
            edge_id += 1
        
        for j in self.signoff_jobs:
            edges.append({"id": f"e{edge_id}", "source": j["task_id"], "target": j["job_id"],
                          "relationship": "has_job"})
            edge_id += 1
        
        for w in self.workspaces:
            edges.append({"id": f"e{edge_id}", "source": w["job_id"], "target": w["workspace_id"],
                          "relationship": "executes_in"})
            edge_id += 1
        
        for res in self.results:
            edges.append({"id": f"e{edge_id}", "source": res["job_id"], "target": res["result_id"],
                          "relationship": "produces"})
            edge_id += 1
            if res["base_result_id"]:
                edges.append({"id": f"e{edge_id}", "source": res["result_id"], 
                              "target": res["base_result_id"], "relationship": "compared_with"})
                edge_id += 1
        
        return json.dumps({
            "metadata": {
                "name": "Signoff Ontology",
                "version": "2.0",
                "created_at": datetime.now().isoformat(),
                "object_types": list(self.COLORS.keys())
            },
            "nodes": nodes,
            "edges": edges
        }, ensure_ascii=False, indent=2)
    
    def to_graph_elements(self) -> List[Dict]:
        """Cytoscape용 그래프 요소"""
        elements = []
        
        # Nodes
        for p in self.products:
            elements.append({"data": {"id": p["product_id"], "label": p["product_name"],
                                       "type": "Product", "color": self.COLORS["Product"]}})
        for r in self.revisions:
            elements.append({"data": {"id": r["revision_id"], "label": r["revision_phase"],
                                       "type": "Revision", "color": self.COLORS["Revision"]}})
        for b in self.blocks:
            elements.append({"data": {"id": b["block_id"], "label": b["block_name"],
                                       "type": "Block", "color": self.COLORS["Block"]}})
        for a in self.signoff_applications:
            elements.append({"data": {"id": a["app_id"], "label": a["app_name"],
                                       "type": "SignoffApplication", "color": self.COLORS["SignoffApplication"]}})
        for d in self.designers:
            elements.append({"data": {"id": d["designer_id"], "label": d["name"],
                                       "type": "Designer", "color": self.COLORS["Designer"]}})
        for t in self.signoff_tasks:
            label = t["task_id"].split("_")[-1] if "_" in t["task_id"] else t["task_id"]
            elements.append({"data": {"id": t["task_id"], "label": label,
                                       "type": "SignoffTask", "color": self.COLORS["SignoffTask"]}})
        for j in self.signoff_jobs:
            elements.append({"data": {"id": j["job_id"], "label": j["lsf_job_id"],
                                       "type": "SignoffJob", "color": self.COLORS["SignoffJob"]}})
        for res in self.results:
            label = f"{res['waiver_progress_pct']}%"
            elements.append({"data": {"id": res["result_id"], "label": label,
                                       "type": "Result", "color": self.COLORS["Result"]}})
        
        # Edges
        for r in self.revisions:
            elements.append({"data": {"source": r["product_id"], "target": r["revision_id"]}})
        for b in self.blocks:
            elements.append({"data": {"source": b["revision_id"], "target": b["block_id"]}})
        for t in self.signoff_tasks:
            elements.append({"data": {"source": t["block_id"], "target": t["task_id"]}})
            elements.append({"data": {"source": t["task_id"], "target": t["app_id"]}})
        for j in self.signoff_jobs:
            elements.append({"data": {"source": j["task_id"], "target": j["job_id"]}})
        for res in self.results:
            elements.append({"data": {"source": res["job_id"], "target": res["result_id"]}})
        
        return elements
    
    def get_all_objects(self) -> Dict[str, List[Dict]]:
        """모든 Object 반환"""
        return {
            "Product": self.products,
            "Revision": self.revisions,
            "Block": self.blocks,
            "SignoffApplication": self.signoff_applications,
            "Designer": self.designers,
            "SignoffTask": self.signoff_tasks,
            "InputConfig": self.input_configs,
            "SignoffJob": self.signoff_jobs,
            "Workspace": self.workspaces,
            "Result": self.results,
        }
    
    # ========== Dropdown Options ==========
    def get_product_options(self):
        return [{"value": p["product_id"], "label": p["product_name"]} for p in self.products]
    
    def get_revision_options(self):
        return [{"value": r["revision_id"], "label": f"{r['product_id']}/{r['revision_phase']}"} for r in self.revisions]
    
    def get_block_options(self):
        return [{"value": b["block_id"], "label": b["block_name"]} for b in self.blocks]
    
    def get_app_options(self):
        return [{"value": a["app_id"], "label": a["app_name"]} for a in self.signoff_applications]
    
    def get_designer_options(self):
        return [{"value": d["designer_id"], "label": d["name"]} for d in self.designers]
    
    def get_task_options(self):
        return [{"value": t["task_id"], "label": t["task_id"]} for t in self.signoff_tasks]
    
    def get_job_options(self):
        return [{"value": j["job_id"], "label": j["job_id"]} for j in self.signoff_jobs]


# Global instance
store = SignoffOntologyStore()
