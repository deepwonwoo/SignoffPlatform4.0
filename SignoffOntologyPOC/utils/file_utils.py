import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Optional

DEFAULT_ONTOLOGY_DIR = "./ontology_data/"

def save_ontology_to_json(ontology_data: Dict, filename: Optional[str] = None) -> str:
    """Ontology를 JSON 파일로 저장"""
    os.makedirs(DEFAULT_ONTOLOGY_DIR, exist_ok=True)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        product = ontology_data["ontology"]["products"][0]["product_id"]
        filename = f"signoff_ontology_{product}_{timestamp}.json"
    
    if not filename.endswith(".json"):
        filename += ".json"
    
    filepath = os.path.join(DEFAULT_ONTOLOGY_DIR, filename)
    
    # 메타데이터 업데이트
    ontology_data["meta"]["updated_at"] = datetime.now().isoformat()
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(ontology_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def load_ontology(filepath: str) -> Dict:
    """JSON 파일에서 Ontology 로드"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def list_ontology_files() -> List[Dict]:
    """저장된 Ontology 파일 목록 반환"""
    os.makedirs(DEFAULT_ONTOLOGY_DIR, exist_ok=True)
    
    files = glob.glob(os.path.join(DEFAULT_ONTOLOGY_DIR, "*.json"))
    file_list = []
    
    for filepath in sorted(files, key=os.path.getmtime, reverse=True):
        stat = os.stat(filepath)
        file_list.append({
            "filepath": filepath,
            "filename": os.path.basename(filepath),
            "size_kb": stat.st_size // 1024,
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
        })
    
    return file_list

def delete_ontology(filepath: str) -> bool:
    """Ontology 파일 삭제"""
    try:
        os.remove(filepath)
        return True
    except:
        return False
