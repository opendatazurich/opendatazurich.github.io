# -*- coding: utf-8 -*-
"""Fetch json from BFS API

Usage:
  fetch_all_data.py --file <path-to-csv> [--no-verify]
  fetch_all_data.py (-h | --help)
  fetch_all_data.py --version

Options:
  -h, --help                      Show this screen.
  --version                       Show version.
  -f, --file <path-to-csv>        Path to CSV file
  --no-verify                     Option to disable SSL verification for reqests.
"""
from fetch_functions import *
from docopt import docopt

# Parse command line arguments using docopt > __doc__ references to docstring (special attribute)
arguments = docopt(__doc__, version='Fetch CSV from CKAN API 1.0')

# Fetching eidgenoessische Abstimmungen
url = base_absitmmung_url()['Eidgenössisch']
url_list_eidg = make_url_list(url, headers, SSL_VERIFY)
df_eidg = get_eidgenoessische_resultate(url_list_eidg)

# Fetching kantonale Abstimmungen
url = base_absitmmung_url()['Kanton Zürich']
url_list_kant = make_url_list(url, headers, SSL_VERIFY)
df_kant = get_kantonale_resultate(url_list_kant)

# Fetching kommunale Abstimmungen
url = base_absitmmung_url()['Stadt Zürich']
url_list_komm = make_url_list(url, headers, SSL_VERIFY)
df_komm = get_kommunale_resultate(url_list_komm)

# type casting
df_eidg[['geoLevelnummer']] = df_eidg[['geoLevelnummer']].fillna(value=-1)
df_kant[['geoLevelnummer']] = df_kant[['geoLevelnummer']].fillna(value=-1)
df_komm[['geoLevelnummer']] = df_komm[['geoLevelnummer']].fillna(value=-1)

df_eidg = df_eidg.astype({'geoLevelnummer':'int64'})
df_kant = df_kant.astype({'geoLevelnummer':'int64'})
df_komm = df_komm.astype({'geoLevelnummer':'int64'})

# Concatenating all pd's together
df_tot = pd.concat([df_eidg, df_kant, df_komm])

# filtering results (only valid result)
df_tot = df_tot[(df_tot['vorlageBeendet'] == True) & (df_tot['gebietAusgezaehlt'] == True)]
df_tot.drop_duplicates(inplace=True)

# adding columns
df_tot = pd.merge(df_tot, get_zaehlkreise_translation(), how='left', on="geoLevelnummer")
df_tot["neinStimmenInProzent"] = 100 - df_tot["jaStimmenInProzent"]

df_tot['jaStaendeGanz'] = df_tot['jaStaendeGanz'].apply(lambda x: str(int(x)) if not pd.isna(x) else '')
df_tot['jaStaendeHalb'] = df_tot['jaStaendeHalb'].apply(lambda x: str(int(x)) if not pd.isna(x) else '')
df_tot.loc[df_tot['jaStaendeGanz'] == "", 'StaendeJa'] = ""
df_tot.loc[df_tot['jaStaendeGanz'] != "", 'StaendeJa'] = df_tot['jaStaendeGanz'] + " " + df_tot['jaStaendeHalb'] + "/2"

df_tot['neinStaendeGanz'] = df_tot['neinStaendeGanz'].apply(lambda x: str(int(x)) if not pd.isna(x) else '')
df_tot['neinStaendeHalb'] = df_tot['neinStaendeHalb'].apply(lambda x: str(int(x)) if not pd.isna(x) else '')
df_tot.loc[df_tot['neinStaendeGanz'] == "", 'StaendeNein'] = ""
df_tot.loc[df_tot['neinStaendeGanz'] != "", 'StaendeNein'] = df_tot['neinStaendeGanz'] + " " + df_tot['neinStaendeHalb'] + "/2"

# subsetting an renaming columns
df_tot.rename(get_rename_dict(), axis = 'columns', inplace=True)

# Subset columns based on dictionary keys (old column names)
subset_columns = list(get_rename_dict().values())
df_tot = df_tot[subset_columns]

# format and sort columns
df_tot['Abstimmungs_Datum'] = df_tot['Abstimmungs_Datum'].str.replace('-', '')
df_tot['Abstimmungs_Datum'] = pd.to_datetime(df_tot['Abstimmungs_Datum'], format='%Y%m%d')
df_tot['Abstimmungs_Datum'] = df_tot['Abstimmungs_Datum'].dt.date
df_tot["Stimmbeteiligung (%)"] = round(df_tot["Stimmbeteiligung (%)"], 1)
df_tot["Nein (%)"] = round(df_tot["Nein (%)"], 1)
df_tot["Ja (%)"] = round(df_tot["Ja (%)"], 1)

df_tot.sort_values(by=['Abstimmungs_Datum',"Nr_Politische_Ebene",'Abstimmungs_Text','Nr_Resultat_Gebiet','Nr_Wahlkreis_StZH'], ascending=[False, True, True, True, True], inplace=True)

# TODO: Subset df_tot to abstimmungen from the beginning of 2021
# TODO: Save existing file to repo > subset abstimmungen from the very start to end of 2020
# TODO: Load existing file from repo and concat it to the subsetted df_tot
# TODO: Write out df_tot to parquet > control dtypes

# writing pdf out as csv
csv_path = arguments['--file']
df_tot.to_csv(csv_path, index = False)
