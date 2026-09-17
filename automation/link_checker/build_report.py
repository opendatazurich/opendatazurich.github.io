"""
Baut einen Markdown-Report aus Lychees JSON-Output, gruppiert nach Dataset.

Eingabe:
  - lychee/out.json              : Lychee JSON-Report (--format json)
  - .cache/url_dataset_map.json  : Mapping URL → Dataset-Name

Ausgabe:
  - lychee/out.md                : Markdown-Report für Issue-Body

Statt Text-Ersetzung im Markdown (fragil) wird der Report direkt aus dem
strukturierten JSON gebaut — Fehler sind sauber nach Dataset gruppiert.

Abhängigkeiten: Nur Python-Standardbibliothek.
"""

import json
import sys
from collections import defaultdict

LYCHEE_JSON = "lychee/out.json"
MAP_PATH = ".cache/url_dataset_map.json"
OUTPUT_PATH = "lychee/out.md"


def format_status(status) -> str:
    """Lychee-Status (string oder dict) in kompakte Form bringen."""
    if isinstance(status, str):
        return status
    if isinstance(status, dict):
        if "code" in status:
            code = status["code"]
            text = status.get("text")
            return f"HTTP {code}" + (f" {text}" if text else "")
        if len(status) == 1:
            key, val = next(iter(status.items()))
            if val in (None, ""):
                return key
            if isinstance(val, dict):
                if "code" in val:
                    return f"{key} {val['code']}"
                if "message" in val:
                    return f"{key}: {val['message']}"
            return f"{key}: {val}"
    return str(status)


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    try:
        report = load_json(LYCHEE_JSON)
    except FileNotFoundError:
        print(f"ERROR: {LYCHEE_JSON} nicht gefunden - ist Lychee gelaufen?", file=sys.stderr)
        sys.exit(1)

    try:
        url_to_dataset = load_json(MAP_PATH)
    except FileNotFoundError:
        print(f"WARN: {MAP_PATH} nicht gefunden - Dataset-Namen fehlen", file=sys.stderr)
        url_to_dataset = {}

    total = report.get("total", 0)
    errors = report.get("errors", 0)
    timeouts = report.get("timeouts", 0)
    error_map = report.get("error_map", {}) or {}

    # Fehler nach Dataset gruppieren
    by_dataset: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for entries in error_map.values():
        for entry in entries:
            url = entry.get("url", "")
            dataset = url_to_dataset.get(url, "(unbekannter Datensatz)")
            status = format_status(entry.get("status"))
            by_dataset[dataset].append((url, status))

    lines: list[str] = []
    lines.append("# Link Checker Report (Catalog)")
    lines.append("")
    lines.append(
        f"**{errors + timeouts} fehlerhafte URLs** von {total} geprüft "
        f"— aus {len(by_dataset)} Datensätzen."
    )
    lines.append("")

    if not by_dataset:
        lines.append("Keine Fehler gefunden. ✅")
    else:
        for dataset in sorted(by_dataset):
            lines.append(f"## {dataset}")
            lines.append("")
            for url, status in sorted(by_dataset[dataset]):
                lines.append(f"- `{status}` {url}")
            lines.append("")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(
        f"Report geschrieben: {OUTPUT_PATH} "
        f"({errors + timeouts} Fehler, {len(by_dataset)} Datensätze)",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
