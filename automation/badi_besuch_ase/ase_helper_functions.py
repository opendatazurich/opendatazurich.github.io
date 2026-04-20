import re
import requests
import pandas as pd
from datetime import datetime, timedelta

# Documentation:https://zuerich.pas.ch/v2/swagger/index.html
# functions

def get_auth_header(url, credentials, headers, proxies, verify):
    bearer = requests.post(url + "/v2/api/Auth/login", json=credentials, headers=headers, 
                            proxies=proxies, 
                            verify=verify)
    if bearer.status_code != 200:
        raise Exception("Failed to authenticate: {bearer.text}")

    token = bearer.json().get('accessToken')
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
            count_json = response.json()
            #print(count_json)
            values = count_json#['value']
            df = pd.DataFrame.from_dict(values, orient='columns')
            # final_df = pd.concat([final_df, df], ignore_index=True)
            # final_df = final_df._append(df, ignore_index=True)
            final_df = pd.concat([final_df, df], ignore_index=True, axis=0)
        # The result might contain multiple locationIds as each sensor/location can have multiple sub-locations/measureitems
        final_df['LocationName'] = location_name
        final_df['LocationId'] = location_id
        print("Number of rows and columns:", final_df.shape)
        # count = count._append(final_df, ignore_index=True)
        count = pd.concat([count, final_df], ignore_index=True, axis=0)

    count = count.sort_values(["LocationName", "DateId", "TimeId"])

    count = format_timestamp(count)

    print("Data from", count["Datetime"].min(), " to ", count["Datetime"].max())
    print(count)
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

