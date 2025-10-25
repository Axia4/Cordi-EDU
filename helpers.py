from pathlib import Path
import json

DATA_DIR = Path('_data')
if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True)

# --- helpers -----------------------------------------------------------------
def read_json_file(p: Path):
    try:
        with p.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def list_items(folder_name: str):
    p = DATA_DIR / folder_name
    if not p.exists():
        return []
    # list only directories (IDs) or files without leading dot
    items = [d.name for d in p.iterdir() if not d.name.startswith('.')]
    return sorted(items)

def read_json_file(p):
    try:
        with p.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None
    
def save_json_file(p: Path, data):
    with p.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def create_directory(p: Path):
    if not p.exists():
        p.mkdir(parents=True)