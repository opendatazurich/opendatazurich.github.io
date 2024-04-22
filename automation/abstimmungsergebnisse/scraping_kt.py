"""
This script describes how to scrape kant. Abstimmungsresultate for all political levels (kanton zh / stadt zueraich / zaehlkreise zuerich)
"""
import pandas as pd

from abstimmungsergebnisse.hilfsfunktionen import *

url = base_absitmmung_url()['Kanton Zürich']
url_list = make_url_list(url, headers, SSL_VERIFY)



i = url_list[2]
i = "https://app-prod-static-voteinfo.s3.eu-central-1.amazonaws.com/v1/ogd/sd-t-17-02-20210425-kantAbstimmung.json"





with pd.ExcelWriter("abstimmungsergebnisse/data/kant_test.xlsx") as writer:
    df_tot.to_excel(writer, sheet_name="kant", index=False)
