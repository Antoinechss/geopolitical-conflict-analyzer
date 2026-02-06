import time
import hashlib
from typing import Optional, Dict, List

from llm_actor_target_processing.llm_client import OllamaClient
from llm_actor_target_processing.helpers import extract_json_object
from llm_actor_target_processing.prompts_ground import build_prompt


# In-memory cache (per run)
IN_MEMORY_CACHE: Dict[str, Dict[str, Optional[str]]] = {}


def _normalize_state_name(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    s = str(s).strip()
    if s.lower() in {"null", "none", ""}:
        return None
    return s


def _make_cache_key(
    actor: str,
    target: str,
    event_type: str,
    sentence_text: str,
) -> str:
    blob = f"{actor}||{target}||{event_type}||{sentence_text}".encode(
        "utf-8", errors="ignore"
    )
    return hashlib.sha256(blob).hexdigest()


async def resolve_states(
    *,
    client: OllamaClient,
    states_list: List[str],
    states_set: set,
    actor: str,
    target: str,
    event_type: str,
    sentence_text: str,
    max_retries: int = 2,
) -> Dict[str, Optional[str]]:
    """
    Pure async grounding function.
    No DB access.
    """

    key = _make_cache_key(actor, target, event_type, sentence_text)
    if key in IN_MEMORY_CACHE:
        return IN_MEMORY_CACHE[key]

    prompt = build_prompt(actor, target, event_type, sentence_text)

    parsed = None
    for _ in range(max_retries + 1):
        try:
            out = await client.run(prompt)
            parsed = extract_json_object(out)
            if isinstance(parsed, dict):
                break
        except Exception:
            pass
        time.sleep(0.2)

    actor_state = _normalize_state_name(parsed.get("actor_state") if parsed else None)
    target_state = _normalize_state_name(parsed.get("target_state") if parsed else None)

    # whitelist enforcement
    if actor_state not in states_set:
        actor_state = None
    if target_state not in states_set:
        target_state = None

    result = {
        "actor_state": actor_state,
        "target_state": target_state,
    }

    IN_MEMORY_CACHE[key] = result
    return result
