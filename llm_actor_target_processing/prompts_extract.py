def build_prompt(sentence_text: str) -> str:
    """
    Build prompt for actor-target extraction from a sentence.
    """
    return f"""Extract geopolitical actor-target relations from this sentence.

Rules:
- Identify the ACTOR (who is acting)
- Identify the TARGET (who/what is being acted upon)
- Classify the EVENT_TYPE from: ATTACK, THREAT, COERCIVE_ACTION, DIPLOMATIC_ACTION, PROTEST, CYBER_OPERATION, TERRORISM
- If no clear event, return "UNDEFINED" for event_type
- Output VALID JSON ONLY with keys: actor, target, event

Sentence: {sentence_text}

Return JSON:
{{
  "actor": "...",
  "target": "...",
  "event": "..."
}}
""".strip()
