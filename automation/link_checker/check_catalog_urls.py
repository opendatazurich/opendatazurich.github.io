"""
URL-Extraktion aus dem Open Data Katalog der Stadt Zürich (CKAN API).

Liest alle Datensätze inkl. Ressourcen über die CKAN API und extrahiert URLs
aus drei Quellen:
  1. resources[].url          — direkte Download/API-Endpunkte
  2. sszBemerkungen           — Markdown-Links [text](url)
  3. notes                    — URLs im Fliesstext

Ausgabe:
  - stdout: deduplizierte, sortierte URL-Liste pro Zeile
  - /tmp/lychee_catalog_config.yaml: Lychee [include]-Config mit URL → Dataset-Namen Mapping

Abhängigkeiten: Nur Python-Standardbibliothek.
"""

import json
import re
import sys
import urllib.request

API_URL = "https://data.stadt-zuerich.ch/api/3/action/current_package_list_with_resources?limit=9999"
CONFIG_PATH = "/tmp/lychee_catalog_config.yaml"

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


def write_lychee_config(url_to_dataset: dict[str, str], config_path: str) -> None:
    """Lychee TOML-Config schreiben.

    Format:
      [include]
        "https://example.com/data.csv" = "geo_abstimmungsgeraete_taz"
        "https://example.com/image.png" = "geo_erholungs__und_sporteinrichtungen"

    Lychee zeigt dann im Markdown-Report "URL # Label" an.
    """
    lines = ["[include]"]
    for url in sorted(url_to_dataset.keys()):
        lines.append(f'"{url}" = "{url_to_dataset[url]}"')
    lines.append("")

    with open(config_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Lychee Config geschrieben: {config_path} ({len(url_to_dataset)} Einträge)", file=sys.stderr)


def main():
    print(f"Lade Pakete von {API_URL}", file=sys.stderr)
    packages = load_packages()
    print(f"Gefunden: {len(packages)} Pakete", file=sys.stderr)

    url_to_dataset = build_url_dataset_mapping(packages)

    write_lychee_config(url_to_dataset, CONFIG_PATH)

    # Deduplizierte URL-Liste auf stdout
    all_urls = set(url_to_dataset.keys())
    print(f"Ausgabe: {len(all_urls)} eindeutige URLs", file=sys.stderr)
    for url in sorted(all_urls):
        print(url)


if __name__ == "__main__":
    main()