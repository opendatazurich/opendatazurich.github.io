import re
from xml.etree.ElementTree import Element
import defusedxml.ElementTree as etree
import xmltodict
from . import errors


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
        self.namespaces = {
        }
        self.dict_namespaces = {
            'http://www.zetcom.com/ria/ws/module': None,
        }

    def parse(self, content):
        try:
            return etree.fromstring(content)
        except Exception as e:
            raise errors.XMLParsingError("Error while parsing XML: %s" % e)

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

    def todict(self, xml, **kwargs):
        if isinstance(xml, XMLNone):
            return None
        if isinstance(xml, Element):
            xml = self.tostring(xml)

        dict_args = {
            'dict_constructor': dict,
            'process_namespaces': True,
            'namespaces': self.dict_namespaces,
            'attr_prefix': '',
            'cdata_key': 'text',
        }
        dict_args.update(kwargs)
        return dict(xmltodict.parse(xml, **dict_args))

    def namespace(self, element):
        m = re.match(r'\{(.*)\}', element.tag)
        return m.group(1) if m else ''
