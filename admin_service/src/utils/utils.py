from typing import Any, Dict

def safe_json(r):
    try:
        return r.json()
    except Exception:
        return {"status_code": r.status_code, "text": r.text}
