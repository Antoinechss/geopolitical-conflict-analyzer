# geopolitical-conflict-analyzer

## DATA SOURCING
---------------------------------------------

### Entities (V1)
---------------------------------------------

| Type | Description | Examples | Sources | 
| ---- | ----------- | -------- | ------- | 
| STATE | Sovereign states | USA, Russia, Ukraine | Wikidata + ISO-3166 |
| STATE_EXECUTIVE | Government / leadership | Trump administration, Kremlin | Wikidata (gov bodies, offices) |
| INT_ORG | International organizations | UN, EU, NATO | Wikidata |
| NON_STATE_ACTOR | Armed groups, militias | Hamas, ISIS | ACLED lists + Wikidata |
| ORG | Companies, institutions | Gazprom, Lockheed Martin | Wikidata |
| LOCATION | Cities, regions | Gaza, Donetsk | GeoNames + Wikidata |

### Grounding of entities

Using Wikidata

## ANALYSIS 

### 2.1 Actor Target RelationShip Detection ---------------------------------------------

This section focuses on **extracting structured actor–target geopolitical events from unstructured social media posts**

### Event Representation

Each sentence within a post is annotated independently. 

Presence of event: 

```json
{
  "sentence": "France intercepted the Russian tanker.",
  "event": {
    "event_type": "ATTACK",
    "trigger": "intercepted",
    "arguments": [
      {
        "role": "AGENT",
        "text": "France"
      },
      {
        "role": "TARGET",
        "text": "the Russian tanker"
      }
    ]
  }
}
```

No event or actor target relation : 

```json
{
  "sentence": "Markets reacted nervously to the announcement.",
  "event": null
}
```

This explicit null labeling is critical to teach the model when not to extract events, significantly reducing false positives.

### Event Ontology (V1)

Here are the type of events (actor-target relations) chosen in this first version of the model. It is intentionally coarse-grained to prioritize precision and model stability. Fine-grained distinctions will be handled downstream via post-processing.

| Event Type | Description |
| ---------- | ----------- |
| ATTACK | Kinetic or physical attacks, strikes, targeting |
| THREAT | Explicit threats or warnings of action |
| COERCIVE_ACTION | Sanctions, tariffs, arms sales, funding cuts |
| DIPLOMATIC_ACTION | Agreements, MOUs, formal diplomatic acts |
| PROTEST | Organized public protests or unrest |
| CYBER_OPERATION | Cyber attacks or cyber coercion |
| TERRORISM | Terrorist attacks or operations |


## LEGAL AND ETHICAL NOTICE
----------------------------------------------------------

* Source content originates from publicly available accessible Telegram channel 
* No private, restricted, or paywalled content is included