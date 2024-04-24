"""
This script describes how to scrape kant. Abstimmungsresultate for all political levels (kanton zh / stadt zuerich / zaehlkreise zuerich)
"""

from abstimmungsergebnisse.hilfsfunktionen import *

url = base_absitmmung_url()['Stadt Zürich']
url_list = make_url_list(url, headers, SSL_VERIFY)

i = url_list[1]


with pd.ExcelWriter("abstimmungsergebnisse/data/test_error.xlsx") as writer:
    df_tot.to_excel(writer, sheet_name="kant", index=False)
