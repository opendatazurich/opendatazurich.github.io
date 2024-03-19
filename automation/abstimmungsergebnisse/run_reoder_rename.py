# Select Rows and Columns of Interest 
# Rename and Reorder Columns 

from parameter_function import *
from scraping_function import *

pol_nr, pol_name, wahl_nr, wahl_name = rename_pol_and_wahlkreis('eidg', 'zaehlkreis')

result = scraping('gemeinde')

print(result.columns)

# Rename Columns
result = result.rename(columns={
    "abstimmtag": "Abstimmungs_Datum",
    "text": "Abstimmungs_Text",
    "geoLevelname": "Name_Resultat_Gebiet",
    "geoLevelnummer": "Nr_Resultat_Gebiet",
    "resultat.anzahlStimmberechtigte": "Stimmberechtigt",
    "resultat.jaStimmenAbsolut": "Ja",
    "resultat.neinStimmenAbsolut": "Nein",
    "resultat.stimmbeteiligungInProzent": "Stimmbeteiligung (%)",
    "resultat.jaStimmenInProzent": "Ja (%)"
})

# Create missing variables
result["Nein (%)"] = 100 - result["Ja (%)"]
result["StaendeJa"] = result["staende.jaStaendeGanz"] + result["staende.jaStaendeHalb"]
result["StaendeNein"] = result["staende.neinStaendeGanz"] + result["staende.neinStaendeHalb"]
result["Nr_Politische_Ebene"] = pol_nr
result["Name_Politische_Ebene"] = pol_name

result["Nr_Wahlkreis_StZH"] = wahl_nr
result["Name_Wahlkreis_StZH"] = wahl_name
# wahlkreis(result)

# Order Columns
cols = [
    "Abstimmungs_Datum",
    "Nr_Politische_Ebene",
    "Name_Politische_Ebene",
    "Abstimmungs_Text",
    "Nr_Resultat_Gebiet",
    "Name_Resultat_Gebiet",
    "Nr_Wahlkreis_StZH",
    "Name_Wahlkreis_StZH",
    "Stimmberechtigt",
    "Ja",
    "Nein",
    "Stimmbeteiligung (%)",
    "Ja (%)",
    "Nein (%)",
    "StaendeJa",
    "StaendeNein"
]

df = result[cols]
df.to_csv('C:/Projekte/GitLab/abstimmungs_scraper/eidg_gmd.csv', index=False)
