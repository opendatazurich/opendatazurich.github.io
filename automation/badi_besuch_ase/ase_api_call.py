import os
import ase_helper_functions as ase
import ase_parameters as ase_p

from dotenv import load_dotenv


# Einstellungen und constanten
# base url
url = ase_p.BASE_URL # base url for api
# filepaths for exports
filepath_locations = ase_p.FILEPATH_LOCATIONS
filepath_counter = ase_p.FILEPATH_COUNTER
# parameters for local execution
local_execution = ase_p.LOCAL_EXECUTION
# granularity and how many days back you get get data
granularity_range = ase_p.GRANULARITY_RANGE
# locations, die in den Datensatz dürfen
valid_locations = ase_p.VALID_LOCATIONS
# dieser Suffix wird später von den Locations entfernt
suffix_to_remove = ase_p.SUFFIX_TO_REMOVE
# Granularität nach der ausgewertet wird
granularity = ase_p.GRANULARITY_TO_USE #"Hour"#"FiveMinutes" 

# load env
load_dotenv(verbose=True)
# set env vars
ASE_USERNAME = os.getenv('ASE_USERNAME')
ASE_PASSWORD = os.getenv('ASE_PASSWORD')
PROXYUSER = os.getenv('PROXYUSER_STREETDIRECTORY')
PROXYPASSWORD = os.getenv('PROXYPASSWORD_STREETDIRECTORY')


# set end date
end_date = ase.date_today() #20260323 
# get start date, based on end date and granularity_range
start_date = ase.compute_start_date(end_date, granularity, granularity_range, days_override=None)


# setup for requests
credentials = {
    'username': ASE_USERNAME, 
    'password': ASE_PASSWORD,
}

headers = {
    'Content-Type': 'application/json',
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




# get auth header for api calls
ase_headers = ase.get_auth_header(url, credentials, headers, proxies, verify=verify)

# get location data
location_df = ase.get_location_names_by_type(url,location_type="Mall", headers=ase_headers, proxies=proxies, verify=verify, filter_locations=valid_locations)
location_df["LocalName"] = ase.replace_suffix(location_df["LocalName"], suffix_to_remove)
ase.export_locations(location_df, export_filepath=filepath_locations)

# get counter data
badi_counter = ase.download_and_merge_badi_counter(url, location_df, start_date, end_date, granularity, headers=ase_headers, proxies=proxies, verify=verify)
badi_counter["LocationName"] = ase.replace_suffix(badi_counter["LocationName"], suffix_to_remove)
ase.export_badi_counter(badi_counter, export_filepath=filepath_counter)

