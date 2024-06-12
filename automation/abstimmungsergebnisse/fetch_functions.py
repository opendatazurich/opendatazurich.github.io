import pandas as pd
from abstimmungsergebnisse.helper_functions import *


def get_kommunale_resultate(url_list):
    """
    @ ......
    """
    # initalizing empty list to store all data.frames / empty dicionary for all general infos about a vorlage
    df_tot = pd.DataFrame()
    vorlagen_info = {}

    for i in url_list:

        res = get_request(i, headers,SSL_VERIFY)  # eine URL entspricht einem Abstimmungstag >> kann mehrere Abstimmungen enthalten

        ## Resultatebene: Stadt Zürich
        df_stadtzuerich = pd.json_normalize(res, record_path=["kantone", "vorlagen"], meta=["abstimmtag"], errors='ignore')
        df_stadtzuerich = df_stadtzuerich.astype({'geoLevelnummer': 'int'}, copy=True)
        df_stadtzuerich = df_stadtzuerich[(df_stadtzuerich['geoLevelnummer'] == 261)]

        if (len(df_stadtzuerich) > 0):

            df_stadtzuerich["url"] = i
            df_stadtzuerich = add_columns_resultat_gebiet(df_stadtzuerich, 3)
            df_stadtzuerich.rename(columns=clean_names(df_stadtzuerich.columns), inplace=True)

            # updating vorlagen_info
            i_vorlagen_info = {
                int(df_stadtzuerich['vorlagenId'].iloc[v]): [get_de(df_stadtzuerich['vorlagenTitel'].iloc[v]),
                                                             df_stadtzuerich['vorlageBeendet'].iloc[v],
                                                             df_stadtzuerich['abstimmtag'].iloc[v]] for v in range(len(df_stadtzuerich))}
            vorlagen_info.update(i_vorlagen_info)

            ## Resultatebene: Zaehlkreise Stadt Zürich (nicht immer vorhanden)
            df_stadtzuerichkreise = [pd.json_normalize(dict(df_stadtzuerich.iloc[i]), record_path=["zaehlkreise"], meta=["vorlagenId"]) for i in range(len(df_stadtzuerich))]

            if (len(df_stadtzuerichkreise) > 0):
                df_stadtzuerichkreise = pd.concat(df_stadtzuerichkreise)
                df_stadtzuerichkreise = df_stadtzuerichkreise[df_stadtzuerichkreise['geoLevelname'].str.contains("Zürich")]  # subsetting to zaehlkreise of stadt zuerich
                df_stadtzuerichkreise = add_columns_resultat_gebiet(df_stadtzuerichkreise, 3)
                df_stadtzuerichkreise.rename(columns=clean_names(df_stadtzuerichkreise.columns), inplace=True)
                df_stadtzuerichkreise.drop(columns_to_drop(), axis=1, inplace=True,errors='ignore')

            ## Bereinigung (renaming, dropping columns, appending df to list)
            df_stadtzuerich.drop(columns_to_drop(), axis=1, inplace=True,errors='ignore')
            df_tot = pd.concat([df_tot, df_stadtzuerich, df_stadtzuerichkreise])

    # joining vorlagen_info
    rows = [{'vorlagenId': key, 'vorlagenTitel': values[0], 'vorlageBeendet': values[1], 'abstimmtag': values[2]} for key, values in vorlagen_info.items()]
    vorlagen_info = pd.DataFrame(rows)
    df_tot = pd.merge(df_tot, vorlagen_info, how='left', on="vorlagenId")
    df_tot = add_columns_politische_ebene(df_tot, 3)

    return df_tot

def get_kantonale_resultate(url_list):
    """
    ......
    """
    # initalizing empty list to store all data.frames / empty dicionary for all general infos about a vorlage
    df_tot = pd.DataFrame()
    vorlagen_info = {}

    for i in url_list:

        res = get_request(i, headers, SSL_VERIFY)  # eine URL entspricht einem Abstimmungstag >> kann mehrere Abstimmungen enthalten

        ## Resultatebene: Kanton Zürich
        df_ktzuerich = pd.json_normalize(res, record_path=["kantone", "vorlagen"],meta=[['abstimmtag'], ['kantone', 'geoLevelnummer']], errors='ignore')
        df_ktzuerich = df_ktzuerich[df_ktzuerich['kantone.geoLevelnummer'] == 1]

        df_ktzuerich["url"] = i

        if (len(df_ktzuerich) > 0):

            df_ktzuerich = add_columns_resultat_gebiet(df_ktzuerich, 2)
            df_ktzuerich.rename(columns=clean_names(df_ktzuerich.columns), inplace=True)

            # updating vorlagen_info
            i_vorlagen_info = {int(df_ktzuerich['vorlagenId'].iloc[v]): [get_de(df_ktzuerich['vorlagenTitel'].iloc[v]),
                                                                         df_ktzuerich['vorlageBeendet'].iloc[v],
                                                                         df_ktzuerich['vorlagenArtId'].iloc[v],
                                                                         df_ktzuerich['abstimmtag'].iloc[v]] for v in range(len(df_ktzuerich))}
            vorlagen_info.update(i_vorlagen_info)

            ## Resultatebene: Stadt Zürich
            df_stadtzuerich = pd.json_normalize(res, record_path=["kantone", "vorlagen", "gemeinden"],
                                                meta=[['kantone', 'geoLevelnummer'],
                                                      ['kantone', 'vorlagen', 'vorlagenId']], errors='ignore')
            df_stadtzuerich.drop(["kantone.geoLevelnummer"], axis=1, inplace=True,errors='ignore')
            df_stadtzuerich = df_stadtzuerich[df_stadtzuerich['geoLevelnummer'] == "261"]
            df_stadtzuerich = add_columns_resultat_gebiet(df_stadtzuerich, 3)
            df_stadtzuerich.rename(columns=clean_names(df_stadtzuerich.columns), inplace=True)

            ## Resultatebene: Zaehlkreise Stadt Zürich (nicht immer vorhanden)
            df_stadtzuerichkreise = pd.DataFrame()
            if ('zaehlkreise' in df_ktzuerich.columns.tolist()):
                df_stadtzuerichkreise = [pd.json_normalize(dict(df_ktzuerich.iloc[k]), record_path=["zaehlkreise"], meta=["vorlagenId"]) for k in range(len(df_ktzuerich))]

                if (len(df_stadtzuerichkreise) > 0):
                    df_stadtzuerichkreise = pd.concat(df_stadtzuerichkreise)
                    df_stadtzuerichkreise = df_stadtzuerichkreise[df_stadtzuerichkreise['geoLevelname'].str.contains("Zürich")]  # subsetting to zaehlkreise of stadt zuerich

                    df_stadtzuerichkreise = add_columns_resultat_gebiet(df_stadtzuerichkreise, 3)
                    df_stadtzuerichkreise.rename(columns=clean_names(df_stadtzuerichkreise.columns), inplace=True)
                    df_stadtzuerichkreise.drop(columns_to_drop(), axis=1, inplace=True,errors='ignore')

            ## Bereinigung (renaming, dropping columns, appending df to list)
            df_ktzuerich.drop(columns_to_drop(), axis=1, inplace=True, errors='ignore')
            df_stadtzuerich.drop(columns_to_drop(), axis=1, inplace=True,errors='ignore')
            df_tot = pd.concat([df_tot, df_ktzuerich, df_stadtzuerich, df_stadtzuerichkreise])

    # joining vorlagen_info
    rows = [{'vorlagenId': key, 'vorlagenTitel': values[0], 'vorlageBeendet': values[1], 'vorlagenArtId': values[2],'abstimmtag': values[3]} for key, values in vorlagen_info.items()]
    vorlagen_info = pd.DataFrame(rows)
    df_tot = pd.merge(df_tot, vorlagen_info, how='left', on="vorlagenId")
    df_tot = add_columns_politische_ebene(df_tot, 2)

    return df_tot

def get_eidgenoessische_resultate(url_list):
    # initalizing empty list to store all data.frames / empty dicionary for all general infos about a vorlage
    df_tot = pd.DataFrame()
    vorlagen_info = {}

    for i in url_list:

        # URL reflects one voting day > can hold several votes
        res = get_request(i, headers, SSL_VERIFY)

        ## Resultatebene: Eidgenössisch
        df_eidg = pd.json_normalize(res, record_path=["schweiz", "vorlagen"], meta=['abstimmtag'], errors='ignore')
        df_eidg = add_columns_resultat_gebiet(df_eidg, 1)
        df_eidg.rename(columns=clean_names(df_eidg.columns), inplace=True)
        df_eidg["url"] = i

        # updating vorlagen_info
        i_vorlagen_info = {int(df_eidg['vorlagenId'].iloc[v]): [get_de(df_eidg['vorlagenTitel'].iloc[v]),
                                                                df_eidg['vorlageBeendet'].iloc[v],
                                                                df_eidg['provisorisch'].iloc[v],
                                                                df_eidg['vorlagenArtId'].iloc[v],
                                                                df_eidg['abstimmtag'].iloc[v]] for v in
                           range(len(df_eidg))}
        vorlagen_info.update(i_vorlagen_info)

        ## Resultatebene: Kanton Zürich
        df_ktzuerich = pd.json_normalize(res, record_path=["schweiz", "vorlagen", "kantone"],
                                         meta=[['schweiz', 'vorlagen', 'vorlagenId']], errors='ignore')
        df_ktzuerich = df_ktzuerich.astype({'geoLevelnummer': 'int'}, copy=True)
        df_ktzuerich = df_ktzuerich[df_ktzuerich['geoLevelnummer'] == 1]  # subset kanton zh
        df_ktzuerich = add_columns_resultat_gebiet(df_ktzuerich, 2)
        df_ktzuerich.rename(columns=clean_names(df_ktzuerich.columns), inplace=True)

        ## Resultatebene: Total Stadt Zürich
        df_stadtzuerich = pd.json_normalize(res, record_path=["schweiz", "vorlagen", "kantone", "gemeinden"],
                                            meta=[["schweiz", "vorlagen", "vorlagenId"]], errors='ignore')
        df_stadtzuerich = df_stadtzuerich.astype({'geoLevelnummer': 'int'}, copy=True)
        df_stadtzuerich = df_stadtzuerich[df_stadtzuerich['geoLevelnummer'] == 261]  # subset stadt zürich zh
        df_stadtzuerich = add_columns_resultat_gebiet(df_stadtzuerich, 3)
        df_stadtzuerich.rename(columns=clean_names(df_stadtzuerich.columns), inplace=True)

        ## Resultatebene: Zaehlkreise Stadt Zürich (nicht immer vorhanden)
        df_stadtzuerichkreise = pd.DataFrame()

        if ('zaehlkreise' in df_ktzuerich.columns.tolist()):
            df_stadtzuerichkreise = [
                pd.json_normalize(dict(df_ktzuerich.iloc[k]), record_path=["zaehlkreise"], meta=["vorlagenId"]) for k in
                range(len(df_ktzuerich))]
            df_stadtzuerichkreise = pd.concat(df_stadtzuerichkreise)
            df_stadtzuerichkreise = df_stadtzuerichkreise[df_stadtzuerichkreise['geoLevelname'].str.contains("Zürich")]  # subsetting to zaehlkreise of stadt zuerich
            df_stadtzuerichkreise = add_columns_resultat_gebiet(df_stadtzuerichkreise, 3)
            df_stadtzuerichkreise.rename(columns=clean_names(df_stadtzuerichkreise.columns), inplace=True)
            df_stadtzuerich.drop(columns_to_drop(), axis=1, inplace=True, errors='ignore')

        ## Bereinigung (renaming, dropping columns, appending df to list)
        df_eidg.drop(columns_to_drop(), axis=1, inplace=True, errors='ignore')
        df_ktzuerich.drop(columns_to_drop(), axis=1, inplace=True, errors='ignore')
        df_tot = pd.concat([df_tot, df_eidg, df_ktzuerich, df_stadtzuerich, df_stadtzuerichkreise])

    # joining vorlagen_info
    rows = [{'vorlagenId': key, 'vorlagenTitel': values[0], 'vorlageBeendet': values[1], 'provisorisch': values[2],
             'vorlagenArtId': values[3], 'abstimmtag': values[4]} for key, values in vorlagen_info.items()]
    vorlagen_info = pd.DataFrame(rows)
    df_tot = pd.merge(df_tot, vorlagen_info, how='left', on="vorlagenId")
    df_tot = add_columns_politische_ebene(df_tot, 1)

    return df_tot
