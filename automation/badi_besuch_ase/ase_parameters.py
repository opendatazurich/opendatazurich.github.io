# some parameters and constants to control the ase_api_call.py

# base url for api
BASE_URL = "https://arlas.ase.solutions"
# token url for auth
TOKEN_URL = "https://identity.ase.solutions/realms/production/protocol/openid-connect/token"

# export filenames
FILEPATH_LOCATIONS = "Koordinaten.csv"
FILEPATH_COUNTER = "Badi_Besuch.csv"

# local development: if true: use proxies and do not verify requests
LOCAL_EXECUTION = False

# Laut Schnittstellenbeschreibung: Je nach Granularity kann man verschieden viele Tage abfragen
# https://arlas.ase.solutions/v2/swagger/index.html
GRANULARITY_RANGE = {
    "OneMinute": 1,
    "FiveMinutes": 5,
    "Hour": 30,
    "Day": 365,
}

# Auswahl, welche Granulatität tatsächlich verwendet wird
GRANULARITY_TO_USE = "FiveMinutes"

# locations, die in den Datensatz dürfen
VALID_LOCATIONS = [
    'Flussbad Oberer Letten',
    '(TAB) Frauenbad Stadthausquai (Bis Mai 2026)',
    'Frauenbad Stadthausquai',
    'Wärmebad Käferberg',
    '(TAB) Flussbad Unterer Letten',
    'Flussbad Unterer Letten',
    'Hallenbad Leimbach',
    'Freibad Heuried',
    'Seebad Enge - Badi Enge Gesamt',
    '(TAB) Strandbad Tiefenbrunnen (Bis Mai 2026)',
    'Strandbad Tiefenbrunnen',
    'Hallenbad City',
    'Strandbad Mythenquai',
    'Hallenbad Örlikon',
    'Seebad Utoquai - Multisensor (Neu)',
    'Seebad Utoquai',
    'Hallenbad Bungertwies',
    '(TAB) Freibad Auhof (Bis Mai 2026)',
    'Freibad Auhof',
    'Männerbad Schanzengraben',
    'Freibad Zwischen den Hölzern',
    'Schwimmbad / Park Letzigraben',
    'Freibad Allenmoos',
    '(TAB) Freibad Seebach',
    'Freibad Seebach',
    '(TAB) Flussbad Unterer Letten (Flussteil)',
    'Flussbad Unterer Letten',
    'Hallenbad Bläsi',
    'Strandbad Wollishofen',
    'Freibad Dolder',
]

# dieser Suffix wird später von den Locations entfernt
SUFFIX_TO_REMOVE = " (Bis Mai 2026)"