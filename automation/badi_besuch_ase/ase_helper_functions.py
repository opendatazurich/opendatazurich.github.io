import re
import requests
import pandas as pd
from datetime import datetime, timedelta

# Documentation:https://zuerich.pas.ch/v2/swagger/index.html
# functions

def get_auth_header(url, payload, proxies, verify):
    response = requests.post(url, data=payload, 
                            proxies=proxies, 
                            verify=verify)
    if response.status_code != 200:
        raise Exception(f"Failed to authenticate: {response.status_code} | {response.text}")

    token = response.json().get('access_token')
    headers = {"Authorization": "Bearer " + token}

    return headers

def get_location_names_by_type(url, location_type, headers, proxies, verify, filter_locations=[]):
    # hole location names aus der Schnittstelle als Grundlage für spätere Abfraagen
    response = requests.get(url + f"/v2/api/Location?%24top=500&%24filter=Type%20eq%20%27{location_type}%27", headers=headers, proxies=proxies, verify=verify)
    location_json = response.json()['value']
    location_df = pd.DataFrame.from_dict(location_json, orient='columns')
    if filter_locations:
        location_df = location_df[location_df["LocalName"].isin(filter_locations)]
    required_location_names = location_df["LocalName"].unique()


    return location_df

def export_locations(location_df, export_filepath):
    """
    Locations get exported as csv. This function makes the data preparation,
    renaming, filtering and export
    
    :param location_df: dataframe with locations and coordinates
    :param export_filepath: filepath and name
    """

    location_cols = ["Id", "LocalName", "Lat", "Lon"] #, "GlobalName"
    location_df_csv = location_df[location_cols].rename(columns={"Id": "LocationId"})
    location_df_csv.to_csv(export_filepath, index=False)
    print("Exported locations to:", export_filepath)


def get_location_data_by_endpoint(
        url,
        headers,
        proxies,
        verify,
        location_df, 
        endpoint, 
        start_date, 
        end_date, 
        granularity, 
        aggregation_string,

    ):

    count = pd.DataFrame()
    required_location_names = location_df["LocalName"].unique()
    for location_name in required_location_names:
        print("-"*100)
        print(location_name)
        final_df = pd.DataFrame()
        # Fetch the locationid for the required location
        location_id = location_df.loc[location_df["LocalName"]==location_name, 'Id'].values[0]
        # Fetch the count for the required location. 
        count_url = url + "/v2/api/"+ endpoint +"/" + location_id + "?$filter=DateId gt " + str(start_date) + " and DateId le " + str(end_date) + " and Granularity eq '" + granularity + "'" + aggregation_string
        #print(count_url)
        

        count_json = {'@odata.nextLink': count_url}
        while '@odata.nextLink' in count_json:
            print('url: ' + count_json['@odata.nextLink'])
            count_url = count_json['@odata.nextLink']
            response = requests.get(count_url, headers=headers, proxies=proxies, verify=verify)
            # Leere Body / Non-JSON-Response (z.B. Throttling, 204 oder leerer Aggregat-Ergebnis) -> keine Records, Pagination beenden
            if not response.ok or not response.content:
                count_json = {}
                continue
            try:
                count_json = response.json()
            except Exception:
                count_json = {}
                continue
            # Records liegen typischerweise unter ["value"]; bei einer reinen Liste wird die Liste direkt verwendet
            records = count_json["value"] if isinstance(count_json, dict) and "value" in count_json else count_json
            df = pd.DataFrame.from_dict(records, orient="columns") if records else pd.DataFrame()
            final_df = pd.concat([final_df, df], ignore_index=True, axis=0)
        # The result might contain multiple locationIds as each sensor/location can have multiple sub-locations/measureitems
        final_df["LocationName"] = location_name
        final_df["LocationId"] = location_id
        print("Number of rows and columns:", final_df.shape)
        count = pd.concat([count, final_df], ignore_index=True, axis=0)

    if not count.empty and {"DateId", "TimeId"}.issubset(count.columns):
        count = count.sort_values(["LocationName", "DateId", "TimeId"])
        count = format_timestamp(count)
        print("Data from", count["Datetime"].min(), " to ", count["Datetime"].max())
        print(count)
    else:
        # Kein Datenfenster fuer diesen Endpoint (z.B. leere Belegung): Frame mit Standard-Spalten, aber 0 Zeilen zurueck,
        # damit die nachfolgenden Drops/Merges in download_and_merge_badi_counter_windowed nicht fehlschlagen.
        count = pd.DataFrame(columns=["LocationId", "LocationName", "DateId", "TimeId", "Granularity"])
        count["Datetime"] = pd.to_datetime([])
    return count

def download_and_merge_badi_counter(url, location_df, start_date, end_date, granularity, headers, proxies, verify):
    """
    Download counter data from different endpoints and merge together

    returns:
    :badi_counter: df with merged data
    """
    counts = get_location_data_by_endpoint(
        url,
        headers,
        proxies,
        verify,
        location_df, 
        "count", # count OccupancyMax
        start_date, 
        end_date, 
        granularity, 
        aggregation_string="&$apply=groupby((DateId,TimeId,Granularity ), aggregate(InCount with sum as InCount,OutCount with sum as OutCount))",

    )

    occ_max = get_location_data_by_endpoint(
        url,
        headers,
        proxies,
        verify,
        location_df, 
        "OccupancyMax", # count OccupancyMax
        start_date, 
        end_date, 
        granularity, 
        aggregation_string="&$apply=groupby((DateId,TimeId,Granularity ), aggregate(Occupancy with sum as OccupancyMax))",

    )

    merge = counts.drop(columns=["Granularity","TimeId","DateId"]).merge(
        occ_max.drop(columns=["Granularity","TimeId","DateId"]), 
        how='outer', on=["LocationId","LocationName","Datetime"])

    badi_counter = merge

    return badi_counter

def export_badi_counter(badi_counter, export_filepath):
    """
    Filtering and exporting badi counter data to csv
    
    :param export_filepath: Path and filename of the output file
    """
    cols = ["LocationId","LocationName", "Datetime", "InCount", "OutCount", "OccupancyMax"]
    badi_counter[cols].to_csv(export_filepath, index=False)
    print("Exported Badi counter data to:", export_filepath)

def format_timestamp(df):
    date_str = df["DateId"].astype(int).astype(str) # input example 20250501.0 -> output format 20250501 (YYYYmmdd)
    time_str = df["TimeId"].astype(int).astype(str).str.zfill(4) # input example 700.0 -> output format 0700 (HHMM)
    df["Datetime"] = pd.to_datetime(date_str+time_str, format="%Y%m%d%H%M")

    return df



def compute_start_date(end_date, granularity_key, granularity_range, days_override=None):
    """
    Berechnet start_date als end_date minus X Tage.
    - X kommt aus granularity_range[granularity_key], falls days_override nicht gesetzt ist.
    - Ist days_override gesetzt, wird ausschließlich dieser Wert verwendet.

    Parameter
    ---------
    end_date : int | str
        Datum im Format YYYYMMDD (z.B. 20260106).
    granularity_key : str
        Schlüssel im granularity_range-Dictionary (z.B. "Day", "Hour", "FiveMinutes", "OneMinute").
    granularity_range : dict[str, int]
        Mapping von Granularitätsschlüsseln auf Anzahl Tage (Integer).
    days_override : int | None, optional
        Harte Vorgabe für die Anzahl Tage, die abgezogen werden sollen.

    Rückgabewert
    ------------
    int
        start_date im Format YYYYMMDD.
    """
    # end_date in datetime konvertieren
    end_str = str(end_date)
    end_dt = datetime.strptime(end_str, "%Y%m%d")


    # Tage bestimmen: override hat Priorität
    if days_override is not None:
        if not isinstance(days_override, int) or days_override < 0:
            raise ValueError("days_override muss eine nicht-negative ganze Zahl sein.")
        days_to_subtract = days_override
    else:
        days_to_subtract = granularity_range[granularity_key]
        if not isinstance(days_to_subtract, int) or days_to_subtract < 0:
            raise ValueError(f"Wert für '{granularity_key}' muss eine nicht-negative ganze Zahl sein.")

    # Tage abziehen
    start_dt = end_dt - timedelta(days=days_to_subtract)

    return int(start_dt.strftime("%Y%m%d"))


def date_today():
    """
    Get todays date in the expected format for ase (YYYYMMDD)

    return: todays date (str)
    """

    return datetime.today().strftime("%Y%m%d")


def replace_suffix(col: pd.Series, substring: str) -> pd.Series:
    """
    Remove a given substring from the end of each string in a Series
    if it is present.

    :param col: Input pandas Series with string values
    :type col: pd.Series
    :param substring: Substring to remove from the end of the string
    :type substring: str
    :return: Cleaned Series
    :rtype: pd.Series
    """
    if not substring:
        return col
    print("Removing Suffix", substring ,"from", col.name, " if present")
    pattern = re.escape(substring) + r"$"
    return col.str.replace(pattern, "", regex=True)


def export_result(badi_counter, parquet_path=None, csv_path=None, write_parquet=True, write_csv=True):
    """
    Export des Badi-Counter-Daten als Parquet und/oder CSV.

    :param parquet_path: Pfad und Name der Parquet-Ausgabedatei
    :param csv_path: Pfad und Name der CSV-Ausgabedatei
    :param write_parquet: True -> Parquet schreiben
    :param write_csv: True -> CSV schreiben
    """
    cols = ["LocationId", "LocationName", "Datetime", "InCount", "OutCount", "OccupancyMax"]
    cols = [c for c in cols if c in badi_counter.columns]
    result = badi_counter[cols]

    if write_parquet and parquet_path:
        result.to_parquet(parquet_path, index=False)
        print("Exported Parquet to:", parquet_path)
    if write_csv and csv_path:
        result.to_csv(csv_path, index=False)
        print("Exported CSV to:", csv_path)

    if not (write_parquet and parquet_path) and not (write_csv and csv_path):
        raise ValueError("Nichts zu exportieren: weder ein Pfad noch ein aktiviertes Flag gesetzt.")


def download_and_merge_badi_counter_windowed(
    url, location_df, windows, granularity, headers, proxies, verify
):
    """
    Ladt Counter- und OccupancyMax-Daten fensterweise über mehrere Zeitfenster und
    zusammen (analog zu download_and_merge_badi_counter, aber für einen längeren Zeitraum).

    :param windows: Liste von (start_exkl, end_inkl) als ints im Format YYYYMMDD
    :return: zusammengeführtes DataFrame mit den Spalten des Badi-Counter-Exports
    """
    all_merged = []
    for window_start, window_end in windows:
        print("-" * 60)
        print(f"Backfill Fenster: {window_start} -> {window_end}")

        counts = get_location_data_by_endpoint(
            url,
            headers,
            proxies,
            verify,
            location_df,
            "count",
            window_start,
            window_end,
            granularity,
            aggregation_string="&$apply=groupby((DateId,TimeId,Granularity ), aggregate(InCount with sum as InCount,OutCount with sum as OutCount))",
        )

        occ_max = get_location_data_by_endpoint(
            url,
            headers,
            proxies,
            verify,
            location_df,
            "OccupancyMax",
            window_start,
            window_end,
            granularity,
            aggregation_string="&$apply=groupby((DateId,TimeId,Granularity ), aggregate(Occupancy with sum as OccupancyMax))",
        )

        # Leere Endpoints (z.B. historische Belegung nicht verfuegbar) mit Standard-Spalten belegen,
        # damit der Outer-Merge die fehlenden Spalten (InCount/OutCount/OccupancyMax) als NaN fuehrt.
        if counts.empty:
            counts = pd.DataFrame({
                "LocationId": pd.Series(dtype="object"),
                "LocationName": pd.Series(dtype="object"),
                "Datetime": pd.Series(dtype="datetime64[ns]"),
                "InCount": pd.Series(dtype="float"),
                "OutCount": pd.Series(dtype="float"),
            })
        if occ_max.empty:
            occ_max = pd.DataFrame({
                "LocationId": pd.Series(dtype="object"),
                "LocationName": pd.Series(dtype="object"),
                "Datetime": pd.Series(dtype="datetime64[ns]"),
                "OccupancyMax": pd.Series(dtype="float"),
            })

        merge = counts.drop(columns=["Granularity", "TimeId", "DateId"], errors="ignore").merge(
            occ_max.drop(columns=["Granularity", "TimeId", "DateId"], errors="ignore"),
            how='outer',
            on=["LocationId", "LocationName", "Datetime"],
        )
        all_merged.append(merge)

    result = pd.concat(all_merged, ignore_index=True, axis=0)
    # Sicherheitsnetz: falls Fenster sich überschneiden, doppelte Zeitreihen-Einträge entfernen
    result = result.drop_duplicates(subset=["LocationId", "LocationName", "Datetime"])
    return result


def compute_backfill_windows(start_date, end_date, granularity, granularity_range, max_window_days=None):
    """
    Teilt ein Intervall [start_date, end_date] in lückenlose, nicht überlappende Fenster auf.
    Jedes Fenster ist höchstens max_window_days Tage groß (Default: Wert aus granularity_range
    für die angegebene Granularität).

    Die API-Abfrage nutzt den Filter "DateId gt start and DateId le end" (start exklusiv,
    end inklusiv). Jedes Fenster wird daher als (start_exkl, end_inkl)-Tuple zurückgegeben,
    sodass die Fenster zusammen genau das Intervall abdecken (keine Lücken, kein Doppel).

    :param start_date: Startdatum YYYYMMDD (int|str)
    :param end_date: Enddatum YYYYMMDD (int|str)
    :param granularity: Schlüssel in granularity_range (z.B. "FiveMinutes")
    :param granularity_range: Mapping Granularität -> abfragbare Tage
    :param max_window_days: optionales maximales Fenstervolumen in Tagen
    :return: Liste von (start_exkl, end_inkl) als ints im Format YYYYMMDD
    """
    start_dt = datetime.strptime(str(start_date).zfill(8), "%Y%m%d")
    end_dt = datetime.strptime(str(end_date).zfill(8), "%Y%m%d")

    if max_window_days is None:
        max_window_days = granularity_range[granularity]

    windows = []
    cursor = start_dt
    while cursor <= end_dt:
        inclusive_end = min(cursor + timedelta(days=max_window_days - 1), end_dt)
        # Start exkludieren: cursor - 1 Tag, damit die Fenster lückenlos und ohne
        # Überlappung sind (auch wenn das letzte Fenster am Ende abgeschnitten wird).
        start_exkl = cursor - timedelta(days=1)
        windows.append(
            (
                int(start_exkl.strftime("%Y%m%d")),
                int(inclusive_end.strftime("%Y%m%d")),
            )
        )
        cursor = inclusive_end + timedelta(days=1)

    return windows


def get_target_backfill_range(year_override=None, start_override=None, end_override=None):
    """
    Berechnet das Zielintervall des Backfills im Format YYYYMMDD (int) inkl. Zieljahr.

    Priorität:
    - start_override + end_override gesetzt: genau dieser Zeitraum (YYYYMMDD, int|str).
    - ansonsten year_override gesetzt (int|str, z.B. 2024): gesamtes Jahr.
    - sonst: gesamtes Vorjahr (01.01. - 31.12. der vergangenen Kalenderjahr).

    :param year_override: Zieljahr als int|str (z.B. 2024)
    :param start_override: Startdatum YYYYMMDD als int|str (z.B. 20250601)
    :param end_override: Enddatum YYYYMMDD als int|str (z.B. 20250607)
    :return: Tuple (start_date, end_date, year) mit Datum im Format YYYYMMDD (int)
    """
    if start_override is not None and end_override is not None:
        start_dt = datetime.strptime(str(start_override).zfill(8), "%Y%m%d")
        end_dt = datetime.strptime(str(end_override).zfill(8), "%Y%m%d")
        year = start_dt.year
    elif year_override is not None and str(year_override).strip() != "":
        year = int(str(year_override).strip())
        start_dt = datetime(year, 1, 1)
        end_dt = datetime(year, 12, 31)
    else:
        year = datetime.today().year - 1
        start_dt = datetime(year, 1, 1)
        end_dt = datetime(year, 12, 31)

    start_date = int(start_dt.strftime("%Y%m%d"))
    end_date = int(end_dt.strftime("%Y%m%d"))
    return start_date, end_date, year

