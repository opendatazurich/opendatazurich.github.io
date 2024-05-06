"""
This is a sandbox script
"""

from abstimmungsergebnisse.helper_functions import *
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

df_tot['abstimmtag'].sort_values()

df_tot.dtypes
df_tot[df_tot['abstimmtag'] == "20240303"].iloc[2]['url']



# checking kantonale Abstimmungen
url = base_absitmmung_url()['Kanton Zürich']
url_list = make_url_list(url, headers, SSL_VERIFY)
# i = url_list[0]
# i=url_list[2]

df_tot = pd.DataFrame()
i = url_list[0]
for i in url_list:

    print(i)
    res = get_request(i, headers, SSL_VERIFY)
    df_eidg = pd.json_normalize(res, record_path=["kantone"], meta=['abstimmtag'], errors='ignore')
    df_eidg['url'] = i
    df_tot = pd.concat([df_tot, df_eidg])


# checking kommunale Abstimmungen
url = base_absitmmung_url()['Stadt Zürich']
url_list = make_url_list(url, headers, SSL_VERIFY)

df_tot = pd.DataFrame()
i = url_list[0]
for i in url_list:

    print(i)
    res = get_request(i, headers, SSL_VERIFY)
    df_eidg = pd.json_normalize(res, record_path=["kantone"], meta=['abstimmtag'], errors='ignore')
    df_eidg['url'] = i
    df_tot = pd.concat([df_tot, df_eidg])

df_tot['abstimmtag'].sort_values()



truth = pd.read_excel("abstimmungsergebnisse/data/abstimmungsergebnisse.xlsx")
test = pd.read_excel("abstimmungsergebnisse/data/total_test.xlsx")

