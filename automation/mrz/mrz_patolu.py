import os
from pprint import pprint
import museumplus
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

user = os.getenv('MRZ_USER')
pw = os.getenv('MRZ_PASS')
auth = (user, pw)

records = museumplus.search(
    url='https://mpzurichrietberg.zetcom.com/MpWeb-mpZurichRietberg/ria-ws/application/module/Object/search',
    query='Patolu',
    limit=1,
    offset=0,
    requests_kwargs={'auth': auth}
)

for record in records:
    pprint(record)

