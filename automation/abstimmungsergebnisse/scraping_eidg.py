"""
This script describes how to scrape eidg. Abstimmungsresultate for all political levels (eidg / kanton zh / stadt zuerich / zaehlkreise zuerich)
"""

from abstimmungsergebnisse.hilfsfunktionen import *
import pandas as pd

url = base_absitmmung_url()['Eidgenössisch']
url_list = make_url_list(url, headers, SSL_VERIFY)
# i = url_list[0]
# i=url_list[2]

df_tot = pd.DataFrame()
i = "https://dam-api.bfs.admin.ch/hub/api/dam/assets/7686378/master"
for i in url_list:

    print(i)
    res = get_request(i, headers, SSL_VERIFY)
    df_eidg = pd.json_normalize(res, record_path=["spatial_reference"], meta=['abstimmtag'], errors='ignore')
    df_eidg['url'] = i
    df_tot = pd.concat([df_tot, df_eidg])

df_tot.dtypes
df_tot[df_tot['abstimmtag'] == "20240303"].iloc[2]['url']

df_tot = pd.merge(df_tot, get_zaehlkreise_translation(), how='left', on="geoLevelnummer")

# adding columns
df_tot["neinStimmenInProzent"] = 100 - df_tot["jaStimmenInProzent"]

df_tot = add_columns_politische_ebene(df_tot, 1)
df_tot["StaendeJa"] = df_tot["jaStaendeGanz"] + df_tot["jaStaendeHalb"] * 0.5
df_tot["StaendeJa"] = df_tot["StaendeJa"].fillna(0)
df_tot["StaendeJa"] = [float_to_mixed_number(x) for x in  df_tot["StaendeJa"]]
df_tot["StaendeJa"] = df_tot["StaendeJa"].str.replace(r'0', '')

df_tot["StaendeNein"] = df_tot["neinStaendeGanz"] + df_tot["neinStaendeHalb"] * 0.5
df_tot["StaendeNein"] = df_tot["StaendeNein"].fillna(0)
df_tot["StaendeNein"] = [float_to_mixed_number(x) for x in  df_tot["StaendeNein"]]
df_tot["StaendeNein"] = df_tot["StaendeNein"].str.replace(r'0', '')

# subsetting an renaming columns
df_tot.rename(get_rename_dict(), axis = 'columns', inplace=True)

# Subset columns based on dictionary keys (old column names)
subset_columns = list(get_rename_dict().values())
df_tot = df_tot[subset_columns]

# format and sort columns
df_tot['Abstimmungs_Datum'] = pd.to_datetime(df_tot['Abstimmungs_Datum'], format='%Y%m%d')
df_tot['Abstimmungs_Datum'] = df_tot['Abstimmungs_Datum'].dt.date
df_tot["Nein (%)"] = round(df_tot["Nein (%)"], 1)
df_tot["Ja (%)"] = round(df_tot["Ja (%)"], 1)

df_tot.sort_values(by=['Abstimmungs_Datum','Abstimmungs_Text','Nr_Resultat_Gebiet','Nr_Wahlkreis_StZH'])

import openpyxl
with pd.ExcelWriter("abstimmungsergebnisse/data/eidg_test.xlsx") as writer:
    df_tot.to_excel(writer, sheet_name="eidg", index=False)


old_dat = pd.read_csv("https://data.stadt-zuerich.ch/dataset/politik_abstimmungen_seit1933/download/abstimmungen_seit1933.csv")
old_dat.to_excel("abstimmungsergebnisse/data/abstimmungsergebnisse.xlsx", sheet_name="eidg", index=False)
