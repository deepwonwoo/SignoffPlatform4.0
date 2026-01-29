"""
Signoff Ontology Store (v2.1 Refactored)
Based on: updated_Signoff Platform Ontology.md (13 Object Types, InputConfig Separated)

3-Layer Architecture:
  Semantic Layer (7개):
    Product, Revision, Block, Designer, SignoffApplication, CriteriaSet, Workspace
  Kinetic Layer (3개):
    InputConfig (New!), SignoffJob, Result
  Dynamic Layer (4개):
    CategorizePart, CompareResult, WaiverDecision, SignoffIssue
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import random
import json

class SignoffOntologyStore:
    """Signoff Ontology - 13개 핵심 Object Type 관리 (InputConfig 분리됨)"""
    
    # ========== LAYER DEFINITIONS ==========
    LAYERS = {
        "Semantic": ["Product", "Revision", "Block", "Designer", "SignoffApplication", "CriteriaSet", "Workspace"],
        "Kinetic": ["InputConfig", "SignoffJob", "Result"], # InputConfig Added
        "Dynamic": ["CategorizePart", "CompareResult", "WaiverDecision", "SignoffIssue"]
    }
    
    # Colors & Icons
    COLORS = {
        "Product": "#4263eb", "Revision": "#5c7cfa", "Block": "#748ffc", "Designer": "#fab005",
        "SignoffApplication": "#fd7e14", "CriteriaSet": "#e8590c", "Workspace": "#fcc419",
        "InputConfig": "#20c997", "SignoffJob": "#40c057", "Result": "#69db7c", # InputConfig: Teal
        "CategorizePart": "#f06595", "CompareResult": "#e64980", "WaiverDecision": "#be4bdb", "SignoffIssue": "#9c36b5",
    }
    ICONS = {
        "Product": "📦", "Revision": "📋", "Block": "🔲", "Designer": "👤",
        "SignoffApplication": "🔧", "CriteriaSet": "📏", "Workspace": "📁",
        "InputConfig": "⚙️", "SignoffJob": "⚡", "Result": "📊",
        "CategorizePart": "👥", "CompareResult": "🔄", "WaiverDecision": "✅", "SignoffIssue": "❓",
    }

    # Reference Data
    DESIGN_STAGES = {"R00": "SCHEMATIC", "R30": "POST_LAYOUT", "R60": "FINAL"}
    BLOCK_NAMES = ["FULLCHIP", "CORE", "PHY", "PAD"]
    PVT_CORNERS = [
        {"name": "SSPLVCT", "desc": "Slow/Low/Cold"},
        {"name": "FFPHVHT", "desc": "Fast/High/Hot"},
        {"name": "TTTVCT", "desc": "Typical"}
    ]
    APPLICATIONS = [
        {"app_id": "DSC", "app_name": "Driver Size Check", "app_group": "STATIC", "engine_type": "SPACE"},
        {"app_id": "LSC", "app_name": "Latch Setup Check", "app_group": "STATIC", "engine_type": "SPACE"},
        {"app_id": "PEC", "app_name": "Power/ESD Checker", "app_group": "PRE_LAYOUT", "engine_type": "SPACE"},
    ]
    DESIGNERS = [
        {"id": "kim_cs", "name": "Kim Cheolsoo", "role": "LEAD"},
        {"id": "lee_yh", "name": "Lee Younghee", "role": "ENGINEER"},
    ]

    def __init__(self):
        self.clear_all()
    
    def clear_all(self):
        # Semantic
        self.products = []
        self.revisions = []
        self.blocks = []
        self.designers = []
        self.signoff_applications = []
        self.criteria_sets = []
        self.workspaces = []
        # Kinetic
        self.input_configs = [] # New
        self.signoff_jobs = []
        self.results = []
        # Dynamic
        self.categorize_parts = []
        self.compare_results = []
        self.waiver_decisions = []
        self.signoff_issues = []

    # ========== SEMANTIC LAYER ==========
    def add_product(self, product_id, product_name=None):
        if any(p["product_id"] == product_id for p in self.products): return
        self.products.append({
            "product_id": product_id, "product_name": product_name or product_id,
            "created_at": datetime.now().isoformat()
        })

    def add_revision(self, revision_id, product_id, revision_code, status="IN_PROGRESS"):
        if any(r["revision_id"] == revision_id for r in self.revisions): return
        self.revisions.append({
            "revision_id": revision_id, "product_id": product_id, "revision_code": revision_code,
            "status": status, "created_at": datetime.now().isoformat()
        })

    def add_block(self, block_id, revision_id, block_name, designer_id=None):
        if any(b["block_id"] == block_id for b in self.blocks): return
        self.blocks.append({
            "block_id": block_id, "revision_id": revision_id, "block_name": block_name,
            "designer_id": designer_id, "created_at": datetime.now().isoformat()
        })

    def add_designer(self, designer_id, name, role="ENGINEER"):
        if any(d["designer_id"] == designer_id for d in self.designers): return
        self.designers.append({"designer_id": designer_id, "name": name, "role": role})

    def add_signoff_application(self, app_id, app_name, app_group, engine_type="SPACE"):
        if any(a["app_id"] == app_id for a in self.signoff_applications): return
        self.signoff_applications.append({
            "app_id": app_id, "app_name": app_name, "app_group": app_group, 
            "engine_type": engine_type
        })
    
    def add_criteria_set(self, criteria_id, app_id, criteria_name=None):
        if any(c["criteria_id"] == criteria_id for c in self.criteria_sets): return
        self.criteria_sets.append({
            "criteria_id": criteria_id, "app_id": app_id, 
            "criteria_name": criteria_name or f"{app_id} Criteria"
        })

    def add_workspace(self, workspace_id, workspace_type="LOCAL", base_path=None):
        if any(w["workspace_id"] == workspace_id for w in self.workspaces): return
        self.workspaces.append({
            "workspace_id": workspace_id, "workspace_type": workspace_type, 
            "base_path": base_path or f"/ws/{workspace_id}"
        })

    # ========== KINETIC LAYER ==========
    def add_input_config(self, config_id, app_id, revision_id, config_name=None, pvt_corner="SSPLVCT"):
        if any(c["config_id"] == config_id for c in self.input_configs): return
        self.input_configs.append({
            "config_id": config_id, "app_id": app_id, "revision_id": revision_id,
            "config_name": config_name or f"CFG-{app_id}", "pvt_corner": pvt_corner,
            "is_validated": True, "created_at": datetime.now().isoformat()
        })

    def add_signoff_job(self, job_id, config_id, block_id, workspace_id, executed_by, status="DONE"):
        if any(j["job_id"] == job_id for j in self.signoff_jobs): return
        # Find related data for graph links
        cfg = next((c for c in self.input_configs if c["config_id"] == config_id), None)
        self.signoff_jobs.append({
            "job_id": job_id, "config_id": config_id, "block_id": block_id,
            "workspace_id": workspace_id, "executed_by": executed_by, "status": status,
            "app_id": cfg["app_id"] if cfg else "Unknown",
            "created_at": datetime.now().isoformat()
        })

    def add_result(self, result_id, job_id, row_count, waiver_count=0, fixed_count=0, fail_count=None):
        if any(r["result_id"] == result_id for r in self.results): return
        if fail_count is None: fail_count = row_count - waiver_count - fixed_count
        self.results.append({
            "result_id": result_id, "job_id": job_id, 
            "row_count": row_count, "fail_count": fail_count, 
            "waiver_count": waiver_count, "fixed_count": fixed_count,
            "created_at": datetime.now().isoformat()
        })

    # ========== DYNAMIC LAYER ==========
    def add_compare_result(self, compare_id, source_res, target_res, new_fail=0):
        if any(c["compare_id"] == compare_id for c in self.compare_results): return
        self.compare_results.append({
            "compare_id": compare_id, "source_result_id": source_res, 
            "target_result_id": target_res, "new_fail_count": new_fail
        })

    # ========== SCENARIO ==========
    def load_template(self, name="full_lifecycle"):
        self.clear_all()
        # Common
        self.add_product("HBM4E")
        for d in self.DESIGNERS: self.add_designer(d["id"], d["name"], d["role"])
        for a in self.APPLICATIONS: 
            self.add_signoff_application(a["app_id"], a["app_name"], a["app_group"])
            self.add_criteria_set(f"{a['app_id']}_CRIT", a["app_id"])
        
        # Scenarios
        revs = ["R30", "R40"]
        for r_code in revs:
            rev_id = f"HBM4E_{r_code}"
            self.add_revision(rev_id, "HBM4E", r_code, "COMPLETED" if r_code=="R30" else "IN_PROGRESS")
            self.add_block(f"{rev_id}_FULLCHIP", rev_id, "FULLCHIP", "kim_cs")
            
            # Workspace & Config per App
            self.add_workspace(f"WS_{r_code}", "LOCAL")
            
            for app in self.APPLICATIONS:
                # 1. Config Creation is now REQUIRED
                cfg_id = f"CFG-{r_code}-{app['app_id']}"
                self.add_input_config(cfg_id, app['app_id'], rev_id)
                
                # 2. Job Creation uses Config
                job_id = f"JOB-{r_code}-{app['app_id']}"
                self.add_signoff_job(job_id, cfg_id, f"{rev_id}_FULLCHIP", f"WS_{r_code}", "kim_cs")
                
                # 3. Result
                res_id = f"RES-{job_id}"
                self.add_result(res_id, job_id, 10000, 500, 100)
        
        # Compare
        if name == "compare":
            self.add_compare_result("CMP-R30-R40", "RES-JOB-R30-DSC", "RES-JOB-R40-DSC", 50)

    # ========== EXPORT & STATS ==========
    def get_object_schema(self):
        # Simplified schema return for v2.0 UI
        return {
            "InputConfig": {"layer": "Kinetic", "color": self.COLORS["InputConfig"], "icon": self.ICONS["InputConfig"], "description": "재사용 가능한 입력 설정 (Netlist, PVT 등)", "properties": ["config_id", "pvt_corner"]},
            "Product": {"layer": "Semantic", "color": self.COLORS["Product"], "icon": self.ICONS["Product"], "description": "제품", "properties": ["product_id"]},
            "Revision": {"layer": "Semantic", "color": self.COLORS["Revision"], "icon": self.ICONS["Revision"], "description": "버전", "properties": ["revision_code", "status"]},
            "Block": {"layer": "Semantic", "color": self.COLORS["Block"], "icon": self.ICONS["Block"], "description": "회로 블록", "properties": ["block_name"]},
            "SignoffJob": {"layer": "Kinetic", "color": self.COLORS["SignoffJob"], "icon": self.ICONS["SignoffJob"], "description": "실행 이력", "properties": ["status", "executed_by"]},
            "Result": {"layer": "Dynamic", "color": self.COLORS["Result"], "icon": self.ICONS["Result"], "description": "검증 결과", "properties": ["fail_count", "waiver_count"]},
            # ... others can be added if needed
        }

    def get_statistics(self):
        return {
            "products": len(self.products), "revisions": len(self.revisions), "blocks": len(self.blocks),
            "configs": len(self.input_configs), "jobs": len(self.signoff_jobs), "results": len(self.results),
            "total_rows": sum(r["row_count"] for r in self.results),
            "waiver_count": sum(r["waiver_count"] for r in self.results),
            "fixed_count": sum(r["fixed_count"] for r in self.results),
            "pending_count": sum(r["fail_count"] for r in self.results),
            "progress_pct": 50 # Mock
        }

    def get_full_json(self):
        return {
            "input_configs": self.input_configs, "signoff_jobs": self.signoff_jobs, "results": self.results
        }

    def to_graph_elements(self):
        el = []
        for c in self.input_configs:
            el.append({"data": {"id": c["config_id"], "label": "CFG", "type": "InputConfig", "color": self.COLORS["InputConfig"]}})
            el.append({"data": {"source": c["config_id"], "target": c["app_id"], "label": "for_app"}})
        for j in self.signoff_jobs:
            el.append({"data": {"id": j["job_id"], "label": "JOB", "type": "SignoffJob", "color": self.COLORS["SignoffJob"]}})
            el.append({"data": {"source": j["job_id"], "target": j["config_id"], "label": "uses_config"}})
            el.append({"data": {"source": j["job_id"], "target": j["workspace_id"], "label": "in_ws"}})
            el.append({"data": {"source": j["job_id"], "target": j["block_id"], "label": "target"}})
        
        # Add minimal nodes for referenced objects to avoid graph errors
        for a in self.signoff_applications: el.append({"data": {"id": a["app_id"], "label": a["app_id"], "type": "SignoffApplication", "color": self.COLORS["SignoffApplication"]}})
        for b in self.blocks: el.append({"data": {"id": b["block_id"], "label": b["block_name"], "type": "Block", "color": self.COLORS["Block"]}})
        for w in self.workspaces: el.append({"data": {"id": w["workspace_id"], "label": "WS", "type": "Workspace", "color": self.COLORS["Workspace"]}})
        return el

    def get_revision_progress(self):
        return []

store = SignoffOntologyStore()
