"""
URL-Extraktion aus dem Open Data Katalog der Stadt Zürich (CKAN API).

Liest alle Datensätze inkl. Ressourcen über die CKAN API und extrahiert URLs
aus drei Quellen:
  1. resources[].url          — direkte Download/API-Endpunkte
  2. sszBemerkungen           — Markdown-Links [text](url)
  3. notes                    — URLs im Fliesstext

Ausgabe:
  - .cache/catalog_urls.txt: Deduplizierte, sortierte URL-Liste (für Post-Prozessor)
  - .cache/lychee_catalog.toml: Lychee TOML-Config mit [include] Array
  - /tmp/url_dataset_map.json: Mapping URL → Dataset-Name (für Post-Prozessor)

Abhängigkeiten: Nur Python-Standardbibliothek.
"""

import json
import os
import re
import sys
import urllib.request

API_URL = "https://data.stadt-zuerich.ch/api/3/action/current_package_list_with_resources?limit=9999"
URLS_PATH = ".cache/catalog_urls.txt"
CONFIG_PATH = ".cache/lychee_catalog.toml"
MAP_PATH = "/tmp/url_dataset_map.json"

MD_LINK_RE = re.compile(r"\[([^\]]*)\]\((https?://[^)]+)\)")
PLAIN_URL_RE = re.compile(r"https?://[^\s\)\"\']+(?=[\s\)\]\"']|$)")

EXCLUDE_DOMAINS = [
    "data.integ.stadt-zuerich.ch",
]


def is_valid_url(url: str) -> bool:
    """Check ob URL gültig ist (HTTP/HTTPS, kein javascript:/data:)."""
    if not url:
        return False
    url_stripped = url.strip()
    if url_stripped.startswith(("javascript:", "data:", "mailto:")):
        return False
    if url_stripped.startswith("http://") or url_stripped.startswith("https://"):
        return True
    return False


def is_excluded(url: str) -> bool:
    """Check ob URL auf einer Exclude-Domain liegt."""
    for domain in EXCLUDE_DOMAINS:
        if url.startswith(f"http://{domain}") or url.startswith(f"https://{domain}"):
            return True
    return False


def load_packages() -> list[dict]:
    """Pakete von der CKAN API laden."""
    req = urllib.request.Request(API_URL, headers={"User-Agent": "opendata-zuerich-link-checker"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if not data.get("success"):
        print(f"ERROR: API returned success={data.get('success')}", file=sys.stderr)
        sys.exit(1)
    return data["result"]


def build_url_dataset_mapping(packages: list[dict]) -> dict[str, str]:
    """Mapping URL → Dataset Name aufbauen.

    resources[].url erhält Vorrang (präziser). URLs aus sszBemerkungen und notes
    bekommen den Dataset-Namen nur zugewiesen, wenn sie noch kein Mapping haben.
    """
    url_to_dataset: dict[str, str] = {}

    for pkg in packages:
        pkg_name = pkg.get("name", "")
        if not pkg_name:
            continue

        # 1. resources[].url — höchster Präzedenz (direkter Download-Link)
        for res in pkg.get("resources", []):
            url = res.get("url", "")
            if url and is_valid_url(url) and not is_excluded(url):
                url_to_dataset[url] = pkg_name

        # 2. sszBemerkungen — Markdown-Links
        text = pkg.get("sszBemerkungen", "")
        if text:
            for _text, url in MD_LINK_RE.findall(text):
                if is_valid_url(url) and not is_excluded(url) and url not in url_to_dataset:
                    url_to_dataset[url] = pkg_name

        # 3. notes — Fliesstext-URLs
        text = pkg.get("notes", "")
        if text:
            for url in PLAIN_URL_RE.findall(text):
                if is_valid_url(url) and not is_excluded(url) and url not in url_to_dataset:
                    url_to_dataset[url] = pkg_name

    return url_to_dataset


def main():
    print(f"Lade Pakete von {API_URL}", file=sys.stderr)
    packages = load_packages()
    print(f"Gefunden: {len(packages)} Pakete", file=sys.stderr)

    url_to_dataset = build_url_dataset_mapping(packages)

    # Mapping als JSON speichern (für Post-Prozessor)
    with open(MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(url_to_dataset, f, ensure_ascii=False, indent=2)
    print(f"URL-Dataset-Mapping geschrieben: {MAP_PATH} ({len(url_to_dataset)} Einträge)", file=sys.stderr)

    # Deduplizierte URL-Liste in .cache/catalog_urls.txt schreiben
    os.makedirs(".cache", exist_ok=True)
    all_urls = sorted(set(url_to_dataset.keys()))
    
    # URL-Liste (für Post-Prozessor)
    with open(URLS_PATH, "w", encoding="utf-8") as f:
        for url in all_urls:
            f.write(url + "\n")
    print(f"URL-Liste geschrieben: {URLS_PATH} ({len(all_urls)} URLs)", file=sys.stderr)

    # Lychee TOML-Config generieren
    config_lines = ["[include]"]
    for url in all_urls:
        config_lines.append(f'"{url}"')
    config_lines.append("")

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(config_lines))
    print(f"Lychee Config geschrieben: {CONFIG_PATH} ({len(all_urls)} Einträge)", file=sys.stderr)


if __name__ == "__main__":
    main()