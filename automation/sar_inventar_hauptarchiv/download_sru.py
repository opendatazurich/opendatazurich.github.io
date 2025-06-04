import sruthi
import pandas as pd
from bs4 import BeautifulSoup
import requests


def scrape_doc_url(record):
    """
    API does not return direct download urls and file name. So, we try to scrape them from the website.
    """
    # get additional info from link
    r = requests.get(record['extra']['link'])
    soup = BeautifulSoup(r.text, 'html.parser')
    pdf_link = soup.find('td', {'class': 'veXDetailAttributLabel'}, string="Dateien:") \
                .next_sibling \
                .find('a')
    pdf_path = pdf_link['href'].replace("JavaScript:openDoc('", '').replace("');", "")
    download_url = f"https://amsquery.stadt-zuerich.ch/{pdf_path}"
    pdf_name = pdf_link.string
    return download_url, pdf_name

def make_row(row_dict):
    """
    Tries to find download url and file name, if there are digitized items.
    Defines which fields are transferred from the API.
    Returns pandas compatible row.

    Legt fest, welche Spalten mit welchem Spaltennamen übernommen werden.
    """
    # suche nach PDF url, falls vorhanden:
    if row_dict['extra']['hasDigitizedItems']=='1':
        try:
            download_url, pdf_name = scrape_doc_url(row_dict)
        except Exception as e:
            print(e)
            download_url = ""
            pdf_name = ""
    else:
        download_url = ""
        pdf_name = ""

    row = {
        'signatur': [row_dict['reference']],
        'titel': [row_dict['title']],
        'jahr': [row_dict['date']],
        'stufe': [row_dict['descriptionlevel']],
        'link_query': [row_dict['extra']['link']],
        'hasDigitizedItems': [row_dict['extra']['hasDigitizedItems']],
        'dateiname': pdf_name,
        'download_url': [download_url],
    }
    return row


def sort_signature(df, signature_col='signatur', split_regex=r'[.:]',zfill_width=4):
    """
    Sorting the :df by :signature_col.
    Values in :signature_col consist of character-number combinations like v.A.A.80.:2.129.
    The function will split the col by split_regex in new columns and fill the new columns
    with zeros from the left. The new columns will be used to sort the df and then be dropped.
    Returns the sorted df
    """
    # split the col
    df_sort = df[signature_col].str.split(split_regex, expand=True).fillna(pd.NA).replace("",pd.NA)
    # fill cols with zeros
    for col in df_sort.columns:
        df_sort[col] = df_sort[col].str.zfill(zfill_width)
    
    # merge sort colums to df
    merge = pd.concat([df,df_sort], axis=1)
    # sort by sort columns
    merge = merge.sort_values(list(df_sort.columns), na_position='first')
    # drop sort columns
    merge = merge.drop(columns=df_sort.columns)

    # return sorted df
    return merge

def create_search_strings():
    """
    Creating Search strings for SRU API at https://amsquery.stadt-zuerich.ch/SRU/.
    Using different levels, based on the signature (reference)
    """
    
    level1 = ["V"]
    level2 = ["A","B","C","D","E","F","G","H","J","J.P","J.W","K","L"]
    level3 = ["a","b","c"]
    search_strings = []
    for i in level1:
        for j in level2:
            for k in level3:
                search_string = f"{i}.{j}.{k}."
                search_strings.append(search_string) 
    
    return search_strings



############ Start Downloading ########################

# empty dataframe to gather the data
df = pd.DataFrame()

search_strings = create_search_strings()

for search_string in search_strings:
    print(search_string)
    # = entspricht der Feldsuche mit Operator "enthält" 
    # == und exact sind synonym und entsprechen der Feldsuche mit Operator "beginnt mit" 
    records = sruthi.searchretrieve(
        'https://amsquery.stadt-zuerich.ch/SRU/',
        query=f'''isad.reference == "{search_string}" ''' #"isad.reference = V.B.b.43.:1 AND isad.descriptionlevel = Dossier"
    )
    print(records)
    if records.count >=1500:
        print("VORSICHT: Suchergebniss hat mehr als 1500 Ergebnisse:", records.count)

    if records.count ==0:
        print("Keine Ergebnisse für Anfrage", f'''isad.reference == "{search_string}" ''', "weiter mit nächster")
        continue
    
    for record in records:
        df = df._append(pd.DataFrame(make_row(record)), ignore_index=True)

df = df.drop_duplicates()
df = sort_signature(df)
filepath_out = "download_sru" 
#df.to_csv(f'{filepath_out}.csv', index=False)
#df.to_excel(f'{filepath_out}.xlsx', index=False)

print(f"Schreibe {filepath_out}.parquet mit {df.shape[0]} Zeilen")
df.to_parquet(f'{filepath_out}.parquet', index=False)

print(df)
