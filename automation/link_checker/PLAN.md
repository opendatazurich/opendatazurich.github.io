# Plan: Link-Checker CKAN-Katalog-Erweiterung

## Überblick

Der Workflow `link_checker.yml` hat zwei Jobs:

| Job | Zweck | Issue-Titel |
|---|---|---|
| `linkChecker` | Prüft URLs in Repo-Dateien direkt via lychee-action | Link Checker Report |
| `linkCheckerCatalog` | Prüft URLs aus dem CKAN-Open-Data-Katalog | Link Checker Report (Catalog) |

Trigger: `workflow_dispatch` (manuell) und `repository_dispatch`. Kein CRON aktiv.

## Katalog-Pipeline

```
┌─────────────────────────┐
│ check_catalog_urls.py   │  CKAN-API → URL-Liste + URL→Dataset-Mapping
└──────────┬──────────────┘
           │  .cache/catalog_urls.txt
           │  .cache/url_dataset_map.json
           ▼
┌─────────────────────────┐
│ lychee (JSON-Output)    │  prüft URLs, schreibt strukturiertes JSON
└──────────┬──────────────┘
           │  lychee/out.json
           ▼
┌─────────────────────────┐
│ build_report.py         │  JSON + Mapping → Markdown gruppiert nach Dataset
└──────────┬──────────────┘
           │  lychee/out.md
           ▼
┌─────────────────────────┐
│ create-issue-from-file  │  Issue nur wenn Fehler (exit_code != 0)
└─────────────────────────┘
```

## Dateien

| Datei | Zweck |
|---|---|
| `automation/link_checker/check_catalog_urls.py` | URL-Extraktion aus CKAN |
| `automation/link_checker/build_report.py` | Report-Aufbau aus Lychee-JSON |
| `automation/link_checker/PLAN.md` | Diese Spezifikation |
| `.github/workflows/link_checker.yml` | Workflow-Definition |

## URL-Quellen

Aus jedem CKAN-Paket werden URLs extrahiert aus:

1. **`resources[].url`** — direkte Download/API-Endpunkte (Vorrang beim Dataset-Mapping)
2. **`sszBemerkungen`** — Markdown-Links `[text](url)`
3. **`notes`** — URLs im Fliesstext

Filter: nur `http://`/`https://`, dedupliziert. `data.integ.stadt-zuerich.ch` wird ausgeschlossen (SSL-Probleme).

## Design-Entscheidungen

| Punkt | Entscheidung | Grund |
|---|---|---|
| Lychee-Input | URL-Liste als Textdatei (positional) | Lychee scannt Textdateien nach URLs — kein TOML nötig |
| Dataset-Anreicherung | Report aus Lychee-JSON neu bauen | Robust; keine Regex-Ersetzung im Markdown |
| Mapping-Speicherort | `.cache/url_dataset_map.json` | Konsistent mit URL-Liste (nicht `/tmp/`) |
| Issue-Erstellung | Nur bei `exit_code != 0` | Kein Rauschen bei erfolgreichen Runs |
| Externe URLs (Geocat, gis, WMS/WFS) | Mitgeprüft | 4xx im Report akzeptiert |
| Akzeptierte Status | `200-204, 403, 429, 500` | 403/429/500 sind oft Rate-Limits/Fingerprinting, keine echten Fehler |
| Rate-Limiting | `--max-concurrency 10`, `--max-retries 5 --retry-wait-time 5` | Schonend, tolerant gegenüber 429 |
