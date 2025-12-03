import random
from datetime import datetime, timedelta
from typing import Dict, List

class OntologyGenerator:
    """Signoff Ontology Mock 데이터 생성기"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.ontology = {
            "products": [],
            "revisions": [],
            "blocks": [],
            "designers": [],
            "applications": [],
            "tasks": [],
            "results": []
        }
        self.graph = {"nodes": [], "edges": []}
    
    def generate(self) -> Dict:
        """전체 Ontology 생성"""
        self._generate_designers()
        self._generate_applications()
        self._generate_product()
        self._generate_revisions()
        self._generate_blocks()
        self._generate_tasks()
        self._generate_results()
        self._generate_graph()
        
        return {
            "meta": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "description": f"{self.config['product_id']} Signoff Ontology POC"
            },
            "config": self.config,
            "ontology": self.ontology,
            "graph": self.graph
        }
    
    def _generate_product(self):
        """Product 생성 (Semantic Layer)"""
        self.ontology["products"].append({
            "product_id": self.config["product_id"],
            "product_name": f"{self.config['product_id']} Memory",
            "product_type": self.config["product_type"],
            "status": "ACTIVE",
            "created_at": datetime.now().isoformat()
        })
    
    def _generate_revisions(self):
        """Revision 생성 (Semantic Layer)"""
        phases = {
            "R00": "Schematic", "R10": "Pre-Layout", "R20": "Post-Layout",
            "R30": "MPW", "R40": "Verification", "R50": "Final", "R60": "Tapeout"
        }
        
        prev_id = None
        for rev_code in self.config["active_revisions"]:
            rev_id = f"{self.config['product_id']}-{rev_code}"
            
            # 이 Revision에서 수행할 Application 목록
            required_apps = [
                app for app, revs in self.config["signoff_matrix"].items()
                if rev_code in revs
            ]
            
            self.ontology["revisions"].append({
                "revision_id": rev_id,
                "product_id": self.config["product_id"],
                "revision_code": rev_code,
                "phase": phases.get(rev_code, "Unknown"),
                "required_applications": required_apps,
                "previous_revision_id": prev_id,
                "created_at": datetime.now().isoformat()
            })
            prev_id = rev_id
    
    def _generate_blocks(self):
        """Block 생성 (Semantic Layer) - 각 Revision별로"""
        for revision in self.ontology["revisions"]:
            for i, block_config in enumerate(self.config["blocks"]):
                designer = self.ontology["designers"][i % len(self.ontology["designers"])]
                
                self.ontology["blocks"].append({
                    "block_id": f"{revision['revision_id']}-{block_config['block_name']}",
                    "revision_id": revision["revision_id"],
                    "block_name": block_config["block_name"],
                    "block_type": block_config.get("block_type", "ANALOG"),
                    "designer_id": designer["designer_id"],
                    "instance_count": block_config.get("instance_count", 1000000),
                    "created_at": datetime.now().isoformat()
                })
    
    def _generate_tasks(self):
        """SignoffTask 생성 (Kinetic Layer)"""
        task_id = 1
        status_dist = self.config.get("status_distribution", {
            "DONE": 0.70, "RUNNING": 0.15, "PENDING": 0.10, "FAILED": 0.05
        })
        
        for block in self.ontology["blocks"]:
            revision = next(r for r in self.ontology["revisions"] 
                          if r["revision_id"] == block["revision_id"])
            
            for app_id in revision["required_applications"]:
                pvt_conditions = self.config.get("pvt_conditions", {}).get(app_id, ["DEFAULT"])
                
                for pvt in pvt_conditions:
                    status = random.choices(
                        list(status_dist.keys()),
                        weights=list(status_dist.values())
                    )[0]
                    
                    self.ontology["tasks"].append({
                        "task_id": f"TASK-{task_id:04d}",
                        "revision_id": block["revision_id"],
                        "block_id": block["block_id"],
                        "app_id": app_id,
                        "pvt_corner": pvt,
                        "status": status,
                        "owner_id": block["designer_id"],
                        "created_at": self._random_date()
                    })
                    task_id += 1
    
    def _generate_results(self):
        """Result 생성 (Dynamic Layer) - 완료된 Task만"""
        result_id = 1
        
        for task in self.ontology["tasks"]:
            if task["status"] != "DONE":
                continue
            
            row_count = random.randint(500, 3000)
            waiver_pct = random.uniform(0.75, 0.98)
            fixed_pct = random.uniform(0.01, 0.10)
            
            waiver_count = int(row_count * waiver_pct)
            fixed_count = int(row_count * fixed_pct)
            result_count = row_count - waiver_count - fixed_count
            
            self.ontology["results"].append({
                "result_id": f"RESULT-{result_id:04d}",
                "task_id": task["task_id"],
                "row_count": row_count,
                "waiver_count": waiver_count,
                "fixed_count": fixed_count,
                "result_count": result_count,
                "waiver_progress_pct": round((waiver_count + fixed_count) / row_count * 100, 1),
                "comparison_summary": {
                    "same_count": int(row_count * random.uniform(0.6, 0.8)),
                    "diff_count": int(row_count * random.uniform(0.05, 0.15)),
                    "new_count": int(row_count * random.uniform(0.1, 0.2)),
                    "removed_count": int(row_count * random.uniform(0.02, 0.08))
                },
                "created_at": task["created_at"]
            })
            result_id += 1
    
    def _generate_graph(self):
        """Cytoscape용 Graph 데이터 생성"""
        from data.object_schemas import OBJECT_SCHEMAS
        
        # Nodes 생성
        for product in self.ontology["products"]:
            self._add_node(product["product_id"], "Product", product["product_id"])
        
        for revision in self.ontology["revisions"]:
            self._add_node(revision["revision_id"], "Revision", revision["revision_code"])
        
        for block in self.ontology["blocks"]:
            self._add_node(block["block_id"], "Block", block["block_name"])
        
        for designer in self.ontology["designers"]:
            self._add_node(designer["designer_id"], "Designer", designer["name"])
        
        for app in self.ontology["applications"]:
            self._add_node(app["app_id"], "SignoffApplication", app["app_id"])
        
        for task in self.ontology["tasks"]:
            self._add_node(task["task_id"], "SignoffTask", task["app_id"])
        
        for result in self.ontology["results"]:
            self._add_node(result["result_id"], "Result", "Result")
        
        # Edges 생성
        for revision in self.ontology["revisions"]:
            self._add_edge(revision["product_id"], revision["revision_id"], "has_revision")
        
        for block in self.ontology["blocks"]:
            self._add_edge(block["revision_id"], block["block_id"], "has_block")
            self._add_edge(block["block_id"], block["designer_id"], "responsible_designer")
        
        for task in self.ontology["tasks"]:
            self._add_edge(task["block_id"], task["task_id"], "requires_signoff_task")
            self._add_edge(task["task_id"], task["app_id"], "uses_application")
            self._add_edge(task["task_id"], task["owner_id"], "owned_by")
        
        for result in self.ontology["results"]:
            self._add_edge(task["task_id"], result["result_id"], "produces")
    
    def _add_node(self, node_id: str, obj_type: str, label: str):
        """Graph Node 추가"""
        from data.object_schemas import OBJECT_SCHEMAS
        schema = OBJECT_SCHEMAS.get(obj_type, {})
        
        self.graph["nodes"].append({
            "id": node_id,
            "type": obj_type,
            "layer": schema.get("layer", "Unknown"),
            "label": label,
            "color": schema.get("color", "#888888")
        })
    
    def _add_edge(self, source: str, target: str, relationship: str):
        """Graph Edge 추가"""
        self.graph["edges"].append({
            "source": source,
            "target": target,
            "relationship": relationship
        })
    
    def _generate_designers(self):
        """Designer 생성"""
        self.ontology["designers"] = self.config.get("designers", [
            {"designer_id": "kim", "name": "김철수", "team": "HBM팀", "role": "ENGINEER"},
            {"designer_id": "lee", "name": "이영희", "team": "HBM팀", "role": "LEAD"},
            {"designer_id": "park", "name": "박민수", "team": "HBM팀", "role": "ENGINEER"}
        ])
        for d in self.ontology["designers"]:
            d["created_at"] = datetime.now().isoformat()
    
    def _generate_applications(self):
        """SignoffApplication 생성"""
        from data.templates import DEFAULT_SIGNOFF_MATRIX
        
        for group, apps in DEFAULT_SIGNOFF_MATRIX.items():
            for app_name, app_config in apps.items():
                if app_name in self.config.get("signoff_matrix", {}):
                    self.ontology["applications"].append({
                        "app_id": app_name,
                        "app_name": app_name,
                        "app_group": group,
                        "engine_type": app_config.get("engine", "SPACE"),
                        "default_pvt_conditions": app_config.get("condition", []),
                        "created_at": datetime.now().isoformat()
                    })
    
    def _random_date(self) -> str:
        """랜덤 날짜 생성"""
        days_ago = random.randint(1, 30)
        dt = datetime.now() - timedelta(days=days_ago)
        return dt.isoformat()
