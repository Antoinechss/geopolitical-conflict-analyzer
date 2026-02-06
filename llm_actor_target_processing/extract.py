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
        raise ValueError("Invalid JSON")

    event_type = obj.get("event")
    actor = _normalize_field(obj.get("actor"))
    target = _normalize_field(obj.get("target"))
    event_type = _normalize_field(obj.get("event"))

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

        try:
            row = parse_llm_output(
                llm_output,
                event_id,
                sentence_index,
                sentence_text,
            )
        except ValueError:
            # one repair attempt
            repair_prompt = (
                "Fix the JSON below. Do NOT change any values. "
                "Return ONLY valid JSON.\n\n"
                + llm_output
            )

            llm_output = await client.run(repair_prompt)
            row = parse_llm_output(
                llm_output,
                event_id,
                sentence_index,
                sentence_text,
            )

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
