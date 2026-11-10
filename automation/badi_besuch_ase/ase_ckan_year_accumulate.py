#!/usr/bin/env python3
"""Jahres-Akkumulator für Badi Besuch (ASE) aus CKAN.

Lädt die bestehende Jahressource (Parquet) und die frische 5-Tage-Datei (CSV)
aus dem CKAN-Datensatz zusammen, entfernt Dubletten, filtert auf das laufende
Jahr und schreibt das Ergebnis zurück als Parquet + CSV. Die Dateien werden
danach vom Workflow in CKAN überschrieben (resource_patch).

Es werden keine Calls an die ASE-API gemacht - die frischen Daten kommen aus
der vom Live-Feed gepflegten 5-Tage-CSV im CKAN.
"""

import os
import sys
import requests
import pandas as pd
from dotenv import load_dotenv
from ckanapi import RemoteCKAN

load_dotenv()

CKAN_DATASET = "ssd_spo_badi_besuch"
CANONICAL_COLS = ["LocationId", "LocationName", "Datetime", "InCount", "OutCount", "OccupancyMax"]
CSV_FALLBACK_NAME = "badi_besuch.csv"


def download_resource(session, url, out_path):
    """Lädt eine CKAN-Ressource herunter und speichert sie lokal.

    :param session: requests.Session mit SSL-Konfiguration aus der Umgebung
    :param url: Download-URL der Ressource
    :param out_path: lokaler Pfad, in den die Datei geschrieben wird
    """
    with requests.get(url, stream=True, timeout=300) as resp:
        resp.raise_for_status()
        with open(out_path, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=65536):
                if chunk:
                    fh.write(chunk)


def find_year_parquet(resources, year):
    """Gibt die Parquet-Ressource des Zieljahres zurück oder None.

    Passt auf Namen im Format ``Badi_Besuch_<year>.parquet`` (case-insensitive).
    None bei fehlendem Namen, z.B. im ersten Jahr eines neuen Kalenderjahrs.

    :param resources: Liste der Ressource-Dicts aus einer package_show
    :param year: Zieljahr (int)
    :return: passende Ressource-Diktionairy oder None
    """
    year_str = str(year)
    matches = [
        r
        for r in resources
        if r.get("name", "").lower().startswith("badi_besuch_")
        and r.get("name", "").lower().endswith(".parquet")
        and year_str in r.get("name", "").lower()
    ]
    return matches[0] if matches else None


def find_five_day_csv(resources):
    """Gibt die 5-Tage-Live-Feed-Ressource (``badi_besuch.csv``) zurück.

    :param resources: Liste der Ressource-Dicts aus einer package_show
    :return: passende Ressource-Diktionairy oder None
    """
    matches = [r for r in resources if r.get("name", "").lower().endswith(CSV_FALLBACK_NAME)]
    return matches[0] if matches else None


def load_frame(path):
    """Lädt eine Datei in ein DataFrame (Parquet oder CSV).

    Bei fehlender Datei wird ein leeres DataFrame mit den kanonischen Spalten zurückgegeben.

    :param path: Pfad zu einer .parquet- oder .csv-Datei
    :return: DataFrame (leer, wenn die Datei nicht existiert)
    """
    if not os.path.exists(path):
        return pd.DataFrame(columns=CANONICAL_COLS)
    if path.lower().endswith(".parquet"):
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path)
    return df


def normalize(df):
    """Macht ein Badi-Counter-DataFrame passend zur Jahresdatei.

    Wandelt ``Datetime`` in datetime64 um, konvertiert die Zähl-Spalten in
    numerische Werte und beschränkt auf die kanonischen Spalten in der
    erwarteten Reihenfolge.

    :param df: Eingabe-DataFrame
    :return: kanonisiertes DataFrame mit den kanonischen Spalten
    """
    df = df.copy()
    df["Datetime"] = pd.to_datetime(df["Datetime"], errors="coerce")
    df = df.dropna(subset=["Datetime"])
    for col in ["InCount", "OutCount", "OccupancyMax"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[[c for c in CANONICAL_COLS if c in df.columns]]
    return df


def session_from_ssl():
    """Erstellt eine requests.Session je nach SSL-Konfiguration.

    ``SSL_VERIFY=true`` verifiziert Zertifikate, ``SSL_VERIFY=false``
    deaktiviert die Verifizierung, sonst gilt der requests-Standard.

    :return: konfiguriertes requests.Session
    """
    session = requests.Session()
    ssl = os.getenv("SSL_VERIFY")
    if ssl == "true":
        session.verify = True
    elif ssl == "false":
        session.verify = False
    return session


def main():
    """Baut den Jahres-Akkumulator aus CKAN und schreibt ihn zurück.

    Lädt die bestehende Jahressource (Parquet = Akkumulator) und die frische
    5-Tage-CSV zusammen, dedupliziert sie, filtert auf das laufende Jahr und
    schreibt das Ergebnis als ``Badi_Besuch_<year>.csv`` + ``.parquet`` neben
    dieses Skript. Es werden keine ASE-API-Calls gemacht.
    """
    year = int(pd.Timestamp.now().strftime("%Y"))
    session = session_from_ssl()
    print("CKAN-Instanz:", os.getenv("CKAN_BASE_URL"))
    ckan = RemoteCKAN(os.getenv("CKAN_BASE_URL"), session=session, apikey=os.getenv("CKAN_API_KEY"))

    print("Dataset:", CKAN_DATASET)
    pkg = ckan.call_action("package_show", {"id": CKAN_DATASET})
    resources = pkg["resources"]

    year_res = find_year_parquet(resources, year)
    five_res = find_five_day_csv(resources)
    if not five_res:
        print(f"5-Tage-CSV-Ressource ({CSV_FALLBACK_NAME}) nicht im Datensatz gefunden.", file=sys.stderr)
        sys.exit(1)

    out_dir = os.path.dirname(os.path.abspath(__file__))
    year_csv_path = os.path.join(out_dir, f"Badi_Besuch_{year}.csv")
    year_parquet_path = os.path.join(out_dir, f"Badi_Besuch_{year}.parquet")

    print(f"Jahr: {year}")
    print(f"Jahressource (Parquet): {year_res.get('name') if year_res else 'keine -> leerer Start'}")
    print(f"5-Tage-Ressource (CSV): {five_res.get('name')}")

    tmp_dir = os.path.join(out_dir, ".tmp_accumulate")
    os.makedirs(tmp_dir, exist_ok=True)

    full_df = pd.DataFrame(columns=CANONICAL_COLS)
    if year_res:
        tmp_parquet = os.path.join(tmp_dir, f"year_{year}.parquet")
        print(f"Lade Akkumulator {year_res.get('name')} ...")
        download_resource(session, year_res["url"], tmp_parquet)
        full_df = load_frame(tmp_parquet)
        print(f"Akkumulator Zeilen: {len(full_df)}")

    tmp_csv = os.path.join(tmp_dir, f"five_{year}.csv")
    print(f"Lade 5-Tage-CSV {five_res.get('name')} ...")
    download_resource(session, five_res["url"], tmp_csv)
    fresh_df = load_frame(tmp_csv)
    print(f"5-Tage Zeilen: {len(fresh_df)}")

    combined = pd.concat([full_df, fresh_df], ignore_index=True, axis=0)
    combined = normalize(combined)
    combined = combined[combined["Datetime"].dt.year == year]
    combined = combined.drop_duplicates(subset=["LocationId", "LocationName", "Datetime"])
    combined = combined.sort_values("Datetime").reset_index(drop=True)
    combined = combined[[c for c in CANONICAL_COLS if c in combined.columns]]

    print(f"Gekoppelt, dedupliziert & auf {year} gefiltert: {len(combined)} Zeilen")

    combined.to_csv(year_csv_path, index=False)
    combined.to_parquet(year_parquet_path, index=False)
    print(f"Geschrieben: {year_csv_path}")
    print(f"Geschrieben: {year_parquet_path}")


if __name__ == "__main__":
    main()
