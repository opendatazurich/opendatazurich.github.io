# Plan: Link-Checker CKAN-Katalog-Erweiterung

## Überblick

Der bestehende `link_checker.yml` Workflow wird um einen zweiten Job `linkCheckerCatalog` erweitert, der den Open-Data-Katalog der Stadt Zürich auf tote Links prüft.

## Dateien

| Datei | Aktion |
|---|---|
| `automation/link_checker/PLAN.md` | Neu — diese Spezifikation |
| `automation/link_checker/check_catalog_urls.py` | Neu — Python-Skript für URL-Extraktion |
| `.github/workflows/link_checker.yml` | Modify — neuer Job `linkCheckerCatalog` |

Später: `automation/link_checker/README.md` (Beschreibung des gesamten Workflows)

---

## Job-Struktur

```
Job 1: linkChecker (bestehend)     → Repo-Dateien, Issue: "Link Checker Report"
Job 2: linkCheckerCatalog (neu)    → CKAN-Katalog-URLs, Issue: "Link Checker Report (Catalog)"
```

---

## Job 2 — Detail

**Trigger:** Nur `workflow_dispatch` (manuelles Auslösen). Kein CRON.

**Steps:**

```
1. checkout@v6
2. Python-Setup (uv oder pip)
3. URL-Extraktion: python check_catalog_urls.py
   → /tmp/catalog_urls.txt (dedupliziert, sortiert)
4. Lychee: lycheeverse/lychee-action@v2
   → args: --accept '200..=204, 429, 403, 500'
           --max-retries 5 --retry-wait-time 5
           --suggest . --max-concurrency 10
           @/tmp/catalog_urls.txt
   → fail: false
5. Create Issue From File (peter-evans/create-issue-from-file@v5)
   → title: "Link Checker Report (Catalog)"
   → labels: report, automated issue, catalog
```

---

## Python-Skript: `check_catalog_urls.py`

**Pfad:** `automation/link_checker/check_catalog_urls.py`

**Eingabe:**
- API: `https://data.stadt-zuerich.ch/api/3/action/current_package_list_with_resources?limit=9999`

**URL-Extraktion aus drei Quellen:**

1. **`result[].resources[].url`** — Alle direkten Download/API-Endpunkte
2. **`result[].sszBemerkungen`** — Regex `\[([^\]]*)\]\((https?://[^)]+)\)` für Markdown-Links
3. **`result[].notes`** — Regex `https?://[^\s\)\"\'\>\]]+` für URLs im Fliesstext

**Filter:**
- Nur `http://` und `https://` URLs
- Keine `javascript:`, `data:`, oder leere URLs
- Deduplizierung via `set()`
- Optional: Exclude `data.integ.stadt-zuerich.ch/*`

**Ausgabe:**
- Eine URL pro Zeile in `/tmp/catalog_urls.txt`
- Log-Ausgabe: Anzahl extrahierte URLs, Quelle pro Quelle

**Abhängigkeiten:** Nur Standardbibliothek (`json`, `re`, `urllib.request`/`httpx`) — keine externen Pakete.

---

## Rate-Limiting

- `--max-concurrency 10` (Lychee)
- `--max-retries 5 --retry-wait-time 5` (für 429/503)
- Optional: `--exclude` für problematische Domains falls nötig

## Externe URLs

- **Geocat.ch, gis.stadt-zuerich.ch:** Werden mitgeprüft (kein Exclude). Occasional 4xx sind akzeptiert und werden im Issue sichtbar.
- **WMS/WFS/WMTS:** Werden mitgeprüft. Geben i.d.R. 200 → kein False-Positive-Risiko.

---

## Entscheidungen

| # | Punkt | Entscheidung |
|---|---|---|
| 1 | `notes`-Feld | Drinlassen |
| 2 | Geocat / gis.stadt-zuerich.ch | Drinlassen, Deduplizierung |
| 3 | WMS/WFS/WMTS | Drinlassen |
| 4 | Schedule | Nur `workflow_dispatch` |
| 5 | Issues | Separat |
| 6 | Skript-Pfad | `automation/link_checker/check_catalog_urls.py` |