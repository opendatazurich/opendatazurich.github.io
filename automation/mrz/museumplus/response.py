# -*- coding: utf-8 -*-

from . import xmlparse

ZETCOM_NS = "http://www.zetcom.com/ria/ws/module"


class SearchResponse(object):
    def __init__(self, xml_response):
        self.xmlparser = xmlparse.XMLParser()
        self.records = []
        self._extract_records(xml_response)

    def _extract_records(self, xml):
        new_records = []

        xml_recs = self.xmlparser.findall(xml, f'.//{{{ZETCOM_NS}}}module/{{{ZETCOM_NS}}}moduleItem')
        for xml_rec in xml_recs:
            record = self.xmlparser.todict(xml_rec, xml_attribs=True)
            record = dict(record)
            new_records.append(record)
        self.records.extend(new_records)

    def __repr__(self):
        try:
            return (
                'SearchResponse('
                'count=%r)'
                ) % (
                   len(self.records),
                )
        except AttributeError:
            return 'SearchResponse(empty)'

    def __len__(self):
        return len(self.records)

    def __iter__(self):
        yield from self.records

    def __getitem__(self, key):
        return self.records[key]
