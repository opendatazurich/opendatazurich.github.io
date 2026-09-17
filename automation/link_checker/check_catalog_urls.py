"""
URL-Extraktion aus dem Open Data Katalog der Stadt Zürich (CKAN API).

Liest alle Datensätze inkl. Ressourcen über die CKAN API und extrahiert URLs
aus drei Quellen:
  1. resources[].url          — direkte Download/API-Endpunkte
  2. sszBemerkungen           — Markdown-Links [text](url)
  3. notes                    — URLs im Fliesstext

Ausgabe:
  - .cache/catalog_urls.txt      : Deduplizierte URL-Liste (Lychee-Input)
  - .cache/url_dataset_map.json  : Mapping URL → Dataset-Name (für build_report)

Abhängigkeiten: Nur Python-Standardbibliothek.
"""

import json
import os
import re
import sys
import urllib.request

API_URL = "https://data.stadt-zuerich.ch/api/3/action/current_package_list_with_resources?limit=9999"
CACHE_DIR = ".cache"
URLS_PATH = f"{CACHE_DIR}/catalog_urls.txt"
MAP_PATH = f"{CACHE_DIR}/url_dataset_map.json"

MD_LINK_RE = re.compile(r"\[([^\]]*)\]\((https?://[^)]+)\)")
PLAIN_URL_RE = re.compile(r"https?://[^\s\)\"\']+(?=[\s\)\]\"']|$)")

EXCLUDE_DOMAINS = [
    "data.integ.stadt-zuerich.ch",
]


def is_valid_url(url: str) -> bool:
    """HTTP/HTTPS URL, kein javascript:/data:/mailto:."""
    if not url:
        return False
    url_stripped = url.strip()
    if url_stripped.startswith(("javascript:", "data:", "mailto:")):
        return False
    return url_stripped.startswith(("http://", "https://"))


def is_excluded(url: str) -> bool:
    for domain in EXCLUDE_DOMAINS:
        if url.startswith(f"http://{domain}") or url.startswith(f"https://{domain}"):
            return True
    return False


def load_packages() -> list[dict]:
    req = urllib.request.Request(API_URL, headers={"User-Agent": "opendata-zuerich-link-checker"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if not data.get("success"):
        print(f"ERROR: API returned success={data.get('success')}", file=sys.stderr)
        sys.exit(1)
    return data["result"]


def build_url_dataset_mapping(packages: list[dict]) -> dict[str, str]:
    """Mapping URL → Dataset-Name.

    resources[].url erhält Vorrang. URLs aus sszBemerkungen und notes werden
    nur zugewiesen, wenn sie noch kein Mapping haben.
    """
    url_to_dataset: dict[str, str] = {}

    for pkg in packages:
        pkg_name = pkg.get("name", "")
        if not pkg_name:
            continue

        for res in pkg.get("resources", []):
            url = res.get("url", "")
            if url and is_valid_url(url) and not is_excluded(url):
                url_to_dataset[url] = pkg_name

        for field, regex in (("sszBemerkungen", MD_LINK_RE), ("notes", PLAIN_URL_RE)):
            text = pkg.get(field, "")
            if not text:
                continue
            for match in regex.findall(text):
                url = match[1] if isinstance(match, tuple) else match
                if is_valid_url(url) and not is_excluded(url) and url not in url_to_dataset:
                    url_to_dataset[url] = pkg_name

    return url_to_dataset


def main():
    print(f"Lade Pakete von {API_URL}", file=sys.stderr)
    packages = load_packages()
    print(f"Gefunden: {len(packages)} Pakete", file=sys.stderr)

    url_to_dataset = build_url_dataset_mapping(packages)

    os.makedirs(CACHE_DIR, exist_ok=True)

    with open(MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(url_to_dataset, f, ensure_ascii=False, indent=2)
    print(f"Mapping geschrieben: {MAP_PATH} ({len(url_to_dataset)} Einträge)", file=sys.stderr)

    with open(URLS_PATH, "w", encoding="utf-8") as f:
        for url in sorted(url_to_dataset):
            f.write(url + "\n")
    print(f"URL-Liste geschrieben: {URLS_PATH} ({len(url_to_dataset)} URLs)", file=sys.stderr)


if __name__ == "__main__":
    main()
