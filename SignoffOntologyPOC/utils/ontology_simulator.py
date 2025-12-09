from datetime import datetime, timedelta
import random
from typing import Dict, List, Any
from copy import deepcopy

class SignoffSimulator:
    """Signoff Lifecycle Simulator for Educational POC"""
    
    STEPS = [
        "Initialization", # Product created
        "Planning",       # Revisions, Blocks, Designers defined
        "Setup",          # Applications & Requirements mapped
        "Task Definition",# Tasks & InputConfigs created (PENDING)
        "Execution",      # Jobs & Local Workspaces created (RUNNING)
        "Completion",     # Results & Central Workspaces created (DONE)
        "Analysis"        # Analysis & Comparisons (Waiver/Feedback)
    ]
    
    def __init__(self, config: Dict):
        self.config = config
        self.step_index = -1
        self.ontology = {
            "products": [], "revisions": [], "blocks": [], "designers": [],
            "applications": [], "tasks": [], "input_configs": [], 
            "jobs": [], "workspaces": [], "results": [], "comparisons": []
        }
        self.logs = [] 
        self.last_added_ids = [] # IDs added in the most recent step (for highlighting)
        
        # Load base data
        self.base_designers = self.config.get("designers", [])
        
    @property
    def current_step(self):
        if 0 <= self.step_index < len(self.STEPS):
            return self.STEPS[self.step_index]
        return "Not Started"

    def next_step(self) -> Dict:
        """Executes the next step and returns rich educational data."""
        self.last_added_ids = [] # Reset for this step
        
        if self.step_index >= len(self.STEPS) - 1:
            return {
                "step": "Finished",
                "narrative": "All steps completed.",
                "insight": "Simulation Finished.",
                "highlight_ids": [],
                "metrics": self._calculate_metrics(),
                "ontology": self.ontology,
                "graph": self._generate_graph_data()
            }
            
        self.step_index += 1
        step_name = self.STEPS[self.step_index]
        
        result_data = {}
        if step_name == "Initialization":
            result_data = self._step_init()
        elif step_name == "Planning":
            result_data = self._step_planning()
        elif step_name == "Setup":
            result_data = self._step_setup()
        elif step_name == "Task Definition":
            result_data = self._step_task_def()
        elif step_name == "Execution":
            result_data = self._step_execution()
        elif step_name == "Completion":
            result_data = self._step_completion()
        elif step_name == "Analysis":
            result_data = self._step_analysis()
            
        self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {step_name}: {result_data.get('narrative', '')}")
        
        return {
            "step": step_name,
            "narrative": result_data.get("narrative", ""),
            "insight": result_data.get("insight", ""),
            "highlight_ids": self.last_added_ids,
            "metrics": self._calculate_metrics(),
            "ontology": self.ontology,
            "graph": self._generate_graph_data()
        }
        
    def reset(self):
        self.step_index = -1
        self.ontology = {k: [] for k in self.ontology}
        self.logs = []
        self.last_added_ids = []
        return self.next_step()

    def load_scenario(self, scenario_type: str) -> Dict:
        self.reset() # This executes init
        self.step_index = -1 # Hack to restart from 0 for loop
        self.ontology = {k: [] for k in self.ontology}
        
        target_step = 0
        if scenario_type == "early": target_step = 2 # Setup
        elif scenario_type == "full": target_step = 6 # Analysis
        
        final_res = {}
        for _ in range(target_step + 1):
            final_res = self.next_step()
            
        return final_res

    # --- Step Implementations (Returns: narrative, insight) ---

    def _step_init(self):
        prod = {
            "product_id": self.config["product_id"],
            "product_name": f"{self.config['product_id']} Memory",
            "product_type": self.config["product_type"],
            "status": "ACTIVE",
            "created_at": datetime.now().isoformat()
        }
        self.ontology["products"].append(prod)
        self.last_added_ids.append(prod["product_id"])
        
        return {
            "narrative": f"**Project Kickoff**: Created Product master data for `{prod['product_id']}`.",
            "insight": "**Semantic Layer**: The foundation of the ontology. By defining the `Product` as a permanent object, we establish a single source of truth that links all future revisions and results."
        }

    def _step_planning(self):
        # Designers
        if not self.base_designers:
             self.base_designers = [
                {"designer_id": "kim", "name": "Minsoo Kim", "team": "Design", "role": "ENGINEER"},
                {"designer_id": "lee", "name": "Young Lee", "team": "Design", "role": "LEAD"},
            ]
        self.ontology["designers"] = self.base_designers
        for d in self.base_designers: self.last_added_ids.append(d["designer_id"])
        
        # Revisions
        phases = {"R00": "Schematic", "R30": "MPW", "R60": "Tapeout"}
        prev_rev = None
        for rev_code in self.config["active_revisions"]:
            rev_id = f"{self.config['product_id']}_{rev_code}"
            rev = {
                "revision_id": rev_id,
                "product_id": self.config["product_id"],
                "revision_code": rev_code,
                "phase": phases.get(rev_code, "Implementation"),
                "previous_revision_id": prev_rev,
                "created_at": datetime.now().isoformat()
            }
            self.ontology["revisions"].append(rev)
            self.last_added_ids.append(rev_id)
            prev_rev = rev_id
            
        # Blocks
        count = 0
        for r in self.ontology["revisions"]:
            for b_conf in self.config["blocks"]:
                blk_id = f"{r['revision_id']}_{b_conf['block_name']}"
                blk = {
                    "block_id": blk_id,
                    "revision_id": r["revision_id"],
                    "block_name": b_conf["block_name"],
                    "block_type": b_conf.get("block_type", "DIGITAL"),
                    "designer_id": random.choice(self.ontology["designers"])["designer_id"],
                    "created_at": datetime.now().isoformat()
                }
                self.ontology["blocks"].append(blk)
                self.last_added_ids.append(blk_id)
                count += 1
                
        return {
            "narrative": f"**Planning**: Defined {len(self.ontology['revisions'])} Revisions and {count} Blocks. Assigned designers to each block.",
            "insight": "**Hierarchy & Ownership**: The ontology explicitly maps `Product` -> `Revision` -> `Block` -> `Designer`. This answers questions like *'Who is responsible for the IO block in R30?'* instantly."
        }

    def _step_setup(self):
        from data.templates import DEFAULT_SIGNOFF_MATRIX
        
        apps_added = []
        for group, apps in DEFAULT_SIGNOFF_MATRIX.items():
            for app_name, app_conf in apps.items():
                needed = False
                for rev in self.ontology["revisions"]:
                    if rev["revision_code"] in app_conf["revisions"]:
                        needed = True
                
                if needed:
                    self.ontology["applications"].append({
                        "app_id": app_name,
                        "app_name": app_name,
                        "group": group,
                        "created_at": datetime.now().isoformat()
                    })
                    apps_added.append(app_name)
                    self.last_added_ids.append(app_name)
                    
        return {
            "narrative": f"**Signoff Setup**: Configured {len(apps_added)} Applications required for certification.",
            "insight": "**Rule Definition**: We are encoding the 'Definition of Done'. By linking `Applications` to `Revisions`, the system knows exactly what needs to be verified before tapeout."
        }

    def _step_task_def(self):
        task_count = 0
        for block in self.ontology["blocks"]:
            # Find revision code safely
            rev = next((r for r in self.ontology["revisions"] if r["revision_id"] == block["revision_id"]), None)
            if not rev: continue
            
            rev_code = rev["revision_code"]
            matrix = self.config.get("signoff_matrix", {})
            
            for app in self.ontology["applications"]:
                # Check if app applies to this revision
                 if rev_code in ["R30", "R60"]: # Hardcoded filter for demo simplicity
                    task_id = f"TASK_{block['block_id']}_{app['app_id']}"
                    
                    task = {
                        "task_id": task_id,
                        "block_id": block["block_id"],
                        "app_id": app["app_id"],
                        "revision_id": block["revision_id"],
                        "owner_id": block["designer_id"],
                        "status": "PENDING",
                        "pvt_corner": "SS_0.72V_125C",
                        "created_at": datetime.now().isoformat()
                    }
                    self.ontology["tasks"].append(task)
                    self.last_added_ids.append(task_id)
                    
                    cfg_id = f"CFG_{task_id}"
                    self.ontology["input_configs"].append({
                        "config_id": cfg_id,
                        "task_id": task_id,
                        "netlist_path": f"/data/{rev_code}/{block['block_name']}.spi",
                        "created_at": datetime.now().isoformat()
                    })
                    self.last_added_ids.append(cfg_id)
                    task_count += 1
                
        return {
            "narrative": f"**Task Generation**: {task_count} `SignoffTask` objects created in `PENDING` state.",
            "insight": "**Kinetic Layer (Planning)**: We proactively generate 'Tasks' before execution. This allows us to track *coverage* (Proposed vs. Executed) and identify missing checks early."
        }

    def _step_execution(self):
        job_count = 0
        for task in self.ontology["tasks"]:
            if random.random() > 0.2: 
                task["status"] = "RUNNING"
                job_id = f"JOB_{task['task_id']}"
                
                job = {
                    "job_id": job_id,
                    "task_id": task["task_id"],
                    "status": "RUNNING",
                    "workspace_path": f"/user/{task['owner_id']}/rundir/{job_id}",
                    "start_time": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat()
                }
                self.ontology["jobs"].append(job)
                self.last_added_ids.append(job_id)
                
                ws_id = f"WS_{job_id}"
                self.ontology["workspaces"].append({
                    "workspace_id": ws_id,
                    "workspace_type": "LOCAL",
                    "base_path": job["workspace_path"],
                    "created_at": datetime.now().isoformat()
                })
                self.last_added_ids.append(ws_id)
                job_count += 1
                
        return {
            "narrative": f"**Execution**: {job_count} Jobs submitted to LSF. `SignoffJob` objects track runtime info.",
            "insight": "**Execution Tracking**: We separate `Task` (What to do) from `Job` (Execution Instance). If a job fails and we re-run it, we have multiple Jobs linked to one Task, preserving the full debugging history."
        }

    def _step_completion(self):
        res_count = 0
        for job in self.ontology["jobs"]:
            job["status"] = "DONE"
            job["end_time"] = datetime.now().isoformat()
            
            task = next(t for t in self.ontology["tasks"] if t["task_id"] == job["task_id"])
            task["status"] = "DONE"
            
            res_id = f"RES_{job['job_id']}"
            ws = next(w for w in self.ontology["workspaces"] if w["base_path"] == job["workspace_path"])
            
            self.ontology["results"].append({
                "result_id": res_id,
                "job_id": job["job_id"],
                "task_id": task["task_id"],
                "workspace_id": ws["workspace_id"],
                "row_count": random.randint(100, 1000),
                "waiver_count": 0,
                "fixed_count": 0,
                "created_at": datetime.now().isoformat()
            })
            self.last_added_ids.append(res_id)
            res_count += 1
            
        return {
            "narrative": f"**Completion**: {res_count} Jobs finished. `Result` objects captured in the ontology.",
            "insight": "**Data Virtualization**: Instead of hunting for log files in directories, the `Result` object provides a direct handle to the outcome, linked back to the `InputConfig` that produced it."
        }

    def _step_analysis(self):
        migrated = 0
        for res in self.ontology["results"]:
            total = res.get("row_count", 100)
            waived = int(total * 0.8)
            res["waiver_count"] = waived
            res["result_count"] = total - waived
            res["waiver_progress_pct"] = 80.0
            
            cmp_id = f"CMP_{res['result_id']}"
            self.ontology["comparisons"].append({
                "comparison_id": cmp_id,
                "target_result_id": res["result_id"],
                "same_count": int(total * 0.7),
                "diff_count": int(total * 0.3),
                "waiver_migrated_count": waived,
                "created_at": datetime.now().isoformat()
            })
            self.last_added_ids.append(cmp_id)
            migrated += waived
            
        return {
            "narrative": f"**Analysis & Waiver**: AI compared results with previous baseline. {migrated} violations automatically waived.",
            "insight": "**Dynamic Intelligence**: This is the value of the Dynamic Layer. Because the system knows the lineage (Product->Revision->Task), it can intelligent migrate waivers from R29 to R30 automatically."
        }

    def _calculate_metrics(self) -> Dict:
        """Dashboard metrics generation"""
        total_tasks = len(self.ontology["tasks"])
        running_jobs = len([j for j in self.ontology["jobs"] if j["status"] == "RUNNING"])
        results = len(self.ontology["results"])
        
        # Calculate Pass Rate (Conceptual)
        pass_rate = 0
        if results > 0:
            pass_rate = 100.0 # Simplify for POC
            
        return {
            "Total Tasks": total_tasks,
            "Running Jobs": running_jobs,
            "Results Captured": results,
            "Active Revisions": len(self.ontology["revisions"])
        }

    def _generate_graph_data(self):
        """Generates Cytoscape elements from current ontology state"""
        elements = []
        from data.object_schemas import OBJECT_SCHEMAS, LAYERS

        # 1. Add Layers
        for layer_k, layer_v in LAYERS.items():
            elements.append({
                 "data": {"id": layer_k, "label": layer_v["name"], "color": layer_v["color"]},
                 "classes": "layer-node"
            })
            
        # Helper to add node
        def add_node(obj_id, obj_type, label):
             schema = OBJECT_SCHEMAS.get(obj_type, {})
             classes = ""
             if obj_id in self.last_added_ids:
                 classes = "newly-added"
                 
             elements.append({
                 "data": {
                     "id": obj_id, "label": label, "type": obj_type,
                     "parent": schema.get("layer"), "color": schema.get("color", "#888")
                 },
                 "classes": classes
             })
             
        # Helper to add edge
        def add_edge(src, tgt, label):
            # If both source and target are "new", maybe highlight edge too?
            # For simplicity, just add edge
            elements.append({"data": {"source": src, "target": tgt, "label": label}})
            
        # Products
        for p in self.ontology["products"]:
            add_node(p["product_id"], "Product", p["product_id"])
            
        # Revisions
        for r in self.ontology["revisions"]:
            add_node(r["revision_id"], "Revision", r["revision_code"])
            add_edge(r["product_id"], r["revision_id"], "has_revision")
            
        # Blocks
        for b in self.ontology["blocks"]:
            add_node(b["block_id"], "Block", b["block_name"])
            add_edge(b["revision_id"], b["block_id"], "has_block")
            
        # Applications
        for a in self.ontology["applications"]:
            add_node(a["app_id"], "SignoffApplication", a["app_name"])
            
        # Tasks
        for t in self.ontology["tasks"]:
            add_node(t["task_id"], "SignoffTask", "Task")
            add_edge(t["block_id"], t["task_id"], "requires")
            add_edge(t["task_id"], t["app_id"], "uses")
            
        # Configs
        for c in self.ontology["input_configs"]:
            add_node(c["config_id"], "InputConfig", "Config")
            add_edge(c["task_id"], c["config_id"], "configured_by")
            
        # Jobs
        for j in self.ontology["jobs"]:
            add_node(j["job_id"], "SignoffJob", "Job")
            add_edge(j["task_id"], j["job_id"], "runs")
            
        # Workspaces
        for w in self.ontology["workspaces"]:
            add_node(w["workspace_id"], "Workspace", "WS")
            
        # Results
        for r in self.ontology["results"]:
            add_node(r["result_id"], "Result", "RES")
            add_edge(r["job_id"], r["result_id"], "produces")
            add_edge(r["result_id"], r["workspace_id"], "stored_in")
            
        # Link Job -> Workspace
        for j in self.ontology["jobs"]:
            ws = next((w for w in self.ontology["workspaces"] if w["base_path"] == j["workspace_path"]), None)
            if ws: add_edge(j["job_id"], ws["workspace_id"], "executes_in")
            
        # Comparisons
        for c in self.ontology["comparisons"]:
             add_node(c["comparison_id"], "ComparisonResult", "Diff")
             add_edge(c["comparison_id"], c["target_result_id"], "analyzes")
            
        return elements
