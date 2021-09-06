class SearchResponse(object):
    def __init__(self, xml_response):
        self.xmlparser = xmlparse.XMLParser()
        self.records = []
        self._extract_records(xml_response)

    def _extract_records(self, xml):
        new_records = []

        xml_recs = self.xmlparser.findall(xml, './sru:records/sru:record')
        for xml_rec in xml_recs:
            record = self.xmlparser.todict(xml_rec, xml_attribs=True)
            record = dict(record)
            new_records.append(record)
        self.records.extend(new_records)