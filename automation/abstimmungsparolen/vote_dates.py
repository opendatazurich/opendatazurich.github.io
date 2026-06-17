# -*- coding: utf-8 -*-
"""Eidgenössische Abstimmungstermine via LINDAS SPARQL.

Datenquelle: BK-0003 "Abstimmungstermine" der Bundeskanzlei,
publiziert als Linked-Data-Cube auf LINDAS.

Cube IRI:   https://politics.ld.admin.ch/political-rights/popular-vote/voting_dates/1
Endpoint:   https://cached.lindas.admin.ch/query
Webansicht: https://www.bk.admin.ch/de/blanko-abstimmungstermine
"""

from datetime import date
import requests


SPARQL_ENDPOINT = "https://cached.lindas.admin.ch/query"

# Termintypen, an denen tatsächlich eine eidg. Volksabstimmung
# stattfindet (im Gegensatz zu reservierten Blankoterminen,
# ungenutzten Reservedaten oder Nationalratswahlen).
SCHEDULED_TYPES = frozenset({"festgelegt", "genutzt"})

_QUERY = """
PREFIX cube: <https://cube.link/>
PREFIX vd:   <https://politics.ld.admin.ch/political-rights/popular-vote/voting_dates/>
SELECT ?datum ?typ WHERE {
  <https://politics.ld.admin.ch/political-rights/popular-vote/voting_dates/1>
    cube:observationSet/cube:observation ?o .
  ?o vd:date ?datum ;
     vd:typ  ?typIri .
  BIND(REPLACE(STR(?typIri), ".*/", "") AS ?typ)
}
ORDER BY ?datum
"""


def fetch_vote_dates():
    """Alle bekannten Abstimmungstermine als Liste (date, typ)."""
    r = requests.get(
        SPARQL_ENDPOINT,
        params={"query": _QUERY},
        headers={"Accept": "application/sparql-results+json"},
    )
    r.raise_for_status()
    return [
        (date.fromisoformat(b["datum"]["value"]), b["typ"]["value"])
        for b in r.json()["results"]["bindings"]
    ]


def get_next_scheduled_vote(today=None):
    """Datum der nächsten festgelegten eidg. Volksabstimmung oder None."""
    today = today or date.today()
    for datum, typ in fetch_vote_dates():
        if datum >= today and typ in SCHEDULED_TYPES:
            return datum
    return None


if __name__ == "__main__":
    print(get_next_scheduled_vote())
