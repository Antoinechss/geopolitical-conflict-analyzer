import json
import re
from typing import Optional, Dict

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def extract_json_object(text: str) -> Optional[Dict]:
    if not text:
        return None
    m = _JSON_RE.search(text.strip())
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
