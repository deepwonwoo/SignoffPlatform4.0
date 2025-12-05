import random
from datetime import datetime, timedelta
from typing import Dict, List
import uuid

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
            "input_configs": [],
            "jobs": [],
            "workspaces": [],
            "results": []
        }
        self.graph = {"nodes": [], "edges": []}
        
        # ID Mappings for Graph Edges
        self.id_map = {} # obj_id -> obj_type
    
    def generate(self) -> Dict:
        """전체 Ontology 생성"""
        self._generate_designers()
        self._generate_applications()
        self._generate_product()
        self._generate_revisions()
        self._generate_blocks()
        self._generate_tasks_chain() # Task -> Config -> Job -> Workspace -> Result
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
        prod = {
            "product_id": self.config["product_id"],
            "product_name": f"{self.config['product_id']} Memory",
            "product_type": self.config["product_type"],
            "status": "ACTIVE",
            "created_at": datetime.now().isoformat()
        }
        self.ontology["products"].append(prod)
        self.id_map[prod["product_id"]] = "Product"
    
    def _generate_revisions(self):
        """Revision 생성 (Semantic Layer)"""
        phases = {
            "R00": "Schematic", "R10": "Pre-Layout", "R20": "Post-Layout",
            "R30": "MPW", "R40": "Verification", "R50": "Final", "R60": "Tapeout"
        }
        
        prev_id = None
        for rev_code in self.config["active_revisions"]:
            rev_id = f"{self.config['product_id']}_{rev_code}"
            
            # 이 Revision에서 수행할 Application 목록
            required_apps = [
                app for app, revs in self.config["signoff_matrix"].items()
                if rev_code in revs
            ]
            
            rev = {
                "revision_id": rev_id,
                "product_id": self.config["product_id"],
                "revision_code": rev_code,
                "phase": phases.get(rev_code, "Unknown"),
                "required_applications": required_apps,
                "previous_revision_id": prev_id,
                "created_at": datetime.now().isoformat()
            }
            self.ontology["revisions"].append(rev)
            self.id_map[rev_id] = "Revision"
            prev_id = rev_id
    
    def _generate_blocks(self):
        """Block 생성 (Semantic Layer) - 각 Revision별로"""
        for revision in self.ontology["revisions"]:
            for i, block_config in enumerate(self.config["blocks"]):
                designer = self.ontology["designers"][i % len(self.ontology["designers"])]
                
                blk_id = f"{revision['revision_id']}_{block_config['block_name']}"
                blk = {
                    "block_id": blk_id,
                    "revision_id": revision["revision_id"],
                    "block_name": block_config["block_name"],
                    "block_type": block_config.get("block_type", "ANALOG"),
                    "designer_id": designer["designer_id"],
                    "instance_count": block_config.get("instance_count", 1000000),
                    "created_at": datetime.now().isoformat()
                }
                self.ontology["blocks"].append(blk)
                self.id_map[blk_id] = "Block"
    
    def _generate_tasks_chain(self):
        """Task -> Config -> Job -> Workspace -> Result 체인 생성"""
        task_seq = 1
        
        status_dist = self.config.get("status_distribution", {
            "DONE": 0.70, "RUNNING": 0.15, "PENDING": 0.10, "FAILED": 0.05
        })
        
        for block in self.ontology["blocks"]:
            revision = next(r for r in self.ontology["revisions"] 
                          if r["revision_id"] == block["revision_id"])
            
            for app_id in revision["required_applications"]:
                pvt_conditions = self.config.get("pvt_conditions", {}).get(app_id, ["DEFAULT"])
                
                for pvt in pvt_conditions:
                    # 1. Create Task
                    status = random.choices(
                        list(status_dist.keys()),
                        weights=list(status_dist.values())
                    )[0]
                    
                    task_id = f"TASK_{block['block_name']}_{app_id}_{revision['revision_code']}_{task_seq:03d}"
                    task = {
                        "task_id": task_id,
                        "revision_id": block["revision_id"],
                        "block_id": block["block_id"],
                        "app_id": app_id,
                        "pvt_corner": pvt,
                        "status": status,
                        "owner_id": block["designer_id"],
                        "created_at": self._random_date()
                    }
                    self.ontology["tasks"].append(task)
                    self.id_map[task_id] = "SignoffTask"
                    task_seq += 1

                    # 2. Create InputConfig (Always exists for a task)
                    config_id = f"CFG_{task_id}"
                    config = {
                        "config_id": config_id,
                        "task_id": task_id,
                        "netlist_path": f"/data/{revision['revision_code']}/{block['block_name']}.spi",
                        "power_definition": {"VDD": "1.2V", "VSS": "0.0V"},
                        "validation_status": "VALID",
                        "created_at": task["created_at"]
                    }
                    self.ontology["input_configs"].append(config)
                    self.id_map[config_id] = "InputConfig"

                    # 3. Create Job (If not PENDING)
                    if status != "PENDING":
                        job_id = f"JOB_{task_id}"
                        job_status = status # Task status mirrors Job status for simplicity
                        
                        job = {
                            "job_id": job_id,
                            "task_id": task_id,
                            "status": job_status,
                            "start_time": task["created_at"],
                            "end_time": datetime.now().isoformat() if status in ["DONE", "FAILED"] else None,
                            "workspace_path": f"/user/{block['designer_id']}/signoff/{job_id}",
                            "error_msg": "Memory Overflow" if status == "FAILED" else None,
                            "created_at": task["created_at"]
                        }
                        self.ontology["jobs"].append(job)
                        self.id_map[job_id] = "SignoffJob"
                        
                        # 4. Create Workspace
                        ws_id = f"WS_{job_id}"
                        ws = {
                            "workspace_id": ws_id,
                            "workspace_type": "LOCAL",
                            "base_path": job["workspace_path"],
                            "product_id": self.config["product_id"],
                            "owner_id": block["designer_id"],
                            "created_at": job["created_at"]
                        }
                        self.ontology["workspaces"].append(ws)
                        self.id_map[ws_id] = "Workspace"

                        # 5. Create Result (Only if DONE)
                        if status == "DONE":
                            res_id = f"RES_{job_id}"
                            row_count = random.randint(100, 5000)
                            waiver_pct = random.uniform(0.8, 0.99)
                            waiver_count = int(row_count * waiver_pct)
                            fixed_count = int((row_count - waiver_count) * 0.5)
                            result_count = row_count - waiver_count - fixed_count
                            
                            res = {
                                "result_id": res_id,
                                "task_id": task_id,
                                "job_id": job_id, # Link to Job
                                "workspace_id": ws_id, # Link to Workspace
                                "row_count": row_count,
                                "waiver_count": waiver_count,
                                "fixed_count": fixed_count,
                                "result_count": result_count,
                                "waiver_progress_pct": round((waiver_count + fixed_count) / row_count * 100, 1),
                                "comparison_summary": {
                                    "same_count": int(row_count * 0.9),
                                    "diff_count": int(row_count * 0.05),
                                    "new_count": int(row_count * 0.05),
                                    "removed_count": 0
                                },
                                "created_at": job["end_time"]
                            }
                            self.ontology["results"].append(res)
                            self.id_map[res_id] = "Result"

    
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
            self._add_node(task["task_id"], "SignoffTask", "Task")
            
        for config in self.ontology["input_configs"]:
            self._add_node(config["config_id"], "InputConfig", "Config")
            
        for job in self.ontology["jobs"]:
            self._add_node(job["job_id"], "SignoffJob", "Job")
            
        for ws in self.ontology["workspaces"]:
            self._add_node(ws["workspace_id"], "Workspace", "WS")
            
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
            
        for config in self.ontology["input_configs"]:
            self._add_edge(config["task_id"], config["config_id"], "uses_config")
            
        for job in self.ontology["jobs"]:
            self._add_edge(job["task_id"], job["job_id"], "has_job")
            
        for ws in self.ontology["workspaces"]:
            pass 
            
        for job in self.ontology["jobs"]:
             # Job -> Workspace
             ws = next((w for w in self.ontology["workspaces"] if w["base_path"] == job["workspace_path"]), None)
             if ws:
                 self._add_edge(job["job_id"], ws["workspace_id"], "executes_in")

        for result in self.ontology["results"]:
            self._add_edge(result["job_id"], result["result_id"], "produces")
            self._add_edge(result["result_id"], result["workspace_id"], "stored_in")
    
    def _add_node(self, node_id: str, obj_type: str, label: str):
        """Graph Node 추가"""
        from data.object_schemas import OBJECT_SCHEMAS
        schema = OBJECT_SCHEMAS.get(obj_type, {})
        
        self.graph["nodes"].append({
            "data": {
                "id": node_id,
                "label": label,
                "type": obj_type,
                "layer": schema.get("layer", "Unknown"),
                "color": schema.get("color", "#888888")
            }
        })
    
    def _add_edge(self, source: str, target: str, relationship: str):
        """Graph Edge 추가"""
        self.graph["edges"].append({
            "data": {
                "source": source,
                "target": target,
                "label": relationship
            }
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
            self.id_map[d["designer_id"]] = "Designer"
    
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
                    self.id_map[app_name] = "SignoffApplication"
    
    def _random_date(self) -> str:
        """랜덤 날짜 생성"""
        days_ago = random.randint(1, 30)
        dt = datetime.now() - timedelta(days=days_ago)
        return dt.isoformat()
