import os
from pprint import pprint
import museumplus
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

search_url = f"{os.getenv('MRZ_BASE_URL')}/ria-ws/application/module/Object/search"
user = os.getenv('MRZ_USER')
pw = os.getenv('MRZ_PASS')

records = museumplus.search(
    url=search_url,
    query='Patolu',
    limit=1,
    offset=0,
    requests_kwargs={'auth': (user, pw)}
)

for record in records:
    pprint(record)

