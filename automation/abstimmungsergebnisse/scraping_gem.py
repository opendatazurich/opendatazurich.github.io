"""
This script describes how to scrape kant. Abstimmungsresultate for all political levels (kanton zh / stadt zuerich / zaehlkreise zuerich)
"""
from hilfsfunktionen import *

url = base_absitmmung_url()['Stadt Zürich']
url_list = make_url_list(url, headers, SSL_VERIFY)

i = url_list[0]
i = "https://app-prod-static-voteinfo.s3.eu-central-1.amazonaws.com/v1/ogd/kommunale_resultate_2024_03_03.json"
###

i = 1 #
i = 3 #
url_list[i]

# Stadt Zürich Gesamt
res = get_request(url_list[i], headers, SSL_VERIFY) # eine URL entspricht einem Abstimmungstag >> kann mehrere Abstimmungen enthalten
res = pd.json_normalize(res, record_path=["kantone","vorlagen"], meta=["abstimmtag"], errors='ignore')
res.iloc[0]
res = res.astype({'geoLevelnummer': 'int'}, copy = True)
res = res[(res['geoLevelnummer'] == 261) & (res['nochKeineInformation'] == False)] # subset stadt zürich zh
res["vorlagenTitel"] = [res['vorlagenTitel'].iloc[i][0]['text'] for i in range(len(res['vorlagenTitel']))]

# Stadt Zürich Zählkreise
res = [pd.json_normalize(dict(res.iloc[i]), record_path=["zaehlkreise"], meta=["vorlagenId", "vorlagenTitel"]) for i in range(len(res))]
res = pd.concat(res)
df_stadtzuerichkreise_tot.append(res)

###
i = "https://app-prod-static-voteinfo.s3.eu-central-1.amazonaws.com/v1/ogd/kommunale_resultate_2024_01_28.json"

df_stadtzuerich_tot = []
df_stadtzuerichkreise_tot = []

for i in url_list:

    print(i)

    # Stadt Zürich Gesamt
    res = get_request(i, headers, SSL_VERIFY) # eine URL entspricht einem Abstimmungstag >> kann mehrere Abstimmungen enthalten
    res = pd.json_normalize(res, record_path=["kantone","vorlagen"], meta=["abstimmtag"], errors='ignore')
    res = res.astype({'geoLevelnummer': 'int'}, copy = True)
    res = res[(res['geoLevelnummer'] == 261) & (res['nochKeineInformation'] == False)] # subset stadt zürich zh
    res["vorlagenTitel"] = [res['vorlagenTitel'].iloc[i][0]['text'] for i in range(len(res['vorlagenTitel']))]

    df_stadtzuerich_tot.append(res)

    # Stadt Zürich Zählkreise
    res = [pd.json_normalize(dict(res.iloc[i]), record_path=["zaehlkreise"], meta=["vorlagenId", "vorlagenTitel"]) for i in range(len(res))]
    if(len(res) > 0):
        res = pd.concat(res)
        df_stadtzuerichkreise_tot.append(res)

## writing out
df_stadtzuerich_tot = pd.concat(df_stadtzuerich_tot)
df_stadtzuerichkreise_tot = pd.concat(df_stadtzuerichkreise_tot)

df_stadtzuerichkreise_tot.iloc[0]


    # # trying to squeeze all in one
    # mynewlist=[]
    # for j in range(len(url_list)):
    #     mynewlist.append(get_request(url_list[j], headers, SSL_VERIFY))
    #
    # result_dict = dict(zip([mynewlist[i]['abstimmtag'] for i in range(len(mynewlist))], mynewlist))
    #
    # {abstimmungen: [{stimmtag: XY}, {INHALT}]} # Versuche diese Struktur nachzubilden, und dann alles durchlassen
    #
    # res = pd.json_normalize(result_dict, record_path=["kantone","vorlagen"],meta = ['abstimmtag'], errors='ignore')
    # res = res.astype({'geoLevelnummer': 'int'}, copy = True)
    # res = res[(res['geoLevelnummer'] == 261) & (res['nochKeineInformation'] == False)] # subset stadt zürich zh
    # res["vorlagenTitel"] = [res['vorlagenTitel'][i][0]['text'] for i in range(len(res['vorlagenTitel']))]
    #

