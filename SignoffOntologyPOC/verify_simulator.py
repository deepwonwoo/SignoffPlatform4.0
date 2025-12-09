import sys
import os
import json

# Add current directory to path
sys.path.append(os.getcwd())

from utils.ontology_simulator import SignoffSimulator

def verify_simulator():
    config = {
        "product_id": "TEST_PROD",
        "product_type": "HBM",
        "active_revisions": ["R30"],
        "blocks": [
            {"block_name": "TEST_BLOCK", "block_type": "TOP"}
        ],
        "signoff_matrix": {"DSC": ["R30"]}
    }
    
    sim = SignoffSimulator(config)
    
    print("Testing One Step (Initialization)...")
    res = sim.next_step()
    print(f"Step: {res.get('step')}")
    print(f"Narrative: {res.get('narrative')}")
    print(f"Insight: {res.get('insight')}")
    
    if not res.get('insight'):
        print("FAILED: No insight provided.")
        return False
        
    if not res.get('highlight_ids'):
        print("FAILED: No highlight_ids provided for new nodes.")
        return False
        
    print("\nTesting Full Cycle Step-by-Step...")
    while res.get("step") != "Finished":
        res = sim.next_step()
        print(f"> {res.get('step')}: {res.get('narrative')[:50]}...")
        if res.get("step") == "Analysis":
            if not res.get("metrics"):
                print("FAILED: No metrics in Analysis step.")
                return False
            print(f"metrics: {res.get('metrics')}")

    # Check final state
    if not sim.ontology["results"]:
        print("FAILED: No results generated after full cycle.")
        return False
        
    print("\nTesting Scenario Load (Full)...")
    full_res = sim.load_scenario("full")
    if not full_res.get("metrics"):
         print("FAILED: Full scenario load missing metrics.")
         return False
         
    if len(sim.ontology["comparisons"]) == 0:
         print("FAILED: Full scenario missing comparisons.")
         return False
         
    print("SUCCESS: Educational Simulator verified.")
    return True

if __name__ == "__main__":
    if verify_simulator():
        sys.exit(0)
    else:
        sys.exit(1)
