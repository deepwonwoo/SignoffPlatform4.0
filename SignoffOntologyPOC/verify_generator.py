import sys
import os
import json

# Add current directory to path
sys.path.append(os.getcwd())

from utils.ontology_generator import OntologyGenerator

def verify_generator():
    config = {
        "product_id": "TEST_PROD",
        "product_type": "HBM",
        "active_revisions": ["R30"],
        "blocks": [
            {"block_name": "TEST_BLOCK", "block_type": "TOP"}
        ],
        "signoff_matrix": {"DSC": ["R30"]}
    }
    
    try:
        generator = OntologyGenerator(config)
        data = generator.generate()
        
        # Check keys
        required_keys = ["products", "revisions", "blocks", "tasks", "jobs", "results", "input_configs", "workspaces"]
        for key in required_keys:
            if key not in data["ontology"]:
                print(f"FAILED: Missing key {key} in ontology data")
                return False
            if not data["ontology"][key]:
                print(f"WARNING: {key} list is empty")
                
        # Check Graph
        if not data["graph"]["nodes"]:
            print("FAILED: Graph nodes are empty")
            return False
            
        print("SUCCESS: Data generation verified.")
        return True
        
    except Exception as e:
        print(f"FAILED: Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if verify_generator():
        sys.exit(0)
    else:
        sys.exit(1)
