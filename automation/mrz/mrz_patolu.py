import os
from pprint import pprint
import museumplus
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

base_url = os.getenv('MRZ_BASE_URL')
user = os.getenv('MRZ_USER')
pw = os.getenv('MRZ_PASS')

client = museumplus.MuseumPlusClient(
    base_url=base_url,
    requests_kwargs={'auth': (user, pw)}
)

group_result = client.search(
    field='OgrNameTxt',
    value='Patolu, MAP',
    module='ObjectGroup'
)

for res in group_result:
    pprint(res)

# records = museumplus.fulltext_search(
#     base_url=base_url,
#     query='Patolu',
#     limit=1,
#     offset=0,
#     requests_kwargs={'auth': (user, pw)}
# )
# 
# for record in records:
#     pprint(record)

