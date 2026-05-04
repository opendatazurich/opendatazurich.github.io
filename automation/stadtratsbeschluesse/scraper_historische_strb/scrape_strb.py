"""
Scraper für Stadtratsbeschlüsse der Stadt Zürich vor dem offenen Datensatz
==========================================================================

Der offizielle Open-Data-Katalog enthält unter ``av_skz_strb_oe_datum``
alle öffentlichen Stadtratsbeschlüsse ab dem 18.02.2025. Dieses Skript
ergänzt die *älteren* Beschlüsse, indem es das JSON-Suchbackend der
Webseite ``stadtratsbeschluesse.html`` abfragt – dasselbe API, das die
Seite für ihre eigene Suche verwendet.

Vorgehen
--------
Anfragen werden pro Kalenderjahr segmentiert. Das hält die Offsets klein,
begrenzt den Re-Run-Radius bei Fehlern und macht den Prozess robust
gegenüber neu publizierten Beschlüssen (die sonst die Sortierung einer
Gesamt-Paginierung verschieben würden). Die Rohantwort jedes Jahres wird
als JSON-Datei abgelegt – das dient als Checkpoint: mit ``--skip-existing``
überspringt ein erneuter Lauf bereits heruntergeladene Jahre, und die
JSON-Dumps erlauben eine spätere erneute Auswertung ohne Netzwerkzugriff.

Ausgabe
-------
CSV, UTF-8 kodiert, Semikolon als Feldtrenner, Spaltenreihenfolge:

    Titel;Beschlussnummer;Beschlussdatum;Federführendes Departement

Das Beschlussdatum ist als ``DD.MM.YYYY`` formatiert. Die Spalte
„Federführendes Departement“ kann leer sein – das Suchbackend liefert sie
z. B. für Beschlüsse der Stadtkanzlei nicht immer mit. Deswegen werden
leere mit ``DEPARTEMENT_FALLBACK`` ersetzt. 

Nutzung
-------
    python scrape_strb.py --help

Beispiel (identisch zum Default):
    python scrape_strb.py --cutoff 2025-02-18 --start-year 2010 \
        --output stadtratsbeschluesse_vor_stichtag.csv --raw-dir raw
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, Iterator
from urllib.parse import urlencode


# --------------------------------------------------------------------------
# Konstanten
# --------------------------------------------------------------------------

API_URL = "https://www.stadt-zuerich.ch/stzh/search"

# Der Server unterscheidet intern nach "compResource", welche Suche gemeint
# ist – dieser Wert ist aus dem HTML der Seite stadtratsbeschluesse.html
# extrahiert und identifiziert die Beschluss-Suche.
COMP_RESOURCE = (
    "/content/web/de/politik-und-verwaltung/politik-und-recht/"
    "stadtratsbeschluesse/jcr:content/mainparsys/search"
)

# Das API liefert Seiten via ``limit`` + ``offset``. 1000 pro Seite wird
# ohne Probleme akzeptiert und reduziert die Anzahl der Requests deutlich.
PAGE_SIZE = 1000

# Höflicher User-Agent, damit Administrator*innen der Stadt Zürich den
# Traffic zuordnen können. Bitte bei Fork anpassen.
USER_AGENT = (
    "stadtratsbeschluesse-scraper/1.0 "
    "(+https://www.stadt-zuerich.ch/opendata)"
)

REQUEST_TIMEOUT = 30          # Sekunden
RETRY_ATTEMPTS = 5
RETRY_BACKOFF_BASE = 2.0      # exponentiell: base**attempt Sekunden

# Das Suchformular auf der Webseite erlaubt Daten ab dem 01.01.2010 –
# davor liegende Beschlüsse sind nicht öffentlich publiziert.
ARCHIVE_MIN_YEAR = 2010

# Erster Tag, den der offene Datensatz abdeckt. Dieses Skript scraped
# strikt Beschlüsse MIT Datum < CUTOFF, um Doppelerfassung zu vermeiden.
CUTOFF_DEFAULT = date(2025, 2, 18)

CSV_FIELDS = [
    "Titel",
    "Beschlussnummer",
    "Beschlussdatum",
    "Federführendes Departement",
]

log = logging.getLogger("strb_scraper")


# --------------------------------------------------------------------------
# Datentypen
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Beschluss:
    """Ein einzelner Stadtratsbeschluss in der Zielstruktur der CSV."""

    titel: str
    beschlussnummer: str       # Format "LAUF/JAHR", z. B. "1361/2026"
    beschlussdatum: date
    departement: str           # kann "" sein


# --------------------------------------------------------------------------
# HTTP-Client
# --------------------------------------------------------------------------


def _fetch_json(params: dict) -> dict:
    """Führt einen einzelnen GET-Request aus und gibt das JSON als Dict zurück.

    Bei transienten Fehlern (Netzwerk, Timeout, kaputtes JSON) wird bis zu
    ``RETRY_ATTEMPTS`` mal mit exponentiellem Backoff wiederholt. Bleibt
    der Fehler, wird ein ``RuntimeError`` geworfen.
    """
    url = f"{API_URL}?{urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    last_exc: Exception | None = None
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            if payload.get("error"):
                raise RuntimeError(f"API-Fehler: {payload!r}")
            return payload
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_exc = exc
            wait = RETRY_BACKOFF_BASE ** attempt
            log.warning(
                "Request fehlgeschlagen (Versuch %d/%d): %s – retry in %.1fs",
                attempt, RETRY_ATTEMPTS, exc, wait,
            )
            time.sleep(wait)

    raise RuntimeError(
        f"API-Request nach {RETRY_ATTEMPTS} Versuchen fehlgeschlagen: {last_exc}"
    )


def fetch_range(q_fd: date, q_td: date, sleep_seconds: float) -> dict:
    """Lädt alle Treffer im Datumsbereich [q_fd, q_td] (inklusiv).

    Paginiert intern mit ``limit=PAGE_SIZE`` über ``offset``, konkateniert
    die Einzelantworten und gibt die gesammelte Rohstruktur zurück::

        {
          "meta": {"total": <API-Gesamttreffer>,
                   "fetched": <tatsächlich geladen>,
                   "q_fd": "...", "q_td": "..."},
          "results": [ ... API-Items ... ]
        }
    """
    # Das API erwartet Datumsangaben ausschliesslich im Format DD.MM.YYYY;
    # ISO-Format liefert stillschweigend 0 Treffer.
    base = {
        "lang": "de",
        "compResource": COMP_RESOURCE,
        "q_dt": "beschlussDate",
        "q_fd": q_fd.strftime("%d.%m.%Y"),
        "q_td": q_td.strftime("%d.%m.%Y"),
        "limit": PAGE_SIZE,
    }

    all_results: list[dict] = []
    offset = 0
    total: int | None = None

    while True:
        params = {**base, "offset": offset}
        log.info("GET %s..%s offset=%d", q_fd, q_td, offset)
        data = _fetch_json(params)

        batch = data.get("results") or []
        all_results.extend(batch)
        total = data.get("meta", {}).get("total", len(all_results))

        # Abbruchkriterium: letzte Seite erreicht (entweder weniger als
        # PAGE_SIZE zurück, oder Summe ≥ Gesamttreffer laut meta).
        if len(batch) < PAGE_SIZE or len(all_results) >= total:
            break

        offset += PAGE_SIZE
        time.sleep(sleep_seconds)

    return {
        "meta": {
            "total": total,
            "fetched": len(all_results),
            "q_fd": q_fd.isoformat(),
            "q_td": q_td.isoformat(),
        },
        "results": all_results,
    }


# --------------------------------------------------------------------------
# Parser
# --------------------------------------------------------------------------

# Beispiele für das Feld ``topic``: "STRB Nr. 1361/2026" oder "STRB Nr.1361/2026".
_TOPIC_RE = re.compile(r"STRB\s*Nr\.?\s*(\d+)\s*/\s*(\d+)", re.IGNORECASE)

# Beschlussdatum steht im Feld ``meta`` in der Form "Beschlussdatum: 15.04.2026".
_BESCHLUSSDATUM_RE = re.compile(r"Beschlussdatum:\s*(\d{1,2}\.\d{1,2}\.\d{4})")

# Fallback-Departement: Das Suchbackend liefert für Stadtkanzlei-Beschlüsse
# keinen Departements-Eintrag im meta-Feld. Diese Beschlüsse werden hier
# dem Wert unten zugeordnet.
DEPARTEMENT_FALLBACK = "Stadtkanzlei (SKZ)"


def parse_result(item: dict) -> Beschluss | None:
    """Konvertiert einen API-Treffer in einen :class:`Beschluss`.

    Gibt ``None`` zurück, wenn essentielle Felder (STRB-Nr., Titel,
    Beschlussdatum) fehlen oder nicht geparst werden können – solche
    Einträge werden geloggt, aber nicht in die CSV aufgenommen.
    """
    titel = (item.get("heading") or "").strip()
    topic = item.get("topic") or ""
    meta_entries = item.get("meta") or []

    m = _TOPIC_RE.search(topic)
    if not m:
        log.warning("Kein STRB-Nr.-Match in topic=%r – übersprungen", topic)
        return None
    beschlussnummer = f"{m.group(1)}/{m.group(2)}"

    beschlussdatum: date | None = None
    departement = ""
    for raw_entry in meta_entries:
        entry = (raw_entry or "").strip()
        if not entry:
            continue
        dm = _BESCHLUSSDATUM_RE.search(entry)
        if dm:
            try:
                beschlussdatum = datetime.strptime(dm.group(1), "%d.%m.%Y").date()
            except ValueError:
                log.warning("Ungültiges Datum %r in STRB %s", dm.group(1), beschlussnummer)
        elif ":" in entry:
            # z. B. "Publikationsdatum: ..." – für dieses CSV nicht relevant.
            continue
        elif not departement:
            departement = entry

    if beschlussdatum is None:
        log.warning("Kein Beschlussdatum für STRB %s (meta=%r) – übersprungen",
                    beschlussnummer, meta_entries)
        return None
    if not titel:
        log.warning("Kein Titel für STRB %s – übersprungen", beschlussnummer)
        return None

    return Beschluss(
        titel=titel,
        beschlussnummer=beschlussnummer,
        beschlussdatum=beschlussdatum,
        departement=departement or DEPARTEMENT_FALLBACK,
    )


# --------------------------------------------------------------------------
# Orchestrierung
# --------------------------------------------------------------------------


def year_ranges(start_year: int, cutoff: date) -> list[tuple[date, date]]:
    """Liefert die Liste jährlicher [von, bis]-Bereiche bis exklusiv ``cutoff``.

    Das letzte Range wird bei Bedarf auf ``cutoff - 1 Tag`` gekürzt, damit
    der erste Tag des offenen Datensatzes nicht doppelt erfasst wird.
    """
    ranges: list[tuple[date, date]] = []
    for year in range(start_year, cutoff.year + 1):
        fd = date(year, 1, 1)
        td = min(date(year, 12, 31), cutoff - timedelta(days=1))
        if fd > td:
            break
        ranges.append((fd, td))
    return ranges


def scrape(
    start_year: int,
    cutoff: date,
    raw_dir: Path,
    sleep_seconds: float,
    skip_existing: bool,
) -> Iterator[Beschluss]:
    """Generator, der alle Beschlüsse im Zielzeitraum liefert.

    Pro Jahr wird zuerst geprüft, ob bereits ein Roh-JSON-Dump existiert.
    Falls ja und ``skip_existing`` gesetzt ist, wird dieser gelesen,
    ansonsten wird das Jahr neu aus dem API geladen und der Dump frisch
    geschrieben.

    Ergebnis-Deduplizierung erfolgt über die Beschlussnummer, Einträge mit
    Datum >= ``cutoff`` werden als Sicherheitsnetz herausgefiltert.
    """
    raw_dir.mkdir(parents=True, exist_ok=True)
    ranges = year_ranges(start_year, cutoff)
    if not ranges:
        log.warning("Kein Jahres-Range gefunden (start_year=%d, cutoff=%s).",
                    start_year, cutoff)
        return
    log.info("Plane %d Jahres-Ranges von %s bis %s",
             len(ranges), ranges[0][0], ranges[-1][1])

    seen_nummern: set[str] = set()
    for fd, td in ranges:
        raw_file = raw_dir / f"strb_{fd.year}.json"

        if skip_existing and raw_file.exists():
            log.info("Nutze bestehenden Checkpoint %s", raw_file.name)
            payload = json.loads(raw_file.read_text(encoding="utf-8"))
        else:
            payload = fetch_range(fd, td, sleep_seconds=sleep_seconds)
            raw_file.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            log.info(
                "%s: %d Treffer gespeichert (API-meta.total=%s)",
                raw_file.name, len(payload["results"]),
                payload["meta"].get("total"),
            )

        for item in payload["results"]:
            b = parse_result(item)
            if b is None:
                continue
            if b.beschlussdatum >= cutoff:
                # Sicherheitsnetz: sollte das API mal einen Randtag zu
                # viel zurückgeben, wird er hier zuverlässig verworfen.
                continue
            if b.beschlussnummer in seen_nummern:
                continue
            seen_nummern.add(b.beschlussnummer)
            yield b


# --------------------------------------------------------------------------
# CSV-Export
# --------------------------------------------------------------------------


def write_csv(path: Path, beschluesse: Iterable[Beschluss]) -> int:
    """Schreibt die Beschlüsse als UTF-8-CSV mit Semikolon-Trenner.

    Die Zeilen werden aufsteigend nach (Beschlussdatum, Beschlussnummer)
    sortiert, damit identische Eingaben reproduzierbar identische Dateien
    erzeugen.
    """
    items = sorted(
        beschluesse,
        key=lambda b: (b.beschlussdatum, b.beschlussnummer),
    )
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(CSV_FIELDS)
        for b in items:
            writer.writerow([
                b.titel,
                b.beschlussnummer,
                b.beschlussdatum.strftime("%d.%m.%Y"),
                b.departement,
            ])
    return len(items)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Ungültiges Datum {value!r}, erwartet YYYY-MM-DD"
        ) from exc


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Lädt öffentliche Stadtratsbeschlüsse der Stadt Zürich vor dem "
            "Stichtag des offenen Datensatzes (av_skz_strb_oe_datum) in eine "
            "CSV-Datei."
        ),
    )
    p.add_argument(
        "--cutoff",
        type=_parse_date,
        default=CUTOFF_DEFAULT,
        metavar="YYYY-MM-DD",
        help=(
            "Erster Tag, der NICHT mehr gescraped wird. Default: "
            f"{CUTOFF_DEFAULT.isoformat()} (Start des offenen Datensatzes)."
        ),
    )
    p.add_argument(
        "--start-year",
        type=int,
        default=ARCHIVE_MIN_YEAR,
        help=f"Erstes Kalenderjahr (Default: {ARCHIVE_MIN_YEAR}).",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=Path("stadtratsbeschluesse_vor_stichtag.csv"),
        help="Pfad der CSV-Ausgabedatei.",
    )
    p.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("raw"),
        help="Verzeichnis für die Roh-JSON-Checkpoints pro Jahr.",
    )
    p.add_argument(
        "--sleep",
        type=float,
        default=1.0,
        metavar="SEKUNDEN",
        help="Pause zwischen API-Calls (höflicher Client, Default: 1.0).",
    )
    p.add_argument(
        "--skip-existing",
        action="store_true",
        help="Bereits vorhandene Roh-JSON-Dumps nicht neu laden.",
    )
    p.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Ausführlicheres Logging (DEBUG).",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if args.cutoff <= date(args.start_year, 1, 1):
        log.error("Cutoff %s liegt vor start-year %d – nichts zu tun.",
                  args.cutoff, args.start_year)
        return 2

    beschluesse = list(scrape(
        start_year=args.start_year,
        cutoff=args.cutoff,
        raw_dir=args.raw_dir,
        sleep_seconds=args.sleep,
        skip_existing=args.skip_existing,
    ))
    count = write_csv(args.output, beschluesse)
    log.info("Fertig: %d Beschlüsse nach %s geschrieben.", count, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
