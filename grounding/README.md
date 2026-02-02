## Sources for grounding json files

states.json
------------------------------------------

states.json contains UN member states plus UN observer states (Holy See and State of Palestine), totaling approximately 195 internationally recognized sovereign entities. The file intentionally excludes disputed territories and subnational regions.

193 UN members + Holy See (Vatican) + Palestine = 195 entries

SPARQL Wikidata Query Service 

```SQL
SELECT ?state ?stateLabel ?altLabel ?iso2 ?iso3 ?capitalLabel ?lat ?lon WHERE {
  {
    ?state wdt:P463 wd:Q1065.   # UN member
  }
  UNION
  {
    VALUES ?state { wd:Q159583 wd:Q219060 }  # Holy See, Palestine
  }

  OPTIONAL { ?state wdt:P297 ?iso2. }
  OPTIONAL { ?state wdt:P298 ?iso3. }

  OPTIONAL {
    ?state skos:altLabel ?altLabel .
    FILTER (lang(?altLabel) = "en")
  }

  OPTIONAL {
    ?state wdt:P36 ?capital .
    ?capital wdt:P625 ?coord .
    BIND(geof:latitude(?coord) AS ?lat)
    BIND(geof:longitude(?coord) AS ?lon)
  }

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en".
  }
}
```

