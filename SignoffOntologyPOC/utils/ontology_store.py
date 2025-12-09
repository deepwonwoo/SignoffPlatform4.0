"""
Signoff Ontology Store - 온톨로지 상태 관리 모듈
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

class OntologyStore:
    """Signoff Ontology 객체들을 저장하고 관리하는 클래스"""
    
    # 객체 유형별 색상 (Layer 대신 색상으로 구분)
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
            return None  # 중복
        
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
            return None  # 중복
            
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
            return None  # 중복
            
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
            return None  # 중복
        
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
            return None  # 중복
        
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
            return None  # 중복
            
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
            
        job = {
            "id": f"JOB_{task_id}_{len(self.jobs)+1}",
            "task_id": task_id,
            "status": "실행중",
            "type": "Job",
            "created_at": datetime.now().isoformat()
        }
        self.jobs.append(job)
        task["status"] = "실행중"
        return job
    
    def add_result(self, job_id: str, violation_count: int = 0, waiver_count: int = 0) -> Optional[Dict]:
        """Result 추가 (Job 완료)"""
        job = next((j for j in self.jobs if j["id"] == job_id), None)
        if not job:
            return None
            
        result = {
            "id": f"RES_{job_id}",
            "job_id": job_id,
            "violation_count": violation_count,
            "waiver_count": waiver_count,
            "status": "완료",
            "type": "Result",
            "created_at": datetime.now().isoformat()
        }
        self.results.append(result)
        job["status"] = "완료"
        
        # Task도 완료 처리
        task = next((t for t in self.tasks if t["id"] == job["task_id"]), None)
        if task:
            task["status"] = "완료"
            
        return result
    
    # ===== Template Data =====
    
    def load_template(self):
        """샘플 HBM4E Signoff 시나리오 로드"""
        self.clear_all()
        
        # Products
        self.add_product("HBM4E")
        
        # Revisions
        self.add_revision("PROD_HBM4E", "R30")
        self.add_revision("PROD_HBM4E", "R60")
        
        # Blocks
        for rev in ["R30", "R60"]:
            self.add_block(f"PROD_HBM4E_{rev}", "PHY")
            self.add_block(f"PROD_HBM4E_{rev}", "Core")
            self.add_block(f"PROD_HBM4E_{rev}", "IO")
        
        # Designers
        self.add_designer("김철수")
        self.add_designer("이영희")
        self.add_designer("박준호")
        
        # Signoff Apps
        self.add_signoff_app("STA")
        self.add_signoff_app("LVS")
        self.add_signoff_app("DRC")
        self.add_signoff_app("Power")
        
        # Tasks (Block + App 조합)
        designers = ["USER_김철수", "USER_이영희", "USER_박준호"]
        import random
        
        for block in self.blocks[:3]:  # R30 blocks만
            for app in self.signoff_apps:
                designer = random.choice(designers)
                self.add_task(block["id"], app["id"], designer)
        
        # Jobs & Results (일부만)
        for task in self.tasks[:6]:
            job = self.add_job(task["id"])
            if job:
                self.add_result(job["id"], 
                    violation_count=random.randint(10, 100),
                    waiver_count=random.randint(0, 50))
    
    # ===== Graph Generation =====
    
    def to_graph_elements(self) -> List[Dict]:
        """Cytoscape 그래프 요소 생성"""
        elements = []
        
        def add_node(obj: Dict):
            elements.append({
                "data": {
                    "id": obj["id"],
                    "label": obj["name"] if "name" in obj else obj["id"].split("_")[-1],
                    "type": obj["type"],
                    "color": self.COLORS.get(obj["type"], "#868e96")
                }
            })
        
        def add_edge(source: str, target: str, label: str = ""):
            elements.append({
                "data": {
                    "source": source,
                    "target": target,
                    "label": label
                }
            })
        
        # Nodes
        for p in self.products:
            add_node(p)
        for r in self.revisions:
            add_node(r)
            add_edge(r["product_id"], r["id"], "버전")
        for b in self.blocks:
            add_node(b)
            add_edge(b["revision_id"], b["id"], "블록")
        for d in self.designers:
            add_node(d)
        for a in self.signoff_apps:
            add_node(a)
        for t in self.tasks:
            add_node(t)
            add_edge(t["block_id"], t["id"], "검증")
            add_edge(t["id"], t["app_id"], "도구")
            if t.get("designer_id"):
                add_edge(t["id"], t["designer_id"], "담당")
        for j in self.jobs:
            add_node(j)
            add_edge(j["task_id"], j["id"], "실행")
        for r in self.results:
            add_node(r)
            add_edge(r["job_id"], r["id"], "결과")
            
        return elements
    
    # ===== Data Export =====
    
    def get_all_data(self) -> Dict[str, List[Dict]]:
        """모든 데이터를 딕셔너리로 반환"""
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
        """통계 정보 반환"""
        return {
            "제품 수": len(self.products),
            "리비전 수": len(self.revisions),
            "블록 수": len(self.blocks),
            "담당자 수": len(self.designers),
            "검증 도구 수": len(self.signoff_apps),
            "Task 수": len(self.tasks),
            "Job 수": len(self.jobs),
            "Result 수": len(self.results)
        }
    
    # ===== Dropdown Options =====
    
    def get_product_options(self) -> List[Dict]:
        return [{"value": p["id"], "label": p["name"]} for p in self.products]
    
    def get_revision_options(self) -> List[Dict]:
        return [{"value": r["id"], "label": f"{r['product_id'].replace('PROD_', '')} / {r['name']}"} for r in self.revisions]
    
    def get_block_options(self) -> List[Dict]:
        return [{"value": b["id"], "label": b["name"]} for b in self.blocks]
    
    def get_app_options(self) -> List[Dict]:
        return [{"value": a["id"], "label": a["name"]} for a in self.signoff_apps]
    
    def get_designer_options(self) -> List[Dict]:
        return [{"value": d["id"], "label": d["name"]} for d in self.designers]
    
    def get_task_options(self) -> List[Dict]:
        return [{"value": t["id"], "label": t["id"]} for t in self.tasks]
    
    def get_job_options(self) -> List[Dict]:
        return [{"value": j["id"], "label": j["id"]} for j in self.jobs if j["status"] != "완료"]


# Global instance
store = OntologyStore()
