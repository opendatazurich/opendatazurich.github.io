# -*- coding: utf-8 -*-

import requests
from . import errors
from . import xmlparse
from . import response

SEARCH_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<application xmlns="http://www.zetcom.com/ria/ws/module/search" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.zetcom.com/ria/ws/module/search http://docs.zetcom.com/ws/module/search/search_1_4.xsd">
  <modules>
    <module name="{module_name}">
      <search limit="{limit}" offset="{offset}">
        <fulltext>{query}</fulltext>
      </search>
    </module>
  </modules>
</application>"""


class MuseumPlusClient(object):
     def __init__(self, url=None, requests_kwargs=None):
        self.session = requests.Session()
        self.url = url
        self.params = params
        self.xmlparser = xmlparse.XMLParser()
        self.requests_kwargs = requests_kwargs or {}

    def search(self, query, limit=100, offset=1):
        data = SEARCH_TEMPLATE.format(
            module_name='Object', limit=limit, offset=offset
        )
        xml = xmlparse.parse(data.encode("utf-8"))
        xml_response = self._get_content(self.url, xml)
        return response.SearchResponse(xml_response)

    def _get_content(self, url, xml):
        try:
            headers = {'Content-Type': 'application/xml'}
            res = self.session.get(
                url,
                data=xml,
                headers=headers,
                **self.requests_kwargs
            )
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise errors.MuseumPlusError("HTTP error: %s" % e)
        except requests.exceptions.RequestException as e:
            raise errors.MuseumPlusError("Request error: %s" % e)

        return self.xmlparser.parse(res.content)