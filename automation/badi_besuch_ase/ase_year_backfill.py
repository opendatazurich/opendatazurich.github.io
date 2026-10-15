import os

import ase_helper_functions as ase
import ase_parameters as ase_p

from dotenv import load_dotenv


# base url + token url
url = ase_p.BASE_URL
token_url = ase_p.TOKEN_URL

# Backfill-Einstellungen
local_execution = ase_p.LOCAL_EXECUTION
granularity = ase_p.BACKFILL_GRANULARITY
backfill_write_parquet = ase_p.BACKFILL_WRITE_PARQUET
backfill_write_csv = ase_p.BACKFILL_WRITE_CSV
backfill_start_date_param = ase_p.BACKFILL_START_DATE
backfill_end_date_param = ase_p.BACKFILL_END_DATE


# env laden
load_dotenv(verbose=True)
ASE_USERNAME = os.getenv('ASE_USERNAME')
ASE_PASSWORD = os.getenv('ASE_PASSWORD')
PROXYUSER = os.getenv('PROXYUSER_STREETDIRECTORY')
PROXYPASSWORD = os.getenv('PROXYPASSWORD_STREETDIRECTORY')
BACKFILL_YEAR = os.getenv('BACKFILL_YEAR') or None
BACKFILL_START = os.getenv('BACKFILL_START') or None
BACKFILL_END = os.getenv('BACKFILL_END') or None

# Zielzeitraum bestimmen (Default Vorjahr, optional per BACKFILL_YEAR oder beliebigem Fenster).
# Env-Überschreibung hat Priorität vor den Params; Start/Ende schlägt BACKFILL_YEAR.
start_override = BACKFILL_START if BACKFILL_START is not None else backfill_start_date_param
end_override = BACKFILL_END if BACKFILL_END is not None else backfill_end_date_param
backfill_start, backfill_end, backfill_year = ase.get_target_backfill_range(
    BACKFILL_YEAR, start_override=start_override, end_override=end_override
)
windows = ase.compute_backfill_windows(
    backfill_start, backfill_end, granularity, ase_p.GRANULARITY_RANGE
)
print(
    f"Backfill Zeitraum: {backfill_start} -> {backfill_end} "
    f"in {len(windows)} Fenster (Granularität: {granularity}, Jahr: {backfill_year})"
)


# Auth-Payload
payload = {
    'username': ASE_USERNAME,
    'password': ASE_PASSWORD,
    'grant_type': 'password',
    'client_id': 'arlas-api',
}

if local_execution:
    proxies = {
        'http': f'http://{PROXYUSER}:{PROXYPASSWORD}@proxy.szh.loc:8080',
        'https': f'http://{PROXYUSER}:{PROXYPASSWORD}@proxy.szh.loc:8080',
    }
    verify = False
    print(f"Using parameters for LOCAL_EXECUTION = {local_execution} (Proxy user = {PROXYUSER}, Verify requests = {verify})")
else:
    proxies = None
    verify = True


# Auth-Header holen
ase_headers = ase.get_auth_header(token_url, payload, proxies=proxies, verify=verify)

# Locations holen, Suffix entfernen
location_df = ase.get_location_names_by_type(url, location_type="Mall", headers=ase_headers, proxies=proxies, verify=verify, filter_locations=ase_p.VALID_LOCATIONS)
location_df["LocalName"] = ase.replace_suffix(location_df["LocalName"], ase_p.SUFFIX_TO_REMOVE)

# fensterweiser Download + Merge über das ganze Intervall
badi_counter = ase.download_and_merge_badi_counter_windowed(url, location_df, windows, granularity, headers=ase_headers, proxies=proxies, verify=verify)
badi_counter["LocationName"] = ase.replace_suffix(badi_counter["LocationName"], ase_p.SUFFIX_TO_REMOVE)

# Ziel-Dateinamen + Pfade (neben diesem Skript)
parquet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ase_p.BACKFILL_PARQUET_NAME.replace("{year}", str(backfill_year)))
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ase_p.BACKFILL_CSV_NAME.replace("{year}", str(backfill_year)))
ase.export_result(badi_counter, parquet_path=parquet_path, csv_path=csv_path, write_parquet=backfill_write_parquet, write_csv=backfill_write_csv)
