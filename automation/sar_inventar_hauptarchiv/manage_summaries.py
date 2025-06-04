import os
import time
import pandas as pd
import summarize_text
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

############################################################################################
# Simple script to merge existing summaries to the new dataset
# if there are missing summaries, try to make them via an LLM API call
# in summarize_text.py there functions for several apis (hugging face, openai, google)
############################################################################################


google_api_key = os.getenv('GOOGLE_API')


print("Lade aktuelles Inventar")
download_sru = pd.read_parquet("download_sru.parquet")
print("-->", download_sru.shape[0], "Zeilen")

print("Lade bestehende Zusammenfassungen von CKAN")
download_ckan = pd.read_parquet("https://data.stadt-zuerich.ch/dataset/sar_inventar_hauptarchiv/download/sar_inventar_hauptarchiv.parquet")
existing_summaries = download_ckan[['download_url', 'zusammenfassung']].dropna()
print("-->", existing_summaries.shape[0], "Zeilen mit Zusammenfassungen")

print("Join bestehende Zusammenfassungen")
output_df = download_sru.merge(existing_summaries, how='left', on='download_url')
print("-->", output_df.shape[0], "Zeilen")

# remove a summary to test summary generation
output_df.loc[output_df['download_url']=='https://amsquery.stadt-zuerich.ch/Dateien/30/D152436.pdf','zusammenfassung'] = pd.NA

print("Filtere fehlende Zusammenfassungen")
datasets_without_summary = output_df[(output_df['download_url'].notna())&(output_df['zusammenfassung'].isna())]
print(datasets_without_summary)

count_datasets_without_summary = datasets_without_summary.shape[0]
if count_datasets_without_summary > 0:
    print(f"Es gibt {count_datasets_without_summary} Dokumente ohne Zusammenfassungen")

    print("Verbinde mit AI Client")
    client = summarize_text.connect_google_client(google_api_key)

    print("Erstelle Zusammenfassungen")
    for index, row in datasets_without_summary.iterrows():
        print("-----------------------------------------------------")
        doc_url = row['download_url']
        print(doc_url)
        doc_filename = 'pdf_download.pdf'
        doc_type = row['dateiname'].split('_')[0]
        print("Dokumententyp:", doc_type)
        try:
            output_message = summarize_text.google_client_call(doc_url, doc_filename, client, doc_type)
        except Exception as e:
            # show error message (mostly because doc is too large)
            print(e)
            output_message = pd.NA
        print(output_message)
        output_df.loc[index, 'zusammenfassung'] = output_message
        # wait because of api restrictions
        time.sleep(4)
else:
    print("Zusammenfassungen zu allen downloadbaren Dokumenten sind vorhanden. Es keine keine neuen erstellt")

output_filename = 'sar_inventar_hauptarchiv'
ouptut_cols = ['signatur', 'titel', 'jahr', 'stufe', 'link_query', 'dateiname', 'download_url', 'zusammenfassung']
print(f"Schreibe {output_filename}.parquet")
output_df[ouptut_cols].to_parquet(f"{output_filename}.parquet", index=False)
print(f"Schreibe {output_filename}.csv")
output_df[ouptut_cols].to_csv(f"{output_filename}.csv", index=False)