dataset_metadata = [
    # Dataset https://data.stadt-zuerich.ch/dataset/sid_dav_verkehrszaehlung_miv_od2031
    {
    "dataset_id": "sid_dav_verkehrszaehlung_miv_od2031",
    "parquet_filename": "sid_dav_verkehrszaehlung_miv_OD2031_alle_jahre.parquet",
    "date_col": "MessungDatZeit",
    "date_format_input": "%Y-%m-%dT%H:%M:%S",
    "dtypes": {
        'MSID': str, 
        'MSName': str,
        'ZSID': str,
        'ZSName': str,
        'Achse': str,
        'HNr': str,
        'Hoehe': str, 
        'EKoord': "float64",
        'NKoord': "float64", 
        'Richtung': str, 
        'Knummer': "Int64", 
        'Kname': str, 
        'AnzDetektoren': "Int64", 
        'D1ID': str,
        'D2ID': str,
        'D3ID': str,
        'D4ID': str, 
        'MessungDatZeit': str, 
        'LieferDat': str, 
        'AnzFahrzeuge': "Int64",
        'AnzFahrzeugeStatus': str,
        },
    },
    # Dataset: https://data.stadt-zuerich.ch/dataset/ted_taz_verkehrszaehlungen_werte_fussgaenger_velo
    {
        "dataset_id": "ted_taz_verkehrszaehlungen_werte_fussgaenger_velo",
        "parquet_filename": "verkehrszaehlungen_werte_fussgaenger_velo_alle_jahre.parquet",
        #"date_col": "DATUM",
        #"date_format_input": "%Y-%m-%dT%H:%M",
        "dtypes": {
            'FK_STANDORT': "Int64", 
            'DATUM': str,
            'VELO_IN': "Int64",
            'VELO_OUT': "Int64",
            'FUSS_IN': "Int64",
            'FUSS_OUT': "Int64",
            'OST': "Int64", 
            'NORD': "Int64",
        },
    }
]
