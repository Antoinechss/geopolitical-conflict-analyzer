def build_prompt(actor, target, event_type, sentence_text):
    return f"""
You resolve actors and targets to sovereign states.

Rules:
- Return the sovereign state name in English.
- If the actor or target is a person, infer the state if unambiguous.
- If no clear sovereign state applies, return null.
- Output VALID JSON ONLY.
- No explanations.

Actor: {actor}
Target: {target}
Event type: {event_type}
Sentence: {sentence_text}

Return JSON with keys:
actor_state
target_state
""".strip()
