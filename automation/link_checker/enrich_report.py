"""
Post-Prozessor für Lychee-Report: Anreicherung mit Dataset-Namen.

Liest den Lychee-Markdown-Report (lychee/out.md), sucht nach URLs und
ersetzt sie mit der Form "URL (# dataset_name)". Das Mapping kommt aus
/tmp/url_dataset_map.json.

Ausgabe: Angereicherter Report auf stdout, überschreibt lychee/out.md.

Abhängigkeiten: Nur Python-Standardbibliothek.
"""

import json
import re
import sys

MAP_PATH = "/tmp/url_dataset_map.json"
OUTPUT_PATH = "lychee/out.md"

URL_RE = re.compile(r"(https?://[^\s)]+)")


def load_mapping() -> dict[str, str]:
    """Mapping URL → Dataset-Name laden."""
    try:
        with open(MAP_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"WARNING: Mapping-Datei nicht gefunden: {MAP_PATH}", file=sys.stderr)
        return {}


def enrich_line(line: str, url_to_dataset: dict[str, str]) -> str:
    """Eine Zeile des Reports nach URLs durchsuchen und mit Dataset-Namen anreichern."""
    if not URL_RE.search(line):
        return line

    def replace_url(match: re.Match) -> str:
        url = match.group(1)
        # Normalize: trailing punctuation entfernen (z.B. Klammern, Leerzeichen)
        clean_url = url.rstrip(")>,.;:!?'\"")
        dataset = url_to_dataset.get(clean_url)
        if dataset:
            return f"{clean_url} (# {dataset})"
        return url

    return URL_RE.sub(replace_url, line)


def main():
    url_to_dataset = load_mapping()
    print(f"Mapping geladen: {len(url_to_dataset)} Einträge", file=sys.stderr)

    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    enriched_lines = []
    for line in content.splitlines():
        enriched_lines.append(enrich_line(line, url_to_dataset))

    enriched_content = "\n".join(enriched_lines)

    # Angefertigter Report in Datei schreiben
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(enriched_content)

    print(f"Report angereichert: {OUTPUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()