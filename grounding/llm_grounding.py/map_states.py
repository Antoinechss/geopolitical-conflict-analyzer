import time
import hashlib
import subprocess
from typing import Optional, Dict, List

from storage.db import get_connection  # your existing helper
from configs import BATCH_SIZE, SLEEP_SECONDS, MAX_RETRIES, LLM_RUNNER_CMD
from helpers import _extract_json_object
from prompts import build_prompt
from db_operations import fetch_batch, update_row, load_states_whitelist

# Cache to reduce repeated LLM calls in one run
IN_MEMORY_CACHE: Dict[str, Dict[str, Optional[str]]] = {}


def _normalize_state_name(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    s = str(s).strip()
    if s.lower() in {"null", "none", ""}:
        return None
    return s


def _make_cache_key(actor: str, target: str, event_type: str, sentence_text: str) -> str:
    # Include event/sentence context to reduce wrong reuse. Hash to keep key small.
    blob = f"{actor}||{target}||{event_type}||{sentence_text}".encode("utf-8", errors="ignore")
    return hashlib.sha256(blob).hexdigest()


# def call_llm(prompt: str) -> Optional[dict]:
#     """
#     Calls llm_runner.py via subprocess. Returns parsed JSON dict or None.
#     """
#     cmd = LLM_RUNNER_CMD.split()
#     r = subprocess.run(
#         cmd,
#         input=prompt,
#         text=True,
#         capture_output=True,
#     )
#     if r.returncode != 0:
#         return None
#     return _extract_json_object(r.stdout)

def call_llm(prompt: str) -> Optional[dict]:
    cmd = LLM_RUNNER_CMD.split()
    r = subprocess.run(cmd, input=prompt, text=True, capture_output=True)
    if r.returncode != 0:
        print("LLM CALL FAILED:", r.returncode)
        print("STDERR:", r.stderr.strip())
        return None
    return _extract_json_object(r.stdout)


def resolve_states(states_list: List[str], states_set: set, actor: str, target: str, event_type: str, sentence_text: str) -> Dict[str, Optional[str]]:
    # in-process cache
    key = _make_cache_key(actor, target, event_type, sentence_text)
    if key in IN_MEMORY_CACHE:
        return IN_MEMORY_CACHE[key]

    prompt = build_prompt(actor, target, event_type, sentence_text)

    parsed = None
    for _ in range(MAX_RETRIES + 1):
        parsed = call_llm(prompt)
        if parsed is not None and isinstance(parsed, dict):
            break
        time.sleep(0.2)

    actor_state = _normalize_state_name(parsed.get("actor_state") if parsed else None)
    target_state = _normalize_state_name(parsed.get("target_state") if parsed else None)

    # Whitelist enforcement (prevents hallucinations)
    if actor_state not in states_set:
        actor_state = None
    if target_state not in states_set:
        target_state = None

    out = {"actor_state": actor_state, "target_state": target_state}
    IN_MEMORY_CACHE[key] = out
    return out


def run_batches():
    conn = get_connection()
    conn.autocommit = False  # explicit commits per batch

    try:
        states_list, states_set = load_states_whitelist(conn)

        total_updated = 0
        batch_num = 0

        while True:
            batch = fetch_batch(conn, BATCH_SIZE)
            if not batch:
                break

            batch_num += 1
            batch_updated = 0

            for (row_id, actor, target, event_type, sentence_text) in batch:
                actor = (actor or "").strip()
                target = (target or "").strip()
                event_type = (event_type or "").strip()
                sentence_text = (sentence_text or "").strip()

                mapping = resolve_states(
                    states_list=states_list,
                    states_set=states_set,
                    actor=actor,
                    target=target,
                    event_type=event_type,
                    sentence_text=sentence_text,
                )

                update_row(conn, row_id, mapping["actor_state"], mapping["target_state"])
                batch_updated += 1

                if SLEEP_SECONDS > 0:
                    time.sleep(SLEEP_SECONDS)

            conn.commit()
            total_updated += batch_updated

            # Minimal operational logging (stderr only recommended; here using stdout is fine for a CLI tool)
            print(f"[batch {batch_num}] updated {batch_updated} rows (total {total_updated})")

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run_batches()
