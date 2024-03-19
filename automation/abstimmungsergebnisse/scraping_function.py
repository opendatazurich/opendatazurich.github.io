
from parameter_function import *

def scraping(pol_ebene_val):
    print(pol_ebene_val)
    vorlagen = politischeEbene.loc[pol_ebene_val]['record_path_vorlage']
    record_path_gmd = vorlagen + politischeEbene.loc[pol_ebene_val]['record_path_gmd']
    record_path_zk = vorlagen + politischeEbene.loc[pol_ebene_val]['record_path_zk']
    vorlagen_titel = vorlagen + politischeEbene.loc[pol_ebene_val]['record_path_vorlageTitel']
    vorlagen_id = vorlagen + ["vorlagenId"]
    vorlagen_id_var = politischeEbene.loc[pol_ebene_val]['vorlagenId_var']
    print(vorlagen_id_var)
    metadaten = politischeEbene.loc[pol_ebene_val]['meta']
    print(record_path_zk)

    # Import Metadata and Define List with all URLs
    META_EID = metadaten
    r = requests.get(META_EID, headers=headers, verify=SSL_VERIFY)
    data = r.json()
    daten = pd.json_normalize(data, record_path=["result", "resources"])
    url_list = daten["url"]

    print('bis hier ok url')
    # Create Dataframe with All Results Gemeinde-Ebene und Zählkreis-Ebene
    gmd = pd.DataFrame()
    zaehlkreis_alle = pd.DataFrame()
    print('bis hier ok leere df')
    for url in url_list:
        r = requests.get(url, headers=headers, verify=SSL_VERIFY)
        data = r.json()
        print(url)
        # vorlagen text
        vorlage_text = pd.json_normalize(data, record_path=vorlagen_titel, meta=[["abstimmtag"],vorlagen_id] , errors='ignore')
        vorlage_text_de = vorlage_text[(vorlage_text['langKey']=='de')]
        print('bis hier ok 2 in loop')
        print(vorlage_text_de.keys())
        # stände resultate
        vorlage = pd.json_normalize(data, record_path=vorlagen)
        filter_col = [col for col in vorlage if col.startswith('staende') or col == "vorlagenId"]
        staende = vorlage[filter_col]
        print(vorlage.keys())
        print('bis hier ok 3 in loop')
        # vorlage und staende resulate
        print(staende.keys())
        ch_single = pd.merge(vorlage_text_de, staende, left_on = vorlagen_id_var, right_on="vorlagenId")
        print('bis hier ok 4 in loop')
        # gemeinde resultate
        gmd_single = pd.json_normalize(data, record_path=record_path_gmd, 
                                    meta=[["abstimmtag"],vorlagen_id])
        print('bis hier ok 5 in loop')

        # join stände vorlage gemeinde-resultate
        join = pd.merge(ch_single, gmd_single, how='inner', on = [vorlagen_id_var, "abstimmtag"])

        # join abstimmungstag zu allen abstimmungen
        gmd = pd.concat([gmd, join], ignore_index=True, sort=False)
        print('bis hier ok 6 in loop')
        print(data.keys())
        # zaehlkreis resultate
        df = pd.json_normalize(data, record_path=record_path_zk, meta=[["abstimmtag"],vorlagen_id] , errors='ignore')
        print('bis hier ok 7 in loop')
        try:
            df_zk = df[df['zaehlkreise'].notna()]
            for i in list(df_zk["zaehlkreise"].keys()):
                try:
                    zk = df['zaehlkreise'][i]
                    zaehlkreise_norm = pd.json_normalize(zk)
                    zaehlkreise_norm['i'] = i
                    zaehlkreise_norm[vorlagen_id_var] = df[vorlagen_id_var][i]
                    zaehlkreise_norm['abstimmtag'] = df['abstimmtag'][i]
                                    
                    # join stände vorlage zaehlkreis-resultate
                    join_zk = pd.merge(ch_single, zaehlkreise_norm, how='inner', on = [vorlagen_id_var, "abstimmtag"])

                    zaehlkreis_alle = pd.concat([zaehlkreis_alle, join_zk], ignore_index=True, sort=False)
                except:
                    zaehlkreis_alle = zaehlkreis_alle
        except:
            zaehlkreis_alle = zaehlkreis_alle

    result = pd.concat([gmd, zaehlkreis_alle], ignore_index=True, sort=False)
    result.keys()
    result.to_csv('C:/Projekte/GitLab/abstimmungs_scraper/neustesResultat.csv', index=False)
    print(record_path_zk)
    return result






