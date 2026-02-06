from typing import Optional, Tuple, List
import re

from llm_actor_target_processing.llm_client import OllamaClient
from llm_actor_target_processing.helpers import extract_json_object
from llm_actor_target_processing.prompts_extract import build_prompt

# -------------------------
# Sentence splitting
# -------------------------
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def split_sentences(text: str) -> List[str]:
    if not text:
        return []
    return [s.strip() for s in _SENTENCE_SPLIT_RE.split(text) if s.strip()]


# -------------------------
# LLM output parsing
# -------------------------
def parse_llm_output(
    llm_output: str,
    event_id: str,
    sentence_index: int,
    sentence_text: str,
) -> Optional[Tuple[str, int, str, Optional[str], Optional[str], str]]:
    obj = extract_json_object(llm_output)
    if not obj:
        print(f"[parse] No JSON found in output")
        raise ValueError("Invalid JSON")

    print(f"[parse] Extracted JSON: {obj}")
    
    actor = _normalize_field(obj.get("actor"))
    target = _normalize_field(obj.get("target"))
    event_type = _normalize_field(obj.get("event"))

    print(f"[parse] Normalized - actor: {actor}, target: {target}, event: {event_type}")

    if not event_type or event_type == "UNDEFINED":
        return None

    return (
        event_id,
        sentence_index,
        sentence_text,
        actor,
        target,
        event_type,
    )



# -------------------------
# Extraction entry point
# -------------------------
async def extract_actor_target_from_text(
    event_id: str,
    text: str,
    client: OllamaClient,
) -> List[Tuple[str, int, str, Optional[str], Optional[str], str]]:
    """
    Pure async function:
    input  → event_id + text
    output → DB-ready rows
    """

    sentences = split_sentences(text)
    rows: List[Tuple] = []

    for sentence_index, sentence_text in enumerate(sentences):
        prompt = build_prompt(sentence_text)

        # first attempt
        llm_output = await client.run(prompt)
        print(f"[extract] sentence: {sentence_text[:50]}...")
        print(f"[extract] LLM output: {llm_output[:200]}...")

        try:
            row = parse_llm_output(
                llm_output,
                event_id,
                sentence_index,
                sentence_text,
            )
            if row:
                print(f"[extract] parsed: actor={row[3]}, target={row[4]}, event={row[5]}")
            else:
                print(f"[extract] returned None (no event or UNDEFINED)")
        except ValueError as e:
            print(f"[extract] parse error: {e}, trying repair...")
            # one repair attempt
            repair_prompt = (
                "Fix the JSON below. Do NOT change any values. "
                "Return ONLY valid JSON.\n\n"
                + llm_output
            )

            llm_output = await client.run(repair_prompt)
            print(f"[extract] repair output: {llm_output[:200]}...")
            row = parse_llm_output(
                llm_output,
                event_id,
                sentence_index,
                sentence_text,
            )
            if row:
                print(f"[extract] repaired: actor={row[3]}, target={row[4]}, event={row[5]}")
            else:
                print("[extract] repair returned None")

        if row:
            rows.append(row)

    return rows


def _normalize_field(value) -> Optional[str]:
    """
    Enforce DB-safe scalar values.
    Accepts str | None.
    Everything else is coerced or dropped.
    """
    if value is None:
        return None

    if isinstance(value, str):
        v = value.strip()
        return v if v else None

    # LLM sometimes returns dicts or lists → reject safely
    return None
