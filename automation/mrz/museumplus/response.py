# -*- coding: utf-8 -*-

from . import xmlparse
from flatten_dict import flatten

ZETCOM_NS = "http://www.zetcom.com/ria/ws/module"


class SearchResponse(object):
    def __init__(self, xml_response):
        self.xmlparser = xmlparse.XMLParser()
        self.records = []
        self._extract_records(xml_response)

    def _extract_records(self, xml):
        new_records = []
        
        #print(self.xmlparser.tostring(xml))
        xml_recs = self.xmlparser.findall(xml, f'.//{{{ZETCOM_NS}}}module/{{{ZETCOM_NS}}}moduleItem')
        for xml_rec in xml_recs:

            print(self.xmlparser.tostring(xml_rec))
            record = {
                'hasAttachments': self.xmlparser.find(xml_rec, f'./{{{ZETCOM_NS}}}hasAttachments').text,
                'ObjObjectNumberGrp': self.xmlparser.find(xml_rec, './recordSchema').text,
                'ObjObjectTitleGrp': '',
                'ObjPerAssociationRef': '',
                'ObjGeograficGrp': '',
                'ObjDateGrp': '',
                'ObjDimAllGrp': '',
                'ObjMaterialTechniqueGrp': '',
                'ObjMuseumCollectionVoc': '',
                'ObjCreditlineGrp': '',
                'ObjOwnershipDEDpl': '',
                'ObjBriefDescriptionClb': '',
                'ObjLiteratureRef': '',
                'MulPhotocreditTxt': '',
            }
            record['raw'] = self.xmlparser.todict(xml_rec, xml_attribs=True)
            #record.pop('xmlns', None)
            #record = self._clean_dict(record)
            new_records.append(record)
        self.records.extend(new_records)

    def _clean_dict(self, record_data):
        # check if there is only one element on the top level
        keys = list(record_data.keys())
        if len(record_data) == 1 and len(keys) > 0 and len(record_data[keys[0]]) > 0:
            record_data = record_data[keys[0]]

        return record_data

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
