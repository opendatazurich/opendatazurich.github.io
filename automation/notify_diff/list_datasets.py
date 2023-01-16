from ckanapi import RemoteCKAN
import requests
import os

print("NO_PROXY:", os.getenv('NO_PROXY'))


session = requests.Session()
session.verify = False
#session.trust_env = 

ckan = RemoteCKAN("https://data.integ.stadt-zuerich.ch", session=session)

result = ckan.call_action("package_list")

print(result)