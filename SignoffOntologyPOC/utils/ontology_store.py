"""
Signoff Ontology Store - 온톨로지 상태 관리 모듈 (Enhanced)
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import random

class OntologyStore:
    """Signoff Ontology 객체들을 저장하고 관리하는 클래스"""
    
    # 객체 유형별 색상 및 순서 (왼쪽→오른쪽 레이어 순서)
    OBJECT_ORDER = ["Product", "Revision", "Block", "Designer", "SignoffApp", "Task", "Job", "Result"]
    
    COLORS = {
        "Product": "#4263eb",      # 파란색 - 기준 데이터
        "Revision": "#5c7cfa", 
        "Block": "#748ffc",
        "Designer": "#9775fa",     # 보라색 - 사람
        "SignoffApp": "#20c997",   # 초록색 - 실행 데이터
        "Task": "#38d9a9",
        "Job": "#63e6be",
        "Result": "#ffa94d",       # 주황색 - 결과 데이터
    }
    
    def __init__(self):
        self.clear_all()
        
    def clear_all(self):
        """모든 데이터 초기화"""
        self.products: List[Dict] = []
        self.revisions: List[Dict] = []
        self.blocks: List[Dict] = []
        self.designers: List[Dict] = []
        self.signoff_apps: List[Dict] = []
        self.tasks: List[Dict] = []
        self.jobs: List[Dict] = []
        self.results: List[Dict] = []
        
    # ===== CRUD Operations =====
    
    def add_product(self, name: str) -> Optional[Dict]:
        """Product 추가 (중복 방지)"""
        new_id = f"PROD_{name}"
        if any(p["id"] == new_id for p in self.products):
            return None
        
        product = {
            "id": new_id,
            "name": name,
            "type": "Product",
            "created_at": datetime.now().isoformat()
        }
        self.products.append(product)
        return product
    
    def add_revision(self, product_id: str, name: str) -> Optional[Dict]:
        """Revision 추가 (중복 방지)"""
        product = next((p for p in self.products if p["id"] == product_id), None)
        if not product:
            return None
        
        new_id = f"{product_id}_{name}"
        if any(r["id"] == new_id for r in self.revisions):
            return None
            
        revision = {
            "id": new_id,
            "product_id": product_id,
            "name": name,
            "type": "Revision",
            "created_at": datetime.now().isoformat()
        }
        self.revisions.append(revision)
        return revision
    
    def add_block(self, revision_id: str, name: str) -> Optional[Dict]:
        """Block 추가 (중복 방지)"""
        revision = next((r for r in self.revisions if r["id"] == revision_id), None)
        if not revision:
            return None
        
        new_id = f"{revision_id}_{name}"
        if any(b["id"] == new_id for b in self.blocks):
            return None
            
        block = {
            "id": new_id,
            "revision_id": revision_id,
            "name": name,
            "type": "Block",
            "created_at": datetime.now().isoformat()
        }
        self.blocks.append(block)
        return block
    
    def add_designer(self, name: str) -> Optional[Dict]:
        """Designer 추가 (중복 방지)"""
        new_id = f"USER_{name}"
        if any(d["id"] == new_id for d in self.designers):
            return None
        
        designer = {
            "id": new_id,
            "name": name,
            "type": "Designer",
            "created_at": datetime.now().isoformat()
        }
        self.designers.append(designer)
        return designer
    
    def add_signoff_app(self, name: str) -> Optional[Dict]:
        """Signoff Application 추가 (중복 방지)"""
        new_id = f"APP_{name}"
        if any(a["id"] == new_id for a in self.signoff_apps):
            return None
        
        app = {
            "id": new_id,
            "name": name,
            "type": "SignoffApp",
            "created_at": datetime.now().isoformat()
        }
        self.signoff_apps.append(app)
        return app
    
    def add_task(self, block_id: str, app_id: str, designer_id: Optional[str] = None) -> Optional[Dict]:
        """Task 추가 (중복 방지)"""
        block = next((b for b in self.blocks if b["id"] == block_id), None)
        app = next((a for a in self.signoff_apps if a["id"] == app_id), None)
        
        if not block or not app:
            return None
        
        new_id = f"TASK_{block_id}_{app_id}"
        if any(t["id"] == new_id for t in self.tasks):
            return None
            
        task = {
            "id": new_id,
            "block_id": block_id,
            "app_id": app_id,
            "designer_id": designer_id,
            "status": "대기중",
            "type": "Task",
            "created_at": datetime.now().isoformat()
        }
        self.tasks.append(task)
        return task
    
    def add_job(self, task_id: str) -> Optional[Dict]:
        """Job 추가 (Task 실행)"""
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            return None
        
        # Get block/app info for workspace path
        block = next((b for b in self.blocks if b["id"] == task["block_id"]), None)
        app = next((a for a in self.signoff_apps if a["id"] == task["app_id"]), None)
        block_name = block["name"] if block else "UNKNOWN"
        app_name = app["name"] if app else "UNKNOWN"
        
        start_time = datetime.now()
        
        job = {
            "id": f"JOB_{task_id}_{len(self.jobs)+1}",
            "task_id": task_id,
            "status": "실행중",
            "type": "Job",
            "start_time": start_time.isoformat(),
            "end_time": None,
            "workspace_dir": f"/user/SIGNOFF/{block_name}/{app_name}_{start_time.strftime('%Y%m%d_%H%M%S')}",
            "created_at": start_time.isoformat()
        }
        self.jobs.append(job)
        task["status"] = "실행중"
        return job
    
    def add_result(self, job_id: str, total_rows: int = 100, violation_count: int = 0, waiver_count: int = 0) -> Optional[Dict]:
        """Result 추가 (Job 완료)"""
        job = next((j for j in self.jobs if j["id"] == job_id), None)
        if not job:
            return None
        
        new_id = f"RES_{job_id}"
        if any(r["id"] == new_id for r in self.results):
            return None
        
        waiver_count = min(waiver_count, total_rows)
        violation_count = min(violation_count, total_rows - waiver_count)
        remaining = total_rows - waiver_count - violation_count
        progress_pct = ((waiver_count + violation_count) / total_rows * 100) if total_rows > 0 else 0
        
        task = next((t for t in self.tasks if t["id"] == job["task_id"]), None)
        block_name = ""
        app_name = ""
        if task:
            block = next((b for b in self.blocks if b["id"] == task["block_id"]), None)
            app = next((a for a in self.signoff_apps if a["id"] == task["app_id"]), None)
            block_name = block["name"] if block else "UNKNOWN"
            app_name = app["name"] if app else "UNKNOWN"
            
        result = {
            "id": new_id,
            "job_id": job_id,
            "total_rows": total_rows,
            "violation_count": violation_count,
            "waiver_count": waiver_count,
            "remaining": remaining,
            "progress_pct": round(progress_pct, 1),
            "file_path": f"/WORKSPACE/{block_name}/{app_name}/result.csv",
            "status": "완료" if remaining == 0 else "진행중",
            "type": "Result",
            "created_at": datetime.now().isoformat()
        }
        self.results.append(result)
        
        job["status"] = "완료"
        job["end_time"] = datetime.now().isoformat()
        
        if task:
            task["status"] = "완료" if remaining == 0 else "진행중"
            
        return result
    
    # ===== Template Data =====
    
    def load_template(self, level: str = "medium"):
        """샘플 데이터 로드"""
        self.clear_all()
        
        if level == "simple":
            self._load_simple()
        elif level == "complex":
            self._load_complex()
        elif level == "full":
            self._load_full_lifecycle()
        else:
            self._load_medium()
    
    def _load_simple(self):
        self.add_product("HBM4E")
        self.add_revision("PROD_HBM4E", "R30")
        self.add_block("PROD_HBM4E_R30", "FULLCHIP_NO_CORE")
        self.add_block("PROD_HBM4E_R30", "PAD")
        self.add_designer("최원우")
        self.add_signoff_app("STA")
        self.add_signoff_app("LVS")
        for block in self.blocks:
            for app in self.signoff_apps:
                self.add_task(block["id"], app["id"], "USER_최원우")
    
    def _load_medium(self):
        self.add_product("HBM4E")
        self.add_revision("PROD_HBM4E", "R30")
        self.add_revision("PROD_HBM4E", "R60")
        for rev in ["R30", "R60"]:
            self.add_block(f"PROD_HBM4E_{rev}", "FULLCHIP_NO_CORE")
            self.add_block(f"PROD_HBM4E_{rev}", "PAD")
        for name in ["최원우", "김광선", "서형중"]:
            self.add_designer(name)
        for app in ["STA", "LVS", "DRC", "Power"]:
            self.add_signoff_app(app)
        designers = [d["id"] for d in self.designers]
        for block in [b for b in self.blocks if "R30" in b["id"]]:
            for app in self.signoff_apps:
                self.add_task(block["id"], app["id"], random.choice(designers))
        for task in self.tasks[:6]:
            job = self.add_job(task["id"])
            if job:
                total = random.randint(100, 500)
                violations = random.randint(5, 50)
                waivers = random.randint(20, total - violations)
                self.add_result(job["id"], total, violations, waivers)
    
    def _load_complex(self):
        for prod in ["HBM4E", "DDR5"]:
            self.add_product(prod)
            for rev in ["R30", "R60"]:
                self.add_revision(f"PROD_{prod}", rev)
        for rev in self.revisions:
            for bn in ["FULLCHIP", "PAD", "IO"]:
                self.add_block(rev["id"], bn)
        for name in ["최원우", "김광선", "서형중", "김진호", "이정훈"]:
            self.add_designer(name)
        for app in ["STA", "LVS", "DRC", "Power", "IR-Drop", "EM"]:
            self.add_signoff_app(app)
        designers = [d["id"] for d in self.designers]
        for block in self.blocks:
            for app in self.signoff_apps:
                self.add_task(block["id"], app["id"], random.choice(designers))
        for task in self.tasks[:len(self.tasks)//2]:
            job = self.add_job(task["id"])
            if job:
                total = random.randint(200, 1000)
                violations = random.randint(10, 100)
                waivers = random.randint(50, total - violations)
                self.add_result(job["id"], total, violations, waivers)
    
    def _load_full_lifecycle(self):
        self.add_product("HBM4E")
        for rev in ["R00", "R10", "R30", "R60"]:
            self.add_revision("PROD_HBM4E", rev)
        for rev in self.revisions:
            for bn in ["FULLCHIP", "CORE", "IO", "PHY", "PAD"]:
                self.add_block(rev["id"], bn)
        for name in ["최원우", "김광선", "서형중", "김진호", "이정훈", "박민수"]:
            self.add_designer(name)
        for app in ["DSC", "LSC", "LS", "PEC", "PN-Ratio", "IR-Drop"]:
            self.add_signoff_app(app)
        designers = [d["id"] for d in self.designers]
        for block in self.blocks:
            for app in self.signoff_apps:
                self.add_task(block["id"], app["id"], random.choice(designers))
        
        for t in [t for t in self.tasks if "R00" in t["id"]]:
            job = self.add_job(t["id"])
            if job:
                total = random.randint(500, 1500)
                self.add_result(job["id"], total, 0, total)
        for t in [t for t in self.tasks if "R10" in t["id"]][:int(len([t for t in self.tasks if "R10" in t["id"]])*0.9)]:
            job = self.add_job(t["id"])
            if job:
                total = random.randint(500, 1500)
                violations = random.randint(0, 20)
                self.add_result(job["id"], total, violations, total - violations)
        for t in [t for t in self.tasks if "R30" in t["id"]][:int(len([t for t in self.tasks if "R30" in t["id"]])*0.6)]:
            job = self.add_job(t["id"])
            if job:
                total = random.randint(500, 1500)
                violations = random.randint(20, 100)
                waivers = random.randint(total//2, total - violations)
                self.add_result(job["id"], total, violations, waivers)
        for t in [t for t in self.tasks if "R60" in t["id"]][:int(len([t for t in self.tasks if "R60" in t["id"]])*0.2)]:
            job = self.add_job(t["id"])
            if job:
                total = random.randint(500, 1500)
                violations = random.randint(50, 200)
                waivers = random.randint(0, total//4)
                self.add_result(job["id"], total, violations, waivers)
    
    # ===== Graph Generation =====
    
    def to_graph_elements(self, layout_type: str = "cose") -> List[Dict]:
        elements = []
        
        def add_node(obj: Dict, layer_idx: int = 0):
            elements.append({
                "data": {
                    "id": obj["id"],
                    "label": obj.get("name", obj["id"].split("_")[-1]),
                    "type": obj["type"],
                    "color": self.COLORS.get(obj["type"], "#868e96"),
                    "layer": layer_idx
                }
            })
        
        def add_edge(source: str, target: str, label: str = ""):
            elements.append({"data": {"source": source, "target": target, "label": label}})
        
        for p in self.products:
            add_node(p, 0)
        for r in self.revisions:
            add_node(r, 1)
            add_edge(r["product_id"], r["id"], "버전")
        for b in self.blocks:
            add_node(b, 2)
            add_edge(b["revision_id"], b["id"], "블록")
        for d in self.designers:
            add_node(d, 3)
        for a in self.signoff_apps:
            add_node(a, 4)
        for t in self.tasks:
            add_node(t, 5)
            add_edge(t["block_id"], t["id"], "검증")
            add_edge(t["id"], t["app_id"], "도구")
            if t.get("designer_id"):
                add_edge(t["id"], t["designer_id"], "담당")
        for j in self.jobs:
            add_node(j, 6)
            add_edge(j["task_id"], j["id"], "실행")
        for r in self.results:
            add_node(r, 7)
            add_edge(r["job_id"], r["id"], "결과")
        return elements
    
    def get_layered_positions(self) -> Dict[str, Dict]:
        positions = {}
        layer_x = {i: 150 * i for i in range(8)}
        layer_counts = {i: 0 for i in range(8)}
        
        def set_pos(obj_id: str, layer: int):
            y = 80 * layer_counts[layer]
            positions[obj_id] = {"x": layer_x[layer], "y": y}
            layer_counts[layer] += 1
        
        for p in self.products:
            set_pos(p["id"], 0)
        for r in self.revisions:
            set_pos(r["id"], 1)
        for b in self.blocks:
            set_pos(b["id"], 2)
        for d in self.designers:
            set_pos(d["id"], 3)
        for a in self.signoff_apps:
            set_pos(a["id"], 4)
        for t in self.tasks:
            set_pos(t["id"], 5)
        for j in self.jobs:
            set_pos(j["id"], 6)
        for r in self.results:
            set_pos(r["id"], 7)
        return positions
    
    # ===== Data Export =====
    
    def get_all_data(self) -> Dict[str, List[Dict]]:
        return {
            "Products": self.products,
            "Revisions": self.revisions,
            "Blocks": self.blocks,
            "Designers": self.designers,
            "SignoffApps": self.signoff_apps,
            "Tasks": self.tasks,
            "Jobs": self.jobs,
            "Results": self.results
        }
    
    def get_statistics(self) -> Dict[str, int]:
        completed = len([t for t in self.tasks if t["status"] == "완료"])
        running = len([t for t in self.tasks if t["status"] == "실행중"])
        pending = len([t for t in self.tasks if t["status"] == "대기중"])
        return {
            "Task": len(self.tasks),
            "Job": len(self.jobs),
            "Result": len(self.results),
            "완료": completed,
            "실행중": running,
            "대기중": pending
        }
    
    # ===== GraphRAG Export =====
    
    def to_json(self) -> str:
        import json
        nodes = []
        for obj_type, obj_list in self.get_all_data().items():
            for obj in obj_list:
                nodes.append({
                    "id": obj["id"],
                    "type": obj.get("type", obj_type.rstrip("s")),
                    "label": obj.get("name", obj["id"]),
                    "properties": {k: v for k, v in obj.items() if k not in ["id", "type"]}
                })
        
        edges = []
        edge_id = 0
        for r in self.revisions:
            edges.append({"id": f"edge_{edge_id}", "source": r["id"], "target": r["product_id"], "type": "belongs_to"})
            edge_id += 1
        for b in self.blocks:
            edges.append({"id": f"edge_{edge_id}", "source": b["id"], "target": b["revision_id"], "type": "belongs_to"})
            edge_id += 1
        for t in self.tasks:
            edges.append({"id": f"edge_{edge_id}", "source": t["id"], "target": t["block_id"], "type": "verifies"})
            edge_id += 1
            edges.append({"id": f"edge_{edge_id}", "source": t["id"], "target": t["app_id"], "type": "uses_tool"})
            edge_id += 1
            if t.get("designer_id"):
                edges.append({"id": f"edge_{edge_id}", "source": t["id"], "target": t["designer_id"], "type": "assigned_to"})
                edge_id += 1
        for j in self.jobs:
            edges.append({"id": f"edge_{edge_id}", "source": j["id"], "target": j["task_id"], "type": "executes"})
            edge_id += 1
        for res in self.results:
            edges.append({"id": f"edge_{edge_id}", "source": res["id"], "target": res["job_id"], "type": "result_of"})
            edge_id += 1
        
        return json.dumps({
            "metadata": {"name": "Signoff Ontology", "created_at": datetime.now().isoformat()},
            "nodes": nodes,
            "edges": edges
        }, ensure_ascii=False, indent=2)
    
    def to_parquet_bytes(self) -> Dict[str, bytes]:
        import pandas as pd
        import io
        result = {}
        
        all_nodes = []
        for obj_type, obj_list in self.get_all_data().items():
            for obj in obj_list:
                all_nodes.append({
                    "id": obj["id"],
                    "type": obj.get("type", obj_type.rstrip("s")),
                    "name": obj.get("name", obj["id"]),
                    "status": obj.get("status", "")
                })
        
        if all_nodes:
            df_nodes = pd.DataFrame(all_nodes)
            buf = io.BytesIO()
            df_nodes.to_parquet(buf, index=False)
            result["nodes.parquet"] = buf.getvalue()
        
        edges = []
        for r in self.revisions:
            edges.append({"source": r["id"], "target": r["product_id"], "type": "belongs_to"})
        for b in self.blocks:
            edges.append({"source": b["id"], "target": b["revision_id"], "type": "belongs_to"})
        for t in self.tasks:
            edges.append({"source": t["id"], "target": t["block_id"], "type": "verifies"})
            edges.append({"source": t["id"], "target": t["app_id"], "type": "uses_tool"})
            if t.get("designer_id"):
                edges.append({"source": t["id"], "target": t["designer_id"], "type": "assigned_to"})
        for j in self.jobs:
            edges.append({"source": j["id"], "target": j["task_id"], "type": "executes"})
        for res in self.results:
            edges.append({"source": res["id"], "target": res["job_id"], "type": "result_of"})
        
        if edges:
            df_edges = pd.DataFrame(edges)
            buf = io.BytesIO()
            df_edges.to_parquet(buf, index=False)
            result["edges.parquet"] = buf.getvalue()
        
        return result
    
    # ===== Search =====
    
    def search(self, query: str, obj_type: Optional[str] = None) -> List[Dict]:
        results = []
        query_lower = query.lower()
        all_objects = self.products + self.revisions + self.blocks + self.designers + self.signoff_apps + self.tasks + self.jobs + self.results
        for obj in all_objects:
            if obj_type and obj.get("type") != obj_type:
                continue
            if query_lower in obj.get("id", "").lower() or query_lower in obj.get("name", "").lower():
                results.append(obj)
        return results
    
    def get_related_objects(self, obj_id: str) -> Dict[str, List[Dict]]:
        related = {"upstream": [], "downstream": []}
        obj = None
        for lst in [self.products, self.revisions, self.blocks, self.designers, self.signoff_apps, self.tasks, self.jobs, self.results]:
            obj = next((o for o in lst if o["id"] == obj_id), None)
            if obj:
                break
        if not obj:
            return related
        
        obj_type = obj.get("type")
        if obj_type == "Revision":
            related["upstream"] = [p for p in self.products if p["id"] == obj.get("product_id")]
        elif obj_type == "Block":
            related["upstream"] = [r for r in self.revisions if r["id"] == obj.get("revision_id")]
        elif obj_type == "Task":
            related["upstream"] = [b for b in self.blocks if b["id"] == obj.get("block_id")]
        elif obj_type == "Job":
            related["upstream"] = [t for t in self.tasks if t["id"] == obj.get("task_id")]
        elif obj_type == "Result":
            related["upstream"] = [j for j in self.jobs if j["id"] == obj.get("job_id")]
        
        if obj_type == "Product":
            related["downstream"] = [r for r in self.revisions if r.get("product_id") == obj_id]
        elif obj_type == "Revision":
            related["downstream"] = [b for b in self.blocks if b.get("revision_id") == obj_id]
        elif obj_type == "Block":
            related["downstream"] = [t for t in self.tasks if t.get("block_id") == obj_id]
        elif obj_type == "Task":
            related["downstream"] = [j for j in self.jobs if j.get("task_id") == obj_id]
        elif obj_type == "Job":
            related["downstream"] = [r for r in self.results if r.get("job_id") == obj_id]
        return related
    
    # ===== Dropdown Options =====
    
    def get_product_options(self) -> List[Dict]:
        return [{"value": p["id"], "label": p["name"]} for p in self.products]
    
    def get_revision_options(self) -> List[Dict]:
        return [{"value": r["id"], "label": f"{r['product_id'].replace('PROD_', '')} / {r['name']}"} for r in self.revisions]
    
    def get_block_options(self) -> List[Dict]:
        options = []
        for b in self.blocks:
            rev = next((r for r in self.revisions if r["id"] == b["revision_id"]), None)
            if rev:
                label = f"{rev['product_id'].replace('PROD_', '')}/{rev['name']}/{b['name']}"
            else:
                label = b["name"]
            options.append({"value": b["id"], "label": label})
        return options
    
    def get_app_options(self) -> List[Dict]:
        return [{"value": a["id"], "label": a["name"]} for a in self.signoff_apps]
    
    def get_designer_options(self) -> List[Dict]:
        return [{"value": d["id"], "label": d["name"]} for d in self.designers]
    
    def get_task_options(self) -> List[Dict]:
        return [{"value": t["id"], "label": t["id"]} for t in self.tasks]
    
    def get_job_options(self) -> List[Dict]:
        return [{"value": j["id"], "label": j["id"]} for j in self.jobs if j["status"] != "완료"]
    
    def get_type_options(self) -> List[Dict]:
        return [{"value": t, "label": t} for t in self.OBJECT_ORDER]


# Global instance
store = OntologyStore()
