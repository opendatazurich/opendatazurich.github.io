"""
This script describes how to scrape eidg. Abstimmungsresultate for all political levels (eidg / kanton zh / stadt zuerich / zaehlkreise zuerich)
"""

from abstimmungsergebnisse.hilfsfunktionen import *
import pandas as pd

url = base_absitmmung_url()['Eidgenössisch']
url_list = make_url_list(url, headers, SSL_VERIFY)
# i = url_list[0]
# i=url_list[2]

def get_eidgenoessische_resultate:

    # initalizing empty list to store all data.frames / empty dicionary for all general infos about a vorlage
    df_tot = pd.DataFrame()
    vorlagen_info = {}

    for i in url_list:

        i_url = i

        # URL reflects one voting day > can hold several votes
        res = get_request(i, headers, SSL_VERIFY)

        ## Resultatebene: Eidgenössisch
        df_eidg = pd.json_normalize(res, record_path=["schweiz", "vorlagen"], meta=['abstimmtag'], errors='ignore')
        df_eidg = add_columns_resultat_gebiet(df_eidg, 1)
        df_eidg.rename(columns=clean_names(df_eidg.columns), inplace=True)
        df_eidg["url"] = i_url

        # updating vorlagen_info
        i_vorlagen_info = {int(df_eidg['vorlagenId'].iloc[v]): [get_de(df_eidg['vorlagenTitel'].iloc[v]),
                                        df_eidg['vorlageBeendet'].iloc[v],
                                        df_eidg['provisorisch'].iloc[v],
                                        df_eidg['vorlagenArtId'].iloc[v],
                                        df_eidg['abstimmtag'].iloc[v]] for v in range(len(df_eidg))}
        vorlagen_info.update(i_vorlagen_info)

        ## Resultatebene: Kanton Zürich
        df_ktzuerich = pd.json_normalize(res, record_path=["schweiz", "vorlagen", "kantone"],meta=[['schweiz','vorlagen','vorlagenId']], errors='ignore')
        df_ktzuerich = df_ktzuerich.astype({'geoLevelnummer': 'int'}, copy=True)
        df_ktzuerich = df_ktzuerich[df_ktzuerich['geoLevelnummer'] == 1]  # subset kanton zh
        df_ktzuerich = add_columns_resultat_gebiet(df_ktzuerich, 2)
        df_ktzuerich.rename(columns=clean_names(df_ktzuerich.columns), inplace=True)

        ## Resultatebene: Total Stadt Zürich
        df_stadtzuerich = pd.json_normalize(res, record_path=["schweiz", "vorlagen", "kantone", "gemeinden"],meta=[["schweiz", "vorlagen", "vorlagenId"]], errors='ignore')
        df_stadtzuerich = df_stadtzuerich.astype({'geoLevelnummer': 'int'}, copy=True)
        df_stadtzuerich = df_stadtzuerich[df_stadtzuerich['geoLevelnummer'] == 261]  # subset stadt zürich zh
        df_stadtzuerich = add_columns_resultat_gebiet(df_stadtzuerich, 3)
        df_stadtzuerich.rename(columns=clean_names(df_stadtzuerich.columns), inplace=True)

        ## Resultatebene: Zaehlkreise Stadt Zürich (nicht immer vorhanden)
        df_stadtzuerich = pd.DataFrame()

        if('zaehlkreise' in df_ktzuerich.columns.tolist()):
            df_stadtzuerichkreise = [pd.json_normalize(dict(df_ktzuerich.iloc[k]), record_path=["zaehlkreise"], meta=["vorlagenId"]) for k in range(len(df_ktzuerich))]
            df_stadtzuerichkreise = pd.concat(df_stadtzuerichkreise)
            df_stadtzuerichkreise = df_stadtzuerichkreise[df_stadtzuerichkreise['geoLevelname'].str.contains("Zürich")]  # subsetting to zaehlkreise of stadt zuerich
            df_stadtzuerichkreise = add_columns_resultat_gebiet(df_stadtzuerichkreise, 3)
            df_stadtzuerichkreise.rename(columns=clean_names(df_stadtzuerichkreise.columns), inplace=True)
            # df_stadtzuerich.drop(["geoLevelname","geoLevelParentnummer"], axis=1, inplace=True)
            df_stadtzuerich.drop(["geoLevelParentnummer"], axis=1, inplace=True)

        ## Bereinigung (renaming, dropping columns, appending df to list)
        df_eidg.drop(["vorlagenTitel","kantone","vorlagenArtId","hauptvorlagenId","reserveInfoText","vorlageBeendet","provisorisch","abstimmtag"], axis=1, inplace=True, errors='ignore')
        df_ktzuerich.drop(["bezirke","gemeinden","geoLevelnummer","geoLevelname","vorlageBeendet","zaehlkreise"], axis=1, inplace=True, errors='ignore')

        df_tot = pd.concat([df_tot,df_eidg, df_ktzuerich, df_stadtzuerich, df_stadtzuerichkreise])

    # joining vorlagen_info
    rows = [{'vorlagenId': key, 'vorlagenTitel': values[0], 'vorlageBeendet': values[1], 'provisorisch': values[2], 'vorlagenArtId': values[3], 'abstimmtag': values[4]} for key, values in vorlagen_info.items()]
    vorlagen_info = pd.DataFrame(rows)
    df_tot = pd.merge(df_tot, vorlagen_info, how='left', on="vorlagenId")
    df_tot = add_columns_politische_ebene(df_tot,1)

    # filtering results (only valid result)
    df_tot = df_tot[(df_tot['provisorisch'] == False) & (df_tot['vorlageBeendet'] == True)]

    return df_tot

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
