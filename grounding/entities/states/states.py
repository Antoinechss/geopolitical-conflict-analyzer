import json

states = {}

with open("/Users/antoinechosson/geopolitical-conflict-analyzer/grounding/entities/states/wikidia_states_raw.json", "r", encoding="utf-8") as f:
    rows = json.load(f)

for row in rows:
    iso3 = row.get("iso3")
    if not iso3:
        continue

    state_id = f"{iso3}_STATE"

    if state_id not in states:
        states[state_id] = {
            "type": "STATE",
            "canonical_name": row["stateLabel"],
            "aliases": set(),
            "regex": [],
            "keywords": [],
            "meta": {
                "iso2": row.get("iso2"),
                "iso3": iso3
            },
            "geo": {
                "lat": float(row["lat"]) if row.get("lat") else None,
                "lon": float(row["lon"]) if row.get("lon") else None
            }
        }

    # Always add canonical name
    states[state_id]["aliases"].add(row["stateLabel"])

    # Add alternative label if present
    if row.get("altLabel"):
        states[state_id]["aliases"].add(row["altLabel"])

    # Add ISO codes
    if row.get("iso2"):
        states[state_id]["aliases"].add(row["iso2"])
    states[state_id]["aliases"].add(iso3)

# Convert alias sets to sorted lists
for state in states.values():
    state["aliases"] = sorted(state["aliases"])

with open("states.json", "w", encoding="utf-8") as out:
    json.dump(states, out, indent=2, ensure_ascii=False)
