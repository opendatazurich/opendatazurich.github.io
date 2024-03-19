"""
This script describes how to scrape kant. Abstimmungsresultate for all political levels (kanton zh / stadt zueraich / zaehlkreise zuerich)
"""
import pandas as pd

from hilfsfunktionen import *

Nr_Politische_Ebene = 2
Name_Politische_Ebene = "Kanton Zürich"

url = base_absitmmung_url()['Kanton Zürich']
url_list = make_url_list(url, headers, SSL_VERIFY)

# looping
i = 0

df_ktzuerich_tot = []
df_stadtzuerich_tot = []
df_stadtzuerichkreise_tot = []

i = url_list[0]
i = "https://app-prod-static-voteinfo.s3.eu-central-1.amazonaws.com/v1/ogd/sd-t-17-02-20220925-kantAbstimmung.json"

for i in url_list:

    print(i)
    # Kantonale Resultate
    res = get_request(i, headers, SSL_VERIFY) # eine URL entspricht einem Abstimmungstag >> kann mehrere Abstimmungen enthalten

    df_kanton = pd.json_normalize(res, record_path=["kantone","vorlagen"], meta=[['kantone','geoLevelnummer']], errors='ignore')
    df_kanton["abstimmtag"] = res["abstimmtag"]
    df_kanton = df_kanton[df_kanton['kantone.geoLevelnummer'] == 1]
    df_kanton["vorlagenTitel"] = [df_kanton['vorlagenTitel'][i][0]['text'] for i in range(len(df_kanton['vorlagenTitel']))]
    df_ktzuerich_tot.append(df_kanton)

    ## Resultatebene: Stadt Zürich
    df_stadtzuerich = pd.json_normalize(res, record_path=["kantone","vorlagen","gemeinden"], meta=[['kantone','geoLevelnummer'],['kantone','vorlagen','vorlagenId']], errors='ignore')
    df_stadtzuerich = df_stadtzuerich[df_stadtzuerich['geoLevelnummer'] == "261"]
    df_stadtzuerich_tot.append(df_stadtzuerich)

    ## Zählkreise (first part same as above)
    if('zaehlkreise' in df_kanton.columns.tolist()):
            df_stadtzuerichkreise = [pd.json_normalize(dict(df_kanton.iloc[i]), record_path=["zaehlkreise"], meta=["vorlagenId"]) for i in range(len(df_kanton))]

                if(len(df_stadtzuerichkreise) > 0):
                    df_stadtzuerichkreise = pd.concat(df_stadtzuerichkreise)
                    df_stadtzuerichkreise = df_stadtzuerichkreise[df_stadtzuerichkreise['geoLevelname'].str.contains("Zürich")] # subsetting to zaehlkreise of stadt zuerich
                    df_stadtzuerichkreise_tot.append(df_stadtzuerichkreise)


## writing out
df_ktzuerich_tot = pd.concat(df_ktzuerich_tot)
df_stadtzuerich_tot = pd.concat(df_stadtzuerich_tot)
df_stadtzuerichkreise_tot = pd.concat(df_stadtzuerichkreise_tot)

vorlagen = [*df_ktzuerich_tot[df_ktzuerich_tot["abstimmtag"] == "20240303"]["vorlagenId"]]

import openpyxl
df_ktzuerich_tot = df_ktzuerich_tot[df_ktzuerich_tot["vorlagenId"].isin(vorlagen)]
df_stadtzuerich_tot = df_stadtzuerich_tot[df_stadtzuerich_tot["kantone.vorlagen.vorlagenId"].isin(vorlagen)]
df_stadtzuerichkreise_tot = df_stadtzuerichkreise_tot[df_stadtzuerichkreise_tot["vorlagenId"].isin(vorlagen)]

with pd.ExcelWriter("kant.xlsx") as writer:

    # use to_excel function and specify the sheet_name and index
    # to store the dataframe in specified sheet
    df_ktzuerich_tot.to_excel(writer, sheet_name="kant", index=False)
    df_stadtzuerich_tot.to_excel(writer, sheet_name="stadt", index=False)
    df_stadtzuerichkreise_tot.to_excel(writer, sheet_name="kreis", index=False)


