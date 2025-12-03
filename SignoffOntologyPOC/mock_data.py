import pandas as pd
from datetime import datetime, timedelta

# --- Mock Data Classes ---

class SignoffObject:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self):
        return self.__dict__

# --- Data Generation ---

def generate_mock_data():
    # 1. Products
    products = [
        SignoffObject(
            id="HBM4E",
            type="HBM",
            name="HBM4E 32GB Wide I/O",
            manager="deepwonwoo"
        ),
        SignoffObject(
            id="LPDDR6",
            type="LPDDR",
            name="LPDDR6 16GB Mobile",
            manager="jane.doe"
        )
    ]

    # 2. Revisions
    revisions = [
        SignoffObject(
            id="HBM4E_R29",
            product_id="HBM4E",
            phase="R29",
            status="COMPLETED",
            due_date="2024-10-01"
        ),
        SignoffObject(
            id="HBM4E_R30",
            product_id="HBM4E",
            phase="R30",
            status="IN_PROGRESS",
            due_date="2024-12-01"
        )
    ]

    # 3. Blocks
    blocks = [
        SignoffObject(id="HBM4E_R30_FULLCHIP", revision_id="HBM4E_R30", name="FULLCHIP", type="TOP"),
        SignoffObject(id="HBM4E_R30_IO", revision_id="HBM4E_R30", name="IO", type="PHY"),
        SignoffObject(id="HBM4E_R30_SRAM_A", revision_id="HBM4E_R30", name="SRAM_A", type="MEMORY"),
        SignoffObject(id="HBM4E_R29_FULLCHIP", revision_id="HBM4E_R29", name="FULLCHIP", type="TOP"),
    ]

    # 4. Applications
    apps = [
        SignoffObject(id="DSC", name="Driver Size Check", group="Static"),
        SignoffObject(id="LSC", name="Latch Strength Check", group="Static"),
        SignoffObject(id="LS", name="Level Shifter Check", group="Static"),
        SignoffObject(id="PEC", name="Power Error Check", group="Static"),
        SignoffObject(id="CANATR", name="Coupling Noise Analysis", group="Dynamic"),
    ]

    # 5. Tasks & Jobs & Results
    tasks = []
    jobs = []
    results = []

    # Scenario 1: FULLCHIP DSC (Success)
    task1 = SignoffObject(
        id="DSC_FULLCHIP_R30",
        revision_id="HBM4E_R30",
        block_id="HBM4E_R30_FULLCHIP",
        app_id="DSC",
        status="COMPLETED",
        owner="deepwonwoo"
    )
    tasks.append(task1)

    job1 = SignoffObject(
        id="JOB_DSC_FULLCHIP_R30_001",
        task_id="DSC_FULLCHIP_R30",
        status="DONE",
        start_time="2024-11-20 10:00",
        end_time="2024-11-20 11:30",
        workspace="/WORKSPACE/HBM4E/R30/FULLCHIP/DSC/"
    )
    jobs.append(job1)

    result1 = SignoffObject(
        id="RES_DSC_FULLCHIP_R30_001",
        job_id="JOB_DSC_FULLCHIP_R30_001",
        total_violations=1500,
        waiver_count=1450,
        fixed_count=50,
        pending_count=0,
        waiver_rate=96.7,
        status="PASS" # Derived logic
    )
    results.append(result1)

    # Scenario 2: IO DSC (Failed - Power Error)
    task2 = SignoffObject(
        id="DSC_IO_R30",
        revision_id="HBM4E_R30",
        block_id="HBM4E_R30_IO",
        app_id="DSC",
        status="BLOCKED",
        owner="kim.engineer"
    )
    tasks.append(task2)

    job2 = SignoffObject(
        id="JOB_DSC_IO_R30_001",
        task_id="DSC_IO_R30",
        status="FAILED",
        start_time="2024-11-21 09:00",
        end_time="2024-11-21 09:05",
        workspace="/WORKSPACE/HBM4E/R30/IO/DSC/",
        error_msg="Power Net 'VDD_PERI' not defined in power list"
    )
    jobs.append(job2)

    # Scenario 3: SRAM_A LSC (Running)
    task3 = SignoffObject(
        id="LSC_SRAM_A_R30",
        revision_id="HBM4E_R30",
        block_id="HBM4E_R30_SRAM_A",
        app_id="LSC",
        status="IN_PROGRESS",
        owner="lee.senior"
    )
    tasks.append(task3)

    job3 = SignoffObject(
        id="JOB_LSC_SRAM_A_R30_001",
        task_id="LSC_SRAM_A_R30",
        status="RUNNING",
        start_time="2024-11-21 13:00",
        end_time=None,
        workspace="/WORKSPACE/HBM4E/R30/SRAM_A/LSC/"
    )
    jobs.append(job3)

    return {
        "products": products,
        "revisions": revisions,
        "blocks": blocks,
        "apps": apps,
        "tasks": tasks,
        "jobs": jobs,
        "results": results
    }

def get_ontology_schema():
    # Nodes
    nodes = [
        {'data': {'id': 'Product', 'label': 'Product'}},
        {'data': {'id': 'Revision', 'label': 'Revision'}},
        {'data': {'id': 'Block', 'label': 'Block'}},
        {'data': {'id': 'SignoffApplication', 'label': 'SignoffApplication'}},
        {'data': {'id': 'SignoffTask', 'label': 'SignoffTask'}},
        {'data': {'id': 'SignoffJob', 'label': 'SignoffJob'}},
        {'data': {'id': 'Result', 'label': 'Result'}},
        {'data': {'id': 'Designer', 'label': 'Designer'}},
        {'data': {'id': 'Workspace', 'label': 'Workspace'}},
        {'data': {'id': 'InputConfig', 'label': 'InputConfig'}},
    ]

    # Edges
    edges = [
        {'data': {'source': 'Product', 'target': 'Revision', 'label': 'has_revision'}},
        {'data': {'source': 'Revision', 'target': 'Block', 'label': 'has_block'}},
        {'data': {'source': 'Revision', 'target': 'SignoffApplication', 'label': 'requires'}},
        {'data': {'source': 'Block', 'target': 'SignoffTask', 'label': 'target_of'}},
        {'data': {'source': 'SignoffApplication', 'target': 'SignoffTask', 'label': 'defines'}},
        {'data': {'source': 'SignoffTask', 'target': 'SignoffJob', 'label': 'has_job'}},
        {'data': {'source': 'SignoffJob', 'target': 'Result', 'label': 'produces'}},
        {'data': {'source': 'SignoffJob', 'target': 'Workspace', 'label': 'executes_in'}},
        {'data': {'source': 'SignoffTask', 'target': 'InputConfig', 'label': 'uses'}},
        {'data': {'source': 'Designer', 'target': 'SignoffTask', 'label': 'owns'}},
    ]
    return nodes + edges
