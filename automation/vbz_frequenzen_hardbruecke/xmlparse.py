import re
import defusedxml.ElementTree as etree


class XMLParseError(Exception):
   pass


class XMLNone(object):
    def __nonzero__(self):
        return False

    def __bool__(self):
        return False

    def iter(self):
        return []

    text = None


class XMLParser(object):
    def __init__(self):
        self.namespaces = {}

    def parse(self, content):
        try:
            return etree.fromstring(content)
        except Exception as e:
            raise XMLParseError("Error while parsing XML: %s" % e)

    def find(self, xml, path):
        if isinstance(path, list):
            for p in path:
                elem = self.find(xml, p)
                if not isinstance(elem, XMLNone):
                    return elem
            return XMLNone()
        elem = xml.find(path, self.namespaces)
        if elem is None:
            return XMLNone()
        return elem

    def findall(self, xml, path):
        return xml.findall(path, self.namespaces)

    def tostring(self, xml):
        return etree.tostring(xml)

    def namespace(self, element):
        m = re.match(r'\{(.*)\}', element.tag)
        return m.group(1) if m else ''

