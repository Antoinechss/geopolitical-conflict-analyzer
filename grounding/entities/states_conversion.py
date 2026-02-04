import json

INPUT_FILE = "/Users/antoinechosson/geopolitical-conflict-analyzer/grounding/entities/states_with_regex.json"
OUTPUT_FILE = "states.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw = json.load(f)

states = []

for key, state in raw.items():
    if state.get("type") != "STATE":
        continue

    meta = state.get("meta", {})
    geo = state.get("geo", {})

    iso3 = meta.get("iso3")
    lat = geo.get("lat")
    lon = geo.get("lon")

    # Strict validation
    if not iso3 or lat is None or lon is None:
        continue

    states.append({
        "id": iso3,
        "name": state.get("canonical_name"),
        "lon": float(lon),
        "lat": float(lat)
    })

# Optional: sort for reproducibility
states.sort(key=lambda s: s["id"])

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(states, f, indent=2, ensure_ascii=False)

print(f"Exported {len(states)} states to {OUTPUT_FILE}")
