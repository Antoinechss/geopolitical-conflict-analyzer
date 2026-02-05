from typing import Optional 
import re 
import json

JSON_OBJ_RE = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json_object(text: str) -> Optional[dict]:
    """
    Extract first JSON object from model output.
    Safe handles cases where the LLM adds text before/after.
    """
    if not text:
        return None
    m = JSON_OBJ_RE.search(text.strip())
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None