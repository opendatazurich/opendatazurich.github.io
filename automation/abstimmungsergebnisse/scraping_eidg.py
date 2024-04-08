"""
This script describes how to scrape eidg. Abstimmungsresultate for all political levels (eidg / kanton zh / stadt zuerich / zaehlkreise zuerich)
"""

from abstimmungsergebnisse.hilfsfunktionen import *
import pandas as pd


url = base_absitmmung_url()['Eidgenössisch']
url_list = make_url_list(url, headers, SSL_VERIFY)

# i = url_list[0]
# url_list = url_list[:20]

# initalizing empty list to store all data.frames
df_tot = pd.DataFrame()

# initializing empty dicionary for vorlagenId and VorlagenTitel
vorlagen_id_titel = {}

for i in url_list:

    print(i)

    # URL reflects one voting day > can hold several votes
    res = get_request(i, headers, SSL_VERIFY)

    ## Resultatebene: Eidgenössisch
    df_eidg = pd.json_normalize(res, record_path=["schweiz", "vorlagen"], meta=['abstimmtag'], errors='ignore')
    df_eidg = add_columns_resultat_gebiet(df_eidg, 1)
    df_eidg.rename(columns=clean_names(df_eidg.columns), inplace=True)

    # updating dictionary
    vorlagen_id_titel.update({int(df_eidg['vorlagenId'].iloc[i]): get_de(df_eidg['vorlagenTitel'].iloc[i]) for i in range(len(df_eidg))})

    ## Resultatebene: Kanton Zürich
    df_ktzuerich = pd.json_normalize(res, record_path=["schweiz", "vorlagen", "kantone"],meta=[['abstimmtag'],['schweiz','vorlagen','vorlagenId']], errors='ignore')
    df_ktzuerich = df_ktzuerich.astype({'geoLevelnummer': 'int'}, copy=True)
    df_ktzuerich = df_ktzuerich[df_ktzuerich['geoLevelnummer'] == 1]  # subset kanton zh
    df_ktzuerich = add_columns_resultat_gebiet(df_ktzuerich, 2)
    df_ktzuerich.rename(columns=clean_names(df_ktzuerich.columns), inplace=True)

    ## Resultatebene: Total Stadt Zürich
    df_stadtzuerich = pd.json_normalize(res, record_path=["schweiz", "vorlagen", "kantone", "gemeinden"],meta=[["abstimmtag"], ["schweiz", "vorlagen", "vorlagenId"]], errors='ignore')
    df_stadtzuerich = df_stadtzuerich.astype({'geoLevelnummer': 'int'}, copy=True)
    df_stadtzuerich = df_stadtzuerich[df_stadtzuerich['geoLevelnummer'] == 261]  # subset stadt zürich zh
    df_stadtzuerich = add_columns_resultat_gebiet(df_stadtzuerich, 3)
    df_stadtzuerich.rename(columns=clean_names(df_stadtzuerich.columns), inplace=True)

    ## Resultatebene: Zaehlkreise Stadt Zürich (nicht immer vorhanden)

    if('zaehlkreise' in df_ktzuerich.columns.tolist()):
        df_stadtzuerichkreise = [pd.json_normalize(dict(df_ktzuerich.iloc[i]), record_path=["zaehlkreise"], meta=["vorlagenId"]) for i in range(len(df_ktzuerich))]
        df_stadtzuerichkreise = pd.concat(df_stadtzuerichkreise)
        df_stadtzuerichkreise = df_stadtzuerichkreise[df_stadtzuerichkreise['geoLevelname'].str.contains("Zürich")]  # subsetting to zaehlkreise of stadt zuerich
        df_stadtzuerichkreise.rename(columns=clean_names(df_stadtzuerichkreise.columns), inplace=True)
        df_stadtzuerich.drop(["geoLevelnummer","geoLevelname","geoLevelParentnummer"], axis=1, inplace=True)

    ## Bereinigung (renaming, dropping columns, appending df to list)
    df_eidg.drop(["vorlagenTitel","kantone","vorlagenArtId","hauptvorlagenId","reserveInfoText"], axis=1, inplace=True)
    df_ktzuerich.drop(["bezirke","gemeinden","geoLevelnummer","geoLevelname"], axis=1, inplace=True)

    ##
    df_tot = pd.concat([df_tot,df_eidg, df_ktzuerich, df_stadtzuerich, df_stadtzuerichkreise])


# adding
df_tot = add_columns_politische_ebene(df_tot,1)

# filtering results (only valid result)
df_tot = df_tot[(df_tot['provisorisch'] == False) & (df_tot['vorlageBeendet'] == True)]

# joining vorlagenTitel
vorlagen_id_titel = pd.DataFrame({"vorlagenId":vorlagen_id_titel.keys(), "vorlagenTitel":vorlagen_id_titel.values()})
df_tot = pd.merge(df_tot, vorlagen_id_titel, how='left', on="vorlagenId")
df_tot = pd.merge(df_tot, get_zaehlkreise_translation(), how='left', on="geoLevelnummer")

# adding columns
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
df_tot.rename(rename_dict, axis = 'columns', inplace=True)

# Subset columns based on dictionary keys (old column names)
subset_columns = list(rename_dict.values())
df_tot = df_tot[subset_columns]


import openpyxl
with pd.ExcelWriter("abstimmungsergebnisse/eidg_test.xlsx") as writer:
    df_tot.to_excel(writer, sheet_name="eidg", index=False)
