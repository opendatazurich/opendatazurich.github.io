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

            record = self._map_xml(xml_rec)
            record['raw'] = self.xmlparser.todict(xml_rec, xml_attribs=True)
            new_records.append(record)
        self.records.extend(new_records)

    def _map_xml(self, xml_rec):
        def xml_text(xpath):
            return self.xmlparser.find(xml_rec, xpath).text

        def xml_group(xpath, sep='; '):
            groups =  self.xmlparser.findall(xml_rec, xpath)
            return sep.join([g.text for g in groups])

        record = {
            'hasAttachments': xml_rec.attrib['hasAttachments'],
            'ObjObjectNumberTxt': xml_text(
                f".//{{{ZETCOM_NS}}}dataField[@name='ObjObjectNumberTxt']/{{{ZETCOM_NS}}}value"
            ),
            'ObjObjectTitleGrp': xml_text(
                f".//{{{ZETCOM_NS}}}repeatableGroup[@name='ObjObjectTitleGrp']"
                f"//{{{ZETCOM_NS}}}dataField[@name='TitleTxt']"
                f"//{{{ZETCOM_NS}}}value"
            ),
            'ObjPerAssociationRef': xml_text(
                f".//{{{ZETCOM_NS}}}moduleReference[@name='ObjPerAssociationRef']"
                f"/{{{ZETCOM_NS}}}moduleReferenceItem"
                f"/{{{ZETCOM_NS}}}formattedValue"
            ),
            'ObjGeograficGrp': xml_text(
                f".//{{{ZETCOM_NS}}}repeatableGroup[@name='ObjGeograficGrp']"
                f"//{{{ZETCOM_NS}}}vocabularyReference[@name='PlaceVoc']"
                f"//{{{ZETCOM_NS}}}formattedValue"
            ),
            'ObjDateTxt': xml_text(
                f".//{{{ZETCOM_NS}}}dataField[@name='ObjDateTxt']/{{{ZETCOM_NS}}}value"
            ),
            'ObjDimAllGrp': xml_text(
                f".//{{{ZETCOM_NS}}}repeatableGroup[@name='ObjDimAllGrp']"
                f"//{{{ZETCOM_NS}}}virtualField[@name='PreviewVrt']"
                f"//{{{ZETCOM_NS}}}value"
            ),
            'ObjMaterialTechniqueGrp': xml_text(
                f".//{{{ZETCOM_NS}}}repeatableGroup[@name='ObjMaterialTechniqueGrp']"
                f"//{{{ZETCOM_NS}}}dataField[@name='DetailsTxt']"
                f"//{{{ZETCOM_NS}}}value"
            ),
            'ObjCreditlineGrp': xml_text(
                f".//{{{ZETCOM_NS}}}repeatableGroup[@name='ObjCreditlineGrp']"
                f"//{{{ZETCOM_NS}}}dataField[@name='CreditlineTxt']"
                f"//{{{ZETCOM_NS}}}value"
            ),
            'ObjOwnershipRef': xml_group(
                f".//{{{ZETCOM_NS}}}moduleReference[@name='ObjOwnershipRef']"
                f"/{{{ZETCOM_NS}}}moduleReferenceItem"
                f"/{{{ZETCOM_NS}}}formattedValue"
            ),
            'ObjScientificNotesClb': xml_text(
                f".//{{{ZETCOM_NS}}}dataField[@name='ObjScientificNotesClb']/{{{ZETCOM_NS}}}value"
            ),
            'ObjLiteratureRef': xml_text(
                f".//{{{ZETCOM_NS}}}moduleReference[@name='ObjLiteratureRef']"
                f"/{{{ZETCOM_NS}}}moduleReferenceItem"
                f"/{{{ZETCOM_NS}}}formattedValue"
            ),
            'ObjMultimediaRef': xml_text(
                f".//{{{ZETCOM_NS}}}moduleReference[@name='ObjMultimediaRef']"
                f"/{{{ZETCOM_NS}}}moduleReferenceItem"
                f"/{{{ZETCOM_NS}}}formattedValue"
            ),
        }
        return record

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
