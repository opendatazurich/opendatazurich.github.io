
import os
import logging
from typing import Any, Dict, List, Optional

import requests
import pandas as pd
from dotenv import load_dotenv, find_dotenv


# -------------------------------------------------------------------
# Konfiguration & Logging
# -------------------------------------------------------------------

load_dotenv(find_dotenv())

API_TOKEN = os.getenv("GINTO_API_TOKEN")
API_URL = "https://api.ginto.guide/graphql"
# Filter provided by Ginto/Pro Infirmis: Contains only Object with a pro informis entry
FILTER_ID = "ff8c1e80-51b2-4972-871a-47e5341033c4"

OUTPUT_DIR = "automation/immo_ginto_zugaenglichkeit"
OUTPUT_FILENAME = "immo_ginto_zugaenglichkeit.csv"

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
    "Accept-Language": "de",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# GraphQL Query
# -------------------------------------------------------------------

QUERY = """
query FetchEntries($after: String) {
  entriesByFilter(
    filterId: "%s",
    first: 50,
    after: $after
  ) {
    totalCount
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      node {
        id
        sourceIds(sourceKey: "parks.swiss")
        name
        position {
          street
          housenumber
          postcode
          city
          lat
          lng
        }
        accessibilityInfo {
          defaultRatings {
            descriptionDE: description(locale: DE)
            iconUrl
            key
          }
        }
        publication {
          linkUrl
        }
      }
    }
  }
}
""" % FILTER_ID


# -------------------------------------------------------------------
# API‑Funktionen
# -------------------------------------------------------------------

def fetch_page(after: Optional[str] = None) -> Dict[str, Any]:
    """Holt eine einzelne Seite aus der GraphQL‑API."""
    payload = {"query": QUERY, "variables": {"after": after}}

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()

    logger.debug("Seite erfolgreich abgerufen (after=%s)", after)
    return response.json()


def json_edges_to_df(data: Dict[str, Any]) -> pd.DataFrame:
    """Extrahiert edges → DataFrame."""
    edges = data["data"]["entriesByFilter"]["edges"]
    nodes = [edge["node"] for edge in edges]

    return pd.json_normalize(nodes, sep="_")


def fetch_all_pages() -> pd.DataFrame:
    """Iteriert über alle Seiten der Paginierung."""
    dfs: List[pd.DataFrame] = []
    after: Optional[str] = None
    page = 1

    while True:
        logger.info("Lade Seite %s …", page)
        data = fetch_page(after)

        df = json_edges_to_df(data)
        dfs.append(df)

        pageinfo = data["data"]["entriesByFilter"]["pageInfo"]
        logger.debug("pageInfo: %s", pageinfo)

        if not pageinfo["hasNextPage"]:
            logger.info("Keine weiteren Seiten vorhanden")
            break

        after = pageinfo["endCursor"]
        page += 1

    return pd.concat(dfs, ignore_index=True)


# -------------------------------------------------------------------
# Transformationsfunktionen
# -------------------------------------------------------------------

def extract_default_ratings(ratings: Any) -> Dict[str, Optional[str]]:
    """
    Entpackt accessibilityInfo.defaultRatings in flache Spalten.
    """
    rating_types = ["toilet", "parking", "visual", "cognitive", "inductive"]
    fields = ["descriptionDE", "iconUrl"]

    result: Dict[str, Optional[str]] = {
        f"{rtype}_{field}": None
        for rtype in rating_types + ["general"]
        for field in fields
    }

    if not isinstance(ratings, list):
        return result

    for item in ratings:
        key = (item.get("key") or "").lower()
        matched = False

        for rtype in rating_types:
            if rtype in key:
                for field in fields:
                    result[f"{rtype}_{field}"] = item.get(field)
                matched = True
                break

        if not matched:
            for field in fields:
                result[f"general_{field}"] = item.get(field)

    return result


# -------------------------------------------------------------------
# Orchestrierung
# -------------------------------------------------------------------

def main() -> None:
    logger.info("Starte Ginto‑API‑Import")

    df = fetch_all_pages()

    logger.info("Extrahiere Accessibility‑Ratings")
    ratings_expanded = df["accessibilityInfo_defaultRatings"].apply(
        extract_default_ratings
    )
    ratings_df = pd.DataFrame(ratings_expanded.tolist())

    df = pd.concat([df, ratings_df], axis=1)
    df = df.drop(
        columns=[
            "accessibilityInfo_defaultRatings",
            "id",
            "sourceIds",
        ],
        errors="ignore",
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)

    df.to_csv(output_path, index=False)

    logger.info(f"CSV gespeichert: {output_path} ({len(df)} Zeilen)")


if __name__ == "__main__":
    main()
