"""
Brunnen Image Scraper
--------------------
Lädt Brunnen-Geodaten der Stadt Zürich, ermittelt zugehörige
Webseiten, scraped Bild-URLs und lädt optional die Bilder lokal herunter.
"""

from __future__ import annotations

import os
import logging
import zipfile
from urllib.parse import urlparse

import requests
import pandas as pd
from bs4 import BeautifulSoup


# ---------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------

BRUNNEN_WFS_URL = "https://www.ogd.stadt-zuerich.ch/wfs/geoportal/Brunnen?service=WFS&version=1.1.0&request=GetFeature&outputFormat=GeoJSON&typename=wvz_brunnen"

BRUNNEN_URL_PREFIX = "https://www.stadt-zuerich.ch/content/web/de/umwelt-und-energie/wasser/trinkwasser/brunnen/kreis"

OUTPUT_COLUMNS = ["brunnennummer","brunnen_webseite","foto_url"]

BASE_PATH = "automation/dib_wvz_brunnenfotos"

OUT_DIR = os.path.join(BASE_PATH,"fotos")
CSV_OUT = os.path.join(BASE_PATH, "brunnen_webseite_url.csv")
ZIP_OUT = os.path.join(BASE_PATH, "fotos.zip")


# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Datenaufbereitung
# ---------------------------------------------------------------------

def load_brunnen_data(url: str) -> pd.DataFrame:
    """Lädt Brunnen-Geodaten als Pandas DataFrame.
    Geopandas wird hier mit Absicht nicht verwendet, 
    da die Geometrie nicht gebraucht wird und so die 
    Dependency eingespart werden kann.
    """
    logger.info("Lade Brunnen-Geodaten")

    # falls geopandas vorhanden ist:
    # return gpd.read_file(url)
    
    r = requests.get(url)
    data = r.json()

    df = pd.DataFrame([f["properties"] for f in data["features"]])
    
    return df


def build_brunnen_webseiten(df: pd.DataFrame) -> pd.DataFrame:
    """
    Erzeugt die Brunnen-Webseiten-URLs anhand von Stadtkreis
    und Brunnennummer.
    """
    df = df.copy()

    df["brunnen_webseite"] = (
        BRUNNEN_URL_PREFIX
        + df["stadtkreis"].astype(str)
        + "/"
        + df["brunnennummer"].str.replace(".", "_", regex=False)
    )

    df.loc[df["brunnennummer"].isna(), "brunnen_webseite"] = pd.NA

    logger.info("Brunnen-Webseiten erzeugt")
    return df


# ---------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------

def get_image_url(page_url: str) -> str | None:
    """
    Scrapt die URL des zweiten Brunnen-Bildes (Detailbild)
    von einer stadt-zuerich.ch Brunnen-Seite.
    
    Returns die absolute Bild-URL oder None bei Fehler.
    """
    try:
        resp = requests.get(page_url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        imgs = soup.find_all("img")
        # Index 0: Logo, Index 1: erstes Brunnenbild (pageimage, gross)
        # Index 2: zweites Brunnenbild (texttitleimage, 876px)
        if len(imgs) >= 3:
            src = imgs[1].get("src")
            if src and src.startswith("/"):
                src = "https://www.stadt-zuerich.ch" + src
            return src
    except Exception as e:
        logger.warning("Scraping fehlgeschlagen (%s): %s", page_url, e)
    return None



def scrape_image_urls(df: pd.DataFrame, url_col: str) -> pd.DataFrame:
    """
    Fügt dem DataFrame eine neue Spalte 'foto_url'
    mit dem zweiten Brunnenbild jeder Seite hinzu.
    """
    df = df.copy()
    logger.info("Scrape Bild-URLs")
    df["foto_url"] = df[url_col].apply(get_image_url)
    return df


# ---------------------------------------------------------------------
# Download & Archivierung
# ---------------------------------------------------------------------

def download_images(
    df: pd.DataFrame,
    url_col: str = "foto_url",
    out_dir: str = OUT_DIR,
    filename_col: str | None = "brunnennummer",
    timeout: int = 15,
) -> None:
    """
    Lädt Bilder aus einer URL-Spalte eines DataFrames herunter
    und speichert sie lokal.
    """
    os.makedirs(out_dir, exist_ok=True)

    for _, row in df.iterrows():
        img_url = row.get(url_col)

        if not img_url or pd.isna(img_url):
            continue

        try:
            resp = requests.get(img_url, timeout=timeout)
            resp.raise_for_status()

            if filename_col and pd.notna(row.get(filename_col)):
                safe_name = str(row[filename_col]).replace(".", "_").replace("/", "_")
                ext = os.path.splitext(urlparse(img_url).path)[1]
                filename = f"{safe_name}{ext}"
            else:
                filename = os.path.basename(urlparse(img_url).path)

            file_path = os.path.join(out_dir, filename)

            with open(file_path, "wb") as f:
                f.write(resp.content)

        except Exception as exc:
            logger.error("Download fehlgeschlagen (%s): %s", img_url, exc)


def zip_images(
    img_dir: str,
    zip_path: str,
    include_subdirs: bool = False,
) -> None:
    """Packt alle Bilder eines Verzeichnisses in eine ZIP-Datei."""
    logger.info("Erstelle ZIP-Archiv: %s", zip_path)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        if include_subdirs:
            for root, _, files in os.walk(img_dir):
                for file in files:
                    path = os.path.join(root, file)
                    zipf.write(path, os.path.relpath(path, img_dir))
        else:
            for file in os.listdir(img_dir):
                path = os.path.join(img_dir, file)
                if os.path.isfile(path):
                    zipf.write(path, arcname=file)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:
    brunnen = load_brunnen_data(BRUNNEN_WFS_URL)
    brunnen = build_brunnen_webseiten(brunnen)
    brunnen = scrape_image_urls(brunnen, "brunnen_webseite")

    na = int(brunnen["foto_url"].isna().sum())
    total = len(brunnen)
    logger.info(
        "Fehlende Bild-URLs: %d von %d (%.1f%%)",
        na,
        total,
        na / total * 100,
    )
    os.makedirs(BASE_PATH, exist_ok=True)
    brunnen[OUTPUT_COLUMNS].to_csv(CSV_OUT, index=False)
    logger.info("CSV gespeichert: %s", CSV_OUT)

    # falls man die Bilder herunterladen und zippen möchte
    # download_images(brunnen)
    # zip_images(OUT_DIR, ZIP_OUT)


if __name__ == "__main__":
    main()