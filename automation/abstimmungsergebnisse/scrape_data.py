import pandas as pd
from hilfsfunktionen import *



# TODO
# - defining columns to keep
# - row-binding all levels together
# - read out zaehlkreise data

# Eidgenössische Abstimmungen TEST
url = base_absitmmung_url()['Eidgenössisch']
url_list = make_url_list(url, headers, SSL_VERIFY)
res = get_request(url_list[0], headers, SSL_VERIFY) # eine URL entspricht einem Abstimmungstag >> kann mehrere Abstimmungen enthalten
# result = [get_request(url=u, headers=headers, verify=SSL_VERIFY) for u in url_list] # get all urls


df_kantone = pd.json_normalize(res, record_path=["schweiz", "vorlagen", "kantone"], meta=[["abstimmtag"],["schweiz", "vorlagen", "vorlagenTitel"],["schweiz", "vorlagen", "vorlagenId"]] , errors='ignore')
df_kantone.iloc[0]
df_kantone=df_kantone.astype({'geoLevelnummer':'int'},copy = True)
df_kantone = df_kantone[df_kantone['geoLevelnummer'] == 1] # subset kanton zh
df_kantone.iloc[3]

type(df_kantone["schweiz.vorlagen.vorlagenTitel"].iloc[1][0])
df_kantone["schweiz.vorlagen.vorlagenTitel"].iloc[1][0]['text']

# replacing vorlagenTitel
result_list = [df_kantone["schweiz.vorlagen.vorlagenTitel"].iloc[i][0]['text'] for i in range(len(df_kantone))]
df_kantone['schweiz.vorlagen.vorlagenTitel'] = result_list

df_kantone.index

col_trans = {"abstimmtag":"Abstimmungs_Datum",
             "vorlagenTitel":"Abstimmungs_Text",
             "anzahlStimmberechtigte":"Stimmberechtigt",
             "jaStimmenAbsolut":"Ja",
             "neinStimmenAbsolut":"Nein",
             "stimmbeteiligungInProzent":"Stimmbeteiligung (%)",
             "jaStimmenInProzent":"Ja (%)"}





## renaming columns
df_cols_old = df_kantone.columns.tolist()
r = re.compile("([^\\.]+$)")
df_cols_new = [r.search(x).group() for x in mylist]
df_col_dict = dict(map(lambda i,j : (i,j) , df_cols_old,df_cols_new))
newdf = df_kantone.rename(columns = df_col_dict)



rename_columns(df_kantone).columns

# gemeinden (Subset Zürich)
df_gemeinden = pd.json_normalize(res, record_path=["schweiz", "vorlagen", "kantone", "gemeinden"], meta=[["abstimmtag"],["schweiz", "vorlagen", "vorlagenId"]] , errors='ignore')
df_gemeinden.iloc[0]
df_gemeinden=df_gemeinden.astype({'geoLevelnummer':'int'},copy = True)
df_gemeinden = df_gemeinden[df_gemeinden['geoLevelnummer'] == 261] # subset stadt zürich zh
df_gemeinden.iloc[0]


# zaehlkreise
type(df_kantone.iloc[0])
df_kantone.columns
df_kantone.iloc[0]

l = df_kantone['zaehlkreise'].iloc[0]
l = dict(df_kantone.iloc[0]) # vorlage 1
l = pd.json_normalize(l,record_path=["zaehlkreise"])
l.iloc[0]

l['zaehlkreis']


for i in len(df_kantone):
    l = dict(df_kantone.iloc[l]) # vorlage 1
    l = pd.json_normalize(l,record_path=["zaehlkreise"])
    df_kantone[i]




######
# datasources:
# base urls geben Metadaten zu den Abstimmungen zu den Abstimmungen > beinhalten links zu einzelnen Abstimmungen
# https://ckan.opendata.swiss/api/3/action/package_show?id=echtzeitdaten-am-abstimmungstag-zu-eidgenoessischen-abstimmungsvorlagen


data = [
    {
        "state": "Florida",
        "shortname": "FL",
        "info": {"governor": "Rick Scott"},
        "counties": [
            {"name": "Dade", "population": 12345},
            {"name": "Broward", "population": 40000},
            {"name": "Palm Beach", "population": 60000},
        ],
    },
    {
        "state": "Ohio",
        "shortname": "OH",
        "info": {"governor": "John Kasich"},
        "counties": [
            {"name": "Summit", "population": 1234},
            {"name": "Cuyahoga", "population": 1337},
        ],
    },
]

result = pd.json_normalize(data, record_path = "counties", meta = ["state", "shortname", ["info", "governor"]])
result = pd.json_normalize(data, record_path = "counties")


data = {"A": [1, 2]}
pd.json_normalize(data, "A", record_prefix="Prefix.")

import json
json_file = {"name": "Jon", "last": "Jonny",
             "name": "Jimmy", "last": "johnson", "kids": [{"kidName": "johnson_junior", "kidAge": "1"}, {"kidName": "johnson_junior2", "kidAge": "4"}]}
pd.json_normalize(json_file, record_path='kids',  errors='ignore')

myDict = [{'First_Name': 'Jack', 'Last_Name': 'Smith', 'Job_Data': [{'Company': 'Amazon'}, {'Hire_Date': '2011-04-01', 'Company': 'Target'}]},
          {'First_Name': 'Jill', 'Last_Name': 'Smith'}]

myDict
df = pd.json_normalize(data=myDict, meta=['First_Name', 'Last_Name'], record_path='Job_Data')




data_list = [
    {
        "geoLevelnummer": "1",
        "geoLevelname": "Aeugst am Albis",
        "geoLevelParentnummer": "101",
        "resultat": {
            "gebietAusgezaehlt": True,
            "jaStimmenInProzent": 87.375,
            "jaStimmenAbsolut": 699,
            "neinStimmenAbsolut": 101,
            "stimmbeteiligungInProzent": 59.431900947,
            "eingelegteStimmzettel": 816,
            "anzahlStimmberechtigte": 1373,
            "gueltigeStimmen": 800
        }
    },
    {
        "geoLevelnummer": "2",
        "geoLevelname": "Affoltern am Albis",
        "geoLevelParentnummer": "101",
        "resultat": {
            "gebietAusgezaehlt": True,
            "jaStimmenInProzent": 86.943207127,
            "jaStimmenAbsolut": 3123,
            "neinStimmenAbsolut": 469,
            "stimmbeteiligungInProzent": 52.768313458,
            "eingelegteStimmzettel": 3717,
            "anzahlStimmberechtigte": 7044,
            "gueltigeStimmen": 3592
        }
    }
]

# Using dictionary comprehension to convert the list into a dictionary
result_dict = {"abstimmung": item for item in data_list}
pd.json_normalize(data=result_dict,record_path=["result"])




## fill out
df = {'Links': [{'id': 1, 'Gender': 'X'},
                {'id': 2, 'Gender': 'Y', 'listPeople': [{'Person': 'John', 'Age': 42}]}
                ]
      }

test = pd.json_normalize(df, record_path= "listPeople", errors = "ignore")

[i.update({'listPeople':[{'Person':None,'Age':None}]}) for i in df['Links'] if 'listPeople' not in i.keys()]
test = pd.json_normalize(df['Links'], record_path=['listPeople'], meta=['id','Gender'], errors = "ignore")




import requests
import pandas as pd
import hilfsfunktionen as hf
from flatten_json import flatten

headers = {'Accept': 'application/json'}
SSL_VERIFY = True
url = 'https://dam-api.bfs.admin.ch/hub/api/dam/assets/7686378/master'
data = hf.get_request(url, headers, SSL_VERIFY)

###

####
def flatten_json(y):
    out = {}
    def flatten(x, name=''):
        # If the Nested key-value
        # pair is of dict type
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        # If the Nested key-value
        # pair is of list type
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x
    flatten(y)
    return out

flat_json = flatten_json(data)

df = pd.DataFrame(data=flat_json.values(), index=flat_json.keys()).T
df.iloc[0]

df.to_csv("flatten.csv")

df[df.columns[df.columns.str.contains('(?=.*kantone)(?=.*zaehlkreise)')]]


###############################
flat_json = flatten(data)
with open('result.json', 'w') as fp:
    json.dump(flat_json, fp)

#

# get all vorlagen
# list of numbers > looping through vorlagen

# get_kanton ()
# "schweiz_vorlagen_[i]_kantone_0_geoLevelname": "Zürich"
#  > extract number after kanton_0

#


# f
flat_json.values() == "Zürich"
search_string = "Zürich"
matching_values = [key for key, value in flat_json.items() if value == search_string]
