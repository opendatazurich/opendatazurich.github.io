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
assert len(group_result) == 1, "More than one ObjectGroup found"
group = group_result[0]

ref = group['moduleItem']['moduleReference']
for ref_item in ref['moduleReferenceItem'][:1]:
    print(ref_item)
    print(ref['targetModule'])
    item = client.module_item(ref_item['moduleItemId'], ref['targetModule'])
    pprint(item)
    if item['hasAttachments'] == 'true':
        client.download_attachment(ref_item['moduleItemId'], ref['targetModule'])

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

