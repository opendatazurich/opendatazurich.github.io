"""
This script describes how to scrape eidg. Abstimmungsresultate for all political levels (eidg / kanton zh / stadt zuerich / zaehlkreise zuerich)
"""

from abstimmungsergebnisse.hilfsfunktionen import *
import pandas as pd

Nr_Politische_Ebene = 1
Name_Politische_Ebene = "Eidgenossenschaft"
url = base_absitmmung_url()['Eidgenössisch']
url_list = make_url_list(url, headers, SSL_VERIFY)


# get one abstimmung
# res = get_request(url_list[0], headers, SSL_VERIFY) # eine URL entspricht einem Abstimmungstag >> kann mehrere Abstimmungen enthalten
# url_list[0]
# i = url_list[126]
#
# i = "https://dam-api.bfs.admin.ch/hub/api/dam/assets/7686378/master"
# i = "https://dam-api.bfs.admin.ch/hub/api/dam/assets/7686459/master"

df_eidg_tot = []
df_ktzuerich_tot = []
df_stadtzuerich_tot = []
df_stadtzuerichkreise_tot = []

for i in url_list:
    print(i)
    res = get_request(i, headers, SSL_VERIFY) # eine URL entspricht einem Abstimmungstag >> kann mehrere Abstimmungen enthalten

    ## Resultatebene: Eidgenössisch
    df_eidg = pd.json_normalize(res, record_path=["schweiz", "vorlagen"], errors='ignore')
    df_eidg["vorlagenTitel"] = [df_eidg['vorlagenTitel'][i][0]['text'] for i in range(len(df_eidg['vorlagenTitel']))]
    df_eidg.iloc[0]["vorlagenTitel"]
    df_eidg.columns
    ## Resultatebene: Kanton Zürich

    df_eidg_tot.append(df_eidg)

    # normalize json
    df_ktzuerich = pd.json_normalize(res, record_path=["schweiz", "vorlagen", "kantone"],
                                     meta=[["abstimmtag"], ["schweiz", "vorlagen", "vorlagenTitel"],
                                           ["schweiz", "vorlagen", "vorlagenId"]], errors='ignore')
    df_ktzuerich = df_ktzuerich.astype({'geoLevelnummer': 'int'}, copy=True)
    df_ktzuerich = df_ktzuerich[df_ktzuerich['geoLevelnummer'] == 1]  # subset kanton zh

    # adding further columns
    df_ktzuerich['Nr_Resultat_Gebiet'] = 2
    df_ktzuerich['Name_Resultat_Gebiet'] = "Kanton Zürich"
    df_ktzuerich.iloc[0]
    df_ktzuerich.columns
    df_ktzuerich_tot.append(df_ktzuerich)

    ## Resultatebene: Stadt Zürich

    # Gesamtebene
    df_stadtzuerich = pd.json_normalize(res, record_path=["schweiz", "vorlagen", "kantone", "gemeinden"],meta=[["abstimmtag"], ["schweiz", "vorlagen", "vorlagenId"]], errors='ignore')
    df_stadtzuerich = df_stadtzuerich.astype({'geoLevelnummer': 'int'}, copy=True)
    df_stadtzuerich = df_stadtzuerich[df_stadtzuerich['geoLevelnummer'] == 261]  # subset stadt zürich zh
    if(len(df_stadtzuerich) > 0):
            df_stadtzuerich_tot.append(df_stadtzuerich)

    # Zählkreisebene (nicht immer vorhanden)
    if('zaehlkreise' in df_ktzuerich.columns.tolist()):
        df_stadtzuerichkreise = [pd.json_normalize(dict(df_ktzuerich.iloc[i]), record_path=["zaehlkreise"], meta=["schweiz.vorlagen.vorlagenId"]) for i in range(len(df_ktzuerich))]
        df_stadtzuerichkreise = pd.concat(df_stadtzuerichkreise)
        df_stadtzuerichkreise = df_stadtzuerichkreise[df_stadtzuerichkreise['geoLevelname'].str.contains("Zürich")]  # subsetting to zaehlkreise of stadt zuerich
        df_stadtzuerichkreise_tot.append(df_stadtzuerichkreise)


df_eidg_tot =  pd.concat(df_eidg_tot)
df_ktzuerich_tot = pd.concat(df_ktzuerich_tot)
df_stadtzuerich_tot = pd.concat(df_stadtzuerich_tot)
df_stadtzuerichkreise_tot = pd.concat(df_stadtzuerichkreise_tot)


vorlagen = [*df_ktzuerich_tot[df_ktzuerich_tot["abstimmtag"] == "20240303"]["schweiz.vorlagen.vorlagenId"]]

import openpyxl
df_eidg_tot = df_eidg_tot[df_eidg_tot["vorlagenId"].isin(vorlagen)]
df_ktzuerich_tot = df_ktzuerich_tot[df_ktzuerich_tot["schweiz.vorlagen.vorlagenId"].isin(vorlagen)]
df_stadtzuerich_tot = df_stadtzuerich_tot[df_stadtzuerich_tot["schweiz.vorlagen.vorlagenId"].isin(vorlagen)]
df_stadtzuerichkreise_tot = df_stadtzuerichkreise_tot[df_stadtzuerichkreise_tot["schweiz.vorlagen.vorlagenId"].isin(vorlagen)]


with pd.ExcelWriter("eidg.xlsx") as writer:

    # use to_excel function and specify the sheet_name and index
    # to store the dataframe in specified sheet
    df_eidg_tot.to_excel(writer, sheet_name="eidg", index=False)
    df_ktzuerich_tot.to_excel(writer, sheet_name="kant", index=False)
    df_stadtzuerich_tot.to_excel(writer, sheet_name="stadt", index=False)
    df_stadtzuerichkreise_tot.to_excel(writer, sheet_name="kreis", index=False)


# # adding further columns
# df_ktzuerich['Nr_Resultat_Gebiet'] = 1
# df_ktzuerich['Name_Resultat_Gebiet'] = "Eidgenossenschaft"





# joining vorlagenTitel by vorlagenId
# [res["schweiz"]['vorlagen'][i]['vorlagenTitel'][0]['text'] for i in range(len(res["schweiz"]['vorlagen']))]


